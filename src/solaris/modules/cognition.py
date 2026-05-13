"""
Cognition — meaning assignment.

CONCEPTS.md:

    MEANING is a product of THINKING (it right becomes Need, so it
    is central to the functioning of mechanism)
    > This THINKING is not-logical (otherwise it should naturally
      'animal'), so it is an unconscious THINKING, and it is closer
      to IMAGINATION
    > IMAGINATION is structurally related to the ANTICIPATION
      CAPACITY (forecast)

Whitepaper (Cognition Core): 'Assigns meaning to stimuli, linking
them to memory and context.'

Cognition is the bridge from raw Stimulus to MeaningEvent. The
meaning string is intentionally simple here — modality + type +
short payload — because the point of this conceptualisation is the
flow, not a real semantic engine. Novelty is computed against a
counter of seen meanings: a previously unseen meaning has novelty
1.0; one seen many times tends to 0.

Subscribes to: Stimulus.
Publishes:     MeaningEvent.
"""

from __future__ import annotations

from solaris.modules.base import Module
from solaris.runtime.signals import MeaningEvent, Stimulus


class Cognition(Module):
    name = "cognition"

    def __init__(self, conscience) -> None:
        super().__init__(conscience)
        self._known: dict[str, int] = {}
        self.state = {"known_meanings": 0, "events": 0}

    async def start(self) -> None:
        self.bus.subscribe(Stimulus, self._on_stimulus)

    async def _on_stimulus(self, sig: Stimulus) -> None:
        meaning = self._derive_meaning(sig)
        seen = self._known.get(meaning, 0)
        novelty = 1.0 / (1.0 + seen)
        self._known[meaning] = seen + 1
        self.state["known_meanings"] = len(self._known)
        self.state["events"] += 1
        await self.bus.publish(MeaningEvent(
            origin=self.name,
            stimulus_id=sig.id,
            meaning=meaning,
            novelty=novelty,
        ))

    @staticmethod
    def _derive_meaning(sig: Stimulus) -> str:
        if sig.is_absence:
            return "self.exists"
        if sig.payload is None:
            return f"{sig.modality}/empty"
        type_name = type(sig.payload).__name__
        body = str(sig.payload)[:32]
        return f"{sig.modality}/{type_name}/{body}"
