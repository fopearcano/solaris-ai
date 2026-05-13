"""
Auto-Regeneration — self-rewriting.

MODULES.md:

    AUTO-RIGENERATION PROCESS
    - Code builder
    - Updating process auto-writing

In this conceptual codebase we do *not* rewrite Python source on
disk. Auto-Regeneration rewrites the *configuration* of the running
system: it reads MapUpdate signals published by Backpropagation
and pushes their adjustments into module parameters that have been
declared rewriteable.

This is the operational definition of 'auto-writing' that fits a
runtime: configuration is what the system *currently is*, and
changing it changes the system. Source code is the system's
biology; configuration is its current state.

Subscribes to: MapUpdate (only those starting with 'backprop:').
Publishes:     MapUpdate(key='autoregen:<target>', value={...}).
Effects:       Mutates I/O Module's action_threshold (the only
               currently-rewriteable parameter; more can be added
               by registering them here).
"""

from __future__ import annotations

from solaris.modules.base import Module
from solaris.runtime.signals import MapUpdate


class AutoRegeneration(Module):
    name = "auto_regeneration"

    def __init__(self, conscience) -> None:
        super().__init__(conscience)
        self.state = {"rewrites": 0}

    async def start(self) -> None:
        self.bus.subscribe(MapUpdate, self._on_update)

    async def _on_update(self, sig: MapUpdate) -> None:
        if sig.origin == self.name:
            return
        if not sig.key.startswith("backprop:"):
            return
        target = sig.key[len("backprop:"):]
        if target == "io_module":
            # A negative adjustment means: be slower to commit.
            new = max(0.1, min(0.9, self.conscience.io.action_threshold - 0.05 * sig.value))
            self.conscience.io.action_threshold = new
            self.state["rewrites"] += 1
            await self.bus.publish(MapUpdate(
                origin=self.name,
                key=f"autoregen:{target}",
                value={"action_threshold": round(new, 3)},
            ))
