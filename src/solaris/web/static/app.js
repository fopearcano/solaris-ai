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

  // NERV / MAGI terminal palette.
  const ROLE_COLORS = {
    core:       "#ff2316",  // reactor red
    perception: "#ffcc00",  // amber
    decision:   "#2e8bff",  // cobalt
    self:       "#ff7e29",  // orange
    adapt:      "#ff4d6d",  // rose
    env:        "#aeb8c2",  // steel
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
  let vitalAge, vitalAlive, vitalCount, vitalEvents, vitalSync, timecodeEl;
  let zoomLevelEl;
  let eventCount = 0;
  let bornAt = performance.now();

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

  function triPoints(r) {
    // Equilateral triangle pointing up, circumradius r.
    const p = [];
    for (let i = 0; i < 3; i++) {
      const a = ((-90 + i * 120) * Math.PI) / 180;
      p.push(`${(r * Math.cos(a)).toFixed(2)},${(r * Math.sin(a)).toFixed(2)}`);
    }
    return p.join(" ");
  }

  // ---- orthogonal ("manhattan") edge routing -------------------------
  // The MAGI / gene-map look: right-angle wire runs with rounded
  // corners, fanned out into a ribbon so parallel runs separate.

  function orthWaypoints(x1, y1, x2, y2, spread) {
    const dx = Math.abs(x2 - x1);
    const dy = Math.abs(y2 - y1);
    if (dx < 2 || dy < 2) return [{ x: x1, y: y1 }, { x: x2, y: y2 }];
    if (dy >= dx) {
      const my = (y1 + y2) / 2 + spread;
      return [{ x: x1, y: y1 }, { x: x1, y: my }, { x: x2, y: my }, { x: x2, y: y2 }];
    }
    const mx = (x1 + x2) / 2 + spread;
    return [{ x: x1, y: y1 }, { x: mx, y: y1 }, { x: mx, y: y2 }, { x: x2, y: y2 }];
  }

  function roundedPath(pts, r) {
    if (pts.length < 2) return "";
    if (pts.length === 2) {
      return `M ${pts[0].x} ${pts[0].y} L ${pts[1].x} ${pts[1].y}`;
    }
    let d = `M ${pts[0].x.toFixed(1)} ${pts[0].y.toFixed(1)}`;
    for (let i = 1; i < pts.length - 1; i++) {
      const p0 = pts[i - 1], p1 = pts[i], p2 = pts[i + 1];
      const len1 = Math.hypot(p1.x - p0.x, p1.y - p0.y) || 1;
      const len2 = Math.hypot(p2.x - p1.x, p2.y - p1.y) || 1;
      const rr = Math.min(r, len1 / 2, len2 / 2);
      const ax = p1.x - ((p1.x - p0.x) / len1) * rr;
      const ay = p1.y - ((p1.y - p0.y) / len1) * rr;
      const bx = p1.x + ((p2.x - p1.x) / len2) * rr;
      const by = p1.y + ((p2.y - p1.y) / len2) * rr;
      d += ` L ${ax.toFixed(1)} ${ay.toFixed(1)}`;
      d += ` Q ${p1.x.toFixed(1)} ${p1.y.toFixed(1)} ${bx.toFixed(1)} ${by.toFixed(1)}`;
    }
    const last = pts[pts.length - 1];
    d += ` L ${last.x.toFixed(1)} ${last.y.toFixed(1)}`;
    return d;
  }

  /** Concentric red rings + radial ticks behind the AION core (MAGI). */
  function buildCoreDecor(cx, cy) {
    const g = svgEl("g", { class: "core-decor" });
    // glow disc
    g.appendChild(svgEl("circle", { cx, cy, r: 150, class: "magi-glow" }));
    // concentric rings
    const rings = [
      { r: 40, o: 0.85 }, { r: 64, o: 0.6 }, { r: 90, o: 0.42 },
      { r: 118, o: 0.3 }, { r: 148, o: 0.2 },
    ];
    for (const { r, o } of rings) {
      g.appendChild(svgEl("circle", {
        cx, cy, r, class: "magi-ring",
        style: `opacity:${o}`,
      }));
    }
    // radial tick marks around the outer ring
    const ticks = 48;
    for (let i = 0; i < ticks; i++) {
      const a = (i / ticks) * 2 * Math.PI;
      const r0 = 120, r1 = i % 4 === 0 ? 146 : 138;
      g.appendChild(svgEl("line", {
        x1: (cx + r0 * Math.cos(a)).toFixed(1),
        y1: (cy + r0 * Math.sin(a)).toFixed(1),
        x2: (cx + r1 * Math.cos(a)).toFixed(1),
        y2: (cy + r1 * Math.sin(a)).toFixed(1),
        class: "magi-tick",
      }));
    }
    return g;
  }

  /** The MAGI reactor: glowing triangle + three radiating arm bars. */
  function buildMagiCore(g, label) {
    // three arm bars at 120°, behind the triangle
    for (let i = 0; i < 3; i++) {
      const ang = -90 + i * 120;
      const arm = svgEl("rect", {
        x: -7, y: -64, width: 14, height: 34, rx: 2,
        class: "magi-arm",
        transform: `rotate(${ang})`,
      });
      g.appendChild(arm);
    }
    // outer + inner triangle
    g.appendChild(svgEl("polygon", { points: triPoints(40), class: "node-shape magi-tri-outer" }));
    g.appendChild(svgEl("polygon", { points: triPoints(30), class: "magi-tri-inner" }));
    const t1 = svgEl("text", { y: -2, "text-anchor": "middle", class: "magi-label" });
    t1.textContent = "AION";
    g.appendChild(t1);
    const t2 = svgEl("text", { y: 11, "text-anchor": "middle", class: "magi-sub" });
    t2.textContent = "01";
    g.appendChild(t2);
    // descriptive label below the rings
    const t3 = svgEl("text", { y: 66, "text-anchor": "middle", class: "core-caption" });
    t3.textContent = label;
    g.appendChild(t3);
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

    // MAGI core decor (concentric rings) behind everything.
    const aion = nodeById["aion_impulse"];
    if (aion) viewport.appendChild(buildCoreDecor(aion.x, aion.y));

    // Edges: orthogonal runs with rounded corners, fanned into a
    // ribbon so parallel runs separate (MAGI / gene-map look).
    topology.edges.forEach((e, ei) => {
      const a = nodeById[e.from];
      const b = nodeById[e.to];
      if (!a || !b) return;

      const spread = ((ei % 7) - 3) * 7;
      const pts = orthWaypoints(a.x, a.y, b.x, b.y, spread);
      const path = svgEl("path", {
        d: roundedPath(pts, 12),
        class: `edge via-${e.via}`,
        "data-from": e.from,
        "data-to":   e.to,
        "data-via":  e.via,
      });
      viewport.appendChild(path);
      e.elem = path;

      const key = `${e.from}|${e.via}`;
      (edgeIndex[key] ||= []).push(e);
    });

    // Nodes.
    for (const m of topology.modules) {
      const g = svgEl("g", {
        class: `node role-${m.role}`,
        transform: `translate(${m.x},${m.y})`,
      });

      if (m.id === "aion_impulse") {
        buildMagiCore(g, m.label);
      } else {
        const shape = nodeShapeFor(m.role);
        // Dark "hardware package" fill with a glowing role-coloured edge.
        shape.setAttribute("fill", "rgba(10,7,7,0.92)");
        shape.setAttribute("stroke", ROLE_COLORS[m.role] || "#888");
        g.appendChild(shape);

        const label = svgEl("text", { y: 4, "text-anchor": "middle" });
        label.setAttribute("fill", ROLE_COLORS[m.role] || "#cfd6dd");
        label.textContent = m.label;
        g.appendChild(label);
      }

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
    vitalEvents.textContent = `${eventCount}`;

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
      vitalAlive.textContent = "ACTIVE";
      vitalAlive.className = "alive";
    } else {
      vitalAlive.textContent = "OFFLINE";
      vitalAlive.className = "dead";
    }
    if (snap.modules) {
      vitalCount.textContent = `${Object.keys(snap.modules).length}`;
      for (const [name, st] of Object.entries(snap.modules)) {
        const card = document.getElementById(`state-${name}`);
        if (!card) continue;
        const kv = card.querySelector(".kv");
        kv.innerHTML = formatStateInline(st);
      }
      // 'Synchronization rate' — read from Auto-Determination's
      // Being/Not-Being scalar, the system's self-agreement.
      const being = snap.modules?.auto_determination?.being;
      if (being != null && vitalSync) {
        vitalSync.textContent = `${(being * 100).toFixed(1)}%`;
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
      vitalAlive.textContent = "LINK LOST";
      vitalAlive.className = "dead";
    };
  }

  function startTimecode() {
    const tick = () => {
      const elapsed = (performance.now() - bornAt) / 1000;
      const hh = String(Math.floor(elapsed / 3600)).padStart(2, "0");
      const mm = String(Math.floor((elapsed % 3600) / 60)).padStart(2, "0");
      const ss = String(Math.floor(elapsed % 60)).padStart(2, "0");
      if (timecodeEl) timecodeEl.textContent = `${hh}:${mm}:${ss}`;
    };
    tick();
    setInterval(tick, 1000);
  }

  function attachControls() {
    vitalAge    = document.getElementById("vital-age");
    vitalAlive  = document.getElementById("vital-alive");
    vitalCount  = document.getElementById("vital-count");
    vitalEvents = document.getElementById("vital-events");
    vitalSync   = document.getElementById("vital-sync");
    timecodeEl  = document.getElementById("timecode");
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
    startTimecode();
    startSSE();
  }

  window.addEventListener("DOMContentLoaded", init);
})();
