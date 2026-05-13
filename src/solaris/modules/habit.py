"""
Habit — reinforcement.

MODULES.md:

    HABIT PROCESS
    - Capacity (++) builder
    - = to Reinforcement learning

Habit holds a per-meaning bias scalar in [-1, +1]. When a Reaction
follows an Action whose triggering meaning is recorded, the bias
is moved toward valence. Synthesis can later prune entries with
small magnitudes (subtraction). When a bias crosses one of two
notable thresholds (+0.5 or -0.5) it is published to the Inner MAP
as a *boundary-shaping* fact — Habit is, per MODULES.md, 'forcing
a Boundary'.

Subscribes to: Action (to remember its triggering meaning),
               Reaction (to update the bias for that meaning).
Publishes:     MapUpdate(key='habit:<meaning>', value=score) on
               threshold crossings.
Provides:      .bias_for(meaning), .prune_below(threshold).
"""

from __future__ import annotations

from solaris.modules.base import Module
from solaris.runtime.signals import Action, MapUpdate, Reaction


class Habit(Module):
    name = "habit"

    def __init__(self, conscience, lr: float = 0.2) -> None:
        super().__init__(conscience)
        self.lr = lr
        self.weights: dict[str, float] = {}
        self._action_meaning: dict[int, str] = {}
        self.state = {"weights": 0, "strong": 0}

    async def start(self) -> None:
        self.bus.subscribe(Action, self._on_action)
        self.bus.subscribe(Reaction, self._on_reaction)

    async def _on_action(self, sig: Action) -> None:
        # I/O uses 'react_to:<meaning>' as the action name.
        if sig.name.startswith("react_to:"):
            self._action_meaning[sig.id] = sig.name[len("react_to:"):]

    async def _on_reaction(self, sig: Reaction) -> None:
        meaning = self._action_meaning.pop(sig.action_id, None)
        if meaning is None:
            return
        old = self.weights.get(meaning, 0.0)
        new = max(-1.0, min(1.0, old + self.lr * sig.valence))
        self.weights[meaning] = new
        self.state["weights"] = len(self.weights)
        self.state["strong"] = sum(1 for v in self.weights.values() if abs(v) > 0.5)
        # Publish on threshold crossings — these are the moments
        # where Habit forces a Boundary into the Inner MAP.
        if (old < 0.5 <= new) or (old > -0.5 >= new):
            await self.bus.publish(MapUpdate(
                origin=self.name,
                key=f"habit:{meaning}",
                value=round(new, 3),
            ))

    def bias_for(self, meaning: str) -> float:
        return self.weights.get(meaning, 0.0)

    def prune_below(self, abs_threshold: float) -> int:
        before = len(self.weights)
        self.weights = {
            k: v for k, v in self.weights.items() if abs(v) >= abs_threshold
        }
        self.state["weights"] = len(self.weights)
        return before - len(self.weights)
