"""
Console — a verb-first command interpreter that can drive and inspect
the entire Conscience from a single endpoint.

The web server exposes this at POST /command {"cmd": "..."} and the
NERV terminal panel in the UI is a thin client over it. Because the
parser runs server-side it can reach every module, parameter, and
Lifecycle action.

Design (from the decision log): control everything *except* save/load
(no resurrection); read + write; expose all numeric parameters; per-
module pause/resume; coexist with the existing buttons.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from solaris.runtime.signals import Action, MeaningEvent

if TYPE_CHECKING:
    from solaris.web.server import HttpServer

# Short alias -> module.name, so `set io.action_threshold 0.5` works.
ALIASES = {
    "io": "io_module",
    "aion": "aion_impulse",
    "autodet": "auto_determination",
    "dimcomp": "dimensional_comparison",
    "autoregen": "auto_regeneration",
    "backprop": "backpropagation",
    "memory": "memory_senses",
    "senses": "memory_senses",
}

HELP = """SOLARIS_AI CONSOLE — commands (verb-first)

  INTERACT
    stimulate <payload> [modality] [intensity]   inject a Stimulus   (alias: stim)
    react <valence>                              react to last Action (-1..1)
    no [meaning]                                 say NO to a meaning (or the last)
    bond <source> <weight>                       set an e.Link (0..1)
    sic <modality> <type>                        bind input->output (physical|mental|physicomental)

  ACTIONS (metabolic)
    sleep | wake | activate | reborn | die

  CONTROL
    set <module.attr> <value>                    set a parameter (e.g. set io.action_threshold 0.45)
    get <module.attr>                            read a parameter
    pause <module> | resume <module>             pause / resume a module
    params                                       list common parameters

  INSPECT
    inspect <module>                             a module's live state   (alias: state)
    modules                                      list modules + paused flag
    topology                                     bus subscription counts
    trace [n]                                    last n signals (default 12)
    snapshot                                     lifecycle + metabolism summary
    vitals                                       age / mode / arousal / sync

  MISC
    help                                         this list
    clear                                        clear the console output (client-side)

