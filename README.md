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

A working list, drawn from [`Solaris_Ai_MODULES.md`](./Solaris_Ai_MODULES.md)
and the whitepaper. Each will eventually correspond to a Python package.

**Core / drive**
- `aion_impulse/` — continuous loop, stimulus → push → desire → action quantum
- `core_scheduler/` — foreground / background / latent task arbitration
- `energy_management/` — resource and "wakefulness" monitoring

**Sensory / embodiment**
- `sensory_input/` — modality plugins (vision, audio, tactile, text, …)
- `embodiment/` — body interface (simulated or hardware)
- `feedback/` — sensory-to-actionable conversion

**Reactivity / cognition**
- `reactivity_engine/` — stimulus → response with context
- `emotional_layer/` — modulation by mood / history
- `context_awareness/` — situational framing

**Awareness / meaning**
- `cognition_core/` — meaning assignment, knowledge linking
- `inner_map/` — self-representation and boundaries
- `knowledge_embedding/` — integration into existing structure

**Plasticity / adaptation**
- `plasticity_engine/` — architectural rewrite primitives
- `reinforcement/` — habit formation
- `synthesis/` — subtractive optimisation (the `--` operator)

**Cross-cutting**
- `language/` — inter-module + external communication
- `memory/` — "in-between" state linking brain-like compute to senses
- `auto_determination/` — being / not-being opposition driver
- `auto_regeneration/` — self-rewriting code paths
- `complexity/` — instability + escape sub-process
- `dimensional_comparison/` — limits & boundary perception
- `uncertainty/` — choice under unknown distributions

---

## Suggested project layout (Python)

```
solaris-ai/
├── README.md
├── ROADMAP.md
├── Solaris_Ai_whitepaper.md
├── Solaris_Ai_CONCEPTS.md
├── Solaris_Ai_MODULES.md
├── pyproject.toml
├── src/
│   └── solaris/
│       ├── __init__.py
│       ├── aion_impulse/
│       ├── core_scheduler/
│       ├── sensory_input/
│       ├── embodiment/
│       ├── reactivity_engine/
│       ├── emotional_layer/
│       ├── cognition_core/
│       ├── inner_map/
│       ├── plasticity_engine/
│       ├── synthesis/
│       ├── memory/
│       ├── language/
│       └── ...
└── tests/
```

Nothing under `src/` exists yet — building it out is exactly what the
[ROADMAP](./ROADMAP.md) is for.

---

## Getting started

Solaris_Ai is, at this stage, a **conceptual repository**. There is no
runnable code in the tree. Contributors and readers are expected to:

1. Read [`Solaris_Ai_whitepaper.md`](./Solaris_Ai_whitepaper.md) for the
   architecture and the 2-year vision.
2. Read [`Solaris_Ai_CONCEPTS.md`](./Solaris_Ai_CONCEPTS.md) for the
   philosophical axioms the architecture is meant to encode.
3. Read [`Solaris_Ai_MODULES.md`](./Solaris_Ai_MODULES.md) for the working
   list of modules.
4. Consult [`ROADMAP.md`](./ROADMAP.md) for the phased Python implementation
   plan and pick a module / phase to prototype.

When the first prototypes land, this section will be replaced with real
install / run instructions.

---

## Status

- [x] Whitepaper
- [x] Concepts notes
- [x] Module index
- [x] README and roadmap
- [ ] Repository scaffolding (`pyproject.toml`, `src/solaris/`)
- [ ] AION/IMPULSE prototype
- [ ] First end-to-end stimulus → reaction demo
- [ ] Inner MAP prototype
- [ ] Plasticity engine prototype

See [ROADMAP.md](./ROADMAP.md) for what each of those means in detail.

---

## A note on scope

Solaris_Ai deliberately takes positions that are unfashionable in current
AI practice: that consciousness is reactive rather than representational,
that a system must be *able to die* to be alive, that free will is at best a
useful illusion driven by need. Treat the codebase, when it exists, as a
research instrument for testing those positions — not as a product roadmap
in the commercial sense.
