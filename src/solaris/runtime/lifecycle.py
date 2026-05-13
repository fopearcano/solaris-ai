"""
Lifecycle — birth and death of Conscience.

CONCEPTS.md: 'Must be able to die.'

The Lifecycle object is the only thing allowed to declare the
system dead. Modules read .alive to decide whether to keep their
loops running; AION/IMPULSE reads it to decide whether to keep
beating. Once dead, the only legal transition is back through the
constructor — i.e. the next system is a new system.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Optional


@dataclass
class Lifecycle:
    born_at: Optional[float] = None
    died_at: Optional[float] = None
    alive: bool = False
    cause_of_death: str = ""

    def birth(self) -> None:
        if self.born_at is not None:
            raise RuntimeError("already born")
        self.born_at = time.monotonic()
        self.alive = True

    def die(self, cause: str = "graceful shutdown") -> None:
        if not self.alive:
            return
        self.alive = False
        self.died_at = time.monotonic()
        self.cause_of_death = cause

    @property
    def age(self) -> float:
        if self.born_at is None:
            return 0.0
        end = self.died_at if self.died_at is not None else time.monotonic()
        return end - self.born_at
