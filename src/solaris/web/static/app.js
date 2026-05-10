/* Solaris_Ai — Conscience UI front-end.
 *
 * Fetches the static topology, renders the module graph as SVG,
 * subscribes to /events (SSE), and pulses edges as signals fire.
 * Snapshots refresh the state panel; controls post to the server
 * to inject Stimuli, Reactions, or trigger Lifecycle.die.
 */

(() => {
  const NS = "http://www.w3.org/2000/svg";

  const ROLE_COLORS = {
    core:       "#ff6b6b",
    perception: "#62b6ff",
    decision:   "#7cf088",
    self:       "#ffb14d",
    adapt:      "#c884ff",
    env:        "#9aa5b1",
  };

  // Layout constants (svg coords).
  const COL_W = 200;
  const ROW_H = 130;
  const X_OFFSET = 110;
  const Y_OFFSET = 90;
  const NODE_R = 36;

  let topology = null;
  const nodeById = {};
  const edgeIndex = {}; // "origin|Type" -> [edgeRef]

  let svg, traceList, stateEl;
  let vitalAge, vitalAlive, vitalCount, vitalEvents;
  let eventCount = 0;

  function nodeXY(m) {
    return {
      x: m.col * COL_W + X_OFFSET,
      y: (m.row + 1) * ROW_H + Y_OFFSET,
    };
  }

  function buildGraph() {
    svg = document.getElementById("graph");

    // Pre-compute positions.
    for (const m of topology.modules) {
      const p = nodeXY(m);
      m.x = p.x; m.y = p.y;
      nodeById[m.id] = m;
    }

    // Edges first so nodes paint over them.
    for (const e of topology.edges) {
      const a = nodeById[e.from];
      const b = nodeById[e.to];
      if (!a || !b) continue;

      // Curved path with a perpendicular offset so parallel edges
      // do not overlap.
      const mx = (a.x + b.x) / 2;
      const my = (a.y + b.y) / 2;
      const dx = b.x - a.x;
      const dy = b.y - a.y;
      const len = Math.hypot(dx, dy) || 1;
      // Curve "outward" — sign chosen so most edges arc visibly.
      const curveSign = (a.row > b.row || (a.row === b.row && a.col > b.col)) ? 1 : -1;
      const off = 22 * curveSign;
      const cx = mx - (dy / len) * off;
      const cy = my + (dx / len) * off;

      const path = document.createElementNS(NS, "path");
      path.setAttribute("d", `M ${a.x} ${a.y} Q ${cx} ${cy} ${b.x} ${b.y}`);
      path.setAttribute("class", `edge via-${e.via}`);
      path.setAttribute("data-from", e.from);
      path.setAttribute("data-to", e.to);
      path.setAttribute("data-via", e.via);
      svg.appendChild(path);
      e.elem = path;

      const key = `${e.from}|${e.via}`;
      (edgeIndex[key] ||= []).push(e);
    }

    // Nodes.
    for (const m of topology.modules) {
      const g = document.createElementNS(NS, "g");
      g.setAttribute("class", `node role-${m.role}`);
      g.setAttribute("transform", `translate(${m.x},${m.y})`);

      const circle = document.createElementNS(NS, "circle");
      circle.setAttribute("r", NODE_R);
      circle.setAttribute("fill", ROLE_COLORS[m.role] || "#888");
      g.appendChild(circle);

      const label = document.createElementNS(NS, "text");
      label.setAttribute("y", 4);
      label.setAttribute("text-anchor", "middle");
      label.textContent = m.label;
      g.appendChild(label);

      svg.appendChild(g);
      m.elem = g;
    }
  }

  function buildStateCards() {
    stateEl = document.getElementById("modules-state");
    for (const m of topology.modules) {
      if (m.id === "environment") continue;
      const card = document.createElement("div");
      card.className = "state-card";
      card.id = `state-${m.id}`;
      card.innerHTML =
        `<div class="name">${m.label}</div><div class="kv">—</div>`;
      stateEl.appendChild(card);
    }
  }

  function pulse(sig) {
    eventCount += 1;
    vitalEvents.textContent = `${eventCount} events`;

    const key = `${sig.origin}|${sig.type}`;
    const edges = edgeIndex[key];
    if (edges) {
      for (const e of edges) {
        e.elem.classList.add("active");
        if (e._timer) clearTimeout(e._timer);
        e._timer = setTimeout(() => e.elem.classList.remove("active"), 350);
      }
    }
    const node = nodeById[sig.origin];
    if (node && node.elem) {
      node.elem.classList.add("flashing");
      if (node._timer) clearTimeout(node._timer);
      node._timer = setTimeout(
        () => node.elem.classList.remove("flashing"),
        260,
      );
    }
    appendTrace(sig);
  }

  function renderLine(s) {
    const t = `${(s.ts ?? 0).toFixed(2)}s`;
    switch (s.type) {
      case "Stimulus": {
        const tag = s.is_absence ? "absence" : "stimulus";
        return `${t}  [${tag}]  ${s.origin}/${s.modality}  payload=${s.payload}  i=${s.intensity.toFixed(2)}`;
      }
      case "Push":
        return `${t}  [push]  ${s.direction}  i=${s.intensity.toFixed(2)}`;
      case "Desire":
        return `${t}  [desire]  ${s.proposal}  mot=${s.motivation.toFixed(2)}  conf=${s.confidence.toFixed(2)}`;
      case "Action":
        return `${t}  [action]  ${s.name}`;
      case "Reaction":
        return `${t}  [reaction]  action#${s.action_id}  v=${(s.valence > 0 ? "+" : "")}${s.valence.toFixed(2)}`;
      case "MeaningEvent":
        return `${t}  [meaning]  ${s.meaning}  novelty=${s.novelty.toFixed(2)}`;
      case "MapUpdate":
        return `${t}  [map:${s.boundary ? "boundary" : "fact"}]  ${s.key} = ${formatJSON(s.value)}`;
      case "LogosTension":
        return `${t}  [logos]  dia=${s.division.toFixed(2)}  sun=${s.union.toFixed(2)}  frac=${s.fracture.toFixed(2)}`;
      default:
        return `${t}  [${s.type}]`;
    }
  }

  function appendTrace(sig) {
    const li = document.createElement("li");
    const baseClass = sig.is_absence ? "absence" : sig.type;
    li.className = `t-${baseClass.toLowerCase()}`;
    li.textContent = renderLine(sig);
    traceList.appendChild(li);
    while (traceList.children.length > 80) {
      traceList.removeChild(traceList.firstChild);
    }
    traceList.scrollTop = traceList.scrollHeight;
  }

  function applySnapshot(snap) {
    if (!snap || !snap.lifecycle) return;
    vitalAge.textContent = `${(snap.lifecycle.age_s ?? 0).toFixed(1)}s`;
    if (snap.lifecycle.alive) {
      vitalAlive.textContent = "alive";
      vitalAlive.className = "alive";
    } else {
      vitalAlive.textContent = "dead";
      vitalAlive.className = "dead";
    }
    if (snap.modules) {
      vitalCount.textContent = `${Object.keys(snap.modules).length} modules`;
      for (const [name, st] of Object.entries(snap.modules)) {
        const card = document.getElementById(`state-${name}`);
        if (!card) continue;
        const kv = card.querySelector(".kv");
        kv.innerHTML = formatStateInline(st);
      }
    }
  }

  function formatStateInline(st) {
    const parts = [];
    for (const [k, v] of Object.entries(st)) {
      if (k === "name") continue;
      parts.push(
        `<span class="k">${k}</span> <span class="v">${formatValue(v)}</span>`,
      );
    }
    return parts.join("&nbsp;·&nbsp;") || "—";
  }

  function formatValue(v) {
    if (typeof v === "number") {
      if (!Number.isFinite(v)) return String(v);
      if (Number.isInteger(v)) return String(v);
      return v.toFixed(Math.abs(v) >= 1 ? 2 : 3);
    }
    if (typeof v === "object" && v !== null) return formatJSON(v);
    return String(v);
  }

  function formatJSON(v) {
    try {
      return JSON.stringify(v);
    } catch {
      return String(v);
    }
  }

  function startSSE() {
    const evt = new EventSource("/events");
    evt.onmessage = (e) => {
      try {
        const env = JSON.parse(e.data);
        if (env.event === "signal") pulse(env.data);
        else if (env.event === "snapshot") applySnapshot(env.data);
      } catch (err) {
        console.error("event parse failed", err, e.data);
      }
    };
    evt.onerror = () => {
      vitalAlive.textContent = "disconnected";
      vitalAlive.className = "dead";
    };
  }

  function attachControls() {
    vitalAge    = document.getElementById("vital-age");
    vitalAlive  = document.getElementById("vital-alive");
    vitalCount  = document.getElementById("vital-count");
    vitalEvents = document.getElementById("vital-events");
    traceList   = document.getElementById("trace-log");

    document.getElementById("stim-form")
      .addEventListener("submit", async (e) => {
        e.preventDefault();
        const payload  = document.getElementById("payload").value || "ping";
        const modality = document.getElementById("modality").value || "external";
        const intensity = parseFloat(
          document.getElementById("intensity").value || "0.7",
        );
        const r = await fetch("/stimulate", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ payload, modality, intensity }),
        });
        if (!r.ok) systemMessage(`stimulate failed: ${r.status}`);
      });

    document.getElementById("react-pos").addEventListener("click", () => react( 0.7));
    document.getElementById("react-neg").addEventListener("click", () => react(-0.8));

    document.getElementById("die").addEventListener("click", async () => {
      if (!confirm("Trigger Lifecycle.die? The Conscience will stop.")) return;
      await fetch("/die", { method: "POST" });
    });
  }

  async function react(valence) {
    const r = await fetch("/react", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ valence }),
    });
    const data = await r.json().catch(() => ({}));
    if (!data.ok) systemMessage(`react: ${data.error || "failed"}`);
  }

  function systemMessage(msg) {
    const li = document.createElement("li");
    li.className = "t-system";
    li.textContent = `--- ${msg} ---`;
    traceList.appendChild(li);
    traceList.scrollTop = traceList.scrollHeight;
  }

  async function init() {
    const resp = await fetch("/topology");
    topology = await resp.json();
    attachControls();
    buildGraph();
    buildStateCards();
    startSSE();
  }

  window.addEventListener("DOMContentLoaded", init);
})();
