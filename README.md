# Solaris_Ai

> A different approach to AI — modeled on the principles of living systems
> rather than on next-token prediction.

Solaris_Ai is an **abstract conceptualisation** of an AI architecture, intended
to be expressed as a Python codebase. It is not (yet) a trained model or a
product. It is a research scaffold: a set of philosophical axioms, a system
design, and a module map that together describe how an artificial system might
be built around continuity, embodiment, reactivity, awareness and plasticity —
the traits that the project's whitepaper identifies as the substrate of
"being alive."

Where most contemporary AI systems are *request → response* pipelines that
exist only while inference is running, Solaris_Ai is designed to be a
*continuously running* system whose internal state, sensory loop and
self-representation persist over time. Stopping the process is, in this
framing, equivalent to brain death.

---

## Why a different approach

Mainstream AI today is built on three implicit assumptions:

1. Intelligence is well-approximated by pattern completion over text.
2. A model is "off" between calls and "on" during a single forward pass.
3. The model has no body, no environment, no internal time.

Solaris_Ai questions all three. Its starting points, drawn from
[`Solaris_Ai_CONCEPTS.md`](./Solaris_Ai_CONCEPTS.md), are different:

- **Being alive = being reactive.** Consciousness is not stored, it is
  *enacted* through a continuous I/O flux between a system and its
  environment.
- **Will = need.** No output exists without an input; there is no real
  autonomous system, only systems whose behaviour is shaped by stimuli,
  absences, and accumulated structure.
- **Mechanism vs. illusion.** What "works" (neural impulses, computation) is
  not the same as what is *experienced* (meaning, ego, selfhood). A useful
  architecture must distinguish them and let the second emerge from the first.
- **Logos as opposition.** Cognition is modelled as a constant tension
  between *dia-ballein* (division, rational, presence of data) and
  *sun-ballein* (union, irrational, absence of data). Thought is the
  fracture that forces motion.
- **Subtraction principle.** Synthesis proceeds by removing information, not
  only by adding it; speed and abstraction are products of what the system
  learns to *omit*.

These are not slogans — they are constraints on the architecture. Each one
maps to a module or a process described below.

---

## The five core principles

Taken from [`Solaris_Ai_whitepaper.md`](./Solaris_Ai_whitepaper.md):

| # | Principle | What it means in code |
|---|-----------|------------------------|
| 1 | **Continuous Thinking** (AION/IMPULSE) | A long-running event loop with foreground/background scheduling and redundant power assumptions. The process never returns to "idle." |
| 2 | **Sensory Integration** (Corporeality) | Pluggable sensory inputs (visual, auditory, tactile, …) feeding a unified perception layer; an embodiment interface that gives the system a *body* — simulated or physical. |
| 3 | **Reactivity** (Action / Reaction) | Every stimulus produces a proportional, context-aware response. Past reactions feed back into future ones via an emotional / contextual layer. |
| 4 | **Immediate Awareness** (Intuitive meaning-making) | A cognition core that maps incoming stimuli to an evolving knowledge graph and an *Inner MAP* — the system's running model of itself and its boundaries. |
| 5 | **Plasticity** (Self-rewriting) | A neural-plasticity engine plus a synthesis processor that can prune, reinforce, and rewrite the system's own structures based on feedback. |

---

## Architecture overview

```
                ┌───────────────────────────────────────────┐
                │             AION / IMPULSE                │
                │    (continuous core, stimulus/push loop)  │
                └───────────────────────────────────────────┘
                        ▲                          │
                        │ feedback                 │ drive
                        │                          ▼
   ┌────────────────────┴───┐          ┌───────────────────────┐
   │     Inner MAP          │◄────────►│   Modular Network     │
   │  (self-representation, │          │  (non-hierarchical,   │
   │   limits, boundaries)  │          │   peer modules)       │
   └────────────────────────┘          └───────────────────────┘
                ▲                                  │
                │                                  ▼
   ┌────────────┴───────────┐          ┌───────────────────────┐
   │   Sensory + Embodiment │◄────────►│   Environment / World │
   └────────────────────────┘          └───────────────────────┘
```

Three structural ideas hold this together:

