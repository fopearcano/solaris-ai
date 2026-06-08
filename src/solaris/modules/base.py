"""
Module — the base class every Conscience module inherits from.

A Module is a peer in the Modular Network. It holds:

- a reference to Conscience (to read shared services like Logos,
  not for imperative coupling);
- a reference to the Bus (for pub/sub);
- a small, observable .state dict that the Inner MAP can read.

Lifecycle: start() registers subscriptions and launches background
tasks; stop() cancels them. The Bus itself is torn down by
Conscience.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from solaris.conscience import Conscience
    from solaris.runtime import Bus


class Module:
    name: str = ""

    def __init__(self, conscience: "Conscience") -> None:
        self.conscience = conscience
        self.bus: "Bus" = conscience.bus
        self.state: dict[str, Any] = {}
        # When False the module is paused: the Bus skips its handlers
        # and its background loops idle. Toggled by the Console.
        self.enabled: bool = True

    async def start(self) -> None:
        """Register subscriptions and start any background tasks."""

    async def stop(self) -> None:
        """Stop background tasks. Conscience handles bus teardown."""

    def observe(self) -> dict[str, Any]:
        """What the Inner MAP sees of this module."""
        return {"name": self.name, **self.state}

    def __repr__(self) -> str:
        return f"<{type(self).__name__} {self.name!r}>"
