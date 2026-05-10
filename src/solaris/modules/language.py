"""
Language — cross-function meaning builder.

MODULES.md:

    LANGUAGE PROCESS
    - Cross-function (meaning builder)
    - language doesn't happen only in the brain

CONCEPTS.md treats language as the medium that lets distinct
modules *mean* the same thing when they exchange a Signal.
Internally that property is enforced by the typed Signal classes
themselves; the Language module's job is the externalisation: it
listens to every Signal on the Bus and renders a human-readable
narration of the system's life.

Subscribes to: every Signal (wildcard).
Publishes:     nothing.
Provides:      .narrate(n).
"""

from __future__ import annotations

from collections import deque

from solaris.modules.base import Module
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


class Language(Module):
    name = "language"

    def __init__(self, conscience, capacity: int = 256) -> None:
        super().__init__(conscience)
        self.lines: deque[str] = deque(maxlen=capacity)
        self.state = {"lines": 0}

    async def start(self) -> None:
        self.bus.subscribe_all(self._on_signal)

    async def _on_signal(self, sig: Signal) -> None:
        line = self._render(sig)
        if line is not None:
            self.lines.append(line)
            self.state["lines"] = len(self.lines)

    @staticmethod
    def _render(sig: Signal) -> str | None:
        if isinstance(sig, Stimulus):
            kind = "absence" if sig.is_absence else "stimulus"
            return (
                f"[{kind}] from={sig.origin} modality={sig.modality} "
                f"payload={sig.payload!r} i={sig.intensity:.2f}"
            )
        if isinstance(sig, Push):
            return f"[push] {sig.direction} i={sig.intensity:.2f}"
        if isinstance(sig, Desire):
            return (
                f"[desire] {sig.proposal!r} mot={sig.motivation:.2f} "
                f"conf={sig.confidence:.2f}"
            )
        if isinstance(sig, Action):
            return f"[action] {sig.name} payload={sig.payload!r}"
        if isinstance(sig, Reaction):
            return f"[reaction] action#{sig.action_id} v={sig.valence:+.2f}"
        if isinstance(sig, MeaningEvent):
            return f"[meaning] {sig.meaning} novelty={sig.novelty:.2f}"
        if isinstance(sig, MapUpdate):
            tag = "boundary" if sig.boundary else "fact"
            return f"[map:{tag}] {sig.key} = {sig.value!r}"
        if isinstance(sig, LogosTension):
            return (
                f"[logos] dia={sig.division:.2f} sun={sig.union:.2f} "
                f"frac={sig.fracture:.2f}"
            )
        return None

    def narrate(self, n: int = 20) -> list[str]:
        return list(self.lines)[-n:]