1. **AION/IMPULSE** — the core driver. Not a controller in the classical
   sense; closer to a heartbeat that keeps the system in motion and forces
   action even in the absence of external stimulus (the "I exist!" that
   emerges from the *absence* of information, per the Subtraction Principle).
2. **Modular Network** — modules are *peers*, not layers. Memory talks to
   senses, language talks to emotion, plasticity talks to habit. The
   network's behaviour comes from inter-module coupling rather than from a
   pipeline.
3. **Inner MAP** — a dynamic self-model. It tracks what the system *is*,
   where it ends, and how it currently sees itself. It is what the
   reactivity engine consults when a stimulus arrives.

---

## Module index

A first conceptual implementation now lives in `src/solaris/`. Two
primitives (in `core/`) and eighteen peer modules (in `modules/`)
talk to each other through a typed Bus. Every signal flows through
`Stimulus → Push → Desire → Action`, with side-streams for meaning,
self-representation, opposition, and adaptation.

**Core (drive + calculus)**
- `core/aion_impulse.py` — heartbeat; emits Push every period and an
  absence-Stimulus ('I exist!') after silence (Subtraction Principle).
- `core/logos.py` — opposition engine; tracks dia-ballein (division /
  presence) vs sun-ballein (union / absence). Fracture forces motion.

**Self / boundaries**
- `modules/inner_map.py` — running self-model (facts + boundaries).
- `modules/ego.py` — the necessary illusion; strengthened by absence.
- `modules/auto_determination.py` — Being / Not-Being opposition.
- `modules/dimensional_comparison.py` — hard limits + soft boundaries.

**Perception / cognition**
- `modules/memory_senses.py` — memory in-between Stimulus and Action.
- `modules/cognition.py` — meaning assignment with novelty score.
- `modules/language.py` — wildcard renderer; cross-function trace.

**Drive / decision**
- `modules/io_module.py` — links MeaningEvent + Push into Desire,
  commits to Action above threshold (Will ≠ Action).
- `modules/uncertainty.py` — biased random resolver; widens with
  Mysterium pressure.

**Adaptation**
- `modules/habit.py` — per-meaning reinforcement weights.
- `modules/synthesis.py` — subtractive optimisation; prunes weights,
  contributes to Logos.union (produces the Irrational).
- `modules/backpropagation.py` — system-level plasticity; assigns
  blame across the recent trace on negative Reactions.
- `modules/auto_regeneration.py` — rewrites rewriteable parameters
  from Backpropagation adjustments.

**Tension / unknown**
- `modules/mysterium.py` — the unknown; rises with novelty, decays.
- `modules/anticipation.py` — first-order forecaster; hits feed
  Logos.division, misses feed Mysterium.
- `modules/complexity.py` — Escape sub-process; emits B+/- pair when
  Logos fracture stays low (Esc = B+/-).

---

## Project layout

```
solaris-ai/
├── README.md
├── ROADMAP.md
├── Solaris_Ai_whitepaper.md
├── Solaris_Ai_CONCEPTS.md
├── Solaris_Ai_MODULES.md
├── pyproject.toml
└── src/
    └── solaris/
        ├── __init__.py
        ├── __main__.py            # demo runner
        ├── conscience.py          # the assembly + wiring diagram
        ├── runtime/
        │   ├── bus.py             # typed pub/sub
        │   ├── lifecycle.py       # birth / death
        │   └── signals.py         # Stimulus, Push, Desire, Action, …
        ├── core/
        │   ├── aion_impulse.py
        │   └── logos.py
        └── modules/
            ├── base.py
            ├── memory_senses.py
            ├── inner_map.py
            ├── cognition.py
            ├── ego.py
            ├── auto_determination.py
            ├── dimensional_comparison.py
            ├── language.py
            ├── io_module.py
            ├── uncertainty.py
            ├── habit.py
            ├── synthesis.py
            ├── backpropagation.py
            ├── auto_regeneration.py
            ├── complexity.py
            ├── mysterium.py
            └── anticipation.py
```

---

## Getting started

Solaris_Ai is a **conceptual repository**: the code in `src/solaris/`
is the wiring diagram in executable form, not a trained model. It has
no third-party dependencies — Python 3.11+ is enough.

