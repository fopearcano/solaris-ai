"""
Parallelisation — thinking runs in parallel because opposition needs
two parts.

`Logos` is opposition: dia-ballein (division / presence) vs sun-ballein
(union / absence). An opposition *always* has two poles, so thought is
naturally inclined to fork into two concurrent streams — one per pole —
which then **merge**. This module reads `LogosTension`, runs the two
poles as parallel branches (`asyncio.gather`), and merges them into a
single resolution.

The **parallelism** degree is high when the two poles are balanced
(genuine two-stream thinking) and low when one dominates (thought
collapses to a single serial stream). A merged parallel thought is a
small rational resolution, so it feeds a little `division` back into
Logos — closing the loop opposition → parallel branches → merge →
presence.

Subscribes to: LogosTension.
Publishes:     MapUpdate(key='parallel.merge', ...).
Direct write:  Logos.division (the merged resolution).
"""

from __future__ import annotations

import asyncio

from solaris.modules.base import Module
from solaris.runtime.signals import LogosTension, MapUpdate


class Parallelisation(Module):
    name = "parallelisation"

    def __init__(self, conscience, period: float = 0.4) -> None:
        super().__init__(conscience)
        self.period = period
        self._tension: LogosTension | None = None
        self._task: asyncio.Task | None = None
        self.parallelism = 0.0
        self.state = {"merges": 0, "parallelism": 0.0, "dominant": ""}

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
        self._tension = sig

    async def _branch(self, pole: str, weight: float) -> float:
        """One parallel stream of thought, for one pole of the opposition."""
        await asyncio.sleep(0)   # yield — the two branches run concurrently
        return weight

    async def _tick(self) -> None:
        try:
            while self.conscience.lifecycle.alive:
                await asyncio.sleep(self.period)
                if not self.enabled:
                    continue
                t = self._tension
                if t is None:
                    continue
                # Run the two poles in parallel, then merge.
                a, b = await asyncio.gather(
                    self._branch("dia", t.division),
                    self._branch("sun", t.union),
                )
                total = a + b + 1e-6
                parallelism = 1.0 - abs(a - b) / total   # balanced -> high
                dominant = "dia" if a >= b else "sun"
                resolution = round(a - b, 4)
                self.parallelism = parallelism
                self.state.update({
                    "merges": self.state["merges"] + 1,
                    "parallelism": round(parallelism, 3),
                    "dominant": dominant,
                })
                # the merge is a small rational resolution -> presence.
                self.conscience.logos.add_division(0.02 * parallelism)
                await self.bus.publish(MapUpdate(
                    origin=self.name,
                    key="parallel.merge",
                    value={
                        "parallelism": round(parallelism, 3),
                        "dominant": dominant,
                        "resolution": resolution,
                    },
                ))
        except asyncio.CancelledError:
            return
