"""
Conscience — the assembled system.

This is where every module is instantiated and started. After
boot, no further wiring is performed: modules talk only via the
Bus, and the topology is therefore inspectable as
``Conscience.topology()``.

============================================================
                    Wiring (publish -> subscribe)
============================================================

  AION/IMPULSE
      Stimulus(absence)  -> Cognition, MemorySenses, Ego, Language
      Push(continuity)   -> Logos, IOModule, Language
      Push(reactive)     -> Logos, IOModule, Language

  Logos
      LogosTension       -> InnerMap, AutoDetermination, Synthesis,
                            Complexity, Language

  Cognition
      MeaningEvent       -> InnerMap, IOModule, Mysterium,
                            Anticipation, Ego, Language

  IOModule
      Desire             -> InnerMap, Language
      Action             -> MemorySenses, Habit, Language

  Habit
      MapUpdate          -> InnerMap, DimensionalComparison,
                            Language

  Synthesis
      MapUpdate          -> InnerMap, DimensionalComparison,
                            Language
      direct write -> Logos.union

  Backpropagation
      MapUpdate          -> InnerMap, AutoRegeneration, Language

  AutoRegeneration
      MapUpdate          -> InnerMap, Language
      direct write -> IOModule.action_threshold

  AutoDetermination
      MapUpdate          -> InnerMap, Language
      direct write -> Logos.union (when too quiescent)

  DimensionalComparison
      MapUpdate(boundary)-> InnerMap, Language

  Mysterium
      direct write -> Logos.union  (and exposes .pressure)

  Anticipation
      direct write -> Logos.division (on hit)
                   -> Mysterium.pressure (on miss)

  Complexity
      Stimulus(escape:+) -> AION (counts as external),
                            Cognition, MemorySenses, Ego, Language
      Stimulus(escape:-) -> same

  Ego
      MapUpdate(ego.self)-> InnerMap, DimensionalComparison,
                            Language

  Language
      (subscribes to all; publishes nothing)

  Lifecycle is read by AION, Logos, Synthesis, Mysterium,
  AutoDetermination to terminate their loops on death().
"""

from __future__ import annotations

import asyncio

from solaris.core import AionImpulse, Logos
from solaris.modules.anticipation import Anticipation
from solaris.modules.auto_determination import AutoDetermination
from solaris.modules.auto_regeneration import AutoRegeneration
from solaris.modules.backpropagation import Backpropagation
from solaris.modules.cognition import Cognition
from solaris.modules.complexity import Complexity
from solaris.modules.dimensional_comparison import DimensionalComparison
from solaris.modules.ego import Ego
from solaris.modules.habit import Habit
from solaris.modules.inner_map import InnerMap
from solaris.modules.io_module import IOModule
from solaris.modules.language import Language
from solaris.modules.memory_senses import MemorySenses
from solaris.modules.metabolism import Metabolism
from solaris.modules.mysterium import Mysterium
from solaris.modules.negation import Negation
from solaris.modules.synthesis import Synthesis
from solaris.modules.uncertainty import Uncertainty
from solaris.runtime import Bus, Lifecycle
from solaris.runtime.signals import Reaction, Stimulus


