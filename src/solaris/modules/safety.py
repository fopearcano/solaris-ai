"""
Safety — protect the child from Death-from-the-Environment.

Death can come from the world: harsh `threat` stimuli, overstimulation,
and the bodily cost of sustained survival mode (Activate). This module
gives the system a **vitality** (life-integrity) in [0, 1] that
environmental harshness depletes — and then, *like a parent shielding a
child*, it protects:

- when vitality falls into danger it raises a **shield** (Conscience
  dampens incoming harm via `Safety.filter`) and puts the child to
  **rest** to heal (induces Sleep);
- while `protection_enabled` (the default), vitality is clamped above a
  floor — the parent will not let the child die.

Environmental death (`conscience.death(cause="environment")`) is reached
only if protection is *disabled* (an explicit, drastic operator choice —
"Die could happen everywhere in the world") and vitality hits 0. By
default, the parent protects.

Subscribes to: Stimulus (harm depletes vitality).
Publishes:     MapUpdate(key='safety:shield', ...) on shield changes.
Provides:      .filter(modality, intensity) for Conscience.stimulate.
"""

from __future__ import annotations

import asyncio

from solaris.modules.base import Module
from solaris.runtime.signals import MapUpdate, Stimulus

HARMFUL_MODALITIES = {"threat"}


class Safety(Module):
    name = "safety"

    def __init__(
        self,
        conscience,
        period: float = 0.5,
        danger: float = 0.3,
        release: float = 0.55,
        floor: float = 0.05,
    ) -> None:
        super().__init__(conscience)
        self.period = period
        self.danger = danger
        self.release = release
        self.floor = floor
        self.vitality = 1.0
        self.protection_enabled = True   # the parent protects (default)
        self.shielded = False
        self._recovering = False
        self._task: asyncio.Task | None = None
        self.state = {
            "vitality": 1.0, "shielded": False,
            "protection": True, "interventions": 0,
        }

    async def start(self) -> None:
        self.bus.subscribe(Stimulus, self._on_stimulus)
        self._task = asyncio.create_task(self._tick())

    async def stop(self) -> None:
        if self._task is not None:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

    def filter(self, modality: str, intensity: float) -> float:
        """Parent shields the child: dampen harmful stimuli when shielded."""
        harmful = modality in HARMFUL_MODALITIES or intensity > 0.85
        if self.shielded and harmful:
            return intensity * 0.4
        return intensity

    async def _on_stimulus(self, sig: Stimulus) -> None:
        if sig.origin == self.name or sig.is_absence:
            return
        harmful = sig.modality in HARMFUL_MODALITIES or sig.intensity > 0.85
        if harmful:
            dmg = 0.18 * sig.intensity if sig.modality in HARMFUL_MODALITIES else 0.06
            self.vitality = max(0.0, self.vitality - dmg)

    async def _tick(self) -> None:
        try:
            while self.conscience.lifecycle.alive:
                await asyncio.sleep(self.period)
                if not self.enabled:
                    continue
                meta = self.conscience.metabolism
                # survival mode costs vitality; calm / sleep heals it.
                if meta.activated:
                    self.vitality = max(0.0, self.vitality - 0.03)
                elif meta.asleep:
                    self.vitality = min(1.0, self.vitality + 0.08)
                else:
                    self.vitality = min(1.0, self.vitality + 0.03)

                if self.vitality < self.danger:
                    if not self.shielded:
                        self.shielded = True
                        self.state["interventions"] += 1
                        await self.bus.publish(MapUpdate(
                            origin=self.name, key="safety:shield",
                            value=True, boundary=True))
                    # the parent puts the child to rest to heal.
                    if self.protection_enabled and not meta.asleep and not self._recovering:
                        self._recovering = True
                        await self.conscience.sleep()
                elif self.vitality > self.release:
                    if self.shielded:
                        self.shielded = False
                        await self.bus.publish(MapUpdate(
                            origin=self.name, key="safety:shield",
                            value=False, boundary=True))
                    self._recovering = False

                # protection floor — or environmental death if disabled.
                if self.protection_enabled:
                    self.vitality = max(self.floor, self.vitality)
                elif self.vitality <= 0.0:
                    await self.conscience.death(cause="environment")
                    return

                self.state.update({
                    "vitality": round(self.vitality, 3),
                    "shielded": self.shielded,
                    "protection": self.protection_enabled,
                })
        except asyncio.CancelledError:
            return
