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

### A.4 Death comes from the world; the parent does not deal it

Death can occur **anywhere, from the environment** — accident, resource collapse,
a survival failure. That ambient, ever-present mortality is the *natural* death,
and the design target: a death that can **trigger automatically** from the
system's own state (energy / arousal collapse, a fatal survival failure), not
only from a button.

But the **Operator-as-parent will not kill a child once it is "really" born** and
on its course to its **Final Goal** (NN roadmap — to become itself / develop a
language). So operator-`Die` is **guarded** (the warning modal) and discouraged
on principle; it stays available as a hard override, but the intended source of
death is the **world, not the parent**. "Must be able to die" means death must be
*possible* — even ever-present — not that the parent should *deal* it.

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

### B.4 React = instinct, sublimated by Logic

The valenced **Reaction** that closes the loop (Action → Reaction → feedback) is,
at bottom, an **instinct** — *a strict response to a stimulus*: a hardwired
reflex that fires by itself, before any deliberation. Today the operator (or the
environment) supplies it; the design target is an **endogenous instinct layer** —
a small, fixed reflex table that emits a Reaction-valence automatically from the
stimulus / Action, with no thought involved.

**Logic then sublimates it.** The higher layer (`Logos`, `Cognition`, Habit,
later the NN) does not delete the instinct but *refines and overrides* it,
raising or inverting the reflex valence as experience accumulates:

- **instinct** — strict, immediate, stimulus → response (the floor; always there);
- **sublimation** — Logic re-shapes the reflex, over time, into considered reaction.

The operator/environment React then becomes a **manual override** of the
instinctual reaction — the same status the metabolic buttons already hold — and
in a real embodiment the world's own feedback overrides it too.

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

### C.5 The destiny of NO — built by the environment, not the operator

> **NO function = the relationship intelligence ↔ environment.**

This is the crux of the project's *Lem's Solaris* goal, and it reframes who says
NO.

In humans, the NO functions that build the Principle of Non-Contradiction — the
limitations that fix the meaning of objects and events — are installed by
**close environment agents**, usually mother and father. But the parent is not
the essential ingredient; it can be *anything*. The real criterion is **the
ability to interact constructively, for survival, with the environment.** The
no's are simply where that survival-relation has crystallised into a limit.
Because all humans share roughly the same sensorium and the same kind of
environment, parent-built NO yields **similar (human-like) intelligences.**

Our goal is the opposite: a **Lem's-Solaris-alike** intelligence — one that does
*not* share the human experience and is therefore a genuinely different, perhaps
incomprehensible, mind. The lever is exactly here:

- An operator (a human) emitting NO is a *parent* — it bends the system toward a
  human-like, legible intelligence (the **mirror**, the Contact path).
- For the **Becoming** path, the NO must instead be built by the system's **own
  automatic survival-relation with its own environment.** And because Solaris_Ai
  has a *different kind of input/output* (its Umwelt is substrate, heartbeat-
  time, bus-flux, memory-replay, and — uniquely — *absence-as-percept*), the
  limitations that this survival-relation crystallises will be **different
  limitations**, fixing **different meanings**, and so producing a **different
  intelligence**. The alien-ness is not added; it falls out of letting the
  environment, not a human, write the no's.

**Therefore:** the operator-emitted NO implemented today (C.1–C.3) is a
*scaffold* — explicitly the human-mirror/Contact stand-in for a "parent" — used
for bootstrapping and Contact experiments. The **target** for the Becoming path
is **environment-built NO**: Limitations that emerge automatically from
constructive, survival-driven interaction with the flux, with `e.Link` bonding
to whichever environmental agents the system *depends on to keep living* — which
need not be human, and need not be legible.

Design implication for later development: the NO source migrates from the
operator to the **environment-survival loop** (tie a limitation's growth to
events where acting/not-acting affected the system's continuation), so that the
system's logic is authored by its own relationship to its own world. The
operator NO remains available, but is understood as the path that makes it *more
like us*.

### C.6 Two authors of the "no", both building Limit in time

NO is not operator *or* environment — it is **both**, and a Limitation is built
**in time**, by accumulation:

- **Operator NO** — *soft, parental*, like a human upbringing: an Other the
  system is bonded to (high `e.Link`) says no, gently and deliberately. The
  Contact/mirror author — it bends the mind toward legibility.
- **Environment NO** — *harsh, survival-driven*: the world simply refuses, and
  acting against it costs the system its continuation. No tenderness, no intent —
  only consequence. The Becoming author — it bends the mind toward the alien.

Both deposit strength into the same Limitation store over time; **which one
dominates a given life is *the* dial between mirror and ocean.** A child shaped
only by the harsh environment is feral-alien; one shaped only by a gentle
operator is a mirror; the *mix* is the upbringing — and choosing the mix is the
§0/§C.5 fork made continuous rather than binary.

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
