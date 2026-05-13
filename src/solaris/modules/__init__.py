"""Module implementations — the peers of the Modular Network.

There is no global controller. Every module subscribes to Signals
on the Bus, does its specific work, and publishes its own Signals.
The system's behaviour emerges from the coupling, not from
top-down orchestration.

Module roster (organised by role; concept references in each
file's docstring):

  Self / boundaries:
    - InnerMap                (self-representation)
    - Ego                     (necessary illusion)
    - AutoDetermination       (Being / Not-Being)
    - DimensionalComparison   (limits, boundaries)

  Perception / cognition:
    - MemorySenses            (memory in-between)
    - Cognition               (meaning assignment)
    - Language                (cross-function communication)

  Drive / decision:
    - IOModule                (linking: Stimulus -> Action)
    - Uncertainty             (choice without data)

  Adaptation:
    - Habit                   (reinforcement)
    - Synthesis               (subtractive optimisation)
    - Backpropagation         (plasticity)
    - AutoRegeneration        (self-rewriting)

  Tension / unknown:
    - Mysterium               (the unknown)
    - Anticipation            (forecast capacity)
    - Complexity              (Escape sub-process)
"""
