"""
I/O Module — linking builder.

MODULES.md: 'Input-Output Module — Linking builder.'

I/O is where the spine of the system closes. It consumes
MeaningEvent (what the system knows about an input) and Push (what
the system must do) and produces Desire, then optionally Action.

Decision rule:

  1. Form a Desire when MeaningEvent and Push are both present in
     a short window. Without both, no Desire (Will = Need).
  2. Habit biases the Desire's motivation: frequently-rewarded
     meanings raise it; punished ones drop it.
  3. Confidence starts as 1 - novelty. If too low, hand to
     Uncertainty.
  4. Commit to Action only when motivation * confidence clears
     action_threshold. Otherwise the Desire dies — a Will that
     does not become an Action (CONCEPTS.md, no real free will).

action_threshold is a *rewriteable* parameter — Auto-Regeneration
adjusts it based on Backpropagation feedback.

SIC -> RO (Specific Input Consequence -> Relevant Output): every
committed Action is *typed* — physical / mental / physicomental —
via a small SIC table keyed on modality (operator-seeded, Habit-
reweighted). A `physical` (or physicomental) act performs a tiny,
bounded, real computation on the substrate, so it shows up in the
resource stats: the body acting on its own body. Relevance is an
entropy quantity: Logos-fracture x SIC-determinacy.

Limitations from Negation ("NO") *filter* RO: a forbidden meaning's
Desire dies before becoming an Action (unless Activate suspends the
Limitation).

Subscribes to: MeaningEvent, Push.
Publishes:     Desire, Action (typed).
"""

from __future__ import annotations

import time

from solaris.modules.base import Module
from solaris.runtime.signals import Action, Desire, MeaningEvent, Push

# SIC seed: modality -> Relevant-Output type. Default is "mental".
SIC_SEED: dict[str, str] = {
    "threat":   "physical",        # survival acts on the world
    "tactile":  "physical",
    "external": "physical",
    "vision":   "mental",
    "audio":    "physicomental",   # heard -> uttered
    "absence":  "mental",
    "oneiric":  "mental",          # dreams act inwardly
}


class IOModule(Module):
    name = "io_module"

    def __init__(
        self,
        conscience,
        action_threshold: float = 0.3,
        window: float = 0.3,
    ) -> None:
        super().__init__(conscience)
        self.action_threshold = action_threshold
        self.window = window
        self.sic: dict[str, str] = dict(SIC_SEED)
        self._last_meaning: MeaningEvent | None = None
        self._last_push: Push | None = None
        self.state = {
            "desires": 0,
            "actions": 0,
            "forbidden": 0,
            "action_threshold": action_threshold,
        }

    def set_sic(self, modality: str, output_type: str) -> None:
        """Operator override of a SIC binding."""
        self.sic[modality] = output_type

    def _output_type(self, meaning: str) -> tuple[str, float]:
        """Return (output_type, sic_determinacy) for a meaning.

        meaning is '{modality}/{type}/{body}' or 'self.exists'.
        """
        modality = meaning.split("/", 1)[0]
        if modality in self.sic:
            return self.sic[modality], 1.0
        return "mental", 0.5

    @staticmethod
    def _perform_physical() -> None:
        """A tiny, bounded substrate act — real CPU, harmless, visible."""
        total = 0
        for i in range(20000):
            total += i * i
        return None

    async def start(self) -> None:
        self.bus.subscribe(MeaningEvent, self._on_meaning)
        self.bus.subscribe(Push, self._on_push)

    async def _on_meaning(self, sig: MeaningEvent) -> None:
        self._last_meaning = sig
        await self._maybe_link()

    async def _on_push(self, sig: Push) -> None:
        self._last_push = sig
        await self._maybe_link()

    async def _maybe_link(self) -> None:
        m, p = self._last_meaning, self._last_push
        if m is None or p is None:
            return
        if time.monotonic() - max(m.timestamp, p.timestamp) > self.window:
            return

        bias = self.conscience.habit.bias_for(m.meaning)
        motivation = max(0.0, min(1.0, p.intensity * (1.0 + bias)))
        confidence = 1.0 - m.novelty
        if confidence < 0.3:
            confidence = self.conscience.uncertainty.resolve(m.meaning, confidence)

        desire = Desire(
            origin=self.name,
            proposal=f"react_to:{m.meaning}",
            motivation=motivation,
            confidence=confidence,
        )
        self.state["desires"] += 1
        self.state["action_threshold"] = round(self.action_threshold, 3)
        await self.bus.publish(desire)

        # Negation ("NO") filters RO: a forbidden meaning's Desire
        # dies before becoming an Action (unless Activate suspends it).
        neg = getattr(self.conscience, "negation", None)
        forbidden = neg is not None and neg.is_forbidden(m.meaning)

        if not forbidden and motivation * confidence >= self.action_threshold:
            out_type, determinacy = self._output_type(m.meaning)
            if out_type in ("physical", "physicomental"):
                self._perform_physical()
            # Relevance is an entropy quantity: fracture x SIC-determinacy.
            fracture = self.conscience.logos.state.get("fracture", 0.0)
            relevance = round(fracture * determinacy, 3)
            action = Action(
                origin=self.name,
                name=desire.proposal,
                payload={
                    "motivation": round(motivation, 3),
                    "confidence": round(confidence, 3),
                    "output_type": out_type,
                    "relevance": relevance,
                },
            )
            self.state["actions"] += 1
            await self.bus.publish(action)
        elif forbidden:
            self.state["forbidden"] += 1

        # Consume the pair so the same stimulus is not turned into
        # multiple Desires.
        self._last_meaning = None
        self._last_push = None
