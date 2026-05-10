/* Solaris_Ai — Conscience UI front-end.
 *
 * Fetches the static topology, renders the module graph as SVG
 * (with role-specific shapes), subscribes to /events (SSE), and
 * pulses edges as signals fire. Snapshots refresh the state panel;
 * controls post to the server to inject Stimuli, Reactions, or
 * trigger Lifecycle.die.
 *
 * The graph contents are wrapped in a <g id="viewport"> so we can
 * apply a single 2D transform for zoom + pan.
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

  // Zoom limits.
  const MIN_ZOOM = 0.3;
  const MAX_ZOOM = 3.0;

  let topology = null;
  const nodeById = {};
  const edgeIndex = {}; // "origin|Type" -> [edgeRef]

  let svg, viewport, traceList, stateEl;
  let vitalAge, vitalAlive, vitalCount, vitalEvents;
  let zoomLevelEl;
  let eventCount = 0;

  // Zoom + pan state (in SVG-viewBox units).
  let zoom = 1;
  let pan = { x: 0, y: 0 };
  let isPanning = false;
  let panStart = null;

  // ---- helpers --------------------------------------------------------

  function svgEl(name, attrs = {}) {
    const e = document.createElementNS(NS, name);
    for (const [k, v] of Object.entries(attrs)) {
      if (v != null) e.setAttribute(k, String(v));
    }
    return e;
  }

  function nodeXY(m) {
    return {
      x: m.col * COL_W + X_OFFSET,
      y: (m.row + 1) * ROW_H + Y_OFFSET,
    };
  }

  function hexPoints(r, pointyTop) {
    const pts = [];
    const phaseDeg = pointyTop ? 90 : 0;
    for (let i = 0; i < 6; i++) {
      const a = ((phaseDeg + i * 60) * Math.PI) / 180;
      pts.push(`${(r * Math.cos(a)).toFixed(2)},${(r * Math.sin(a)).toFixed(2)}`);
    }
    return pts.join(" ");
  }

  /** Build the SVG element that represents a node, sized + shaped by role. */
  function nodeShapeFor(role) {
    switch (role) {
      case "core": {
        // Bigger, distinctive — the heart of the system.
        const r = 54;
        return svgEl("polygon", {
          points: hexPoints(r, true),
          class: "node-shape hex-pointy",
        });
      }
      case "self": {
        const r = 32;
        return svgEl("rect", {
          x: -r, y: -r, width: 2 * r, height: 2 * r, rx: 6, ry: 6,
          class: "node-shape rounded-rect",
        });
      }
      case "decision": {
        const r = 42;
        return svgEl("polygon", {
          points: `0,${-r} ${r},0 0,${r} ${-r},0`,
          class: "node-shape diamond",
        });
      }
      case "adapt": {
        const r = 38;
        return svgEl("polygon", {
          points: hexPoints(r, false),
          class: "node-shape hex-flat",
        });
      }
      case "env": {
        const w = 130, h = 46;
        return svgEl("rect", {
          x: -w / 2, y: -h / 2, width: w, height: h, rx: 8, ry: 8,
          class: "node-shape env-rect",
        });
      }
      case "perception":
      default: {
        const r = 36;
        return svgEl("circle", { r, class: "node-shape circle" });
      }
    }
  }

  // ---- graph build ----------------------------------------------------

  function buildGraph() {
    svg = document.getElementById("graph");

    // Wrap all graph contents in a viewport <g> so a single transform
    // does both zoom and pan.
    viewport = svgEl("g", { id: "viewport" });
    svg.appendChild(viewport);

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
      const curveSign = (a.row > b.row || (a.row === b.row && a.col > b.col)) ? 1 : -1;
      const off = 22 * curveSign;
      const cx = mx - (dy / len) * off;
      const cy = my + (dx / len) * off;

      const path = svgEl("path", {
        d: `M ${a.x} ${a.y} Q ${cx} ${cy} ${b.x} ${b.y}`,
        class: `edge via-${e.via}`,
        "data-from": e.from,
        "data-to":   e.to,
        "data-via":  e.via,
      });
      viewport.appendChild(path);
      e.elem = path;

      const key = `${e.from}|${e.via}`;
      (edgeIndex[key] ||= []).push(e);
    }

    // Nodes.
    for (const m of topology.modules) {
      const g = svgEl("g", {
        class: `node role-${m.role}`,
        transform: `translate(${m.x},${m.y})`,
      });

      const shape = nodeShapeFor(m.role);
      shape.setAttribute("fill", ROLE_COLORS[m.role] || "#888");
      g.appendChild(shape);

      const label = svgEl("text", { y: 4, "text-anchor": "middle" });
      label.textContent = m.label;
      g.appendChild(label);

      viewport.appendChild(g);
      m.elem = g;
    }
  }

  // ---- zoom + pan -----------------------------------------------------

  function applyTransform() {
    viewport.setAttribute(
      "transform",
      `translate(${pan.x.toFixed(2)},${pan.y.toFixed(2)}) scale(${zoom.toFixed(4)})`,
    );
    if (zoomLevelEl) zoomLevelEl.textContent = `${Math.round(zoom * 100)}%`;
  }

  /**
   * Convert a screen-coordinate (clientX, clientY) to a coordinate
   * inside the SVG viewBox.
   */
  function screenToSvg(clientX, clientY) {
    const rect = svg.getBoundingClientRect();
    const vb = svg.viewBox.baseVal;
    return {
      x: ((clientX - rect.left) / rect.width)  * vb.width,
      y: ((clientY - rect.top)  / rect.height) * vb.height,
    };
  }

  /** Zoom by `factor` keeping the SVG-coord point (sx, sy) fixed under cursor. */
  function zoomAt(sx, sy, factor) {
    const newZoom = Math.max(MIN_ZOOM, Math.min(MAX_ZOOM, zoom * factor));
    const ratio = newZoom / zoom;
    pan.x = sx - ratio * (sx - pan.x);
    pan.y = sy - ratio * (sy - pan.y);
    zoom = newZoom;
    applyTransform();
  }

  function resetView() {
    zoom = 1;
    pan = { x: 0, y: 0 };
    applyTransform();
  }

  function attachZoom() {
    zoomLevelEl = document.getElementById("zoom-level");

    document.getElementById("zoom-in").addEventListener("click", () => {
      const vb = svg.viewBox.baseVal;
      zoomAt(vb.width / 2, vb.height / 2, 1.2);
    });
    document.getElementById("zoom-out").addEventListener("click", () => {
      const vb = svg.viewBox.baseVal;
      zoomAt(vb.width / 2, vb.height / 2, 1 / 1.2);
    });
    document.getElementById("zoom-reset").addEventListener("click", resetView);

    // Mouse-wheel zoom, centered on cursor.
    svg.addEventListener("wheel", (e) => {
      e.preventDefault();
      const p = screenToSvg(e.clientX, e.clientY);
      const factor = e.deltaY < 0 ? 1.15 : 1 / 1.15;
      zoomAt(p.x, p.y, factor);
    }, { passive: false });

    // Click-and-drag to pan (background only, not nodes).
    svg.addEventListener("mousedown", (e) => {
      if (e.target.closest(".node")) return;
      e.preventDefault();
      isPanning = true;
      panStart = {
        clientX: e.clientX,
        clientY: e.clientY,
        panX: pan.x,
        panY: pan.y,
      };
      svg.classList.add("panning");
    });
    window.addEventListener("mousemove", (e) => {
      if (!isPanning) return;
      const rect = svg.getBoundingClientRect();
      const vb = svg.viewBox.baseVal;
      const sx = vb.width  / rect.width;
      const sy = vb.height / rect.height;
      pan.x = panStart.panX + (e.clientX - panStart.clientX) * sx;
      pan.y = panStart.panY + (e.clientY - panStart.clientY) * sy;
      applyTransform();
    });
    window.addEventListener("mouseup", () => {
      if (isPanning) {
        isPanning = false;
        svg.classList.remove("panning");
      }
    });

    // Keyboard shortcuts: + / - / 0
    window.addEventListener("keydown", (e) => {
      if (e.target.matches("input, textarea")) return;
      if (e.key === "+" || e.key === "=") {
        const vb = svg.viewBox.baseVal;
        zoomAt(vb.width / 2, vb.height / 2, 1.2);
      } else if (e.key === "-" || e.key === "_") {
        const vb = svg.viewBox.baseVal;
        zoomAt(vb.width / 2, vb.height / 2, 1 / 1.2);
      } else if (e.key === "0") {
        resetView();
      }
    });
  }

  // ---- live updates ---------------------------------------------------

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
    attachZoom();
    buildStateCards();
    startSSE();
  }

  window.addEventListener("DOMContentLoaded", init);
})();
