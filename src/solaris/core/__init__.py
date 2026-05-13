"""Core — the heartbeat (AION/IMPULSE) and the calculus (Logos).

These are not modules in the same sense as the peers in
solaris.modules. They are primitives the rest of the system runs
on:

- AION/IMPULSE provides drive (Stimulus -> Push -> Desire -> Action)
- Logos provides the opposition (dia-ballein vs sun-ballein) whose
  fracture forces motion.
"""

from solaris.core.aion_impulse import AionImpulse
from solaris.core.logos import Logos

__all__ = ["AionImpulse", "Logos"]
