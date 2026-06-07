"""
HTTP + Server-Sent-Events server for the Solaris UI.

Pure-stdlib (asyncio) implementation. Routes:

    GET  /                 -> static/index.html
    GET  /app.css          -> static/app.css
    GET  /app.js           -> static/app.js
    GET  /topology         -> JSON publish/subscribe map
    GET  /events           -> SSE stream of every Signal + periodic
                              snapshots
    POST /stimulate        -> inject a Stimulus
    POST /react            -> inject a Reaction on the most recent
                              Action
    POST /die              -> kill the Conscience (lifecycle.die)

For SSE, each connected client gets its own asyncio.Queue. A
wildcard subscriber on the Bus pushes every Signal as JSON into
every queue; a periodic task pushes Conscience.snapshot() so the
state panel can stay current. If a client disconnects, its queue
is removed.

The HTTP parser is intentionally minimal — this is a localhost UI
server, not a public service.
"""

from __future__ import annotations

import asyncio
import json
import time
from pathlib import Path
from typing import Any

from solaris.conscience import Conscience
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
from solaris.web.resources import ResourceMonitor
from solaris.web.topology import TOPOLOGY

HERE = Path(__file__).parent
STATIC = HERE / "static"


def signal_to_json(sig: Signal) -> dict[str, Any]:
    out: dict[str, Any] = {
        "id": sig.id,
        "ts": sig.timestamp,
        "origin": sig.origin,
        "type": type(sig).__name__,
    }
    if isinstance(sig, Stimulus):
        out.update({
            "modality": sig.modality,
            "payload": str(sig.payload),
            "intensity": sig.intensity,
            "is_absence": sig.is_absence,
        })
    elif isinstance(sig, Push):
        out.update({"intensity": sig.intensity, "direction": sig.direction})
    elif isinstance(sig, Desire):
        out.update({
            "proposal": sig.proposal,
            "motivation": sig.motivation,
            "confidence": sig.confidence,
        })
    elif isinstance(sig, Action):
        out.update({"name": sig.name, "payload": sig.payload})
    elif isinstance(sig, Reaction):
        out.update({"action_id": sig.action_id, "valence": sig.valence})
    elif isinstance(sig, MeaningEvent):
        out.update({"meaning": sig.meaning, "novelty": sig.novelty})
    elif isinstance(sig, MapUpdate):
        out.update({"key": sig.key, "value": sig.value, "boundary": sig.boundary})
    elif isinstance(sig, LogosTension):
        out.update({
            "division": sig.division,
            "union": sig.union,
            "fracture": sig.fracture,
        })
    return out


