#!/usr/bin/env python3
"""
Generate Solaris_Ai_SCHEMATIC.svg — a detailed infographic of the
entire Conscience system.

Module positions and edges are read from solaris.web.topology so the
schematic can never drift from the live system. Re-run after any
change to the topology:

    python3 tools/generate_schematic.py -o Solaris_Ai_SCHEMATIC.svg
"""

from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

# Make the local src/ importable without installing.
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from solaris.web.topology import EDGES, MODULES  # noqa: E402

# ---------------------------------------------------------------------- constants

W, H = 1400, 2870

BG            = "#0a0d12"
SECTION_BG    = "#0c1016"
BAND_BG       = "#11161e"
BORDER        = "#1f2630"
TXT_PRIMARY   = "#d6dee0"
TXT_SECONDARY = "#8794a3"
TXT_MUTED     = "#6b7682"
TXT_LIGHT     = "#c0c8cf"

ROLE_COLORS = {
    "core":       "#ff6b6b",
    "perception": "#62b6ff",
    "decision":   "#7cf088",
    "self":       "#ffb14d",
    "adapt":      "#c884ff",
    "env":        "#9aa5b1",
}
SIGNAL_COLORS = {
    "Stimulus":     "#62b6ff",
    "Push":         "#ff8888",
    "Desire":       "#ffb14d",
    "Action":       "#7cf088",
    "Reaction":     "#ff85aa",
    "MeaningEvent": "#7df0ff",
    "MapUpdate":    "#c884ff",
    "LogosTension": "#d0d6dd",
}

# Schematic-specific layout for the architecture section. The web UI
# uses a row/col grid (topology.py); the schematic uses an
# anchored layout where AION/IMPULSE sits centrally with everything
# else organised around it — to make the user's mental model
# ("everything is driven by the Core") visually unambiguous.
SCHEMATIC_POSITIONS: dict[str, tuple[float, float]] = {
    # Top: external world.
    "environment":            (700, 970),
    # Sensory in.
    "memory_senses":          (700, 1080),
    "anticipation":           (430, 1145),
    "mysterium":              (970, 1145),
    # Meaning.
    "cognition":              (700, 1210),
    # CORE.
    "aion_impulse":           (570, 1350),
    "logos":                  (830, 1350),
    # Decision row (driven by Push).
    "uncertainty":            (560, 1500),
    "io_module":              (700, 1500),
    "habit":                  (840, 1500),
    "synthesis":              (1000, 1500),
    # Self column (left).
    "inner_map":              (180, 1160),
    "ego":                    (180, 1270),
    "auto_determination":     (180, 1380),
    "dimensional_comparison": (180, 1490),
    # Adaptation row (bottom).
    "backpropagation":        (440, 1620),
    "auto_regeneration":      (590, 1620),
    "complexity":             (770, 1620),
    "language":               (940, 1620),
    # Metabolic + Negation sub-modules.
    "metabolism":             (1180, 1210),
    "negation":               (1180, 1500),
}


# Highlighted flows: the architectural narrative the diagram tells.
# (from_id, to_id, color, label, dashed)
HIGHLIGHTED_FLOWS = [
    ("environment",       "memory_senses",     "#ffb14d", "sensory channel",    True),
    ("memory_senses",     "cognition",         "#7df0ff", "perception",         False),
    ("cognition",         "io_module",         "#62b6ff", "meaning",            False),
    ("aion_impulse",      "logos",             "#ff8888", "calculus",           False),
    ("aion_impulse",      "io_module",         "#ff5d5d", "PUSH",               False),
    ("io_module",         "habit",             "#7cf088", "action",             False),
    ("auto_regeneration", "io_module",         "#c884ff", "self-rewrite",       True),
]
HIGHLIGHTED_PAIRS = {(f, t) for f, t, *_ in HIGHLIGHTED_FLOWS}


# Per-role description offset below the shape (for the schematic only).
SCHEMATIC_DESC_OFFSET = {
    "core":       102,
    "perception": 56,
    "decision":   58,
    "self":       50,
    "adapt":      52,
    "env":        38,
}

# One-line description per module.
MODULE_DESC = {
    "environment":            "external world",
    "memory_senses":          "memory in-between",
    "aion_impulse":           "heartbeat · drive",
    "logos":                  "opposition engine",
    "cognition":              "meaning assignment",
    "anticipation":           "first-order forecast",
    "mysterium":              "the unknown",
    "io_module":              "links meaning + push",
    "uncertainty":            "choice without data",
    "habit":                  "reinforcement",
    "synthesis":              "subtractive optimisation",
    "inner_map":              "self-representation",
    "ego":                    "necessary illusion",
    "auto_determination":     "Being / Not-Being",
    "dimensional_comparison": "limits &amp; boundaries",
    "backpropagation":        "system plasticity",
    "auto_regeneration":      "self-rewriting",
    "complexity":             "escape sub-process",
    "language":               "wildcard renderer",
    "metabolism":             "wake / sleep / survival",
    "negation":               "the NO · limits",
}

# ---------------------------------------------------------------------- helpers


