"""
Signals — the typed messages that flow on the Bus.

Each signal corresponds to a concept from CONCEPTS.md or MODULES.md.

The spine of the system is the chain

    Stimulus  ->  Push  ->  Desire  ->  Action

drawn from MODULES.md (CORE: Action / Push). Everything else
(MeaningEvent, MapUpdate, LogosTension, Reaction) is produced and
consumed by individual modules to enrich that spine.
"""

from __future__ import annotations

import itertools
import time
from dataclasses import dataclass, field
from typing import Any, Optional

_id_counter = itertools.count(1)


def _new_id() -> int:
    return next(_id_counter)


@dataclass
class Signal:
    """Base for everything that travels on the Bus."""

    id: int = field(default_factory=_new_id)
    timestamp: float = field(default_factory=time.monotonic)
    origin: str = "unknown"


@dataclass
class Stimulus(Signal):
    """An input event.

    Per the Subtraction Principle (CONCEPTS.md), a Stimulus may also
    be the *absence* of expected data — that is the origin of the
    self-referential 'I exist!' that the Ego module reads.
    """

    modality: str = "internal"
    payload: Any = None
    intensity: float = 0.5
    is_absence: bool = False


@dataclass
class Push(Signal):
    """Traction toward action — gravity, drive.

    Emitted by AION/IMPULSE on every heartbeat (continuity Push)
    plus on any sufficiently strong Stimulus (reactive Push).
    """

    intensity: float = 0.0
    direction: str = "continuity"
    source_stimulus_id: Optional[int] = None


@dataclass
class Desire(Signal):
    """A formulated intention, awaiting commitment.

    Will = Need (CONCEPTS.md): a Desire is a Need passed through
    cognition. It is not yet an Action; the I/O Module commits it
    to one only when confidence and Push both clear threshold.
    """

    proposal: str = ""
    motivation: float = 0.0
    confidence: float = 0.5


@dataclass
class Action(Signal):
    """A quantum of behaviour.

    Per MODULES.md every Action is also both a Stimulus (re-entering
    the loop) and a Reaction (to whatever pushed it).
    """

    name: str = ""
    payload: Any = None


@dataclass
class Reaction(Signal):
    """A measured consequence of an Action.

    Used by Habit (reinforcement) and Backpropagation (plasticity).
    valence in [-1, +1].
    """

    action_id: Optional[int] = None
    valence: float = 0.0


@dataclass
class MeaningEvent(Signal):
    """Cognition's output — a Stimulus has been mapped to meaning.

    novelty in [0, 1]; high novelty feeds Mysterium (the unknown).
    """

    stimulus_id: Optional[int] = None
    meaning: str = ""
    novelty: float = 0.0


@dataclass
class MapUpdate(Signal):
    """A change to the Inner MAP — the self-representation."""

    key: str = ""
    value: Any = None
    boundary: bool = False


@dataclass
class LogosTension(Signal):
    """Current dia-ballein / sun-ballein balance.

    division: rational, presence of data
    union:    irrational, absence of data
    fracture: |division - union|; large fracture forces motion.
    """

    division: float = 0.0
    union: float = 0.0

    @property
    def fracture(self) -> float:
        return abs(self.division - self.union)
