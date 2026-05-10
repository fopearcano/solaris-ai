"""
AION/IMPULSE — the heartbeat of Conscience.

From MODULES.md (CORE):

    Action / Push (codebase)
        Stimulus  (attractive power)
        Push      (Traction = Gravity)
        Desire    (Need of Action)
        Action    (Quantum) — every Action is also both a Stimulus
                              and a ReAction.

This is not a controller. It is a driver. It guarantees three
properties:

1. Continuity. The loop never returns to idle. Stopping it = brain
   death (CONCEPTS.md, whitepaper).
2. Push. Each heartbeat emits a small continuity-Push. Strong
   external Stimuli additionally produce a reactive Push,
   proportional to their intensity.
3. Subtraction Principle. After a configurable silence window, AION
   generates a Stimulus from the absence itself: 'I exist!' This is
   the only path the system has to itself.

It does not assign meaning, decide, or commit. Those belong to
Cognition, I/O, and the Lifecycle respectively.

Subscribes to: Stimulus (to reset the silence clock).
Publishes:     Push (every period), Stimulus (on prolonged silence).
"""

from __future__ import annotations

import asyncio
import time

from solaris.modules.base import Module
from solaris.runtime.signals import Push, Stimulus


class AionImpulse(Module):
    name = "aion_impulse"

    def __init__(
        self,
        conscience,
        period: float = 0.1,
        silence_threshold: float = 0.5,
    ) -> None:
        super().__init__(conscience)
        self.period = period
        self.silence_threshold = silence_threshold
        self._last_external = 0.0
        self._task: asyncio.Task | None = None
        self.state = {"beats": 0, "absences": 0, "last_external_at": 0.0}

    async def start(self) -> None:
        self.bus.subscribe(Stimulus, self._on_stimulus)
        self._last_external = time.monotonic()
        self._task = asyncio.create_task(self._beat())

    async def stop(self) -> None:
        if self._task is not None:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

    async def _on_stimulus(self, sig: Stimulus) -> None:
        # Absence-stimuli are our own; they must not reset silence.
        if sig.is_absence or sig.origin == self.name:
            return
        self._last_external = time.monotonic()
        self.state["last_external_at"] = self._last_external
        # Real external stimulus -> reactive Push, proportional.
        await self.bus.publish(Push(
            origin=self.name,
            intensity=sig.intensity,
            direction="reactive",
            source_stimulus_id=sig.id,
        ))

    async def _beat(self) -> None:
        try:
            while self.conscience.lifecycle.alive:
                await asyncio.sleep(self.period)
                self.state["beats"] += 1
                # Continuity push: the system never goes inert.
                await self.bus.publish(Push(
                    origin=self.name,
                    intensity=0.05,
                    direction="continuity",
                ))
                # Subtraction Principle.
                silence = time.monotonic() - self._last_external
                if silence > self.silence_threshold:
                    self.state["absences"] += 1
                    await self.bus.publish(Stimulus(
                        origin=self.name,
                        modality="absence",
                        payload="I exist!",
                        is_absence=True,
                        intensity=min(1.0, silence / (self.silence_threshold * 5)),
                    ))
                    # Reset so we do not flood; absence becomes its
                    # own 'last input'.
                    self._last_external = time.monotonic()
        except asyncio.CancelledError:
            return
