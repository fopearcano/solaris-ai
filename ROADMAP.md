# Solaris_Ai — Roadmap

This document turns the high-level phases described in
[`Solaris_Ai_whitepaper.md`](./Solaris_Ai_whitepaper.md) into a concrete
**Python implementation plan**. It is structured as a sequence of phases,
each with explicit deliverables, success criteria, and the modules from
[`Solaris_Ai_MODULES.md`](./Solaris_Ai_MODULES.md) that it brings online.

The roadmap is intentionally written so that each phase produces something
*runnable*, even if minimal. The goal is not to ship features but to keep
the system continuously testable as its capacity grows.

---

## Guiding principles for the implementation

1. **Continuity over throughput.** The default execution model is a
   long-running process, not a request handler. Every component must work
   inside an event loop that does not return to idle.
2. **Modules as peers.** No global controller. Modules expose typed
   message channels and subscribe to each other; the AION/IMPULSE core
   only provides drive, not orchestration.
3. **State must be observable.** Every module exposes its current state in
   a way the Inner MAP can consume. If it cannot be observed, it cannot be
   integrated into self-representation.
4. **Subtraction is a first-class operation.** The synthesis processor must
   be able to *remove* structure, not only add it. Pruning is treated as a
   primary capability, not a cleanup step.
5. **Death is permitted.** Every long-running process must support
   graceful shutdown and cold restart from persisted Inner MAP state.
   "Being able to die" is a design constraint, not an afterthought.

---

## Phase 0 — Foundations (weeks 0–4)

**Objective:** make the repository implementable.

Today the repo contains documents only. Before any module work, we need a
Python skeleton and the project conventions.

**Deliverables**

- `pyproject.toml` with Python ≥ 3.11, dependencies pinned via lockfile.
- `src/solaris/` package skeleton with empty subpackages matching the
  module index in the README.
- `tests/` with a minimal pytest setup.
- Basic CI (lint, type-check, test) on every push.
- `docs/` rendering of the whitepaper, concepts and modules notes.
- A `solaris.runtime` package containing:
  - an `EventLoop` wrapper around `asyncio` with explicit lifecycle hooks
    (start / heartbeat / shutdown);
  - a `Bus` for typed pub/sub between modules;
  - a `State` registry that modules publish observable state into.

**Exit criteria**

- `python -m solaris` starts an empty event loop, logs a heartbeat, and
  exits cleanly on SIGTERM with state persisted to disk.

---

## Phase 1 — AION / IMPULSE: continuous operation (months 1–3)

Maps to whitepaper *Phase 1 / Year 1 Q2*, principle **Continuous Thinking**.

**Objective:** stand up the heart of the system — a process that keeps
itself in motion and produces *something* even with no external input.

**Modules introduced**

- `aion_impulse/` — drive loop. Implements `Stimulus → Push → Desire →
  Action`. When external stimuli are absent, the Subtraction Principle
  generates an internal stimulus from the *absence* of data ("I exist!").
- `core_scheduler/` — three task classes: **foreground** (active
  interaction), **background** (housekeeping), **latent** (slow
  computation, dreaming). Round-robin with priority pre-emption.
- `energy_management/` — tracks per-module CPU / memory budget; exposes
  `wakefulness` as a scalar derived from resource pressure.

**Deliverables**

- `aion_impulse.Loop` class running on the `solaris.runtime` event loop.
- A reference *null sensor* and *null effector* so the loop can be tested
  end-to-end before real I/O exists.
- Trace tooling: every action quantum is recorded with its triggering
  stimulus (or its triggering absence).

**Exit criteria**

- Run for 24 h without intervention.
- Inject and remove stimuli at runtime and observe the
  foreground/background/latent split shifting accordingly.
- Kill -9 the process; on restart, continuity log shows the gap
  ("brain death") explicitly.

---

## Phase 2 — Sensory integration & embodiment (months 3–6)

Maps to whitepaper *Phase 2 / Year 1 Q3*, principle **Sensory Integration**.

**Objective:** give the system a body. Even a poor body is enough — what
matters is that perception and action are *grounded* in something outside
the AION loop.

**Modules introduced**

- `sensory_input/` — modality plugins behind a common interface
  (`SensoryStream`). First two: **text channel** (chat-like input) and
  **clock / proprioception** (the system perceives its own time and
  resource state). Vision and audio plugins follow as stretch goals.