def hex_points(r: float, pointy: bool = True) -> str:
    pts = []
    phase = 90 if pointy else 0
    for i in range(6):
        a = math.radians(phase + i * 60)
        pts.append(f"{r*math.cos(a):.2f},{r*math.sin(a):.2f}")
    return " ".join(pts)


def node_shape(role: str, cx: float, cy: float, fill: str, mod_id: str = "") -> str:
    if role == "core":
        # AION/IMPULSE is the heartbeat — visually dominant.
        # Logos is the paired calculus, slightly smaller.
        r = 80 if mod_id == "aion_impulse" else 60
        return (
            f'<polygon transform="translate({cx},{cy})" '
            f'points="{hex_points(r, True)}" fill="{fill}" '
            f'class="node-shape node-core" />'
        )
    if role == "self":
        r = 32
        return (
            f'<rect x="{cx - r}" y="{cy - r}" width="{2 * r}" height="{2 * r}" '
            f'rx="6" fill="{fill}" class="node-shape" />'
        )
    if role == "decision":
        # I/O is the central action node — bigger than its modulators.
        r = 46 if mod_id == "io_module" else 38
        return (
            f'<polygon transform="translate({cx},{cy})" '
            f'points="0,{-r} {r},0 0,{r} {-r},0" fill="{fill}" '
            f'class="node-shape" />'
        )
    if role == "adapt":
        return (
            f'<polygon transform="translate({cx},{cy})" '
            f'points="{hex_points(36, False)}" fill="{fill}" '
            f'class="node-shape" />'
        )
    if role == "env":
        w, h = 170, 50
        return (
            f'<rect x="{cx - w / 2}" y="{cy - h / 2}" width="{w}" height="{h}" '
            f'rx="10" fill="{fill}" class="node-shape env-shape" />'
        )
    # perception circle. Memory/Senses is the sensory gateway, bigger.
    r = 42 if mod_id == "memory_senses" else 34
    return f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}" class="node-shape" />'


def render_label(role: str, label: str, x: float, y: float) -> str:
    """Render a label inside a node, splitting on '/' for compact two-line labels."""
    cls = {
        "core": "label-core",
        "env":  "label-env",
    }.get(role, "label")
    if "/" in label and role in ("core", "perception"):
        a, b = label.split("/", 1)
        line_h = 12 if role == "core" else 11
        return (
            f'<text x="{x}" y="{y - 2}" text-anchor="middle" class="{cls}">{a}/</text>\n'
            f'<text x="{x}" y="{y - 2 + line_h}" text-anchor="middle" class="{cls}">{b}</text>'
        )
    # Auto-shrink long labels in tight shapes (perception circle).
    extra = ""
    if role == "perception" and len(label) > 10:
        extra = ' font-size="10"'
    return (
        f'<text x="{x}" y="{y + 4}" text-anchor="middle" '
        f'class="{cls}"{extra}>{label}</text>'
    )


def mod_xy(m: dict) -> tuple[float, float]:
    return SCHEMATIC_POSITIONS[m["id"]]


def edge_path(x1, y1, x2, y2, bend=18):
    """Quadratic Bezier with a small perpendicular bend."""
    mx, my = (x1 + x2) / 2, (y1 + y2) / 2
    dx, dy = x2 - x1, y2 - y1
    length = math.hypot(dx, dy) or 1
    cx = mx - (dy / length) * bend
    cy = my + (dx / length) * bend
    return f"M {x1} {y1} Q {cx:.1f} {cy:.1f} {x2} {y2}"


# ---------------------------------------------------------------------- sections


def section_header() -> str:
    out = []
    out.append(f'<rect x="0" y="0" width="{W}" height="220" fill="{BG}" />')
    out.append(f'<text x="60" y="100" class="h1">SOLARIS_AI</text>')
    out.append(
        f'<text x="60" y="140" class="tagline">'
        f"Conscience — a different approach to AI"
        f"</text>"
    )
    desc = [
        "An AI system inspired by the principles of living things: continuous, embodied,",
        "reactive, aware and plastic. Where mainstream AI is a request → response pipeline,",
        "Solaris_Ai is a continuously running event loop that ends only when its Lifecycle.die().",
    ]
    for i, line in enumerate(desc):
        out.append(f'<text x="60" y="{170 + i * 16}" class="body">{line}</text>')

    out.append(
        f'<text x="{W - 60}" y="100" text-anchor="end" class="muted">'
        f"v0.0.1 · Python 3.11+ · stdlib only</text>"
    )
    out.append(
        f'<text x="{W - 60}" y="124" text-anchor="end" class="body-light">'
        f"20 components · 18 peer modules + 2 core primitives"
        f"</text>"
    )
    out.append(
        f'<text x="{W - 60}" y="146" text-anchor="end" class="body-light">'
        f"8 typed signals · one bus · non-hierarchical"
        f"</text>"
    )
    out.append(
        f'<text x="{W - 60}" y="180" text-anchor="end" class="muted">'
        f"sources: Solaris_Ai_whitepaper.md · Solaris_Ai_CONCEPTS.md · Solaris_Ai_MODULES.md"
        f"</text>"
    )
    out.append(
        f'<text x="{W - 60}" y="198" text-anchor="end" class="muted">'
        f"implementation: src/solaris/"
        f"</text>"
    )
    out.append(f'<line x1="0" y1="220" x2="{W}" y2="220" class="divider" />')
    return "\n".join(out)


