"""
Uncertainty — choice without (full) data.

MODULES.md:

    UNCERTAINTY
    Action (choice) without known data (degree of certainty, but
    what if it's 50/50%? ... like throwing a dice).

When confidence is too low to commit, decision cannot be derived
from data alone. Uncertainty closes the gap. We model it as a
biased random resolver: the noise widens with Mysterium pressure
(unknown grows -> spread grows), and the resolution is nudged
toward the extremes by the current Logos fracture (a torn system
acts more decisively than a balanced one).

The result is a confidence value that I/O uses for commitment.
This is not 'noise as randomness for its own sake' — it is the
explicit acknowledgement, from CONCEPTS.md, that some choices
genuinely have no data behind them and that the system must still
move.

Subscribes to: nothing.
Publishes:     nothing.
Provides:      .resolve(key, baseline_confidence).
"""

from __future__ import annotations

import random

from solaris.modules.base import Module


class Uncertainty(Module):
    name = "uncertainty"

    def __init__(self, conscience, seed: int = 0) -> None:
        super().__init__(conscience)
        self._rng = random.Random(seed)
        self.state = {"resolves": 0, "last_resolution": 0.0}

    def resolve(self, key: str, baseline: float) -> float:
        unknown = self.conscience.mysterium.pressure
        fracture = self.conscience.logos.state.get("fracture", 0.0)
        roll = self._rng.gauss(baseline, 0.1 + 0.3 * unknown)
        roll = max(0.0, min(1.0, roll + 0.1 * fracture))
        self.state["resolves"] += 1
        self.state["last_resolution"] = round(roll, 3)
        return roll
