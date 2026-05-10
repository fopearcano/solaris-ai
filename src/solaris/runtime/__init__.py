"""Runtime primitives — Bus, Lifecycle, and the typed Signals.

Modules speak to each other only through the Bus. Signals are typed
dataclasses. Lifecycle owns birth and death of the system; per
CONCEPTS.md the system 'must be able to die', and the Lifecycle
object is the only thing that can declare it.
"""

from solaris.runtime.bus import Bus
from solaris.runtime.lifecycle import Lifecycle
from solaris.runtime.signals import (
    Action,
    Desire,
    LogosTension,
    MapUpdate,
    MeaningEvent,
    Push,
    Reaction,
    Signal,
    Stimulus,
)

__all__ = [
    "Bus",
    "Lifecycle",
    "Signal",
    "Stimulus",
    "Push",
    "Desire",
    "Action",
    "Reaction",
    "MeaningEvent",
    "MapUpdate",
    "LogosTension",
]
