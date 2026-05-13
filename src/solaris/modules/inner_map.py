"""
Inner MAP — the system's running model of itself.

MODULES.md:

    INNER MAP
    - Sensorial function
    - LIMIT
    - Self-Determination

Whitepaper: 'a dynamic representation of the system's
self-awareness and boundaries.'

The Inner MAP listens for MapUpdate signals from any module and
maintains two dictionaries:

    facts       — what the system currently believes about itself
    boundaries  — where the self ends (limits / habituated edges)

The MAP does not modify itself; it is the consumer of every
module's view. It also tracks the latest Logos fracture so other
readers can ask 'how torn is the self right now?'.

Subscribes to: MapUpdate, MeaningEvent, LogosTension.
Publishes:     nothing.
"""

from __future__ import annotations

from typing import Any

from solaris.modules.base import Module
from solaris.runtime.signals import LogosTension, MapUpdate, MeaningEvent


class InnerMap(Module):
    name = "inner_map"

    def __init__(self, conscience) -> None:
        super().__init__(conscience)
        self.facts: dict[str, Any] = {}
        self.boundaries: dict[str, Any] = {}
        self._meaning_count: dict[str, int] = {}
        self.state = {"facts": 0, "boundaries": 0, "fracture": 0.0}

    async def start(self) -> None:
        self.bus.subscribe(MapUpdate, self._on_update)
        self.bus.subscribe(MeaningEvent, self._on_meaning)
        self.bus.subscribe(LogosTension, self._on_tension)

    async def _on_update(self, sig: MapUpdate) -> None:
        if sig.boundary:
            self.boundaries[sig.key] = sig.value
            self.state["boundaries"] = len(self.boundaries)
        else:
            self.facts[sig.key] = sig.value
            self.state["facts"] = len(self.facts)

    async def _on_meaning(self, sig: MeaningEvent) -> None:
        self._meaning_count[sig.meaning] = self._meaning_count.get(sig.meaning, 0) + 1
        self.facts[f"meaning:{sig.meaning}"] = self._meaning_count[sig.meaning]
        self.state["facts"] = len(self.facts)

    async def _on_tension(self, sig: LogosTension) -> None:
        self.state["fracture"] = round(sig.fracture, 4)

    def snapshot(self) -> dict[str, Any]:
        return {"facts": dict(self.facts), "boundaries": dict(self.boundaries)}
