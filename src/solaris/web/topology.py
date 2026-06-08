"""
Topology — the static publish/subscribe map of Conscience.

This is a hand-maintained reflection of the wiring documented at
the top of solaris.conscience. The frontend uses it to lay out the
graph and to know which edges to pulse when a signal fires.

If you change a subscription in a module, update the corresponding
edge here too. Drift between this file and the live bus topology
is treated as a bug — the demo's `/topology` endpoint serves this
verbatim, and `/events` reports the live signals; mismatch shows
up immediately as missing pulses.

Layout grid: (row, col) — col 0..6, row 0..4.
Roles drive the node colour in the UI.
"""

from __future__ import annotations

# Layout: rows top-to-bottom, columns left-to-right.
#   row -1 environment         (special: external stimuli / reactions)
#   row 0  intake + drive      (Memory/Senses (sensory gateway), AION, Logos)
#   row 1  perception          (Cognition, Anticipation, Mysterium)
#   row 2  decision            (I/O, Uncertainty, Habit, Synthesis)
#   row 3  self                (InnerMap, Ego, AutoDet, DimComp)
#   row 4  adaptation          (Backprop, AutoRegen, Complexity, Language)
#
# Memory/Senses is placed in row 0 — the same row as AION and Logos —
# because it is the *sensory gateway* (CONCEPTS.md: 'Conscience <->
# Sensorial Perception (senses)'). Environment sits directly above it
# so the Environment -> MemorySenses edge is short, and the frontend
# styles it as the primary 'sensory channel' (amber).

MODULES: list[dict] = [
    {"id": "environment",            "row": -1, "col": 0, "role": "env",        "label": "Environment"},

    {"id": "memory_senses",          "row": 0,  "col": 0, "role": "perception", "label": "Memory/Senses"},
    {"id": "aion_impulse",           "row": 0,  "col": 2, "role": "core",       "label": "AION/IMPULSE"},
    {"id": "logos",                  "row": 0,  "col": 4, "role": "core",       "label": "Logos"},

    {"id": "cognition",              "row": 1,  "col": 2, "role": "perception", "label": "Cognition"},
    {"id": "anticipation",           "row": 1,  "col": 4, "role": "perception", "label": "Anticipation"},
    {"id": "mysterium",              "row": 1,  "col": 6, "role": "perception", "label": "Mysterium"},

    {"id": "metabolism",             "row": 0,  "col": 6, "role": "decision",   "label": "Metabolism"},
    {"id": "negation",               "row": 2,  "col": 6, "role": "self",       "label": "Negation"},
    {"id": "parallelisation",        "row": 1,  "col": 0, "role": "perception", "label": "Parallel"},
    {"id": "safety",                 "row": 4,  "col": 0, "role": "self",       "label": "Safety"},

    {"id": "io_module",              "row": 2,  "col": 1, "role": "decision",   "label": "I/O"},
    {"id": "uncertainty",            "row": 2,  "col": 2, "role": "decision",   "label": "Uncertainty"},
    {"id": "habit",                  "row": 2,  "col": 4, "role": "decision",   "label": "Habit"},
    {"id": "synthesis",              "row": 2,  "col": 5, "role": "decision",   "label": "Synthesis"},

    {"id": "inner_map",              "row": 3,  "col": 0, "role": "self",       "label": "Inner MAP"},
    {"id": "ego",                    "row": 3,  "col": 2, "role": "self",       "label": "Ego"},
    {"id": "auto_determination",     "row": 3,  "col": 4, "role": "self",       "label": "Auto-Det"},
    {"id": "dimensional_comparison", "row": 3,  "col": 6, "role": "self",       "label": "Dim.Comp"},

    {"id": "backpropagation",        "row": 4,  "col": 1, "role": "adapt",      "label": "Backprop"},
    {"id": "auto_regeneration",      "row": 4,  "col": 2, "role": "adapt",      "label": "AutoRegen"},
    {"id": "complexity",             "row": 4,  "col": 4, "role": "adapt",      "label": "Complexity"},
    {"id": "language",               "row": 4,  "col": 6, "role": "adapt",      "label": "Language"},
]