class HttpServer:
    def __init__(
        self,
        conscience: Conscience,
        host: str = "127.0.0.1",
        port: int = 8765,
        snapshot_period: float = 0.4,
    ) -> None:
        self.conscience = conscience
        self.host = host
        self.port = port
        self.snapshot_period = snapshot_period
        self.clients: set[asyncio.Queue[str]] = set()
        self._server: asyncio.AbstractServer | None = None
        self._snapshot_task: asyncio.Task | None = None
        self._resource_task: asyncio.Task | None = None
        self.monitor = ResourceMonitor()
        self.resources: dict = {}

    async def start(self) -> None:
        self.conscience.bus.subscribe_all(self._broadcast)
        self._server = await asyncio.start_server(self._handle, self.host, self.port)
        self._snapshot_task = asyncio.create_task(self._snapshot_loop())
        self._resource_task = asyncio.create_task(self._resource_loop())

    async def stop(self) -> None:
        for task in (self._snapshot_task, self._resource_task):
            if task is not None:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
        if self._server is not None:
            self._server.close()
            try:
                await self._server.wait_closed()
            except Exception:
                pass

    def _payload(self) -> dict:
        snap = self.conscience.snapshot()
        snap["resources"] = self.resources
        return snap

    async def _resource_loop(self) -> None:
        # Sample once a second; run the (occasionally blocking) sampler
        # in a thread so it never stalls the event loop.
        loop = asyncio.get_running_loop()
        try:
            while True:
                try:
                    self.resources = await loop.run_in_executor(None, self.monitor.sample)
                except Exception:  # noqa: BLE001
                    pass
                await asyncio.sleep(1.0)
        except asyncio.CancelledError:
            return

    # ---- SSE plumbing -------------------------------------------------

    async def _broadcast(self, sig: Signal) -> None:
        msg = json.dumps({"event": "signal", "data": signal_to_json(sig)})
        dead: list[asyncio.Queue[str]] = []
        for q in self.clients:
            try:
                q.put_nowait(msg)
            except asyncio.QueueFull:
                dead.append(q)
        for q in dead:
            self.clients.discard(q)

    async def _snapshot_loop(self) -> None:
        try:
            while True:
                await asyncio.sleep(self.snapshot_period)
                msg = json.dumps({"event": "snapshot", "data": self._payload()}, default=str)
                for q in list(self.clients):
                    try:
                        q.put_nowait(msg)
                    except asyncio.QueueFull:
                        pass
        except asyncio.CancelledError:
            return

    # ---- HTTP plumbing ------------------------------------------------

    async def _handle(
        self,
        reader: asyncio.StreamReader,
        writer: asyncio.StreamWriter,
    ) -> None:
        try:
            request_line = await reader.readline()
            if not request_line:
                return
            try:
                method, path, _ = request_line.decode("ascii", errors="replace").split(maxsplit=2)
            except ValueError:
                return
            headers: dict[str, str] = {}
            while True:
                line = await reader.readline()
                if line in (b"\r\n", b"\n", b""):
                    break
                k, _, v = line.decode("latin-1").partition(":")
                headers[k.strip().lower()] = v.strip()
            length = int(headers.get("content-length", "0") or "0")
            body = await reader.readexactly(length) if length > 0 else b""
            await self._route(method, path, body, writer)
        except (ConnectionResetError, BrokenPipeError):
            return
        except Exception as exc:  # noqa: BLE001
            try:
                self._send(writer, 500, "text/plain", f"server error: {exc}".encode())
                await writer.drain()
            except Exception:
                pass
        finally:
            try:
                writer.close()
                await writer.wait_closed()
            except Exception:
                pass

    async def _route(
        self,
        method: str,
        path: str,
        body: bytes,
        writer: asyncio.StreamWriter,
    ) -> None:
        if method == "GET" and path == "/":
            await self._serve_static(writer, "index.html", "text/html; charset=utf-8")
        elif method == "GET" and path == "/app.css":
            await self._serve_static(writer, "app.css", "text/css; charset=utf-8")
        elif method == "GET" and path == "/app.js":
            await self._serve_static(writer, "app.js", "application/javascript; charset=utf-8")
        elif method == "GET" and path == "/topology":
            self._send(writer, 200, "application/json",
                       json.dumps(TOPOLOGY).encode("utf-8"))
            await writer.drain()
        elif method == "GET" and path == "/events":
            await self._stream_events(writer)
        elif method == "POST" and path == "/stimulate":
            await self._handle_stimulate(body, writer)
        elif method == "POST" and path == "/react":
            await self._handle_react(body, writer)
        elif method == "POST" and path == "/die":
            await self._handle_die(writer)
        else:
            self._send(writer, 404, "text/plain", b"not found")
            await writer.drain()

    async def _serve_static(
        self,
        writer: asyncio.StreamWriter,
        name: str,
        ctype: str,
    ) -> None:
        try:
            data = (STATIC / name).read_bytes()
            self._send(writer, 200, ctype, data)
        except FileNotFoundError:
            self._send(writer, 404, "text/plain", b"not found")
        await writer.drain()

    async def _stream_events(self, writer: asyncio.StreamWriter) -> None:
        q: asyncio.Queue[str] = asyncio.Queue(maxsize=2000)
        self.clients.add(q)
        try:
            writer.write(
                b"HTTP/1.1 200 OK\r\n"
                b"Content-Type: text/event-stream; charset=utf-8\r\n"
                b"Cache-Control: no-cache\r\n"
                b"Connection: keep-alive\r\n"
                b"X-Accel-Buffering: no\r\n"
                b"\r\n"
            )
            await writer.drain()
            # Initial snapshot so the UI does not start blank.
            initial = json.dumps({
                "event": "snapshot",
                "data": self._payload(),
            }, default=str)
            writer.write(f"data: {initial}\n\n".encode("utf-8"))
            await writer.drain()
            while True:
                msg = await q.get()
                writer.write(f"data: {msg}\n\n".encode("utf-8"))
                await writer.drain()
        except (ConnectionResetError, BrokenPipeError, asyncio.CancelledError):
            return
        finally:
            self.clients.discard(q)

    async def _handle_stimulate(
        self,
        body: bytes,
        writer: asyncio.StreamWriter,
    ) -> None:
        try:
            data = json.loads(body) if body else {}
        except json.JSONDecodeError:
            data = {}
        if not self.conscience.lifecycle.alive:
            self._send(writer, 409, "application/json",
                       b'{"ok":false,"error":"system is dead"}')
            await writer.drain()
            return
        await self.conscience.stimulate(
            data.get("payload", "ping"),
            modality=str(data.get("modality", "external")),
            intensity=float(data.get("intensity", 0.7)),
        )
        self._send(writer, 200, "application/json", b'{"ok":true}')
        await writer.drain()

    async def _handle_react(
        self,
        body: bytes,
        writer: asyncio.StreamWriter,
    ) -> None:
        try:
            data = json.loads(body) if body else {}
        except json.JSONDecodeError:
            data = {}
        if not self.conscience.lifecycle.alive:
            self._send(writer, 409, "application/json",
                       b'{"ok":false,"error":"system is dead"}')
            await writer.drain()
            return
        trace = self.conscience.bus.trace
        last_action = next(
            (s for s in reversed(trace) if isinstance(s, Action)),
            None,
        )
        if last_action is None:
            self._send(writer, 200, "application/json",
                       b'{"ok":false,"error":"no action yet"}')
            await writer.drain()
            return
        await self.conscience.react(last_action.id, float(data.get("valence", 0.5)))
        self._send(writer, 200, "application/json",
                   json.dumps({"ok": True, "action_id": last_action.id}).encode())
        await writer.drain()

    async def _handle_die(self, writer: asyncio.StreamWriter) -> None:
        # Send the response, *then* schedule death — so the client
        # gets its 200 before the bus stops broadcasting.
        self._send(writer, 200, "application/json", b'{"ok":true}')
        await writer.drain()
        if self.conscience.lifecycle.alive:
            asyncio.create_task(self.conscience.death(cause="die button"))

    @staticmethod
    def _send(
        writer: asyncio.StreamWriter,
        code: int,
        ctype: str,
        body: bytes,
    ) -> None:
        reason = {200: "OK", 404: "Not Found", 409: "Conflict",
                  500: "Server Error"}.get(code, "OK")
        head = (
            f"HTTP/1.1 {code} {reason}\r\n"
            f"Content-Type: {ctype}\r\n"
            f"Content-Length: {len(body)}\r\n"
            f"Cache-Control: no-store\r\n"
            f"Connection: close\r\n"
            f"\r\n"
        ).encode("ascii")
        writer.write(head)
        writer.write(body)
