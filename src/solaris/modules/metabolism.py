"""
Metabolism — the wake / sleep / survival state machine and arousal.

Promotes bare Lifecycle (birth/die) into a metabolic cycle:

    AWAKE  <-- Re-Gain (wake Push) --  DREAM_SLEEP { oMBA, oTD }
      |  Sleep (operator / auto low-arousal) -->
      |
      |  Activate (threat / operator): survival mode (prey-predator)

Death stays with Lifecycle; this module owns everything between.

- arousal (0..1): raised by external stimuli (Conscience.stimulate),
  decays over time. Sustained low arousal triggers auto-Sleep.
- Sleep gates the *sensory* layer only (Conscience.stimulate drops
  external stimuli while asleep; a `threat` wakes + activates). The
  internal flux continues: that is the dreaming.
- oMBA (Oniric Metabolic Brain Activity): consolidation + pruning +
  energy recovery.
- oTD (Oniric Thought activity): replays a recent memory as an
  internal `oneiric` Stimulus, which then flows the normal pipeline.
- Activate: raise arousal, lower I/O threshold, suspend non-vital
  Limitations (Negation), prioritise reacting; decays unless
  re-triggered.

Publishes: MetabolicState (on transitions and each tick).
"""

from __future__ import annotations

import asyncio
import random
import time

from solaris.modules.base import Module
from solaris.runtime.signals import MetabolicState, Push, Stimulus


class Metabolism(Module):
    name = "metabolism"

    def __init__(
        self,
        conscience,
        period: float = 0.5,
        rested_arousal: float = 0.55,
        low_arousal: float = 0.22,
        sleep_after_low: float = 4.0,
        sleep_duration: float = 6.0,
    ) -> None:
        super().__init__(conscience)
        self.period = period
        self.rested_arousal = rested_arousal
        self.low_arousal = low_arousal
        self.sleep_after_low = sleep_after_low
        self.sleep_duration = sleep_duration

        self.mode = "awake"          # awake | dream_sleep
        self.substate = ""           # "" | dream | activate
        self.arousal = rested_arousal
        self.activated = False
        self._io_threshold_saved: float | None = None
        self._low_since: float | None = None
        self._asleep_since: float | None = None
        self._rng = random.Random(7)
        self._task: asyncio.Task | None = None
        self.state = {
            "state": "awake", "arousal": rested_arousal,
            "substate": "", "activated": False,
            "oMBA": 0, "oTD": 0,
        }

    async def start(self) -> None:
        self._task = asyncio.create_task(self._tick())
        await self._publish()

    async def stop(self) -> None:
        if self._task is not None:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

    # ---- operator / auto transitions ----------------------------------

    def bump_arousal(self, amount: float) -> None:
        self.arousal = max(0.0, min(1.0, self.arousal + amount))

    @property
    def asleep(self) -> bool:
        return self.mode == "dream_sleep"

    async def sleep(self) -> None:
        if self.mode == "dream_sleep":
            return
        self.mode = "dream_sleep"
        self.substate = "dream"
        self._asleep_since = time.monotonic()
        self._low_since = None
        await self._publish()

    async def wake(self) -> None:
        """Re-Gain: push to the post-sleep state."""
        if self.mode == "awake":
            return
        self.mode = "awake"
        self.substate = "activate" if self.activated else ""
        self.arousal = max(self.arousal, self.rested_arousal)
        self._asleep_since = None
        await self.bus.publish(Push(
            origin=self.name, intensity=0.3, direction="wake",
        ))
        await self._publish()

    async def activate(self, reason: str = "operator") -> None:
        """Survival Push (prey-predator). Sharpen + suspend limits."""
        if self.mode == "dream_sleep":
            await self.wake()
        self.activated = True
        self.substate = "activate"
        self.arousal = 0.95
        # Lower the I/O threshold so the system acts fast under threat.
        io = self.conscience.io
        if self._io_threshold_saved is None:
            self._io_threshold_saved = io.action_threshold
        io.action_threshold = max(0.12, self._io_threshold_saved * 0.5)
        # Suspend non-vital Limitations.
        neg = getattr(self.conscience, "negation", None)
        if neg is not None:
            neg.suspended = True
        # Survival has reasons -> division (rational presence).
        self.conscience.logos.add_division(0.6)
        await self.bus.publish(Push(
            origin=self.name, intensity=0.95, direction="survival",
        ))
        await self._publish()

    def _deactivate(self) -> None:
        self.activated = False
        if self.substate == "activate":
            self.substate = "" if self.mode == "awake" else "dream"
        io = self.conscience.io
        if self._io_threshold_saved is not None:
            io.action_threshold = self._io_threshold_saved
            self._io_threshold_saved = None
        neg = getattr(self.conscience, "negation", None)
        if neg is not None:
            neg.suspended = False

    # ---- loop ---------------------------------------------------------

    async def _tick(self) -> None:
        try:
            while self.conscience.lifecycle.alive:
                await asyncio.sleep(self.period)
                now = time.monotonic()

                if self.mode == "awake":
                    # arousal decays toward 0 when nothing stimulates.
                    self.arousal = max(0.0, self.arousal - 0.04)
                    if self.activated and self.arousal <= self.rested_arousal:
                        self._deactivate()
                    # auto-sleep on sustained low arousal.
                    if not self.activated and self.arousal < self.low_arousal:
                        self._low_since = self._low_since or now
                        if now - self._low_since >= self.sleep_after_low:
                            await self.sleep()
                    else:
                        self._low_since = None

                elif self.mode == "dream_sleep":
                    await self._oMBA()
                    await self._oTD()
                    # energy recovery while asleep.
                    self.arousal = min(self.rested_arousal, self.arousal + 0.05)
                    if self.activated and self.arousal <= self.rested_arousal:
                        self._deactivate()
                    # auto Re-Gain after a full sleep.
                    if self._asleep_since and now - self._asleep_since >= self.sleep_duration:
                        await self.wake()

                await self._publish()
        except asyncio.CancelledError:
            return

    async def _oMBA(self) -> None:
        """Metabolic maintenance: prune (Synthesis) + consolidate (Habit)."""
        pruned = self.conscience.habit.prune_below(0.06)
        if pruned:
            self.conscience.logos.add_union(0.04 * pruned)  # subtraction
        self.state["oMBA"] += 1

    async def _oTD(self) -> None:
        """Oniric thought: replay a recent memory as an internal stimulus."""
        recent = self.conscience.memory.recent(24)
        stimuli = [s for s in recent if isinstance(s, Stimulus) and not s.is_absence]
        if not stimuli:
            return
        src = self._rng.choice(stimuli)
        self.state["oTD"] += 1
        await self.bus.publish(Stimulus(
            origin=self.name,
            modality="oneiric",
            payload=src.payload,
            intensity=0.4 * src.intensity,
        ))

    async def _publish(self) -> None:
        self.state.update({
            "state": self.mode,
            "arousal": round(self.arousal, 3),
            "substate": self.substate,
            "activated": self.activated,
        })
        await self.bus.publish(MetabolicState(
            origin=self.name,
            state=self.mode,
            arousal=self.arousal,
            substate=self.substate,
            activated=self.activated,
        ))
