"""
Ego — the necessary illusion.

CONCEPTS.md:

    EGO is a necessary (forced) illusion (it is false, what is then
    a mathematical belief?)
    > Limits (boundaries) build definitions (shapes)
    > Reverse definition of Self (from hypothetical everything,
      Cut)
    > So WILL (illusory, connected to ego) comes from a Complexity
      of Stimuli, but moreover from an ABSENCE
      ('I do exist!' / Choice)

Ego is constructed; it is not a primitive. It is the running
synthesis of two streams:

    - affirmations  — absence-stimuli emitted by AION ('I exist!')
    - distinctions  — distinct meanings emitted by Cognition,
                      each one a 'cut' that distinguishes self
                      from not-self.

The Ego module reports a self_strength scalar via MapUpdate to the
Inner MAP. It is deliberately a scalar — Ego is one number, not a
graph, because that is the whole point of the illusion: a unified
self that the system can refer to.

Subscribes to: Stimulus (only is_absence=True), MeaningEvent.
Publishes:     MapUpdate(key='ego.self', ...).
"""

from __future__ import annotations

from solaris.modules.base import Module
from solaris.runtime.signals import MapUpdate, MeaningEvent, Stimulus


class Ego(Module):
    name = "ego"

    def __init__(self, conscience) -> None:
        super().__init__(conscience)
        self.affirmations = 0
        self.distinctions = 0
        self.state = {"affirmations": 0, "distinctions": 0, "self_strength": 0.0}

    async def start(self) -> None:
        self.bus.subscribe(Stimulus, self._on_stimulus)
        self.bus.subscribe(MeaningEvent, self._on_meaning)

    async def _on_stimulus(self, sig: Stimulus) -> None:
        if not sig.is_absence:
            return
        self.affirmations += 1
        self.state["affirmations"] = self.affirmations
        await self._publish_self()

    async def _on_meaning(self, sig: MeaningEvent) -> None:
        if sig.meaning == "self.exists":
            return
        self.distinctions += 1
        self.state["distinctions"] = self.distinctions

    async def _publish_self(self) -> None:
        strength = self.affirmations + 0.1 * self.distinctions
        self.state["self_strength"] = round(strength, 3)
        await self.bus.publish(MapUpdate(
            origin=self.name,
            key="ego.self",
            value={
                "affirmations": self.affirmations,
                "distinctions": self.distinctions,
                "strength": strength,
            },
        ))