def section_title(y: int, num: str, title: str, subtitle: str = "") -> str:
    out = [
        f'<rect x="0" y="{y}" width="{W}" height="46" fill="{BAND_BG}" stroke="{BORDER}" />',
        f'<text x="60" y="{y + 22}" class="section-num">{num}</text>',
        f'<text x="60" y="{y + 38}" class="section-title">{title}</text>',
    ]
    if subtitle:
        out.append(
            f'<text x="{W - 60}" y="{y + 30}" text-anchor="end" '
            f'class="body">{subtitle}</text>'
        )
    return "\n".join(out)


def section_principles() -> str:
    """Section 01 — five core principles."""
    y0 = 230
    out = [section_title(y0, "01", "FIVE CORE PRINCIPLES",
                         "from the whitepaper")]
    cards_y = y0 + 60
    cards_h = 250

    principles = [
        {
            "num": "01",
            "icon": ("hex-pointy", "#ff6b6b", 24),
            "name": "CONTINUOUS\nTHINKING",
            "lines": [
                "AION/IMPULSE drives an event",
                "loop that never returns to idle.",
                "Stopping it = brain death.",
            ],
            "modules": "AION/IMPULSE",
        },
        {
            "num": "02",
            "icon": ("circle", "#62b6ff", 24),
            "name": "SENSORY\nINTEGRATION",
            "lines": [
                "Memory/Senses gateway between",
                "Environment and Conscience.",
                "Memory occurs *in-between*.",
            ],
            "modules": "Memory/Senses, Cognition",
        },
        {
            "num": "03",
            "icon": ("diamond", "#7cf088", 26),
            "name": "REACTIVITY",
            "lines": [
                "Stimulus → Push → Desire →",
                "Action. Every action is also",
                "stimulus and reaction.",
            ],
            "modules": "I/O, Habit, Uncertainty",
        },
        {
            "num": "04",
            "icon": ("rounded-rect", "#ffb14d", 22),
            "name": "IMMEDIATE\nAWARENESS",
            "lines": [
                "Cognition assigns meaning;",
                "Inner MAP keeps a running",
                "self-representation alive.",
            ],
            "modules": "Cognition, Inner MAP, Ego",
        },
        {
            "num": "05",
            "icon": ("hex-flat", "#c884ff", 24),
            "name": "PLASTICITY",
            "lines": [
                "Habit reinforces, Synthesis",
                "subtracts, Backprop reassigns",
                "blame, AutoRegen rewrites.",
            ],
            "modules": "Habit, Synthesis, Backprop",
        },
    ]

    n = len(principles)
    margin = 26
    gap = 8
    avail = W - 2 * margin - (n - 1) * gap
    card_w = avail / n

    for i, p in enumerate(principles):
        x = margin + i * (card_w + gap)
        out.append(
            f'<rect x="{x}" y="{cards_y}" width="{card_w}" height="{cards_h}" '
            f'rx="6" class="panel" />'
        )
        # Number badge
        out.append(
            f'<text x="{x + 16}" y="{cards_y + 22}" class="section-num">{p["num"]}</text>'
        )
        # Icon
        kind, fill, r = p["icon"]
        ix, iy = x + card_w / 2, cards_y + 60
        out.append(_icon(kind, ix, iy, r, fill))
        # Name (multi-line)
        name_lines = p["name"].split("\n")
        for li, ln in enumerate(name_lines):
            out.append(
                f'<text x="{x + card_w / 2}" y="{cards_y + 110 + li * 18}" '
                f'text-anchor="middle" class="h2">{ln}</text>'
            )
        # Body lines
        body_y = cards_y + 110 + len(name_lines) * 18 + 14
        for li, ln in enumerate(p["lines"]):
            out.append(
                f'<text x="{x + card_w / 2}" y="{body_y + li * 16}" '
                f'text-anchor="middle" class="body">{ln}</text>'
            )
        # Modules tag
        out.append(
            f'<line x1="{x + 16}" y1="{cards_y + cards_h - 32}" '
            f'x2="{x + card_w - 16}" y2="{cards_y + cards_h - 32}" class="divider" />'
        )
        out.append(
            f'<text x="{x + card_w / 2}" y="{cards_y + cards_h - 14}" '
            f'text-anchor="middle" class="muted">{p["modules"]}</text>'
        )

    return "\n".join(out)


def _icon(kind: str, cx: float, cy: float, r: float, fill: str) -> str:
    if kind == "hex-pointy":
        return (
            f'<polygon transform="translate({cx},{cy})" '
            f'points="{hex_points(r, True)}" fill="{fill}" '
            f'class="node-shape" />'
        )
    if kind == "hex-flat":
        return (
            f'<polygon transform="translate({cx},{cy})" '
            f'points="{hex_points(r, False)}" fill="{fill}" '
            f'class="node-shape" />'
        )
    if kind == "diamond":
        return (
            f'<polygon transform="translate({cx},{cy})" '
            f'points="0,{-r} {r},0 0,{r} {-r},0" fill="{fill}" '
            f'class="node-shape" />'
        )
    if kind == "rounded-rect":
        return (
            f'<rect x="{cx - r}" y="{cy - r}" width="{2 * r}" height="{2 * r}" '
            f'rx="6" fill="{fill}" class="node-shape" />'
        )
    return (
        f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}" '
        f'class="node-shape" />'
    )


