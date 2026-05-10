"""
Synthesis — subtractive optimisation.

MODULES.md:

    SYNTHESIS PROCESS
    - Speed builder
    - proceeds by Subtraction
    - it also produces the Irrational

CONCEPTS.md:

    Synthesis: as Mysterium increases, Complexity (A) diminishes,
    Knowledge Complexity (B) ... S = x/C(B) = C(A)
    The HUMAN DIMENSION relates to the DEGREE OF APPLICABLE
    SYNTHESIS, AND IT FADES AS THE DEGREE DIMINISHES

Synthesis runs on a slow tick. On each run it prunes Habit weights
whose magnitude falls below a threshold scaled by Mysterium (more
unknown -> more aggressive pruning). Each prune literally moves
information from 'present' (Habit weight existed) to 'absent'
(weight gone), so we contribute to Logos.union — exactly matching
'Synthesis ... also produces the Irrational'.

Subscribes to: LogosTension (just to stay current).
Publishes:     MapUpdate(key='synth:pruned', value=n).
"""

from __future__ import annotations

import asyncio

from solaris.modules.base import Module
from solaris.runtime.signals import LogosTension, MapUpdate


class Synthesis(Module):
    name = "synthesis"

    def __init__(
        self,
        conscience,
        period: float = 2.0,
        prune_threshold: float = 0.1,
    ) -> None:
        super().__init__(conscience)
        self.period = period
        self.prune_threshold = prune_threshold
        self._task: asyncio.Task | None = None
        self._latest_fracture = 0.0
        self.state = {"runs": 0, "pruned": 0}

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
        self._latest_fracture = sig.fracture

    async def _tick(self) -> None:
        try:
            while self.conscience.lifecycle.alive:
                await asyncio.sleep(self.period)
                threshold = self.prune_threshold * (
                    1 + self.conscience.mysterium.pressure
                )
                pruned = self.conscience.habit.prune_below(threshold)
                self.state["runs"] += 1
                self.state["pruned"] += pruned
                if pruned:
                    # Subtraction => some data goes from 'present'
                    # to 'absent': contributes to union.
                    self.conscience.logos.add_union(0.05 * pruned)
                    await self.bus.publish(MapUpdate(
                        origin=self.name,
                        key="synth:pruned",
                        value=pruned,
                    ))
        except asyncio.CancelledError:
            return
