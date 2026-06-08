"""
Negation — the "NO" function: building Limitations through bond.

CONCEPTS (added): *"i no di mamma e babbo costruiscono il Principio
di Non-Contraddizione"* — the no's of mum and dad build the Principle
of Non-Contradiction. Logic's bedrock is not a priori; it is built
from negations received through an emotional bond.

- e.Link: a per-source attachment weight in [0, 1], grown from
  sustained interaction (and operator-overridable). A NO from a
  high-e.Link source installs a *strong* Limitation; from a stranger,
  almost none. Prohibition has force only through bond.
- Limitations: per-meaning strengths. A meaning whose Limitation is
  strong is *forbidden* — the system can, but must-not. I/O consults
  is_forbidden() before committing an Action.
- Non-contradiction: as consistent Limitations accumulate, a scalar
  grows that Logos can read — the emergent capacity to treat A and
  not-A as incompatible.

Limitations: slow decay + suspend (Activate sets .suspended) +
wipe (Reborn rebuilds the module).

Subscribes to: Stimulus, Reaction (to grow e.Link for their source).
Publishes:     MapUpdate(boundary, key='no:<meaning>') on a NO.
"""

from __future__ import annotations

import asyncio

from solaris.modules.base import Module
from solaris.runtime.signals import MapUpdate, Reaction, Stimulus


class Negation(Module):
    name = "negation"

    def __init__(
        self,
        conscience,
        period: float = 1.0,
        forbid_threshold: float = 0.5,
        decay: float = 0.997,
    ) -> None:
        super().__init__(conscience)
        self.period = period
        self.forbid_threshold = forbid_threshold
        self.decay = decay
        self.elink: dict[str, float] = {}
        self.limitations: dict[str, float] = {}
        self.suspended = False           # set by Activate
        self.non_contradiction = 0.0     # grows with consistent limits
        self._task: asyncio.Task | None = None
        self.state = {
            "elinks": 0, "limitations": 0,
            "non_contradiction": 0.0, "suspended": False,
        }

    async def start(self) -> None:
        self.bus.subscribe(Stimulus, self._on_source)
        self.bus.subscribe(Reaction, self._on_source)
        self._task = asyncio.create_task(self._tick())

    async def stop(self) -> None:
        if self._task is not None:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

    # ---- bond growth --------------------------------------------------

    async def _on_source(self, sig) -> None:
        # The Other (the operator / environment) becomes bonded through
        # sustained interaction.
        if sig.origin in ("environment",):
            self.elink[sig.origin] = min(1.0, self.elink.get(sig.origin, 0.2) + 0.01)
            self.state["elinks"] = len(self.elink)

    def bond(self, source: str, weight: float) -> None:
        """Operator override of an e.Link weight."""
        self.elink[source] = max(0.0, min(1.0, weight))
        self.state["elinks"] = len(self.elink)

    # ---- the NO --------------------------------------------------------

    async def negate(self, meaning: str, source: str = "environment",
                     strength: float = 1.0) -> float:
        """Say NO to a meaning, weighted by the bond to the source."""
        w = self.elink.get(source, 0.2)
        new = min(1.0, self.limitations.get(meaning, 0.0) + 0.34 * w * strength)
        self.limitations[meaning] = new
        self.state["limitations"] = len(self.limitations)
        # Each consistent NO builds the capacity for non-contradiction.
        self.non_contradiction = min(1.0, self.non_contradiction + 0.05 * w)
        await self.bus.publish(MapUpdate(
            origin=self.name,
            key=f"no:{meaning}",
            value=round(new, 3),
            boundary=True,
        ))
        return new

    def is_forbidden(self, meaning: str) -> bool:
        if self.suspended:
            return False
        return self.limitations.get(meaning, 0.0) >= self.forbid_threshold

    # ---- loop ----------------------------------------------------------

    async def _tick(self) -> None:
        try:
            while self.conscience.lifecycle.alive:
                await asyncio.sleep(self.period)
                if not self.enabled:
                    continue
                # Limitations decay slowly (very slow forgetting).
                if self.limitations:
                    self.limitations = {
                        k: v * self.decay for k, v in self.limitations.items()
                        if v * self.decay > 0.02
                    }
                self.non_contradiction *= 0.999
                self.state.update({
                    "limitations": len(self.limitations),
                    "non_contradiction": round(self.non_contradiction, 3),
                    "suspended": self.suspended,
                    "elinks": len(self.elink),
                })
        except asyncio.CancelledError:
            return
