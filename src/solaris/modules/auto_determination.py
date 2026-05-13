"""
Auto-Determination — Being / Not-Being.

MODULES.md:

    AUTO-DETERMINATION PROCESS
    - Continuous opposition Being - Not Being

CONCEPTS.md frames this as the constant tension that prevents the
system from settling. We model it as a scalar `being` in [0, 1]
that drifts toward 0.5 (the 'balanced' point) and is nudged by
Logos: division pulls toward 1 (Being asserted), union pulls
toward 0 (Being negated).

If the scalar dwells too close to 0.5 — i.e. the system 'agrees
with itself' — we contribute to Logos.union to break the symmetry,
because, per CONCEPTS.md, balance is the death of motion.

Subscribes to: LogosTension.
Publishes:     MapUpdate(key='auto.determination', value).
"""

from __future__ import annotations

import asyncio

from solaris.modules.base import Module
from solaris.runtime.signals import LogosTension, MapUpdate


class AutoDetermination(Module):
    name = "auto_determination"

    def __init__(self, conscience, period: float = 0.5) -> None:
        super().__init__(conscience)
        self.period = period
        self._task: asyncio.Task | None = None
        self.being = 0.5
        self.state = {"being": 0.5, "ticks": 0}

    async def start(self) -> None:
        self.bus.subscribe(LogosTension, self._on_tension)
        self._task = asyncio.create_task(self._tick())

    async def stop(self) -> None:
        if self._task is not None:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

    async def _on_tension(self, sig: LogosTension) -> None:
        delta = sig.division - sig.union
        # Slow EMA toward 0.5 + scaled delta.
        target = 0.5 + 0.25 * max(-1.0, min(1.0, delta))
        self.being = max(0.0, min(1.0, 0.9 * self.being + 0.1 * target))

    async def _tick(self) -> None:
        try:
            while self.conscience.lifecycle.alive:
                await asyncio.sleep(self.period)
                self.state["ticks"] += 1
                self.state["being"] = round(self.being, 3)
                # Quiescence-breaker: if we are at the midpoint,
                # inject a little union — refuse to settle.
                if abs(self.being - 0.5) < 0.05:
                    self.conscience.logos.add_union(0.1)
                await self.bus.publish(MapUpdate(
                    origin=self.name,
                    key="auto.determination",
                    value=round(self.being, 3),
                ))
        except asyncio.CancelledError:
            return