- `embodiment/` — pluggable body backends. First backend: a simulated
  2-D environment the system can act in (move, look, touch). Second
  backend: a process-level body — files, sockets, processes — treated as
  the system's "limbs."
- `feedback/` — converts raw sensory data into actionable events on the
  bus.

**Deliverables**

- A demo where Solaris_Ai, with no language model attached, develops
  consistent reactions to a small set of stimuli in the simulated
  environment over a long run.
- Logging of perception → reaction latencies per modality.

**Exit criteria**

- Sensory streams can be added or removed at runtime without restarting
  the AION loop.
- The Inner MAP (Phase 4) will later read from the same stream interfaces
  unchanged.

---

## Phase 3 — Reactivity & emotional modulation (months 6–9)

Maps to whitepaper *Phase 3 / Year 2 Q1*, principle **Reactivity**.

**Objective:** make reactions *contextual*. The same stimulus should
produce different actions based on history, mood, and current state.

**Modules introduced**

- `reactivity_engine/` — stimulus matching → action selection, with
  pluggable policies (rule-based, learned, hybrid).
- `emotional_layer/` — slow-moving scalar fields (valence, arousal,
  fatigue) that bias action selection without overriding it.
- `context_awareness/` — short-horizon memory of recent stimuli and
  actions, exposed to the reactivity engine as features.

**Deliverables**

- Same stimulus, repeated under different `emotional_layer` states,
  produces visibly different actions in the simulated environment.
- Reactivity policies can be swapped at runtime via the bus.

**Exit criteria**

- A reproducible test where the system "tires" of a repeated stimulus
  (habituation) and recovers after a rest period.

---

## Phase 4 — Immediate awareness & Inner MAP (months 9–12)

Maps to whitepaper *Phase 3 / Year 2 Q2*, principle **Immediate Awareness**.

**Objective:** give the system a model of itself. Without it, none of the
later plasticity work has anything to operate on.

**Modules introduced**

- `cognition_core/` — meaning assignment: maps stimuli to nodes in a
  knowledge graph and emits *meaning events* on the bus.
- `knowledge_embedding/` — integrates new stimuli into the existing
  graph; uses both addition and the Subtraction Principle.
- `inner_map/` — the running self-model. Tracks: which modules exist,
  what they currently do, the system's perceived boundaries (limits in
  the sense of `MODULES.md` § Dimensional Comparison), and the
  active emotional state. Persisted across restarts.

**Deliverables**

- A read-only `solaris.inner_map` API that any module can query.
- A visualisation of the Inner MAP as a graph, updated live.

**Exit criteria**

- After a restart, the Inner MAP is restored and the AION loop resumes
  without re-deriving its self-model from scratch.
- Reactivity policies can read from the Inner MAP and adjust based on
  it (e.g. refusing actions outside current boundaries).

---

## Phase 5 — Plasticity, habit and synthesis (months 12–18)

Maps to whitepaper *Phase 3 / Year 2 Q3*, principle **Plasticity**.

**Objective:** allow the system to change itself. This is where the
project's most ambitious claim — self-rewriting — is tested.

**Modules introduced**

- `plasticity_engine/` — primitives for adding, removing, and rewiring
  modules at runtime. Operates on a typed module graph; refuses
  operations that would orphan the AION loop.
- `reinforcement/` (Habit Process) — strengthens frequently used
  pathways; tracks per-pathway use counts and adjusts default action
  costs.
- `synthesis/` (Synthesis Process) — the subtractive counterpart.
  Identifies redundancy in the module graph and proposes pruning
  operations to the plasticity engine. Implements the `--` operator
  as a first-class API.
- `auto_regeneration/` — controlled self-rewriting of module
  configuration; out of scope (for now) is rewriting Python source.

**Deliverables**

- A long-running experiment where the module graph at hour 100 is
  measurably different from hour 0, with documented reasons for each
  change.
- A "rollback" capability: any plasticity step can be reverted from the
  Inner MAP's history.

**Exit criteria**

- The system reduces its own latency on a fixed benchmark task by at
  least one synthesis-driven simplification, without external
  intervention.
- No plasticity step has been able to crash the AION loop in a 7-day
  soak test.

---

## Phase 6 — Language & cross-module communication (months 15–20, overlaps Phase 5)

Maps to whitepaper *Supporting Processes / Cross-Functional Language
Processing*.

**Objective:** give the system a single shared language for inter-module
communication and external interaction. Per `CONCEPTS.md`, language is
not just an output channel — it is the medium that lets modules *mean*
the same thing when they talk.

