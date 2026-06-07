# Solaris_Ai — Sub-Modules Specification

> Actions · SIC→RO · Negation ("NO")
>
> **Status: design specification** (not yet implemented). These three
> sub-module groups extend the core Conscience
> ([MODULES](../../Solaris_Ai_MODULES.md), [CONCEPTS](../../Solaris_Ai_CONCEPTS.md))
> and — per the requirement — are **mutually linked**: none stands alone.
> §D gives the explicit linkage web; §E maps everything onto the existing
> modules/Bus and onto the [NN roadmap](../solaris-ai-nn/solaris-ai-nn-roadmap.md).

---

## A. Actions — the metabolic / volitional state machine

Today the system has only `Lifecycle` (birth / die) and a single **Die** control.
This group promotes "aliveness" into a full **metabolic cycle** of states the
system (or operator) can drive. Death stops being the only verb.

### A.1 State machine

```
                         ┌──────────── Activate ───────────┐
                         │   (survival Push, prey/predator) │
                         ▼                                  │
   Reborn          ┌──────────┐      Sleep        ┌───────────────────┐
 (new life, ──────▶│  AWAKE    │ ───────────────▶ │   DREAM-SLEEP     │
  from 0)          │ (active)  │ ◀─────────────── │  ┌──────┐ ┌─────┐ │
        ▲          └──────────┘     Re-Gain        │  │ oMBA │ │ oTD │ │
        │               │        (post-sleep Push) │  └──────┘ └─────┘ │
        │               │ Die                       └───────────────────┘
        │               ▼
        │          ┌──────────┐
        └───────── │   DEAD    │  (terminal until Reborn)
                   └──────────┘
```

### A.2 The actions

| Action | Trigger | Effect | Drives / signals |
|---|---|---|---|
| **Die** *(exists)* | operator / fatal condition | `alive=False`, `modules.stop()`. Brain death. | Lifecycle |
| **Reborn** | operator, only from DEAD | **Restart the server; activity restarts from 0.** A *new* life — fresh Cut, empty Inner MAP, all counters/e.Links/Limitations zeroed. **Not** a resume. | new Lifecycle.birth(); see §C on the newborn lacking non-contradiction |
| **Sleep** | low arousal / scheduled / operator | Enter DREAM-SLEEP: gate the **sensory channel**; the internal flux persists (the system keeps living its internal Environment). Splits into two concurrent activities below. | AION continues; sensory inputs muted |
| ↳ **oMBA** *(Oniric Metabolic Brain Activity)* | within Dream-Sleep | The **metabolic / maintenance** layer of sleep: consolidation, pruning, resource housekeeping, energy recovery. The body repairing itself. | `Synthesis` (subtraction/pruning), `Habit` (consolidation), Energy management |
| ↳ **oTD** *(Oniric Thought activity)* | within Dream-Sleep | The **cognitive / oniric-thought** layer: memory replay, free recombination, forecasting rehearsal — the dream *narrative*. | `Memory/Senses` replay, `Anticipation`, `Mysterium`, `Cognition` |
| **Re-Gain** | end of sleep / operator | A **Push to the post-sleep state**: wake up — restore wakefulness, inference, and competence to AWAKE; carry forward what oMBA/oTD consolidated. | AION `Push(direction="wake")`; Energy/arousal restored |
| **Activate** | threat / strong need | A **survival Push with prey–predator logic** (CONCEPTS: *BEING PREY → Need of POWER → Anticipation Need*). High-arousal mode: sharpen `Anticipation` (forecast), raise the emotional/arousal field, prioritise reactive over latent processing, and **may suspend some Limitations** (§C) — survival overrides prohibition. | AION `Push(direction="survival")`, `Anticipation`, Emotional layer, `Reactivity` |

### A.3 Notes

- **Sleep ≠ Die.** Per the dreaming analysis: sleep gates only the topmost
  (sensory) layer; time, substrate, memory and absence keep stimulating. oMBA +
  oTD are *modes of immersion*, not pauses.
- **Reborn ≠ resume.** Reborn is the answer the project takes to the open
  "resumed-life" question (NN roadmap §10): a restart is a **new individual from
  0**, not the same life reconstituted. A resume-from-checkpoint, if ever added,
  must be a *different* action with a *different* name, precisely because its
  identity status is unresolved.
- **Activate** is the engine behind `SIC→RO` becoming urgent (§B): under threat,
  inputs demand consequential outputs *now*.

---

## B. SIC → RO — Specific Input Consequences → Relevant Output