Module names: full (io_module, aion_impulse, ...) or alias
(io, aion, autodet, dimcomp, autoregen, backprop, memory)."""

COMMON_PARAMS = [
    "aion.period", "aion.silence_threshold",
    "logos.decay", "logos.period",
    "io.action_threshold", "io.window",
    "mysterium.decay", "synthesis.prune_threshold", "synthesis.period",
    "complexity.dwell", "complexity.low_fracture",
    "auto_determination.period",
    "metabolism.sleep_duration", "metabolism.sleep_after_low",
    "metabolism.rested_arousal", "metabolism.low_arousal",
    "negation.forbid_threshold", "negation.decay",
    "habit.lr", "uncertainty" + "._rng (n/a)",
]


class Console:
    def __init__(self, server: "HttpServer") -> None:
        self.server = server

    @property
    def c(self):
        return self.server.conscience

    def _module_by(self, token: str):
        name = ALIASES.get(token, token)
        for m in self.c._modules:
            if m.name == name:
                return m
        return None

    async def run(self, line: str) -> str:
        line = (line or "").strip()
        if not line:
            return ""
        parts = line.split()
        verb = parts[0].lower()
        args = parts[1:]
        try:
            return await self._dispatch(verb, args)
        except Exception as exc:  # noqa: BLE001
            return f"error: {exc}"

    async def _dispatch(self, verb: str, args: list[str]) -> str:
        alive = self.c.lifecycle.alive

        if verb in ("help", "?"):
            return HELP
        if verb == "clear":
            return "\x00clear"           # sentinel handled client-side

        # ---- interact -------------------------------------------------
        if verb in ("stimulate", "stim"):
            if not args:
                return "usage: stimulate <payload> [modality] [intensity]"
            if not alive:
                return "system is dead (reborn to revive)"
            payload = args[0]
            modality = args[1] if len(args) > 1 else "external"
            intensity = float(args[2]) if len(args) > 2 else 0.7
            await self.c.stimulate(payload, modality=modality, intensity=intensity)
            return f"stimulated {modality}:{payload} @ {intensity}"

        if verb == "react":
            if not alive:
                return "system is dead"
            val = float(args[0]) if args else 0.5
            last = next((s for s in reversed(self.c.bus.trace)
                         if isinstance(s, Action)), None)
            if last is None:
                return "no action to react to yet"
            await self.c.react(last.id, val)
            return f"reacted {val:+} to action #{last.id}"

        if verb in ("no", "negate"):
            if not alive:
                return "system is dead"
            meaning = " ".join(args) if args else None
            if meaning is None:
                last = next((s for s in reversed(self.c.bus.trace)
                             if isinstance(s, MeaningEvent)), None)
                meaning = last.meaning if last else None
            if not meaning:
                return "no meaning to negate yet"
            strength = await self.c.negate(meaning)
            return f"NO -> {meaning}  (limit {round(strength, 3)})"

        if verb == "bond":
            if len(args) < 2:
                return "usage: bond <source> <weight>"
            self.c.negation.bond(args[0], float(args[1]))
            return f"e.Link[{args[0]}] = {self.c.negation.elink[args[0]]}"

        if verb == "sic":
            if len(args) < 2:
                return "usage: sic <modality> <physical|mental|physicomental>"
            self.c.io.set_sic(args[0], args[1])
            return f"SIC[{args[0]}] = {args[1]}"

        # ---- actions --------------------------------------------------
        if verb == "sleep":
            await self.c.sleep(); return "entering DREAM-SLEEP"
        if verb in ("wake", "regain", "re-gain"):
            await self.c.wake(); return "RE-GAIN -> awake"
        if verb == "activate":
            await self.c.activate("console"); return "ACTIVATE -> survival mode"
        if verb == "die":
            if alive:
                await self.c.death(cause="console"); return "DIED"
            return "already dead"
        if verb == "reborn":
            await self.server._do_reborn(); return "REBORN -> a new life from 0"

        # ---- control --------------------------------------------------
        if verb == "set":
            if len(args) < 2 or "." not in args[0]:
                return "usage: set <module.attr> <value>"
            return self._set_param(args[0], args[1])
        if verb == "get":
            if not args or "." not in args[0]:
                return "usage: get <module.attr>"
            return self._get_param(args[0])
        if verb == "params":
            return "settable parameters:\n  " + "\n  ".join(
                p for p in COMMON_PARAMS if "n/a" not in p)
        if verb in ("pause", "resume"):
            if not args:
                return f"usage: {verb} <module>"
            m = self._module_by(args[0])
            if m is None:
                return f"no module '{args[0]}'"
            m.enabled = (verb == "resume")
            return f"{m.name} {'resumed' if m.enabled else 'paused'}"

        # ---- inspect --------------------------------------------------
        if verb in ("inspect", "state"):
            if not args:
                return "usage: inspect <module>"
            m = self._module_by(args[0])
            if m is None:
                return f"no module '{args[0]}'"
            obs = m.observe()
            paused = "" if m.enabled else "  [PAUSED]"
            rows = "\n".join(f"  {k} = {v}" for k, v in obs.items() if k != "name")
            return f"{m.name}{paused}\n{rows}"
        if verb == "modules":
            out = []
            for m in self.c._modules:
                out.append(f"  {m.name}{'' if m.enabled else '  [PAUSED]'}")
            return f"{len(self.c._modules)} modules:\n" + "\n".join(out)
        if verb == "topology":
            subs = self.c.topology()
            lines = [f"  {sig}: {len(hs)}" for sig, hs in subs.items()]
            return "bus subscriptions (signal: #handlers):\n" + "\n".join(lines)
        if verb == "trace":
            n = int(args[0]) if args and args[0].isdigit() else 12
            recent = self.c.bus.trace[-n:]
            return "\n".join(
                f"  #{s.id:<4} {type(s).__name__:<13} {s.origin}"
                for s in recent) or "  (empty)"
        if verb == "snapshot":
            snap = self.c.snapshot()
            return (f"lifecycle: {snap['lifecycle']}\n"
                    f"metabolism: {snap['metabolism']}\n"
                    f"modules: {len(snap['modules'])}")
        if verb == "vitals":
            snap = self.c.snapshot()
            meta = snap["metabolism"]
            being = snap["modules"].get("auto_determination", {}).get("being")
            sync = f"{being * 100:.1f}%" if being is not None else "n/a"
            return (f"age {snap['lifecycle']['age_s']}s · "
                    f"{'ACTIVE' if snap['lifecycle']['alive'] else 'OFFLINE'} · "
                    f"mode {meta['state']} · arousal {meta['arousal']} · sync {sync}")

        return f"unknown command '{verb}' — try 'help'"

    # ---- parameter get/set --------------------------------------------

    def _resolve(self, dotted: str):
        mod_token, _, attr = dotted.partition(".")
        m = self._module_by(mod_token)
        if m is None:
            return None, None, f"no module '{mod_token}'"
        if not hasattr(m, attr):
            return None, None, f"{m.name} has no parameter '{attr}'"
        return m, attr, None

    def _get_param(self, dotted: str) -> str:
        m, attr, err = self._resolve(dotted)
        if err:
            return err
        return f"{dotted} = {getattr(m, attr)}"

    def _set_param(self, dotted: str, raw: str) -> str:
        m, attr, err = self._resolve(dotted)
        if err:
            return err
        old = getattr(m, attr)
        if not isinstance(old, (int, float, bool, str)):
            return f"{dotted} is not a settable scalar ({type(old).__name__})"
        try:
            if isinstance(old, bool):
                new = raw.lower() in ("1", "true", "yes", "on")
            elif isinstance(old, int):
                new = int(float(raw))
            elif isinstance(old, float):
                new = float(raw)
            else:
                new = raw
        except ValueError:
            return f"cannot parse '{raw}' as {type(old).__name__}"
        setattr(m, attr, new)
        # keep observable state in sync where the module mirrors it
        if isinstance(m.state, dict) and attr in m.state:
            m.state[attr] = new
        return f"{dotted}: {old} -> {new}"