def section_spine() -> str:
    """Section 02 — Stimulus → Push → Desire → Action."""
    y0 = 540
    out = [section_title(y0, "02", "THE SPINE",
                         "Stimulus → Push → Desire → Action")]
    panel_x, panel_y = 40, y0 + 60
    panel_w, panel_h = W - 80, 200
    out.append(
        f'<rect x="{panel_x}" y="{panel_y}" width="{panel_w}" '
        f'height="{panel_h}" rx="6" class="panel" />'
    )

    nodes = [
        ("STIMULUS",  "input event",         SIGNAL_COLORS["Stimulus"]),
        ("PUSH",      "traction = gravity",  SIGNAL_COLORS["Push"]),
        ("DESIRE",    "formulated will",     SIGNAL_COLORS["Desire"]),
        ("ACTION",    "quantum of behaviour", SIGNAL_COLORS["Action"]),
    ]
    n = len(nodes)
    margin = 80
    avail = panel_w - 2 * margin
    step = avail / (n - 1)
    cy = panel_y + panel_h // 2 + 6
    box_w, box_h = 168, 56

    # AION above
    aion_x = panel_x + panel_w // 2
    aion_y = panel_y + 38
    out.append(
        f'<rect x="{aion_x - 110}" y="{aion_y - 18}" width="220" height="36" '
        f'rx="6" fill="{ROLE_COLORS["core"]}" class="node-shape" />'
    )
    out.append(
        f'<text x="{aion_x}" y="{aion_y + 6}" text-anchor="middle" '
        f'class="label-core">AION / IMPULSE</text>'
    )
    out.append(
        f'<text x="{aion_x}" y="{aion_y + 38}" text-anchor="middle" '
        f'class="muted">heartbeat · emits Push every period · '
        f"absence → Stimulus 'I exist!'</text>"
    )

    # Chain boxes
    box_xs = []
    for i, (name, sub, col) in enumerate(nodes):
        x = panel_x + margin + i * step
        box_xs.append(x)
        out.append(
            f'<rect x="{x - box_w / 2}" y="{cy - box_h / 2}" width="{box_w}" '
            f'height="{box_h}" rx="6" fill="{col}" class="node-shape" />'
        )
        out.append(
            f'<text x="{x}" y="{cy - 4}" text-anchor="middle" '
            f'class="label-core">{name}</text>'
        )
        out.append(
            f'<text x="{x}" y="{cy + 14}" text-anchor="middle" '
            f'class="label" fill="{BG}" font-size="9">{sub}</text>'
        )

    # Arrows between boxes
    for i in range(n - 1):
        x1 = box_xs[i] + box_w / 2 + 6
        x2 = box_xs[i + 1] - box_w / 2 - 6
        out.append(
            f'<line x1="{x1}" y1="{cy}" x2="{x2}" y2="{cy}" '
            f'stroke="{TXT_SECONDARY}" stroke-width="2" '
            f'marker-end="url(#arrow)" />'
        )

    # AION drive arrow down to PUSH
    push_x = box_xs[1]
    out.append(
        f'<path d="M {aion_x} {aion_y + 18} L {push_x} {cy - box_h / 2 - 4}" '
        f'stroke="{ROLE_COLORS["core"]}" stroke-width="1.5" '
        f'stroke-dasharray="4 3" fill="none" marker-end="url(#arrow-red)" '
        f'opacity="0.85" />'
    )

    # Annotations under chain
    notes_y = cy + box_h / 2 + 26
    out.append(
        f'<text x="{panel_x + 24}" y="{notes_y}" class="body">'
        f"• Will = Need: every output requires an input. "
        f"There is no real autonomous system."
        f"</text>"
    )
    out.append(
        f'<text x="{panel_x + 24}" y="{notes_y + 18}" class="body">'
        f"• Subtraction Principle: prolonged silence becomes its own Stimulus."
        f"</text>"
    )
    out.append(
        f'<text x="{panel_x + 24}" y="{notes_y + 36}" class="body">'
        f"• Every Action is also a Stimulus (re-entering the loop) "
        f"and a Reaction (to whatever pushed it)."
        f"</text>"
    )
    return "\n".join(out)


def absence_banner(y: float) -> str:
    """Banner — ABSENCE OF DATA as the main human stimulus."""
    h = 76
    out = [
        f'<rect x="40" y="{y}" width="{W - 80}" height="{h}" '
        f'rx="6" fill="#1a1410" stroke="#ffb14d" stroke-width="1.5" />',
        f'<rect x="40" y="{y}" width="6" height="{h}" fill="#ffb14d" />',
        f'<text x="64" y="{y + 24}" class="section-num" fill="#ffb14d">'
        f"MAIN STIMULUS · POST-PALEOREVOLUTION"
        f"</text>",
        f'<text x="64" y="{y + 46}" class="h2" fill="{TXT_PRIMARY}">'
        f"ABSENCE OF DATA → SEARCHES AND RESOLUTIONS"
        f"</text>",
        f'<text x="64" y="{y + 66}" class="body">'
        f"For animals, absence does not transfer to need. For the human-like Conscience, "
        f"AION emits a Stimulus from the absence itself: ‘I exist!’ — the seed of every search."
        f"</text>",
    ]
    return "\n".join(out)


