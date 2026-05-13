"""
Web UI runner.

Boots a Conscience and serves the visualisation at
http://127.0.0.1:8765/. The system stays alive until either the UI
posts /die or the user hits Ctrl+C.

Run with:

    PYTHONPATH=src python -m solaris.web
"""

from __future__ import annotations

import argparse
import asyncio

from solaris.conscience import Conscience
from solaris.web.server import HttpServer


async def run(host: str, port: int) -> None:
    c = Conscience()
    await c.birth()
    server = HttpServer(c, host=host, port=port)
    await server.start()
    print("=" * 60)
    print("Solaris_Ai — Conscience BORN")
    print(f"  UI:  http://{host}:{port}/")
    print(f"  modules: {len(c._modules)}")
    print("Press Ctrl+C to die, or use the UI's Die button.")
    print("=" * 60)
    try:
        # Idle loop: hold the process up while the system runs.
        while c.lifecycle.alive:
            await asyncio.sleep(0.5)
    except asyncio.CancelledError:
        pass
    finally:
        await server.stop()
        if c.lifecycle.alive:
            await c.death(cause="server stop")
        print(
            f"DIED — age {c.lifecycle.age:.2f}s, "
            f"cause: {c.lifecycle.cause_of_death}"
        )


def main() -> None:
    parser = argparse.ArgumentParser(prog="solaris.web")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", default=8765, type=int)
    args = parser.parse_args()
    try:
        asyncio.run(run(args.host, args.port))
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
