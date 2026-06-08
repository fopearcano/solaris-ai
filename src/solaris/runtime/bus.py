"""
Bus — typed publish/subscribe for inter-module communication.

Modules never call each other directly. They publish typed Signals
and subscribe to types they care about. The wiring of the system
is therefore a function of subscribe() calls, which Conscience
prints at startup so the topology is auditable.

A handler exception does not sink the bus; it is logged and
ignored. This matches the spirit of CONCEPTS.md: a single failing
neuron does not stop conscience.
"""

from __future__ import annotations

import asyncio
from collections import defaultdict
from typing import Awaitable, Callable, DefaultDict, Type

from solaris.runtime.signals import Signal

Handler = Callable[[Signal], Awaitable[None]]


class Bus:
    def __init__(self, *, trace: bool = True, trace_capacity: int = 4096) -> None:
        self._subscribers: DefaultDict[Type[Signal], list[Handler]] = defaultdict(list)
        self._wildcard: list[Handler] = []
        self._trace: list[Signal] = []
        self._trace_enabled = trace
        self._trace_capacity = trace_capacity

    def subscribe(self, signal_type: Type[Signal], handler: Handler) -> None:
        self._subscribers[signal_type].append(handler)

    def subscribe_all(self, handler: Handler) -> None:
        self._wildcard.append(handler)

    def subscriptions(self) -> dict[str, list[str]]:
        out: dict[str, list[str]] = {}
        for sig_type, handlers in self._subscribers.items():
            out[sig_type.__name__] = [
                getattr(h, "__qualname__", repr(h)) for h in handlers
            ]
        return out

    async def publish(self, signal: Signal) -> None:
        if self._trace_enabled:
            self._trace.append(signal)
            if len(self._trace) > self._trace_capacity:
                self._trace = self._trace[-self._trace_capacity :]
        handlers = list(self._subscribers.get(type(signal), []))
        handlers.extend(self._wildcard)
        # Skip handlers owned by a paused module (Console pause/resume).
        handlers = [
            h for h in handlers
            if getattr(getattr(h, "__self__", None), "enabled", True)
        ]
        await asyncio.gather(
            *(self._safely(h, signal) for h in handlers),
        )

    async def _safely(self, handler: Handler, signal: Signal) -> None:
        try:
            await handler(signal)
        except Exception as exc:  # noqa: BLE001
            print(
                f"[bus] handler {handler!r} failed on "
                f"{type(signal).__name__}: {exc}"
            )

    @property
    def trace(self) -> list[Signal]:
        return list(self._trace)
