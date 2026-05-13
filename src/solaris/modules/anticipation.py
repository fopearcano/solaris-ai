"""
Anticipation — forecast capacity.

CONCEPTS.md:

    Hypothesis: BEING PREY (evolutionary disadvantage, always
    technological)
    > Need of POWER => Anticipation Need (forecast)
    ...
    > IMAGINATION is structurally related to the ANTICIPATION
      CAPACITY (forecast) of increasing Mechanical Capacity / Usage
      (quantitative) of the objects of the world

Anticipation is the simplest possible forecaster: a first-order
transition table over recent meanings. Each MeaningEvent is logged
against the previous one; on the next MeaningEvent, Anticipation
checks whether its prediction was right.

  - Hit  -> contributes to Logos.division (data was present and
            correct: rationality is rewarded).
  - Miss -> raises Mysterium pressure (the unknown grows).

Subscribes to: MeaningEvent.
Publishes:     nothing — its outputs are nudges to Logos and
               Mysterium.
"""

from __future__ import annotations

from solaris.modules.base import Module
from solaris.runtime.signals import MeaningEvent


class Anticipation(Module):
    name = "anticipation"

    def __init__(self, conscience) -> None:
        super().__init__(conscience)
        self._last: str | None = None
        self._predicted: str | None = None
        self.transitions: dict[str, dict[str, int]] = {}
        self.state = {"hits": 0, "misses": 0}

    async def start(self) -> None:
        self.bus.subscribe(MeaningEvent, self._on_meaning)

    async def _on_meaning(self, sig: MeaningEvent) -> None:
        if self._predicted is not None:
            if self._predicted == sig.meaning:
                self.state["hits"] += 1
                self.conscience.logos.add_division(0.1)
            else:
                self.state["misses"] += 1
                self.conscience.mysterium.pressure = min(
                    1.0, self.conscience.mysterium.pressure + 0.05
                )
        if self._last is not None:
            row = self.transitions.setdefault(self._last, {})
            row[sig.meaning] = row.get(sig.meaning, 0) + 1
        self._last = sig.meaning
        self._predicted = self._predict_next(sig.meaning)

    def _predict_next(self, meaning: str) -> str | None:
        row = self.transitions.get(meaning)
        if not row:
            return None
        return max(row.items(), key=lambda kv: kv[1])[0]
