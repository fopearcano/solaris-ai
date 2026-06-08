"""
Instinct — React as a basic reflex, sublimated by Logic.

React is, at bottom, an **instinct** — *a strict response to a
stimulus* — a hardwired reflex that fires by itself, before any
deliberation. **Logic then sublimates it**: Logos / Habit (later the
NN) do not delete the reflex but refine and override it as experience
accumulates.

On every committed Action, Instinct emits an automatic Reaction whose
valence is:

  reflex      — innate, from survival-grounded cues (threat is bad,
                self-affirmation is good; low vitality colours
                everything darker);
  sublimated  — the reflex blended toward the *learned* valence (Habit)
                in proportion to how much Logic already knows the
                meaning. Early life = pure reflex; later = considered
                reaction.

The operator's React button is then a *manual override* of this
instinct — the same status the metabolic buttons already hold.

Subscribes to: Action.
Publishes:     Reaction(origin='instinct').
"""

from __future__ import annotations

from solaris.modules.base import Module
from solaris.runtime.signals import Action, Reaction


class Instinct(Module):
    name = "instinct"

    def __init__(self, conscience) -> None:
        super().__init__(conscience)
        self.state = {
            "reactions": 0, "reflex": 0.0,
            "sublimated": 0.0, "sublimation": 0.0,
        }

    async def start(self) -> None:
        self.bus.subscribe(Action, self._on_action)

    @staticmethod
    def _meaning_of(action: Action) -> str:
        n = action.name or ""
        return n[len("react_to:"):] if n.startswith("react_to:") else n

    def _reflex(self, meaning: str) -> float:
        """The strict, innate response to a stimulus."""
        m = meaning.lower()
        if "threat" in m:
            v = -0.8
        elif "escape" in m:
            v = -0.2
        elif m == "self.exists":
            v = 0.3
        else:
            v = 0.1                       # mild engagement with the world
        # Low vitality colours everything darker (feeling endangered).
        vit = self.conscience.safety.vitality
        if vit < 0.4:
            v -= (0.4 - vit)
        return max(-1.0, min(1.0, v))

    async def _on_action(self, sig: Action) -> None:
        meaning = self._meaning_of(sig)
        reflex = self._reflex(meaning)
        # Sublimation by Logic: blend toward the learned valence (Habit)
        # in proportion to how much Logic already knows this meaning.
        learned = self.conscience.habit.bias_for(meaning)
        k = min(0.8, abs(learned))        # how confident Logic is
        sublimated = max(-1.0, min(1.0, (1 - k) * reflex + k * learned))
        self.state["reactions"] += 1
        self.state["reflex"] = round(reflex, 3)
        self.state["sublimated"] = round(sublimated, 3)
        self.state["sublimation"] = round(abs(sublimated - reflex), 3)
        await self.bus.publish(Reaction(
            origin="instinct", action_id=sig.id, valence=sublimated))