def section_architecture() -> str:
    """Section 03 — the modular network, anchored on the Core."""
    y0 = 800
    out = [section_title(y0, "03", "THE MODULAR NETWORK",
                         "anchored on the Core · driven by the heartbeat")]
    # Section background
    out.append(
        f'<rect x="0" y="{y0 + 46}" width="{W}" height="920" fill="{BG}" />'
    )

    # ABSENCE banner sits at the top of the architecture section.
    out.append(absence_banner(y0 + 60))

    mods = {m["id"]: m for m in MODULES}
    aion_x, aion_y = SCHEMATIC_POSITIONS["aion_impulse"]

    # 1) AION halo — concentric faint rings around the heartbeat.
    for r, op in [(115, 0.22), (160, 0.13), (215, 0.07)]:
        out.append(
            f'<circle cx="{aion_x}" cy="{aion_y}" r="{r}" fill="none" '
            f'stroke="#ff6b6b" stroke-width="1" opacity="{op}" '
            f'stroke-dasharray="2 5" />'
        )

    # 2) Drive rays from AION to every other module — very faint, dotted.
    #    Visual statement: 'everything moves because the heartbeat beats.'
    for m in MODULES:
        if m["id"] == "aion_impulse":
            continue
        mx, my = SCHEMATIC_POSITIONS[m["id"]]
        out.append(
            f'<line x1="{aion_x}" y1="{aion_y}" x2="{mx}" y2="{my}" '
            f'stroke="#ff6b6b" stroke-width="0.7" opacity="0.11" '
            f'stroke-dasharray="1 5" />'
        )

    # 3) Background mesh — every topology edge at very low opacity,
    #    skipping pairs we'll re-draw as highlighted flows.
    for e in EDGES:
        if (e["from"], e["to"]) in HIGHLIGHTED_PAIRS:
            continue
        a = mods.get(e["from"])
        b = mods.get(e["to"])
        if not a or not b:
            continue
        x1, y1 = SCHEMATIC_POSITIONS[a["id"]]
        x2, y2 = SCHEMATIC_POSITIONS[b["id"]]
        col = SIGNAL_COLORS.get(e["via"], "#444")
        d = edge_path(x1, y1, x2, y2)
        out.append(f'<path d="{d}" stroke="{col}" class="edge-faint" />')

    # 4) Highlighted flows — the narrative arrows, with labels.
    for from_id, to_id, col, label, dashed in HIGHLIGHTED_FLOWS:
        x1, y1 = SCHEMATIC_POSITIONS[from_id]
        x2, y2 = SCHEMATIC_POSITIONS[to_id]
        d = edge_path(x1, y1, x2, y2, bend=10)
        dash = ' stroke-dasharray="6 4"' if dashed else ""
        marker_id = f'arrow-{col.lstrip("#")}'
        out.append(
            f'<path d="{d}" fill="none" stroke="{col}" '
            f'stroke-width="3" opacity="0.95"{dash} '
            f'marker-end="url(#{marker_id})" />'
        )
        # Label at midpoint, perpendicular-offset from the line,
        # with a halo so the text reads cleanly over the mesh.
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        dx, dy = x2 - x1, y2 - y1
        length = math.hypot(dx, dy) or 1
        ox = -(dy / length) * 14
        oy =  (dx / length) * 14
        out.append(
            f'<text x="{mx + ox}" y="{my + oy}" text-anchor="middle" '
            f'class="flow-label" fill="{col}">{label}</text>'
        )

    # 5) Nodes (drawn on top of all edges).
    for m in MODULES:
        x, y = SCHEMATIC_POSITIONS[m["id"]]
        fill = ROLE_COLORS.get(m["role"], "#888")
        out.append(node_shape(m["role"], x, y, fill, mod_id=m["id"]))
        out.append(render_label(m["role"], m["label"], x, y))
        desc = MODULE_DESC.get(m["id"], "")
        if desc:
            dy = SCHEMATIC_DESC_OFFSET.get(m["role"], 50)
            if m["id"] == "memory_senses":
                dy = 60
            out.append(
                f'<text x="{x}" y="{y + dy}" text-anchor="middle" '
                f'class="desc">{desc}</text>'
            )

    # 6) Caption: explain the two layers of edges.
    legend_y = y0 + 900
    out.append(
        f'<rect x="40" y="{legend_y}" width="{W - 80}" height="48" '
        f'rx="4" class="panel-strong" />'
    )
    out.append(
        f'<text x="60" y="{legend_y + 18}" class="muted">'
        f"Bold coloured arrows are the narrative flows. Thin lines underneath are the underlying "
        f"bus topology, colour-coded by signal type."
        f"</text>"
    )
    out.append(
        f'<text x="60" y="{legend_y + 36}" class="muted">'
        f"Faint red rays radiating from AION show that every module is moved by the heartbeat — "
        f"‘everything is driven by the Core’."
        f"</text>"
    )
    return "\n".join(out)


