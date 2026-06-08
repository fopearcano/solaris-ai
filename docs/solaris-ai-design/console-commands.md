# Solaris_Ai — Console command list

The Console (the `>_` button right of the top-bar stats, or backtick `` ` `` to
toggle; `Esc` closes; `↑/↓` history) is a verb-first command line that can
**control and inspect the entire running system** from one endpoint
(`POST /command`). It coexists with the on-screen buttons.

Module names accept the full `.name` (`io_module`, `aion_impulse`, …) or a short
alias: `io`, `aion`, `autodet`, `dimcomp`, `autoregen`, `backprop`,
`memory`/`senses`.

---

## Interact

| Command | Effect |
|---|---|
| `stimulate <payload> [modality] [intensity]` | Inject a Stimulus. Alias `stim`. Default modality `external`, intensity `0.7`. While asleep, a non-`threat` stimulus is gated; a `threat` wakes + Activates. |
| `react <valence>` | React to the most recent Action, `-1..1` (feeds Habit / Backprop). |
| `no [meaning]` | Say **NO** to a meaning (or the most recent one) — builds a Limitation through bond. Alias `negate`. |
| `bond <source> <weight>` | Set an e.Link bond `0..1` for a source (override). |
| `sic <modality> <type>` | Bind a Specific Input Consequence: `physical` \| `mental` \| `physicomental`. |

## Actions (metabolic)

| Command | Effect |
|---|---|
| `sleep` | Enter DREAM-SLEEP (oMBA consolidation + oTD dreaming; sensory gated). |
| `wake` | Re-Gain — push to the post-sleep state. Aliases `regain`, `re-gain`. |
| `activate` | Survival Push (prey–predator): raise arousal, lower I/O threshold, suspend Limitations. |
| `reborn` | A **new life from 0** (fresh Bus / Lifecycle / modules — not a resume). |
| `die` | Brain death (Lifecycle.die). Revive with `reborn`. |

## Control

| Command | Effect |
|---|---|
| `set <module.attr> <value>` | Set any scalar parameter, e.g. `set io.action_threshold 0.45`, `set aion.period 0.05`, `set metabolism.sleep_duration 10`. |
| `get <module.attr>` | Read a parameter. |
| `pause <module>` | Pause a module — the Bus skips its handlers and its loop idles. |
| `resume <module>` | Resume a paused module. |
| `params` | List the common settable parameters. |

Common parameters: `aion.period`, `aion.silence_threshold`, `logos.decay`,
`logos.period`, `io.action_threshold`, `io.window`, `mysterium.decay`,
`synthesis.prune_threshold`, `synthesis.period`, `complexity.dwell`,
`complexity.low_fracture`, `auto_determination.period`,
`metabolism.sleep_duration`, `metabolism.sleep_after_low`,
`metabolism.rested_arousal`, `metabolism.low_arousal`,
`negation.forbid_threshold`, `negation.decay`, `habit.lr`.

## Inspect

| Command | Effect |
|---|---|
| `inspect <module>` | A module's live state (+ `[PAUSED]` flag). Alias `state`. |
| `modules` | List all modules with their paused flag. |
| `topology` | Bus subscription counts per signal type. |
| `trace [n]` | The last `n` signals (default 12). |
| `snapshot` | Lifecycle + metabolism summary + module count. |
| `vitals` | age · alive/offline · mode · arousal · sync rate. |

## Misc

| Command | Effect |
|---|---|
| `help` | This command list (also rendered in the panel). Alias `?`. |
| `clear` | Clear the console output (client-side). |

---

## Notes & guarantees

- **No save/load.** By design there is no resurrection: a `reborn` is a new
  individual from 0, and there is no command to persist or restore a life
  (decision log, Q21). The honest position on the unresolved identity problem.
- **Localhost only.** The command surface is unauthenticated and intended for
  the local UI; do not expose the server publicly.
- **Same surface, two faces.** Everything the buttons do, the console does, plus
  parameter tuning, pause/resume, and inspection — the buttons are shortcuts
  over this surface.

## Examples

```
stimulate light vision 0.9
react 0.7
no vision/str/light
set io.action_threshold 0.5
activate
sleep
inspect negation
pause complexity
trace 20
reborn
```