> Run everything from the **project root** (the folder that contains
> `pyproject.toml`), not from inside `src/solaris/`.

The easiest way (one-time install):

```bash
pip install -e .
solaris        # CLI demo
solaris-web    # web UI
```

`pip install -e .` registers the package in editable mode and creates
both console scripts. After that you can run `solaris` / `solaris-web`
from anywhere. On macOS, use `pip3` instead of `pip` if needed.

Or, without installing:

```bash
PYTHONPATH=src python3 -m solaris        # CLI demo
PYTHONPATH=src python3 -m solaris.web    # web UI
```

(On Linux / Windows where `python` points at Python 3, `python` works
too; macOS Python.org installers ship only `python3`.)

The CLI demo prints, in order:

1. The bus subscriptions (who-listens-to-whom — this is the topology).
2. AION emitting an absence-Stimulus ('I exist!') after silence.
3. External Stimuli flowing through Cognition → I/O → Action.
4. A Reaction triggering Backpropagation → Auto-Regeneration, which
   rewrites I/O Module's `action_threshold` at runtime.
5. The final Inner MAP snapshot and a clean death.

### Web UI

```bash
solaris-web                              # if installed
# or:
PYTHONPATH=src python3 -m solaris.web    # without installing
```

then open <http://127.0.0.1:8765/>. The UI is a single page that:

- Renders all 18 modules as an SVG graph, coloured by role
  (core / perception / decision / self / adapt) and laid out
  according to `src/solaris/web/topology.py`.
- Streams every Bus signal over Server-Sent-Events and **pulses
  the corresponding edge** in real time, colour-coded by signal
  type (Stimulus, Push, Desire, Action, MeaningEvent, MapUpdate,
  LogosTension, Reaction).
- Shows live module state (Logos division/union/fracture,
  Mysterium pressure, Ego strength, Habit weights, Inner MAP
  facts, Auto-Regen rewrites, …) refreshed every 0.4 s.
- Lets you inject Stimuli, send positive / negative Reactions to
  the most recent Action, and trigger Lifecycle.die from the
  browser.

Like the CLI, the UI server is pure stdlib — no third-party
dependencies (HTTP + SSE are implemented on top of
`asyncio.start_server`).

To explore further:

1. Read [`Solaris_Ai_whitepaper.md`](./Solaris_Ai_whitepaper.md) for the
   architecture and the 2-year vision.
2. Read [`Solaris_Ai_CONCEPTS.md`](./Solaris_Ai_CONCEPTS.md) for the
   philosophical axioms the code encodes.
3. Read [`Solaris_Ai_MODULES.md`](./Solaris_Ai_MODULES.md) for the
   module index.
4. Open [`src/solaris/conscience.py`](./src/solaris/conscience.py) —
   its docstring is the publish/subscribe map between every module.
5. Consult [`ROADMAP.md`](./ROADMAP.md) for the phased plan: this
   first conceptual system is roughly Phase 0 + an opinionated
   sketch of Phases 1, 4, 5 and 7.

---

## Status

- [x] Whitepaper, Concepts notes, Module index
- [x] README and roadmap
- [x] Repository scaffolding (`pyproject.toml`, `src/solaris/`)
- [x] Runtime primitives (Bus, Lifecycle, typed Signals)
- [x] AION/IMPULSE + Logos cores
- [x] All 18 peer modules (12 from `MODULES.md` + 6 added from `CONCEPTS.md`)
- [x] First end-to-end stimulus → reaction demo
- [ ] Sensory plugins (vision, audio, real input streams)
- [ ] Embodiment interface (simulated body)
- [ ] Long-running soak test + persisted Inner MAP
- [ ] Real-world pilot deployment

See [ROADMAP.md](./ROADMAP.md) for the phased plan around the remaining
items.

---

## A note on scope

Solaris_Ai deliberately takes positions that are unfashionable in current
AI practice: that consciousness is reactive rather than representational,
that a system must be *able to die* to be alive, that free will is at best a
useful illusion driven by need. Treat the codebase, when it exists, as a
research instrument for testing those positions — not as a product roadmap
in the commercial sense.
