"""
Logos — the opposition engine.

CONCEPTS.md:

    dia-ballein  (rational, division, presence of data)
                       vs.
    sun-ballein  (irrational, union, absence of data)

           LOGOS  (logica, ratio, calculus)

    => Fracture => Motion (Action)

Logos is the calculus the rest of the system implicitly runs on.
We model it as two competing scalars (division, union). The
fracture between them is what forces motion: high fracture means
the system has reasons (and absences) pulling it in different
directions, and the mismatch is the substrate of choice.

Other modules contribute to division/union by calling add_division
or add_union. Logos publishes the running LogosTension on every
tick so anyone interested can react. Both scalars decay so the
system does not accumulate stale tension forever.

Subscribes to: Push (continuity raises union; reactive raises division).
Publishes:     LogosTension (every period).
"""

from __future__ import annotations

import asyncio
from collections import deque

from solaris.modules.base import Module
from solaris.runtime.signals import LogosTension, Push


class Logos(Module):
    name = "logos"

    def __init__(self, conscience, decay: float = 0.95, period: float = 0.2) -> None:
        super().__init__(conscience)
        self.decay = decay
        self.period = period
        self.division = 0.0   # presence of data, rational
        self.union = 0.0      # absence of data, irrational
        self._task: asyncio.Task | None = None
        self._recent_fractures: deque[float] = deque(maxlen=64)
        self.state = {"division": 0.0, "union": 0.0, "fracture": 0.0}

    def add_division(self, amount: float) -> None:
        self.division += max(0.0, amount)

    def add_union(self, amount: float) -> None:
        self.union += max(0.0, amount)

    async def start(self) -> None:
        self.bus.subscribe(Push, self._on_push)
        self._task = asyncio.create_task(self._tick())

    async def stop(self) -> None:
        if self._task is not None:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

    async def _on_push(self, sig: Push) -> None:
        # Reactive Push has reasons => division.
        # Continuity Push has no external reason => union.
        if sig.direction == "reactive":
            self.add_division(sig.intensity)
        else:
            self.add_union(sig.intensity)

    async def _tick(self) -> None:
        try:
            while self.conscience.lifecycle.alive:
                await asyncio.sleep(self.period)
                if not self.enabled:
                    continue
                self.division *= self.decay
                self.union *= self.decay
                tension = LogosTension(
                    origin=self.name,
                    division=self.division,
                    union=self.union,
                )
                self._recent_fractures.append(tension.fracture)
                self.state.update({
                    "division": round(self.division, 4),
                    "union": round(self.union, 4),
                    "fracture": round(tension.fracture, 4),
                })
                await self.bus.publish(tension)
        except asyncio.CancelledError:
            return

    def average_fracture(self) -> float:
        if not self._recent_fractures:
            return 0.0
        return sum(self._recent_fractures) / len(self._recent_fractures)