def section_signals() -> str:
    """Section 04 — Signal vocabulary."""
    y0 = 1790
    out = [section_title(y0, "04", "SIGNAL VOCABULARY",
                         "the eight typed messages on the bus")]
    panel_y = y0 + 60
    panel_h = 180
    out.append(
        f'<rect x="40" y="{panel_y}" width="{W - 80}" height="{panel_h}" '
        f'rx="6" class="panel" />'
    )

    signals = [
        ("Stimulus",     "input event · modality / payload / intensity"),
        ("Push",         "traction = gravity · continuity or reactive"),
        ("Desire",       "formulated intention · motivation + confidence"),
        ("Action",       "quantum of behaviour · also stimulus + reaction"),
        ("Reaction",     "measured consequence · valence in [-1, +1]"),
        ("MeaningEvent", "stimulus mapped to meaning · novelty score"),
        ("MapUpdate",    "change to Inner MAP · fact or boundary"),
        ("LogosTension", "dia / sun balance · fracture forces motion"),
    ]

    cols = 4
    rows = 2
    cell_w = (W - 80 - 32) / cols
    cell_h = (panel_h - 32) / rows
    pad = 16

    for i, (name, sub) in enumerate(signals):
        col = i % cols
        row = i // cols
        x = 40 + 16 + col * cell_w
        y = panel_y + 16 + row * cell_h
        cy = y + cell_h / 2
        # Coloured swatch
        out.append(
            f'<rect x="{x + 8}" y="{cy - 14}" width="20" height="28" '
            f'rx="3" fill="{SIGNAL_COLORS[name]}" />'
        )
        out.append(
            f'<text x="{x + 38}" y="{cy - 2}" class="h3">{name}</text>'
        )
        out.append(
            f'<text x="{x + 38}" y="{cy + 16}" class="muted">{sub}</text>'
        )

    return "\n".join(out)


def section_logos_concepts() -> str:
    """Section 05 — Logos opposition + key concepts."""
    y0 = 2030
    out = [section_title(y0, "05", "LOGOS AND FOUNDATIONAL CONCEPTS",
                         "the philosophy behind the wiring")]
    body_y = y0 + 60
    body_h = 380

    # Left: Logos diagram
    left_x, left_w = 40, 580
    out.append(
        f'<rect x="{left_x}" y="{body_y}" width="{left_w}" height="{body_h}" '
        f'rx="6" class="panel" />'
    )
    out.append(
        f'<text x="{left_x + 20}" y="{body_y + 26}" class="h3">'
        f"LOGOS = calculus = ratio</text>"
    )
    out.append(
        f'<text x="{left_x + 20}" y="{body_y + 44}" class="body">'
        f"a constant tension between two pulls; the fracture between them forces motion."
        f"</text>"
    )

    # Two scales
    scale_top    = body_y + 90
    scale_bottom = body_y + body_h - 64
    bar_left     = left_x + 70
    bar_right    = left_x + left_w - 70
    pivot_x      = (bar_left + bar_right) // 2
    pivot_y      = (scale_top + scale_bottom) // 2

    # dia-ballein column (left)
    out.append(
        f'<rect x="{bar_left - 60}" y="{scale_top}" width="120" height="60" '
        f'rx="6" fill="{ROLE_COLORS["decision"]}" class="node-shape" />'
    )
    out.append(
        f'<text x="{bar_left}" y="{scale_top + 26}" text-anchor="middle" '
        f'class="label-core" fill="{BG}">DIA-BALLEIN</text>'
    )
    out.append(
        f'<text x="{bar_left}" y="{scale_top + 46}" text-anchor="middle" '
        f'class="label" fill="{BG}" font-size="10">rational · presence</text>'
    )

    out.append(
        f'<text x="{bar_left}" y="{scale_top + 90}" text-anchor="middle" '
        f'class="muted">division · data · reasons</text>'
    )

    # sun-ballein column (right)
    out.append(
        f'<rect x="{bar_right - 60}" y="{scale_top}" width="120" height="60" '
        f'rx="6" fill="{ROLE_COLORS["adapt"]}" class="node-shape" />'
    )
    out.append(
        f'<text x="{bar_right}" y="{scale_top + 26}" text-anchor="middle" '
        f'class="label-core" fill="{BG}">SUN-BALLEIN</text>'
    )
    out.append(
        f'<text x="{bar_right}" y="{scale_top + 46}" text-anchor="middle" '
        f'class="label" fill="{BG}" font-size="10">irrational · absence</text>'
    )
    out.append(
        f'<text x="{bar_right}" y="{scale_top + 90}" text-anchor="middle" '
        f'class="muted">union · mystery · absence of data</text>'
    )

    # Pivot
    out.append(
        f'<line x1="{bar_left + 60}" y1="{pivot_y}" x2="{bar_right - 60}" y2="{pivot_y}" '
        f'stroke="{TXT_SECONDARY}" stroke-width="2" />'
    )
    out.append(
        f'<polygon points="{pivot_x - 10},{pivot_y + 16} {pivot_x + 10},{pivot_y + 16} '
        f'{pivot_x},{pivot_y}" fill="{TXT_SECONDARY}" />'
    )
    out.append(
        f'<text x="{pivot_x}" y="{pivot_y + 42}" text-anchor="middle" class="h3">LOGOS</text>'
    )

    # Result row
    out.append(
        f'<text x="{left_x + left_w / 2}" y="{scale_bottom + 16}" '
        f'text-anchor="middle" class="body-light">'
        f"FRACTURE → MOTION (Action)"
        f"</text>"
    )
    out.append(
        f'<text x="{left_x + left_w / 2}" y="{scale_bottom + 36}" '
        f'text-anchor="middle" class="muted">'
        f"a balanced system is a dead system; opposition keeps it moving"
        f"</text>"
    )

    # Right: concepts
    right_x = left_x + left_w + 16
    right_w = W - right_x - 40
    concepts = [
        ("ABSENCE → SEARCH  (main stimulus)",
         "Post-paleorevolution distinction: for animals, absence does not "
         "transfer to need. For the human-like Conscience it does — AION "
         "emits a Stimulus from silence itself, and the system searches."),
        ("WILL = NEED",
         "Output is input-dependent. There is no real free will: Desires arise "
         "from a complexity of stimuli, but moreover from absence."),
        ("MYSTERIUM",
         "The unknown that generates the irrational. Rises with novelty; drives "
         "Synthesis and Anticipation. Pushes Logos toward 'union'."),
        ("MEMORY IN-BETWEEN",
         "Memory does not live in brain or senses but in their relation. The "
         "Memory/Senses module records both Stimulus and Action."),
    ]
    card_h    = 84
    card_gap  = 8
    for i, (title, body) in enumerate(concepts):
        cy = body_y + 6 + i * (card_h + card_gap)
        out.append(
            f'<rect x="{right_x}" y="{cy}" width="{right_w}" height="{card_h}" '
            f'rx="6" class="panel-strong" />'
        )
        out.append(
            f'<text x="{right_x + 16}" y="{cy + 22}" class="h3">{title}</text>'
        )
        # naive wrap; allow up to 3 lines.
        words = body.split()
        line, lines = "", []
        for w in words:
            test = (line + " " + w).strip()
            if len(test) > 70:
                lines.append(line)
                line = w
            else:
                line = test
        if line:
            lines.append(line)
        for li, ln in enumerate(lines[:3]):
            out.append(
                f'<text x="{right_x + 16}" y="{cy + 42 + li * 14}" class="body">'
                f"{ln}</text>"
            )
    return "\n".join(out)


