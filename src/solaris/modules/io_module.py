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

Subscribes to: MeaningEvent, Push.
Publishes:     Desire, Action.
"""

from __future__ import annotations

import time

from solaris.modules.base import Module
from solaris.runtime.signals import Action, Desire, MeaningEvent, Push


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
        self._last_meaning: MeaningEvent | None = None
        self._last_push: Push | None = None
        self.state = {
            "desires": 0,
            "actions": 0,
            "action_threshold": action_threshold,
        }

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

        if motivation * confidence >= self.action_threshold:
            action = Action(
                origin=self.name,
                name=desire.proposal,
                payload={
                    "motivation": round(motivation, 3),
                    "confidence": round(confidence, 3),
                },
            )
            self.state["actions"] += 1
            await self.bus.publish(action)

        # Consume the pair so the same stimulus is not turned into
        # multiple Desires.
        self._last_meaning = None
        self._last_push = None
