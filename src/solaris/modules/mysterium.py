"""
Mysterium — the unknown.

CONCEPTS.md:

    The main cardinal element defining HUMAN in human being is the
    MYSTERIUM: the unknown — no-knowledge that generates the
    Irrational (@ Logic deprived of Data)

Mysterium is a scalar in [0, 1] representing the current pressure
of the unknown. It rises when Cognition emits MeaningEvents with
high novelty (the system has just encountered something new) and
decays slowly toward zero. It feeds two things:

    - Synthesis runs more aggressively when Mysterium is high
      (subtraction is the human-dimension response to mystery).
    - Uncertainty's noise widens with Mysterium (decisions made
      under more unknown are less constrained by data).

Mysterium also pushes Logos toward 'union' (irrational, absence of
data), since the unknown is, by definition, absence of data.

Subscribes to: MeaningEvent.
Publishes:     nothing — exposes .pressure for direct read.
"""

from __future__ import annotations

import asyncio

from solaris.modules.base import Module
from solaris.runtime.signals import MeaningEvent


class Mysterium(Module):
    name = "mysterium"

    def __init__(self, conscience, decay: float = 0.98, period: float = 0.3) -> None:
        super().__init__(conscience)
        self.pressure = 0.0
        self.decay = decay
        self.period = period
        self._task: asyncio.Task | None = None
        self.state = {"pressure": 0.0}

    async def start(self) -> None:
        self.bus.subscribe(MeaningEvent, self._on_meaning)
        self._task = asyncio.create_task(self._tick())

    async def stop(self) -> None:
        if self._task is not None:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

    async def _on_meaning(self, sig: MeaningEvent) -> None:
        self.pressure = min(1.0, self.pressure + 0.3 * sig.novelty)
        # The unknown is absence of data; it weights toward sun-ballein.
        self.conscience.logos.add_union(0.2 * sig.novelty)

    async def _tick(self) -> None:
        try:
            while self.conscience.lifecycle.alive:
                await asyncio.sleep(self.period)
                if not self.enabled:
                    continue
                self.pressure *= self.decay
                self.state["pressure"] = round(self.pressure, 3)
        except asyncio.CancelledError:
            return