def section_lifecycle() -> str:
    y0 = 2530
    out = [section_title(y0, "06", "LIFECYCLE",
                         "‘must be able to die’ · CONCEPTS.md")]
    panel_y = y0 + 60
    panel_h = 110
    out.append(
        f'<rect x="40" y="{panel_y}" width="{W - 80}" height="{panel_h}" '
        f'rx="6" class="panel" />'
    )
    cy = panel_y + panel_h // 2
    stages = [
        ("birth()",      "alive = True · modules.start()",  "#7cf088"),
        ("CONTINUOUS",   "AION beats · bus broadcasts · modules adapt",  "#62b6ff"),
        ("die(cause)",   "alive = False · modules.stop()", "#ff6b6b"),
    ]
    margin = 80
    avail = (W - 80) - 2 * margin
    step = avail / (len(stages) - 1)
    box_w, box_h = 220, 50
    xs = []
    for i, (label, sub, col) in enumerate(stages):
        x = 40 + margin + i * step
        xs.append(x)
        out.append(
            f'<rect x="{x - box_w / 2}" y="{cy - box_h / 2}" width="{box_w}" '
            f'height="{box_h}" rx="6" fill="{col}" class="node-shape" />'
        )
        out.append(
            f'<text x="{x}" y="{cy - 6}" text-anchor="middle" '
            f'class="label-core" fill="{BG}">{label}</text>'
        )
        out.append(
            f'<text x="{x}" y="{cy + 12}" text-anchor="middle" '
            f'class="label" fill="{BG}" font-size="9">{sub}</text>'
        )
    for i in range(len(stages) - 1):
        x1 = xs[i] + box_w / 2 + 8
        x2 = xs[i + 1] - box_w / 2 - 8
        out.append(
            f'<line x1="{x1}" y1="{cy}" x2="{x2}" y2="{cy}" '
            f'stroke="{TXT_SECONDARY}" stroke-width="2" '
            f'marker-end="url(#arrow)" />'
        )
    return "\n".join(out)


def section_footer() -> str:
    y0 = 2710
    out = []
    out.append(
        f'<rect x="0" y="{y0}" width="{W}" height="{H - y0}" fill="{BG}" />'
    )
    out.append(f'<line x1="0" y1="{y0}" x2="{W}" y2="{y0}" class="divider" />')
    out.append(
        f'<text x="60" y="{y0 + 36}" class="muted">'
        f"Solaris_Ai · conceptual implementation in Python (stdlib only)"
        f"</text>"
    )
    out.append(
        f'<text x="60" y="{y0 + 56}" class="muted">'
        f"run the CLI demo: solaris · "
        f"interactive web UI: solaris-web → http://127.0.0.1:8765/"
        f"</text>"
    )
    out.append(
        f'<text x="{W - 60}" y="{y0 + 56}" text-anchor="end" class="muted">'
        f"diagram generated from src/solaris/web/topology.py"
        f"</text>"
    )
    return "\n".join(out)


