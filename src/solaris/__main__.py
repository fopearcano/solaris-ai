"""
Demo runner.

Boots a Conscience, prints the wiring, injects a few external
stimuli, delivers a feedback Reaction, then dies cleanly.

Run with:

    python -m solaris
"""

from __future__ import annotations

import asyncio
import json

from solaris.conscience import Conscience
from solaris.runtime.signals import Action


async def run() -> None:
    c = Conscience()
    await c.birth()
    print("=" * 64)
    print(f"BORN — {len(c._modules)} modules wired")
    print("=" * 64)
    print("Bus subscriptions:")
    for sig, handlers in c.topology().items():
        print(f"  {sig}:")
        for h in handlers:
            print(f"    -> {h}")
    print()

    # Let AION beat in silence so the absence-stimulus fires at
    # least once: 'I exist!'
    await asyncio.sleep(0.7)

    print("STIMULUS: 'light' (vision, intensity=0.8)")
    await c.stimulate("light", modality="vision", intensity=0.8)
    await asyncio.sleep(0.4)

    print("STIMULUS: 'sound' (audio, intensity=0.9)")
    await c.stimulate("sound", modality="audio", intensity=0.9)
    await asyncio.sleep(0.4)

    print("STIMULUS: 'light' again — less novel")
    await c.stimulate("light", modality="vision", intensity=0.7)
    await asyncio.sleep(0.4)

    # Drive a positive Reaction so Habit and Backpropagation have
    # something to chew. We pick the most recent Action on the bus.
    last_action = next(
        (s for s in reversed(c.bus.trace) if isinstance(s, Action)),
        None,
    )
    if last_action is not None:
        # Negative valence so Backpropagation actually fires and
        # Auto-Regeneration ends up rewriting IOModule's threshold.
        print(f"REACTION on Action #{last_action.id}: -0.8")
        await c.react(last_action.id, -0.8)
    else:
        print("REACTION skipped — no Action was committed.")
    await asyncio.sleep(0.6)

    print()
    print("Language trace (last 30 lines):")
    for line in c.language.narrate(30):
        print(f"  {line}")

    print()
    print("Snapshot:")
    print(json.dumps(c.snapshot(), indent=2, default=str))

    await c.death(cause="demo end")
    print()
    print(
        f"DIED — age {c.lifecycle.age:.2f}s, cause: "
        f"{c.lifecycle.cause_of_death}"
    )


def main() -> None:
    asyncio.run(run())


if __name__ == "__main__":
    main()