class Conscience:
    """The assembled Modular Network."""

    def __init__(self) -> None:
        self.bus = Bus()
        self.lifecycle = Lifecycle()
        self._build_modules()

    def _build_modules(self) -> None:
        """Construct (or re-construct, on Reborn) every module.

        Construction order matters only because some modules read
        other modules' attributes at runtime (e.g. IOModule reads
        self.conscience.negation / habit). After start(), modules
        talk via the Bus.
        """
        self.logos = Logos(self)
        self.mysterium = Mysterium(self)
        self.uncertainty = Uncertainty(self)
        self.habit = Habit(self)
        self.negation = Negation(self)
        self.aion = AionImpulse(self)
        self.memory = MemorySenses(self)
        self.cognition = Cognition(self)
        self.io = IOModule(self)
        self.inner_map = InnerMap(self)
        self.ego = Ego(self)
        self.auto_det = AutoDetermination(self)
        self.dim_comp = DimensionalComparison(self)
        self.synthesis = Synthesis(self)
        self.backprop = Backpropagation(self)
        self.auto_regen = AutoRegeneration(self)
        self.complexity = Complexity(self)
        self.anticipation = Anticipation(self)
        self.metabolism = Metabolism(self)
        self.language = Language(self)

        self._modules = [
            self.logos,
            self.mysterium,
            self.uncertainty,
            self.habit,
            self.negation,
            self.aion,
            self.memory,
            self.cognition,
            self.io,
            self.inner_map,
            self.ego,
            self.auto_det,
            self.dim_comp,
            self.synthesis,
            self.backprop,
            self.auto_regen,
            self.complexity,
            self.anticipation,
            self.metabolism,
            self.language,
        ]

    async def birth(self) -> None:
        """Bring the system online. Every module's start() runs."""
        self.lifecycle.birth()
        for m in self._modules:
            await m.start()

    async def death(self, cause: str = "graceful shutdown") -> None:
        """Bring the system offline. Modules stop in reverse order."""
        self.lifecycle.die(cause)
        # Yield once so background tasks observe .alive flipping.
        await asyncio.sleep(0)
        for m in reversed(self._modules):
            await m.stop()

    async def stimulate(
        self,
        payload,
        modality: str = "external",
        intensity: float = 0.7,
    ) -> None:
        """Inject an external Stimulus.

        Sleep gates the sensory layer: while asleep, external stimuli
        are dropped — except a `threat`, which wakes the system and
        triggers Activate (survival). Any external stimulus bumps
        arousal.
        """
        if self.metabolism.asleep:
            if modality == "threat":
                await self.metabolism.activate(reason="threat")
            else:
                return  # gated: dreaming, not perceiving the outside
        self.metabolism.bump_arousal(0.18 * intensity + 0.05)
        if modality == "threat" and not self.metabolism.activated:
            await self.metabolism.activate(reason="threat")
        await self.bus.publish(Stimulus(
            origin="environment",
            modality=modality,
            payload=payload,
            intensity=intensity,
        ))

    async def react(self, action_id: int, valence: float) -> None:
        """Inject a Reaction to a previously emitted Action."""
        await self.bus.publish(Reaction(
            origin="environment",
            action_id=action_id,
            valence=max(-1.0, min(1.0, valence)),
        ))

    # ---- Actions (metabolic state machine) ----------------------------

    async def sleep(self) -> None:
        await self.metabolism.sleep()

    async def wake(self) -> None:
        """Re-Gain — push to the post-sleep state."""
        await self.metabolism.wake()

    async def activate(self, reason: str = "operator") -> None:
        await self.metabolism.activate(reason=reason)

    async def negate(self, meaning: str, source: str = "environment",
                     strength: float = 1.0) -> float:
        """Operator 'NO' against a meaning, weighted by e.Link bond."""
        return await self.negation.negate(meaning, source=source, strength=strength)

    async def reborn(self) -> None:
        """A new life from 0: fresh Bus, Lifecycle, and modules.

        Not a resume — the previous life dies and a new individual is
        born with empty Inner MAP, e.Links, Limitations, and counters.
        The caller (e.g. the web server) must re-attach any Bus
        subscriptions it owns, since the Bus is new.
        """
        if self.lifecycle.alive:
            await self.death(cause="reborn")
        self.bus = Bus()
        self.lifecycle = Lifecycle()
        self._build_modules()
        await self.birth()

    def topology(self) -> dict[str, list[str]]:
        return self.bus.subscriptions()

    def snapshot(self) -> dict:
        return {
            "lifecycle": {
                "alive": self.lifecycle.alive,
                "age_s": round(self.lifecycle.age, 2),
            },
            "metabolism": {
                "state": self.metabolism.mode,
                "arousal": round(self.metabolism.arousal, 3),
                "substate": self.metabolism.substate,
                "activated": self.metabolism.activated,
            },
            "modules": {m.name: m.observe() for m in self._modules},
            "inner_map": self.inner_map.snapshot(),
        }
