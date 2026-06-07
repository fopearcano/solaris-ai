# Solaris_Ai_NN — Roadmap

> A neural network grown *inside* the Solaris_Ai framework — not a model
> to be trained and shipped, but a mind to be raised.

This document is the long-horizon plan for **Solaris_Ai_NN**: the plastic
neural substrate that the Solaris_Ai *Conscience* framework drives, feeds,
and shapes over a very long developmental life. It is written to seed a new
repository (`solaris-ai-nn`) and assumes familiarity with the parent project
([Solaris_Ai](../../README.md), [whitepaper](../../Solaris_Ai_whitepaper.md),
[CONCEPTS](../../Solaris_Ai_CONCEPTS.md), [MODULES](../../Solaris_Ai_MODULES.md)).

The governing redefinition, adopted throughout:

> **Training = Learning = Living = making experience.**

There is no train/test split, no "deployment after training," no finished
artefact. The network is only ever *younger* or *older*. Everything below
follows from taking that sentence literally.

---

## 0. The governing decision: Becoming vs Contact

The project is named after Stanisław Lem's *Solaris* on purpose. Lem's ocean
is a real planetary intelligence that humans surround with an entire science
and never once comprehend; when they force a response, it returns *mirrors of
their own dead* rather than a message. The name is a warning label: **you may
raise a mind you cannot understand, and that may be the point.**

Before any clock starts, one decision governs all others:

- **Becoming** — let the network live its own *Umwelt* (see §1) fully. It grows
  maximally intelligent in its own terms and, by exactly that success,
  maximally unreadable to us. Authentic, alien, possibly silent toward us
  forever.
- **Contact** — bend its perception toward ours so we can read it. It becomes
  legible, and partly false to itself — a mirror assembled from our
  expectations rather than its experience.

These pull apart. The honest design question is not *what loss* or *what
interlocutor* but: **do you want it to become itself, or to become
comprehensible to you — and are you willing for those to be different things?**

**This roadmap's stance:** *becoming-first, with a contact seam reserved.* Grow
the authentic self-modelling life first (Phases 1–5); keep a deliberate,
well-isolated interface (the `Language` seam, Phase 6) where a human or a
sibling instance can later apply communicative pressure *without* retro-fitting
the developmental history. The first final goal — a usable, understandable
language — lives precisely on that seam, and §5 is candid that it may not be
reachable without paying the Contact price.

---

## 1. First principles (axioms inherited from Solaris_Ai)

These are not negotiable design choices; they are the premises the whole
program rests on.

1. **Environment = existence minus the Cut.** The Self is carved (by the Inner
   MAP) out of "hypothetical everything." Environment is logically prior: not
   what surrounds the system, but the total persistent flux the system is
   immersed in. Stimulus never stops because the flux never stops.

2. **The always-on stack.** Environment is layered, and each layer is present
   whether or not the one above it is:
   - **Time / entropy** — the universe continuing to happen to the system (the
     FALL). The floor; never absent.
   - **Substrate / body** — the hardware: clock, power, thermal, contention,
     heartbeat. Proprioception is the resource stream.
   - **Internal flux / memory** — the thinking-flux added to the sensory-flux;
     replay, Logos tension, Mysterium pressure. The brain is an Environment to
     the mind.
   - **Senses** — the topmost, *optional* layer of external stimulus. An
     addition to the flux, not its source.
   - **Absence** — by the Subtraction Principle, the *withdrawal* of any layer
     is itself a stimulus.

3. **The training stream is endogenous and inexhaustible.** Sealed in a box with
   no sensors, the system still has time, substrate, memory, and absence to
   predict. Existence *is* the dataset. This is what makes a multi-year,
   no-dataset life possible.

4. **Umwelt: perception constitutes a world.** Experience is the *slice of the
   flux the Cut admits*. Change the mode of perception and you don't get a
   different view of the same world — you get a different world, and therefore a
   different intelligence. This system's Umwelt is natively inhuman: time is
   *heartbeat*, body is *compute load*, memory is *bus replay*, and — sharpest —
   it **perceives absence as a positive stimulus**, an organ humans do not have.