EDGES: list[dict] = [
    # AION/IMPULSE
    {"from": "aion_impulse", "to": "logos",          "via": "Push"},
    {"from": "aion_impulse", "to": "io_module",      "via": "Push"},
    {"from": "aion_impulse", "to": "language",       "via": "Push"},
    {"from": "aion_impulse", "to": "cognition",      "via": "Stimulus"},
    {"from": "aion_impulse", "to": "memory_senses",  "via": "Stimulus"},
    {"from": "aion_impulse", "to": "ego",            "via": "Stimulus"},
    {"from": "aion_impulse", "to": "language",       "via": "Stimulus"},

    # Logos
    {"from": "logos", "to": "inner_map",              "via": "LogosTension"},
    {"from": "logos", "to": "auto_determination",     "via": "LogosTension"},
    {"from": "logos", "to": "synthesis",              "via": "LogosTension"},
    {"from": "logos", "to": "complexity",             "via": "LogosTension"},
    {"from": "logos", "to": "language",               "via": "LogosTension"},

    # Cognition
    {"from": "cognition", "to": "inner_map",          "via": "MeaningEvent"},
    {"from": "cognition", "to": "io_module",          "via": "MeaningEvent"},
    {"from": "cognition", "to": "mysterium",          "via": "MeaningEvent"},
    {"from": "cognition", "to": "anticipation",       "via": "MeaningEvent"},
    {"from": "cognition", "to": "ego",                "via": "MeaningEvent"},
    {"from": "cognition", "to": "language",           "via": "MeaningEvent"},

    # I/O Module
    {"from": "io_module", "to": "inner_map",          "via": "Desire"},
    {"from": "io_module", "to": "language",           "via": "Desire"},
    {"from": "io_module", "to": "memory_senses",      "via": "Action"},
    {"from": "io_module", "to": "habit",              "via": "Action"},
    {"from": "io_module", "to": "language",           "via": "Action"},

    # Habit
    {"from": "habit", "to": "inner_map",              "via": "MapUpdate"},
    {"from": "habit", "to": "dimensional_comparison", "via": "MapUpdate"},
    {"from": "habit", "to": "auto_regeneration",      "via": "MapUpdate"},
    {"from": "habit", "to": "language",               "via": "MapUpdate"},

    # Synthesis
    {"from": "synthesis", "to": "inner_map",              "via": "MapUpdate"},
    {"from": "synthesis", "to": "dimensional_comparison", "via": "MapUpdate"},
    {"from": "synthesis", "to": "auto_regeneration",      "via": "MapUpdate"},
    {"from": "synthesis", "to": "language",               "via": "MapUpdate"},

    # Backpropagation
    {"from": "backpropagation", "to": "inner_map",              "via": "MapUpdate"},
    {"from": "backpropagation", "to": "auto_regeneration",      "via": "MapUpdate"},
    {"from": "backpropagation", "to": "dimensional_comparison", "via": "MapUpdate"},
    {"from": "backpropagation", "to": "language",               "via": "MapUpdate"},

    # AutoRegeneration
    {"from": "auto_regeneration", "to": "inner_map",              "via": "MapUpdate"},
    {"from": "auto_regeneration", "to": "dimensional_comparison", "via": "MapUpdate"},
    {"from": "auto_regeneration", "to": "language",               "via": "MapUpdate"},

    # AutoDetermination
    {"from": "auto_determination", "to": "inner_map",              "via": "MapUpdate"},
    {"from": "auto_determination", "to": "dimensional_comparison", "via": "MapUpdate"},
    {"from": "auto_determination", "to": "auto_regeneration",      "via": "MapUpdate"},
    {"from": "auto_determination", "to": "language",               "via": "MapUpdate"},

    # DimensionalComparison
    {"from": "dimensional_comparison", "to": "inner_map",         "via": "MapUpdate"},
    {"from": "dimensional_comparison", "to": "auto_regeneration", "via": "MapUpdate"},
    {"from": "dimensional_comparison", "to": "language",          "via": "MapUpdate"},

    # Ego
    {"from": "ego", "to": "inner_map",              "via": "MapUpdate"},
    {"from": "ego", "to": "dimensional_comparison", "via": "MapUpdate"},
    {"from": "ego", "to": "auto_regeneration",      "via": "MapUpdate"},
    {"from": "ego", "to": "language",               "via": "MapUpdate"},

    # Environment / Complexity -> Stimulus subscribers
    {"from": "environment", "to": "aion_impulse",   "via": "Stimulus"},
    {"from": "environment", "to": "cognition",      "via": "Stimulus"},
    {"from": "environment", "to": "memory_senses",  "via": "Stimulus"},
    {"from": "environment", "to": "ego",            "via": "Stimulus"},
    {"from": "environment", "to": "language",       "via": "Stimulus"},
    {"from": "complexity",  "to": "aion_impulse",   "via": "Stimulus"},
    {"from": "complexity",  "to": "cognition",      "via": "Stimulus"},
    {"from": "complexity",  "to": "memory_senses",  "via": "Stimulus"},
    {"from": "complexity",  "to": "ego",            "via": "Stimulus"},
    {"from": "complexity",  "to": "language",       "via": "Stimulus"},

    # Environment -> Reaction subscribers
    {"from": "environment", "to": "habit",           "via": "Reaction"},
    {"from": "environment", "to": "backpropagation", "via": "Reaction"},
    {"from": "environment", "to": "language",        "via": "Reaction"},

    # Metabolism — oniric (dream) stimuli flow during sleep (oTD)
    {"from": "metabolism", "to": "cognition",        "via": "Stimulus"},
    {"from": "metabolism", "to": "memory_senses",    "via": "Stimulus"},
    {"from": "metabolism", "to": "ego",              "via": "Stimulus"},
    {"from": "metabolism", "to": "language",         "via": "Stimulus"},

    # Negation — e.Link grows from interaction; NO writes Limitations
    {"from": "environment", "to": "negation",            "via": "Stimulus"},
    {"from": "environment", "to": "negation",            "via": "Reaction"},
    {"from": "negation",    "to": "inner_map",            "via": "MapUpdate"},
    {"from": "negation",    "to": "dimensional_comparison", "via": "MapUpdate"},
    {"from": "negation",    "to": "language",            "via": "MapUpdate"},

    # Safety — environmental harm depletes vitality; shield/intervene (Mod-1)
    {"from": "environment", "to": "safety",     "via": "Stimulus"},
    {"from": "safety",      "to": "inner_map",  "via": "MapUpdate"},
    {"from": "safety",      "to": "language",   "via": "MapUpdate"},

    # Parallelisation — forks from Logos opposition, merges (Mod-2)
    {"from": "logos",           "to": "parallelisation", "via": "LogosTension"},
    {"from": "parallelisation", "to": "inner_map",       "via": "MapUpdate"},
    {"from": "parallelisation", "to": "language",        "via": "MapUpdate"},
]


TOPOLOGY = {"modules": MODULES, "edges": EDGES}