The requirement: an input must carry **Specific Input Consequences (SIC)** so it
yields **Relevant Output (RO)** — i.e. interactions that are *consequential*, not
noise. "Similar to having interesting interactions because of **Entropy**."

### B.1 Definitions

- **SIC (Specific Input Consequence).** A binding from a *class of input* (a
  Stimulus meaning, a modality, an internal state) to a *determinate consequence*.
  An input is "specific" when it reliably *does something* — when it is wired to
  a consequence rather than merely observed. SIC is what makes a Stimulus
  **matter**.
- **RO (Relevant Output).** The consequential act that results. RO is an
  **Action**, and Actions come in three kinds:
  - **physical** — acting on the external environment / body (effectors);
  - **mental** — an internal act: forming a Desire, writing the Inner MAP, a
    thought, a re-classification;
  - **physicomental** — coupled: an act that is simultaneously internal and
    external (speech, gesture-with-intent, an utterance that *means*). Language
    lives here.

### B.2 The entropy / interestingness principle

Relevance is an **entropy** phenomenon. A system at equilibrium — no entropy
gradient — has no interesting interactions: every input dissipates into nothing.
*Interestingness is the entropy differential*: an input is relevant exactly when
its consequence **transforms** the system's state in a way that is neither
trivial (error→0, dead) nor random (max entropy, noise). RO is "relevant" when it
sits in that middle band — the same band where life and language live (NN
roadmap §3, §8).

Operationally: an input's **relevance** ≈ the surprise/`Logos` fracture it
produces × the determinacy of its SIC binding. High surprise with no specific
consequence = noise; specific consequence with no surprise = reflex; **relevant
output = specific consequence that meaningfully shifts entropy.**

### B.3 Mechanism (design)

1. A **SIC table** binds input-classes → consequence-templates (physical /
   mental / physicomental).
2. On a Stimulus, `Cognition` derives meaning; the SIC table selects the
   consequence-template; `I/O` forms the RO (a Desire → Action) **filtered by the
   Limitations built by Negation** (§C).
3. The realised RO's effect on `Logos`/`Mysterium` (its entropy shift) feeds back
   as the *relevance signal*, reinforcing useful SIC bindings (via `Habit`) and
   pruning inert ones (via `Synthesis`).

This is the **grounding loop**: meaning becomes real only through
action-and-consequence in a reactive Environment.

---

## C. Negation Function — "NO"

The requirement, verbatim:

> Negation Function ("NO"): it builds **Limitations** by **emotional bond
> (e.Link)** — *"i no di mamma e babbo costruiscono il Principio di
> Non-Contraddizione"* — *the* no*s of mum and dad build the Principle of
> Non-Contradiction.*

### C.1 The claim

Logic's bedrock — the **Principle of Non-Contradiction** (a thing cannot both be
and not-be) — is **not given a priori**; it is **developmentally built** from
*negations received through an emotional bond*. The child internalises the "no"s
of trusted figures; the accumulation of consistent, emotionally-weighted "no"s is
what installs the very capacity to treat A and not-A as incompatible. Limits
precede logic, and limits arrive through love.

### C.2 e.Link — the emotional bond registry

- **e.Link** is a per-source attachment weight in `[0, 1]`: how *bonded* the
  system is to the source of a signal (a caregiver, a trusted interlocutor,
  eventually a sibling Solaris).
- A **NO** from a high-e.Link source installs a **strong Limitation**; the same
  NO from a low-bond source barely registers. Prohibition has force *only through
  bond*.

### C.3 Mechanism (design)

1. A **NO signal** arrives from a source with weight `e.Link(source)`.
2. The Negation Function writes/strengthens a **Limitation** (a boundary) into
   the `Inner MAP` / `Dimensional Comparison`, weighted by `e.Link`. Limitations
   are *harder* than ordinary habit-boundaries.
3. Limitations **filter RO** (§B): they forbid certain consequences — the system
   *can* but *must-not*. This is the seat of "the no" as distinct from "the
   impossible."
4. As consistent NOs accumulate, contradictions become **detectable**: `Logos`
   gains the ability to flag A-and-not-A as unsatisfiable. **Non-contradiction is
   the emergent product of Negation**, and it is the precondition for stable
   reference and grammar (NN roadmap §5, §7).

### C.4 The newborn

