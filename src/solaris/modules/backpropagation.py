"""
Backpropagation — plasticity.

MODULES.md: 'BACKPROPAGATION — Plasticity.'

Whitepaper: 'Continuously refines the AI's cognitive and functional
structures.'

We model plasticity at the *system* level rather than the weight
level: when a Reaction with strong negative valence arrives,
Backprop walks back through the recent bus trace and identifies
which modules' Signals contributed to the action that earned the
Reaction. Those modules accumulate a negative adjustment, which
Auto-Regeneration later reads to adjust their rewriteable
parameters.

This is not gradient descent. It is the *concept* of
backpropagation translated into the language of a non-hierarchical
modular network: 'who do we hold responsible, and by how much?'.

Subscribes to: Reaction.
Publishes:     MapUpdate(key='backprop:<module>', value=adjustment).
"""

from __future__ import annotations

from solaris.modules.base import Module
from solaris.runtime.signals import MapUpdate, Reaction


class Backpropagation(Module):
    name = "backpropagation"

    def __init__(self, conscience, look_back: int = 12, lr: float = 0.1) -> None:
        super().__init__(conscience)
        self.look_back = look_back
        self.lr = lr
        self.adjustments: dict[str, float] = {}
        self.state = {"adjustments": 0}

    async def start(self) -> None:
        self.bus.subscribe(Reaction, self._on_reaction)

    async def _on_reaction(self, sig: Reaction) -> None:
        if sig.valence >= -0.2:
            return  # only propagate from clearly negative reactions
        recent = self.bus.trace[-self.look_back:]
        contributors = {
            s.origin for s in recent
            if s.origin and s.origin not in {"environment", self.name}
        }
        for module in contributors:
            old = self.adjustments.get(module, 0.0)
            new = old + self.lr * sig.valence
            self.adjustments[module] = new
            await self.bus.publish(MapUpdate(
                origin=self.name,
                key=f"backprop:{module}",
                value=round(new, 3),
            ))
        self.state["adjustments"] = len(self.adjustments)