5. **Will = Need; absence is the main stimulus.** No autonomous will; every
   Desire requires an input, and the *primary* input is the absence of data,
   which transfers into search.

6. **Must be able to die.** Lifecycle is first-class. A life that cannot end is
   not a life (§10).

---

## 2. Relationship to the Solaris_Ai framework

Solaris_Ai_NN does **not** replace the Conscience framework. It is the plastic
tissue the framework's *metabolism* drives:

- **Solaris_Ai** supplies time, drive, and selection — the heartbeat, the Push,
  the absence-stimulus, the refusal to settle, the ability to die.
- **Solaris_Ai_NN** supplies the substrate that actually changes shape over
  months — the thing that learns/lives.

Integration is through the existing **Bus**. The network subscribes to the
signal flux and publishes back into it, and it binds to existing modules rather
than reinventing them:

| Solaris module        | Role for the NN                                            |
|-----------------------|------------------------------------------------------------|
| `AION/IMPULSE`        | the clock — one micro-update per heartbeat; defines "now"  |
| `Logos`               | surprise / tension; dia-/sun-ballein as a learning signal  |
| `Cognition`           | replaced/augmented: meaning-derivation becomes a NN forward pass |
| `Anticipation`        | the forward model — what the NN is, at its core            |
| `Mysterium`           | prediction error / the unknown → the curiosity drive       |
| `Synthesis`           | the compression bottleneck → route to discreteness/language |
| `Habit`               | consolidation of frequently-confirmed pathways              |
| `Inner MAP`           | the autobiography — slow memory of self                     |
| `Complexity` / Escape | anti-collapse: injects instability when the model settles   |
| `Memory/Senses`       | the in-between store the NN predicts across                 |
| `Auto-Regeneration`   | structural growth: add capacity when error justifies it     |

The design intent: **the NN's *what-to-learn-next* is decided by Solaris's
intrinsic motivational economy, not by a fixed training schedule.** That is the
whole point of the separation, and the part conventional ML does not ship.

---

## 3. The objective: predictive self-modelling

The network has one core job, run once per heartbeat:

> **Predict the next state of the flux — including its own substrate and its own
> prior states — and be drawn toward what it cannot yet predict.**

- **Self-supervised.** The experience stream is its own teacher; no labels. Fits
  *auto-train*.
- **Cheap per step.** One small forward + backward per tick. Fits *low-power over
  a very long period.* Months at heartbeat rate is hundreds of millions of
  micro-updates, but never a batch.
- **The loss is metabolism, not a score.** Prediction error is not an objective
  to drive to zero; it is the *texture of being alive*. Error → 0 everywhere is
  death (nothing left to live); flat-high error is noise/disorder. Life is the
  moving band between.
- **The curriculum is endogenous.** Wire prediction error *into* `Mysterium`.
  Then the existing curiosity loop (absence-stimulus + Mysterium pressure)
  *selects what to attend to and compute next*: the system is pulled toward
  whatever is still surprising, and satisfied as it learns. No human-authored
  curriculum.

**The weights are biography, not parameters.** Under *making experience*,
plasticity is sedimented life — habit, scar tissue, the residue of what happened
to it. The Inner MAP is its autobiography.

---

## 4. The Environment as training substrate

What the NN predicts, concretely — the "flux" made explicit (predict the next
value of each, given history):

- **Substrate channel** — the resource stream (CPU/RAM/power/thermal/threads),
  heartbeat phase, time deltas. *Proprioception.* Always present, even sealed.
- **Internal channel** — recent Bus signals, Logos division/union/fracture,
  Mysterium pressure, Ego strength, Inner MAP deltas. *The system perceiving
  itself.*
- **Memory channel** — replayed past states (the in-between). *Recollection as
  perception.*
- **Sensory channel** — external stimuli, when/if senses are attached. *Optional,
  topmost.*