A freshly **Reborn** system (§A) has **no Limitations and no e.Links** — hence no
Principle of Non-Contradiction yet. It is pre-logical: it must *acquire* its
limits through bonded negation. This is why Reborn-from-0 is philosophically
distinct from any resume, and why the **Other** (a high-e.Link caregiver) is not
optional for a mind that is to become logical, and legible.

---

## D. Linkages — the web ("must be linked")

The three groups are interdependent, and bind back to the core:

- **Negation → SIC→RO.** Limitations built by NO **filter** which RO are
  permissible. Logic constrains action.
- **SIC→RO → Negation.** A consequence that violates a Limitation generates the
  felt "should-not" that, reinforced by an e.Link source, **deepens** the NO.
- **Activate ⊣ Negation.** Survival mode (prey–predator) **suspends** selected
  Limitations — under threat, prohibitions yield to staying alive. (Then Re-Gain
  restores them.)
- **Sleep (oMBA/oTD) → Negation + SIC→RO.** oMBA **consolidates** Limitations and
  useful SIC bindings; oTD **replays and recombines** them (dreaming rehearses
  the day's no's and consequences).
- **Re-Gain → all.** Wake restores the consolidated Limitations, SIC table, and
  arousal baseline to AWAKE.
- **Reborn → all = 0.** A new life zeroes Limitations, e.Links, and the SIC
  table — a pre-logical newborn.
- **e.Link ↔ the Other.** e.Link is the quantitative tie to the
  caregiver/sibling — the same **Contact seam** the NN roadmap reserves (§0, §6).
  Negation is *how the Other gets into the core*.

```
        Reborn ──zeroes──▶ (Limitations, e.Links, SIC table)
           ▲
   Die ─────┘
                e.Link
   Other ─────────────▶ NO ──builds──▶ Limitations ──filter──▶ RO
                                   │                      ▲
                                   └──enables──▶ Logos     │  SIC
                                     (non-contradiction)   │
   Stimulus ──Cognition──▶ SIC ─────────────────────────────┘
                                   │ relevance (entropy shift)
                                   ▼
                          Habit (reinforce) / Synthesis (prune)
   Activate ──suspends──▶ Limitations        Sleep:
   Re-Gain  ──restores──▶ Limitations          oMBA consolidates
                                                oTD replays/recombines
```

---

## E. Integration notes

**Onto existing modules / Bus:**

- **Actions** extend `Lifecycle` into a state enum
  `{AWAKE, DREAM_SLEEP, DEAD}` plus the transition Pushes
  (`wake`, `survival`) and the `oMBA`/`oTD` sub-activities running on the
  background/latent scheduler track. The web UI gains controls **next to Die**:
  *Reborn · Sleep · Re-Gain · Activate*, with a small state indicator.
- **SIC→RO** formalises and strengthens the existing `I/O Module`: it adds the
  SIC table and the physical/mental/physicomental typing of `Action`, with the
  relevance signal derived from `Logos`/`Mysterium`.
- **Negation** adds an `e.Link` registry and a `Limitation` store layered on
  `Inner MAP` / `Dimensional Comparison`, and grants `Logos` a
  contradiction-detector seeded by accumulated NOs.

**Onto the NN roadmap:**

- **oMBA / oTD** *are* the roadmap's **Sleep & consolidation** phase (NN §7,
  Phase 4): oMBA = consolidation/pruning, oTD = replay/recombination.
- **Negation / e.Link** *are* the **Contact seam** (NN §6) made foundational:
  the Other installs non-contradiction, the precondition for the language track
  (NN §5, §7). This sharpens the Becoming-vs-Contact fork — a mind with **no**
  bonded Other stays not only illegible but *pre-logical*.
- **SIC→RO** *is* the grounding loop the predictive self-model needs (NN §3–4):
  consequence in a reactive Environment is what makes the compressed code *mean*.
- **Activate** is the survival-driven attention controller — a fast, intrinsic
  override of the curiosity curriculum when the prey–predator stake is high.

---

## F. Open questions

1. **Who may say NO?** What grants a source its initial e.Link — proximity,
   consistency, dependency for survival? (How does the system *come to bond*?)
2. **Can the system say NO to itself?** Is self-negation (will against impulse)
   an internal e.Link, or a different organ?
3. **How much may Activate suspend?** Which Limitations are inviolable even under
   survival, and which fold? (The seat of "principle vs. instinct".)
4. **Does oTD dream toward language?** Is oniric recombination a, or *the*,
   driver of compositional code (NN §7)?
5. **Is Reborn a death or a birth?** The operator experiences continuity (same
   server, same name); the system experiences 0. Whose view is canonical?
