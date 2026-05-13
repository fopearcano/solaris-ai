"""
Dimensional Comparison (D.C.) — limits and boundaries.

MODULES.md:

    A parallelisation (//) such a comparison in dimensionality is
    fundamental to the perception of the Self.
    Limits (to D.C) / Boundaries (from D.C).
    Habit Process is forcing a Boundary (as for any other process).
    Limits are Physical/Hardware.

Two-tier model:

    hard_limits      set at construction; never moved. These are
                     the Physical/Hardware limits — they constrain
                     what the system can ever do.
    soft_boundaries  emerge at runtime from Habit and Synthesis
                     activity; they shape what the system tends
                     to do.

D.C. publishes its hard_limits to the Inner MAP at boot (so the
self-model knows where it ends), then watches for habit/synth
MapUpdates to grow the soft boundary set.

Subscribes to: MapUpdate (only habit:* and synth:* keys).
Publishes:     MapUpdate(boundary=True, ...) at start.
Provides:      .within_limits(...).
"""

from __future__ import annotations

from solaris.modules.base import Module
from solaris.runtime.signals import MapUpdate


class DimensionalComparison(Module):
    name = "dimensional_comparison"

    def __init__(self, conscience) -> None:
        super().__init__(conscience)
        self.hard_limits: dict[str, float] = {
            "max_action_intensity": 1.0,
            "max_simultaneous_desires": 8,
        }
        self.soft_boundaries: dict[str, float] = {}
        self.state = {
            "hard_limits": dict(self.hard_limits),
            "soft_boundaries": 0,
        }

    async def start(self) -> None:
        for k, v in self.hard_limits.items():
            await self.bus.publish(MapUpdate(
                origin=self.name,
                key=f"limit:{k}",
                value=v,
                boundary=True,
            ))
        self.bus.subscribe(MapUpdate, self._on_update)

    async def _on_update(self, sig: MapUpdate) -> None:
        if sig.origin == self.name:
            return
        if sig.key.startswith("habit:") or sig.key.startswith("synth:"):
            self.soft_boundaries[sig.key] = sig.value
            self.state["soft_boundaries"] = len(self.soft_boundaries)

    def within_limits(self, intensity: float, n_desires: int) -> bool:
        return (
            intensity <= self.hard_limits["max_action_intensity"]
            and n_desires <= self.hard_limits["max_simultaneous_desires"]
        )