**Modules introduced**

- `language/` — schema-typed messages on the bus, plus an external
  natural-language interface. The internal layer is always required;
  the external NL layer is optional and pluggable (LLM-backed or
  symbolic).
- `memory/` — explicit "in-between" memory: the state generated by the
  *interaction* between cognition and sensory streams, not stored in
  either alone.

**Deliverables**

- All inter-module messages flow through `language/` with versioned
  schemas.
- An optional CLI / chat interface that lets a human converse with the
  running system without bypassing the AION loop.

---

## Phase 7 — Auto-determination, complexity, uncertainty (months 18–24)

Covers the remaining modules from `MODULES.md` that don't fit neatly
into earlier phases.

**Modules introduced**

- `auto_determination/` — Being / Not-Being driver. Provides the
  baseline tension that keeps the system from settling into a fixed
  point.
- `complexity/` — implements the *Escape sub-process*: a system at full
  balance is dead, so a controlled instability is injected when the
  module graph becomes too quiescent.
- `uncertainty/` — choice under unknown distributions; gives the
  reactivity engine a principled way to act in 50/50 situations rather
  than freezing.
- `dimensional_comparison/` — provides the limits / boundaries the
  Inner MAP and plasticity engine need to talk about "self" coherently.

---

## Phase 8 — Testing, hardening, pilot deployment (months 22–24)

Maps to whitepaper *Phase 4 / Year 2 Q4*.

**Objective:** turn the system from a research instrument into something
that can be observed in a non-trivial environment for an extended
period.

**Deliverables**

- 30-day soak test with full telemetry.
- Reproducibility tooling: given a recorded stimulus stream, the system
  must replay to within a documented tolerance.
- Pilot deployment in at least one bounded real-world environment
  (a sensor-rig, a game world, a long-running service) where its
  behaviour can be evaluated against the five core principles.

**Exit criteria**

- An external reviewer can take the repository, follow the README, and
  reproduce the pilot deployment within one working day.

---

## Cross-cutting workstreams (continuous)

These do not own a phase; they run alongside everything else.

- **Theory ↔ code traceability.** Every module merged into `main` must
  cite the section of the whitepaper or concepts document it
  implements. Drift between theory and code is treated as a bug.
- **Energy & continuity.** UPS / restart / persistence concerns are
  revisited at every phase boundary; "brain death" events are treated
  as first-class incidents.
- **Ethics & shutdown.** A system designed to be continuously running
  and self-modifying needs explicit, easy, irrevocable off-switches.
  Each phase must demonstrate one.

---

## Open questions

These are tracked here rather than hidden in the code, because they
materially affect future phases.

1. **What counts as a module?** A Python package? A process? A subgraph
   of the bus? Phase 5's plasticity engine forces an answer.
2. **How is the Inner MAP serialised?** Phase 4 picks a format; Phase 5
   stress-tests it.
3. **Where does learning live?** Reinforcement (habit) is in Phase 5;
   gradient-based learning has not been placed deliberately, because
   the project's stance on it (see `CONCEPTS.md` on Synthesis vs.
   Mechanism) is not yet settled.
4. **What is the minimal body?** Phase 2 hedges with a simulated
   environment, but the whitepaper's claim that embodiment is
   *necessary* (not optional) for awareness will eventually have to be
   tested against a real-world body.
5. **What does "death" mean operationally?** Process exit is the
   trivial answer; the harder question is whether a system that
   restarts from a persisted Inner MAP is the *same* system. Phase 8
   has to take a position.

---

## Summary timeline

| Phase | Window         | Headline outcome                                          |
|-------|----------------|-----------------------------------------------------------|
| 0     | weeks 0–4      | Repo skeleton, runtime primitives, CI                     |
| 1     | months 1–3     | AION/IMPULSE loop runs continuously                       |
| 2     | months 3–6     | Sensory streams + simulated body                          |
| 3     | months 6–9     | Context-aware, mood-modulated reactivity                  |
| 4     | months 9–12    | Inner MAP: a persisted self-model                         |
| 5     | months 12–18   | Plasticity, habit, synthesis (subtractive optimisation)   |
| 6     | months 15–20   | Cross-module language layer + memory                      |
| 7     | months 18–24   | Auto-determination, complexity, uncertainty               |
| 8     | months 22–24   | Soak test, reproducibility, pilot deployment              |

This timeline is aspirational, not contractual. The order matters more
than the dates: each phase assumes the previous one's exit criteria are
met.