# ---------------------------------------------------------------------- main


def generate() -> str:
    out = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
        f'preserveAspectRatio="xMidYMid meet" '
        f'font-family="ui-monospace, JetBrains Mono, Menlo, Consolas, monospace">',
        "<defs>",
        "<style><![CDATA[",
        f"  .h1 {{ font-size: 56px; font-weight: 700; fill: {TXT_PRIMARY}; letter-spacing: 0.04em; }}",
        f"  .h2 {{ font-size: 14px; font-weight: 600; fill: {TXT_PRIMARY}; }}",
        f"  .h3 {{ font-size: 13px; font-weight: 600; fill: {TXT_PRIMARY}; }}",
        f"  .section-num {{ font-size: 11px; font-weight: 600; fill: {TXT_MUTED}; letter-spacing: 0.18em; }}",
        f"  .section-title {{ font-size: 14px; font-weight: 700; fill: {TXT_PRIMARY}; letter-spacing: 0.18em; }}",
        f"  .tagline {{ font-size: 18px; fill: {TXT_SECONDARY}; font-style: italic; }}",
        f"  .body {{ font-size: 12px; fill: {TXT_SECONDARY}; }}",
        f"  .body-light {{ font-size: 13px; fill: {TXT_LIGHT}; }}",
        f"  .muted {{ font-size: 11px; fill: {TXT_MUTED}; }}",
        f"  .label {{ font-size: 11px; font-weight: 700; fill: #0a0d12; }}",
        f"  .label-core {{ font-size: 13px; font-weight: 700; fill: #0a0d12; }}",
        f"  .label-env {{ font-size: 12px; font-weight: 700; fill: #0a0d12; }}",
        f"  .desc {{ font-size: 10px; fill: {TXT_MUTED}; }}",
        f"  .node-shape {{ stroke: #0a0d12; stroke-width: 1.5; }}",
        f"  .node-core {{ stroke-width: 2.5; }}",
        f"  .env-shape {{ stroke-dasharray: 4 3; opacity: 0.95; }}",
        f"  .edge {{ fill: none; stroke-width: 1; opacity: 0.28; }}",
        f"  .edge-faint {{ fill: none; stroke-width: 1; opacity: 0.14; }}",
        f"  .edge-amber {{ fill: none; stroke: #ffb14d; stroke-width: 3; opacity: 0.95; stroke-dasharray: 7 4; }}",
        f"  .flow-label {{ font-size: 11px; font-weight: 700; "
        f"paint-order: stroke; stroke: {BG}; stroke-width: 4; stroke-linejoin: round; }}",
        f"  .panel {{ fill: {SECTION_BG}; stroke: {BORDER}; stroke-width: 1; }}",
        f"  .panel-strong {{ fill: {BAND_BG}; stroke: {BORDER}; stroke-width: 1; }}",
        f"  .divider {{ stroke: {BORDER}; stroke-width: 1; }}",
        "]]></style>",
        '<marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" '
        'markerWidth="6" markerHeight="6" orient="auto-start-reverse">'
        f'<path d="M 0 0 L 10 5 L 0 10 z" fill="{TXT_SECONDARY}" /></marker>',
        '<marker id="arrow-red" viewBox="0 0 10 10" refX="9" refY="5" '
        'markerWidth="6" markerHeight="6" orient="auto-start-reverse">'
        f'<path d="M 0 0 L 10 5 L 0 10 z" fill="{ROLE_COLORS["core"]}" /></marker>',
        # One arrow-head marker per highlighted-flow colour.
        *[
            f'<marker id="arrow-{c.lstrip("#")}" viewBox="0 0 10 10" '
            f'refX="9" refY="5" markerWidth="7" markerHeight="7" '
            f'orient="auto-start-reverse">'
            f'<path d="M 0 0 L 10 5 L 0 10 z" fill="{c}" /></marker>'
            for c in {col for _, _, col, _, _ in HIGHLIGHTED_FLOWS}
        ],
        "</defs>",
        f'<rect width="{W}" height="{H}" fill="{BG}" />',
        section_header(),
        section_principles(),
        section_spine(),
        section_architecture(),
        section_signals(),
        section_logos_concepts(),
        section_lifecycle(),
        section_footer(),
        "</svg>",
    ]
    return "\n".join(out)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "-o", "--output",
        default=None,
        help="Output file path; if omitted, writes to stdout.",
    )
    args = parser.parse_args()
    svg = generate()
    if args.output:
        Path(args.output).write_text(svg)
        print(f"wrote {args.output} ({len(svg)} bytes, "
              f"{svg.count(chr(10)) + 1} lines)")
    else:
        sys.stdout.write(svg)


if __name__ == "__main__":
    main()