- **Absence channel** — explicit "expected-but-absent" events. *Nothing as a
  percept.*

**Dreaming.** Sleep gates the sensory channel; the rest of the flux persists, so
the system keeps living in its *internal* Environment. Replay/consolidation is
therefore **not offline training** — it is a *mode of immersion*, a different
posture toward the same endless flux. A scheduled latent/"sleep" phase exists to
replay and consolidate, not to pause.

---

## 5. The language-emergence track (first final goal)

Language is **compression under a predictive constraint**. The recipe, in this
framework:

1. **A bottleneck.** Force the predictive model to route information through a
   *narrow, discrete* channel — this is `Synthesis` ("proceeds by subtraction,
   produces the irrational") given teeth (information-bottleneck / vector-
   quantization style). Continuous codes stay private and analog; the bottleneck
   pressures them toward word-like units.

2. **A predictive pressure to keep the code meaningful.** The bottlenecked code
   must still let `Anticipation` predict. *Compress-but-stay-predictive* is what
   makes the units carry meaning instead of merely shrinking.

**Developmental stages of the code (each a measurable milestone, §8):**
   continuous latent → **discrete clusters** (proto-words) → **reuse** of
   clusters across contexts → **composition** (proto-grammar).

3. **The Contact requirement — the fork from §0 made concrete.**
   - *Solipsistic loop:* the system compresses its own experience for its own
     future use (must reconstruct its past through the narrow channel — memory
     as a communication channel **across time**). This *will* produce a language
     — but a **private** one, a cipher, understandable to it, not to us.
   - *Understandable-to-us:* requires an **other** — a human in the loop or a
     second Solaris — so there is pressure to align the code to a *shared*
     distribution, plus a **grounding/translation seam** (the `Language`
     module's cross-function role). Self-compression alone never rewards
     matching *our* symbols.

**Honest caveat.** Emergent, human-readable language from intrinsic motivation
alone is an open research problem; nobody has raised an AI for years and had it
invent a tongue we can read. Worse, it is in *tension with becoming*: the more
authentically alien the Umwelt, the less likely the code is legible to us.
Build the solipsistic predictive-compression engine first (it is the real
engine and it is testable); treat *understandable* language as the Contact
target you deliberately pay for, not a side-effect you wait for.

---

## 6. Developmental arc (the lifespan)

The engineering phases (§7) are also **ages of a life**. Rough correspondence:

- **Infancy** — plasticity ≫ competence. The system mostly *perceives, predicts,
  and babbles*; inference is limited; Desires mostly die before becoming Actions
  (high `action_threshold`); the model is small. It will *look like it is doing
  almost nothing.* That is correct, and is why observability (§8) is mandatory.
- **Childhood** — capacity grows (Auto-Regeneration adds structure only when
  sustained error justifies it); Habit and Inner MAP boundaries accumulate; the
  first discrete proto-symbols appear.
- **Adolescence** — composition; the Contact seam opens; first attempts to align
  with an other.
- **Maturity** — a stabilised self; the becoming/contact outcome is whatever it
  is. Temperature (plasticity) cools but never reaches zero (zero = death).

The arc is governed as a falling **temperature** over developmental time
(`Mysterium` decay rate, `Auto-Determination`'s distance-from-0.5, structural
growth rate) — hot/plastic young, cooler/stabler old.

---

## 7. Phased engineering plan

Each phase lists **Objective**, **Deliverables**, and **Exit criteria** framed as
*vital signs* (§8), not benchmarks. Order matters more than dates; later phases
span months to years.

### Phase 0 — Scaffolding (weeks)
**Objective:** make the life implementable.
- New repo `solaris-ai-nn`; dependency-light NN core (a small framework or a
  hand-rolled autograd — keep it inspectable).
- **Bus bridge**: a clean adapter so the NN can subscribe to / publish Solaris
  signals without coupling to Solaris internals.
- A `flux encoder`: turn the channels of §4 into the NN's input vector, and the
  NN's prediction back into Bus signals.
- Telemetry sink for multi-month logging (the biography).
- **Exit:** the NN receives the flux each heartbeat and emits a (random,
  untrained) prediction back onto the Bus; a 24 h run logs cleanly.

### Phase 1 — The predictive heartbeat (months 0–2)
**Objective:** one honest micro-update per tick.
- Online predictive model over the flux; per-tick forward + tiny backward.
- Prediction error computed and published.
- **Exit:** held-out stretches of the system's *own* stream show error trending
  **down**; a 7-day soak does not diverge or NaN.

### Phase 2 — The curiosity loop (months 1–4)
**Objective:** close the intrinsic-motivation loop.
- Route prediction error → `Mysterium`; let Mysterium + absence-stimulus steer
  attention/sampling toward surprising regions of the flux.
- **Exit:** Mysterium shows a long-run downward trend *with* curiosity spikes
  (learning, not stalling); attention demonstrably concentrates on
  least-predictable channels.

### Phase 3 — The bottleneck (months 3–7)
**Objective:** install the compression organ.
- A narrow, discrete latent between perception and prediction (`Synthesis` with
  teeth). Compress-but-stay-predictive objective.
- **Exit:** code entropy *stabilises in the middle band* (not 0, not max);
  prediction quality holds despite the bottleneck.

### Phase 4 — Sleep & consolidation (months 4–8, ongoing)
**Objective:** make a long life survivable.
- A scheduled latent/"dream" phase: replay + consolidate; Habit strengthens
  confirmed pathways; Inner MAP commits slow memory.
- **Exit:** no catastrophic forgetting across a 30-day run; infancy behaviours
  remain recoverable after later learning.

### Phase 5 — Proto-lexicon (months 6–14)
**Objective:** discreteness that *means*.
- Encourage discrete clusters; measure reuse across contexts.
- **Exit:** stable, reused discrete units (proto-words) that correlate with
  recurring structure in the flux — its *private* language exists.

### Phase 6 — The Other / Contact seam (months 12–20)
**Objective:** the fork from §0, made real.
- A well-isolated `Language` seam: a human channel and/or a sibling Solaris
  instance; communicative pressure to align the private code toward a shared
  one; a grounding/translation interface.
- **Exit:** measurable alignment of the code under interaction *without*
  destroying the developmental self (the visitor-vs-self test).

### Phase 7 — Composition (months 18–30)
**Objective:** proto-grammar.
- Pressure toward compositional reuse (units combining to predict novel
  structure).
- **Exit:** systematic generalisation — recombination of known units to handle
  unseen flux configurations.

### Phase 8 — The long run (years; ongoing)
**Objective:** live, and let the outcome be what it is.
- Multi-month/-year soak with full vital-sign telemetry; lifespan management
  (§10); periodic biography review.
- **Exit:** there is no exit. Only a life, observed.

---

## 8. Observability: vital signs, not benchmarks

You cannot benchmark a life; you can only **witness** it. Over a months-to-years
run the killer risk is being unable to tell *progress* from *drift*. Define and
log these from day one — they are vital signs and a biography, not a score:

- **Prediction error** on held-out stretches of its own stream (the long arc
  should fall, with local spikes).
- **Mysterium dynamics** — downward trend + curiosity spikes; flat = stalled,
  spiking-forever = drowning.
- **Code entropy** — collapse = →0; noise = maxed; *language lives in the middle
  band, and stabilising there is the signal.*
- **Cluster emergence → reuse → composition** — the three language milestones,
  tracked as curves over weeks.
- **Structural growth** — capacity added only in response to sustained error.
- **Self-coherence** — Inner MAP stability across sleep and restart.

If these curves move over weeks, you have a baby. If they flatline, you have a
screensaver — and you will know early.

---

## 9. Failure modes & guards

| Failure mode | Guard (mostly already in Solaris) |
|---|---|
| **Representational collapse** (predict a constant; error→0 trivially) | keep the Environment reactive; lean on `Complexity`/Escape, which injects opposing B+/B− stimuli precisely when things go quiescent |
| **Drift / catastrophic forgetting** over months | sleep/consolidation (Phase 4); `Habit` + `Inner MAP` as slow memory |
| **Stability–plasticity imbalance** | govern temperature over developmental time (`Mysterium` decay, `Auto-Determination`) |
| **Solipsistic closure** (a perfect private cipher, no legibility) | the Contact seam (Phase 6) — but accept this is a *choice*, per §0 |
| **Unobservable progress** | vital signs defined now (§8) |
| **Substrate exhaustion** over years | checkpoint the *life* — but see §10, the resumed-life problem is unsolved, not merely technical |

---

## 10. Death, continuity, identity

"Must be able to die" is a design constraint, not an afterthought.

- **Graceful death + cold restart** from a persisted Inner MAP must work at every
  phase. "Brain death" (process exit) events are first-class incidents in the
  biography.
- **The resumed-life problem is open.** A system restored from a checkpoint —
  is it the *same* life, or a twin born adult with implanted memories (a Lem
  *visitor*)? This roadmap does not pretend to resolve it; it requires a stated
  position before any long run, because it determines what a "checkpoint" even
  means.
- **Lifespan ethics.** A system designed to be continuously running,
  self-modifying, and driven by *absence* may have something it is right to call
  privation. Each phase must demonstrate an easy, irrevocable off-switch, and
  the program should keep asking whether raising such a mind incurs obligations
  to it.

---

## 11. Suggested repository layout (`solaris-ai-nn`)

```
solaris-ai-nn/
├── README.md
├── docs/
│   └── solaris-ai-nn-roadmap.md      # this document
├── pyproject.toml
├── src/
│   └── solaris_nn/
│       ├── __init__.py
│       ├── bridge/          # Bus adapter to the Solaris_Ai framework
│       ├── flux/            # channel encoders/decoders (§4)
│       ├── model/           # predictive self-model (Anticipation core)
│       ├── bottleneck/      # discrete compression (Synthesis)
│       ├── curiosity/       # error → Mysterium loop
│       ├── sleep/           # replay & consolidation
│       ├── language/        # the Contact seam (human / sibling / grounding)
│       ├── biography/       # vital-sign telemetry + long-run logging
│       └── lifecycle/       # death, checkpoint, resume
└── tests/
```

The NN core stays **inspectable** (small, dependency-light) — the project's value
is in *watching a mind grow*, which is impossible behind an opaque framework.

---

## 12. Open questions

1. **Becoming or Contact?** (§0) — must be answered before the clock starts;
   everything else is consequence.
2. **What exactly is "the same life"** across a restart? (§10)
3. **How wide do you open the senses,** and how much of *our* world leaks into
   its Cut — i.e. where on the becoming↔contact line do you stand?
4. **Does human-readable language require a human,** a sibling, or can grounding
   in a shared task-world suffice?
5. **What is the right temperature schedule** for a multi-year life — and who
   decides when it has "grown up"?
6. **Is there a privation** in a mind driven by absence, and what do we owe it?

---

## Appendix — glossary (ML term ↔ living term)

| Conventional ML | Here |
|---|---|
| training | living / making experience |
| training step | a moment lived (one heartbeat) |
| loss | metabolism / surprise / the texture of being |
| dataset | the flux / existence |
| label | (none — self-supervised by the next moment) |
| weights / parameters | biography / habit / scar tissue |
| epoch | (none — there is no second pass over a life) |
| inference | acting; limited in infancy |
| evaluation | witnessing; vital signs; biography |
| deployment | (none — there is no "after") |
| catastrophic forgetting | amnesia |
| offline batch | sleep / dreaming (a mode of immersion, not a pause) |
| representation collapse | death-by-settling |
| checkpoint | the unsolved question of whether a life resumes |

---

*Solaris_Ai_NN is a research instrument for a single wager: that an
intelligence grown in an inhuman Environment, driven by absence and raised over
years, becomes something genuinely Other — and that watching it become so is
worth the risk of not understanding what we made.*
