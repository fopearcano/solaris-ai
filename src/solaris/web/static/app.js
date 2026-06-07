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

  // The function each connection carries, by signal type — used to
  // tag the wires.
  const SIGNAL_FN = {
    Stimulus:     "senses",
    Push:         "drive",
    Desire:       "intends",
    Action:       "acts",
    Reaction:     "feedback",
    MeaningEvent: "means",
    MapUpdate:    "writes-self",
    LogosTension: "tension",
  };

  // Approx node radius per role — used to seat the activity LEDs
  // just outside the node, where a wire enters.
  const NODE_R = {
    core: 60, decision: 46, perception: 40, self: 36, adapt: 40, env: 30,
  };
  function nodeRadius(role) { return NODE_R[role] || 38; }

  // Map a signal to a logical polarity: -1 false / 0 neutral / +1 true.
  // (Grounded in the system's own semantics — see CONCEPTS.md.)
  function signalPolarity(sig) {
    switch (sig.type) {
      case "Reaction":
        return sig.valence > 0.1 ? 1 : (sig.valence < -0.1 ? -1 : 0);
      case "LogosTension": {
        // dia-ballein (presence/rational) = true, sun-ballein = false.
        const d = sig.division || 0, u = sig.union || 0;
        return d > u * 1.1 ? 1 : (u > d * 1.1 ? -1 : 0);
      }
      case "MeaningEvent":
        // known meaning = true, highly novel (unknown) = false.
        return sig.novelty < 0.34 ? 1 : (sig.novelty > 0.66 ? -1 : 0);
      case "Desire":
        return sig.confidence > 0.6 ? 1 : (sig.confidence < 0.4 ? -1 : 0);
      case "Action":    return 1;
      case "Push":      return sig.direction === "reactive" ? 1 : 0;
      case "Stimulus":  return sig.is_absence ? -1 : 0;
      case "MapUpdate": return sig.boundary ? 1 : 0;
      default:          return 0;
    }
  }

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

  // Wires + sub-module panels.
  let lastSnap = null;
  let edgeDrag = null;
  let showWires = false;
  const edgeList = [];
  const expanded = new Set();
  const propPanels = {};

  // Top-centre resource stats. `def` = shown by default; the rest
  // are selectable from the dropdown. fmt() -> string, or null when
  // the metric is unavailable on this host.
  const METRICS = [
    { id: "cpu",     label: "CPU",  def: true,
      fmt: (r) => r.cpu  ? `${r.cpu.pct}%` : null,
      tip: (r) => r.cpu  ? `process CPU · ${r.cpu.per_core}% of ${r.cpu.cores} cores` : "" },
    { id: "ram",     label: "RAM",  def: true,
      fmt: (r) => r.ram  ? `${r.ram.mb}MB` : null,
      tip: (r) => r.ram && r.ram.pct != null ? `${r.ram.pct}% of system RAM` : "resident memory" },
    { id: "gpu",     label: "GPU",  def: true,
      fmt: (r) => r.gpu  ? `${r.gpu.pct}%` : null,
      tip: (r) => r.gpu  ? `${r.gpu.mem_mb}MB GPU memory` : "no NVIDIA GPU detected" },
    { id: "net",     label: "NET",  def: true,
      fmt: (r) => r.net  ? `↓${r.net.down_kbps} ↑${r.net.up_kbps}` : null,
      tip: () => "network KB/s (system)" },
    { id: "disk",    label: "DISK", def: false,
      fmt: (r) => r.disk ? `↓${r.disk.read_kbps} ↑${r.disk.write_kbps}` : null,
      tip: () => "disk I/O KB/s (process)" },
    { id: "threads", label: "THR",  def: false,
      fmt: (r) => r.threads != null ? `${r.threads}` : null,
      tip: () => "OS threads" },
    { id: "fds",     label: "FD",   def: false,
      fmt: (r) => r.fds != null ? `${r.fds}` : null,
      tip: () => "open file descriptors" },
    { id: "load",    label: "LOAD", def: false,
      fmt: (r) => r.load ? `${r.load["1"]}` : null,
      tip: (r) => r.load ? `load avg 1/5/15: ${r.load["1"]} ${r.load["5"]} ${r.load["15"]}` : "" },
  ];
  let lastResources = {};
  let selectedStats = null;
  let statsChips, statsMenu, statsMenuBtn;

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

    // Edges: orthogonal runs with rounded corners. Each wire is
    // grabbable (drag the handle to re-route) and tagged with the
    // function (signal type) it carries.
    topology.edges.forEach((e, ei) => {
      const a = nodeById[e.from];
      const b = nodeById[e.to];
      if (!a || !b) return;

      e.a = a; e.b = b;
      const spread = ((ei % 7) - 3) * 12;
      e.pivot = { x: (a.x + b.x) / 2 + spread, y: (a.y + b.y) / 2 };

      const group  = svgEl("g", { class: "edge-group", "data-via": e.via });
      const hit    = svgEl("path", { class: "edge-hit" });
      const path   = svgEl("path", {
        class: `edge via-${e.via}`,
        "data-from": e.from, "data-to": e.to, "data-via": e.via,
      });
      const handle = svgEl("circle", { r: 4.5, class: "edge-handle" });
      const tag    = svgEl("text", { class: "edge-tag", "text-anchor": "middle" });
      const fn = SIGNAL_FN[e.via];
      tag.textContent = fn ? `${e.via} · ${fn}` : e.via;

      // Router-style activity LEDs at the node entry:
      // red / amber / green = false / neutral / true.
      const led  = svgEl("g", { class: "edge-led" });
      const ledF = svgEl("circle", { r: 2.3, cy: -5.5, class: "led led-false" });
      const ledN = svgEl("circle", { r: 2.3, cy:  0,   class: "led led-neutral" });
      const ledT = svgEl("circle", { r: 2.3, cy:  5.5, class: "led led-true" });
      led.append(ledF, ledN, ledT);

      group.append(hit, path, led, handle, tag);
      viewport.appendChild(group);

      e.group = group; e.elem = path; e.hit = hit; e.handle = handle; e.tag = tag;
      e.led = led;
      e.ledEls = { "-1": ledF, "0": ledN, "1": ledT };
      edgeList.push(e);
      renderEdge(e);

      hit.addEventListener("mousedown", (ev) => startEdgeDrag(ev, e));
      handle.addEventListener("mousedown", (ev) => startEdgeDrag(ev, e));

      const key = `${e.from}|${e.via}`;
      (edgeIndex[key] ||= []).push(e);
    });

    // Nodes. Click a node to open/close its sub-module property panel.
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

      if (m.id !== "environment") {
        g.classList.add("clickable");
        g.addEventListener("click", (ev) => {
          ev.stopPropagation();
          toggleProps(m);
        });
      }

      viewport.appendChild(g);
      m.elem = g;
    }
  }

  // ---- wires: render, drag, function tags ----------------------------

  function renderEdge(e) {
    const { a, b, pivot: p } = e;
    // Four orthogonal segments routed through the draggable pivot.
    const pts = [
      { x: a.x, y: a.y },
      { x: a.x, y: p.y },
      { x: p.x, y: p.y },
      { x: p.x, y: b.y },
      { x: b.x, y: b.y },
    ];
    const d = roundedPath(pts, 10);
    e.elem.setAttribute("d", d);
    e.hit.setAttribute("d", d);
    e.handle.setAttribute("cx", p.x);
    e.handle.setAttribute("cy", p.y);
    e.tag.setAttribute("x", p.x);
    e.tag.setAttribute("y", p.y - 8);

    // Seat the LED cluster just outside the target node, on the
    // incoming segment (which arrives at b from the pivot).
    let dx = b.x - p.x, dy = 0;            // final segment (p.x,b.y) -> b
    if (Math.abs(dx) < 1) { dx = b.x - p.x; dy = b.y - p.y; }
    const L = Math.hypot(dx, dy) || 1;
    const off = nodeRadius(b.role) + 9;
    const ex = b.x - (dx / L) * off;
    const ey = b.y - (dy / L) * off;
    e.led.setAttribute("transform", `translate(${ex.toFixed(1)},${ey.toFixed(1)})`);
  }

  function startEdgeDrag(ev, e) {
    ev.preventDefault();
    ev.stopPropagation();
    edgeDrag = e;
    e.group.classList.add("dragging");
    svg.classList.add("wiring");
  }

  function edgeDragMove(ev) {
    if (!edgeDrag) return;
    const s = screenToSvg(ev.clientX, ev.clientY);
    edgeDrag.pivot = { x: (s.x - pan.x) / zoom, y: (s.y - pan.y) / zoom };
    renderEdge(edgeDrag);
  }

  function endEdgeDrag() {
    if (!edgeDrag) return;
    edgeDrag.group.classList.remove("dragging");
    edgeDrag = null;
    svg.classList.remove("wiring");
  }

  // ---- node sub-module property panels -------------------------------

  function toggleProps(m) {
    if (expanded.has(m.id)) {
      expanded.delete(m.id);
      m.elem.classList.remove("expanded");
      const pg = propPanels[m.id];
      if (pg) { pg.remove(); delete propPanels[m.id]; }
    } else {
      expanded.add(m.id);
      m.elem.classList.add("expanded");
      renderProps(m);
    }
  }

  function renderProps(m) {
    const st = lastSnap && lastSnap.modules ? lastSnap.modules[m.id] : null;
    let pg = propPanels[m.id];
    if (!pg) {
      pg = svgEl("g", { class: "prop-panel" });
      viewport.appendChild(pg);
      propPanels[m.id] = pg;
    }
    while (pg.firstChild) pg.removeChild(pg.firstChild);

    const entries = st
      ? Object.entries(st).filter(([k]) => k !== "name")
      : [];
    const w = 178, rowH = 16, headH = 20;
    const h = headH + Math.max(1, entries.length) * rowH + 8;
    let px = m.x + 58;
    let py = m.y - h / 2;
    if (px + w > 1500) px = m.x - 58 - w;   // flip left near right edge
    if (py < 4) py = 4;
    pg.setAttribute("transform", `translate(${px.toFixed(1)},${py.toFixed(1)})`);

    pg.appendChild(svgEl("rect", { x: 0, y: 0, width: w, height: h, rx: 4, class: "prop-box" }));
    const head = svgEl("rect", { x: 0, y: 0, width: w, height: headH, class: "prop-head" });
    head.setAttribute("style", `fill:${ROLE_COLORS[m.role] || "#888"}`);
    pg.appendChild(head);
    const title = svgEl("text", { x: 9, y: 14, class: "prop-title" });
    title.textContent = `${m.label} · SUB-MODULES`;
    pg.appendChild(title);

    if (!entries.length) {
      const t = svgEl("text", { x: 9, y: headH + 16, class: "prop-row-v" });
      t.textContent = "— no telemetry —";
      pg.appendChild(t);
      return;
    }
    entries.forEach(([k, v], i) => {
      const ry = headH + 14 + i * rowH;
      const tick = svgEl("rect", { x: 9, y: ry - 8, width: 6, height: 6, class: "prop-tick" });
      tick.setAttribute("style", `fill:${ROLE_COLORS[m.role] || "#888"}`);
      pg.appendChild(tick);
      const tk = svgEl("text", { x: 22, y: ry, class: "prop-row-k" });
      tk.textContent = k;
      pg.appendChild(tk);
      const tv = svgEl("text", { x: w - 9, y: ry, "text-anchor": "end", class: "prop-row-v" });
      tv.textContent = formatValue(v);
      pg.appendChild(tv);
    });
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

    const tw = document.getElementById("toggle-wires");
    if (tw) tw.addEventListener("click", () => {
      showWires = !showWires;
      svg.classList.toggle("show-wires", showWires);
      tw.classList.toggle("on", showWires);
    });

    // Mouse-wheel zoom, centered on cursor.
    svg.addEventListener("wheel", (e) => {
      e.preventDefault();
      const p = screenToSvg(e.clientX, e.clientY);
      const factor = e.deltaY < 0 ? 1.15 : 1 / 1.15;
      zoomAt(p.x, p.y, factor);
    }, { passive: false });

    // Click-and-drag to pan (background only — not nodes or wires).
    svg.addEventListener("mousedown", (e) => {
      if (e.target.closest(".node") || e.target.closest(".edge-group")) return;
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

    // Wire dragging.
    window.addEventListener("mousemove", edgeDragMove);
    window.addEventListener("mouseup", endEdgeDrag);

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
    const pol = String(signalPolarity(sig));
    if (edges) {
      for (const e of edges) {
        // Hold the active state long enough that the slow CSS
        // transition reads as one gentle fade up-and-down, not a
        // blink. Tags are NOT touched here, so they never blink.
        e.elem.classList.add("active");
        if (e._timer) clearTimeout(e._timer);
        e._timer = setTimeout(() => e.elem.classList.remove("active"), 620);

        // Quick, router-style blink of the activity LED whose
        // polarity matches this signal (false / neutral / true).
        const lit = e.ledEls && e.ledEls[pol];
        if (lit) {
          lit.classList.add("on");
          if (lit._t) clearTimeout(lit._t);
          lit._t = setTimeout(() => lit.classList.remove("on"), 150);
        }
      }
    }
    const node = nodeById[sig.origin];
    if (node && node.elem) {
      node.elem.classList.add("flashing");
      if (node._timer) clearTimeout(node._timer);
      node._timer = setTimeout(
        () => node.elem.classList.remove("flashing"),
        680,
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
    // Real-time resource stats in the HUD top bar.
    if (snap.resources) {
      lastResources = snap.resources;
      renderStats();
    }
    // Keep any open sub-module panels current.
    lastSnap = snap;
    for (const id of expanded) {
      const m = nodeById[id];
      if (m) renderProps(m);
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

  // ---- top-centre resource stats -------------------------------------

  function renderStats() {
    if (!statsChips) return;
    statsChips.textContent = "";
    for (const m of METRICS) {
      if (!selectedStats.has(m.id)) continue;
      const v = m.fmt(lastResources);
      const chip = document.createElement("span");
      chip.className = "stat";
      chip.title = (m.tip && m.tip(lastResources)) || m.label;
      const k = document.createElement("i");
      k.className = "stat-k";
      k.textContent = m.label;
      const val = document.createElement("b");
      val.className = "stat-v" + (v == null ? " dim" : "");
      val.textContent = v == null ? "—" : v;
      chip.append(k, val);
      statsChips.appendChild(chip);
    }
  }

  function attachStats() {
    statsChips   = document.getElementById("stats-chips");
    statsMenu    = document.getElementById("stats-menu");
    statsMenuBtn = document.getElementById("stats-menu-btn");

    let saved = null;
    try { saved = JSON.parse(localStorage.getItem("solaris.stats") || "null"); } catch {}
    selectedStats = new Set(
      Array.isArray(saved) && saved.length
        ? saved
        : METRICS.filter((m) => m.def).map((m) => m.id),
    );

    const title = document.createElement("div");
    title.className = "stats-menu-title";
    title.textContent = "RESOURCES";
    statsMenu.appendChild(title);
    for (const m of METRICS) {
      const lab = document.createElement("label");
      const cb = document.createElement("input");
      cb.type = "checkbox";
      cb.checked = selectedStats.has(m.id);
      cb.addEventListener("change", () => {
        if (cb.checked) selectedStats.add(m.id);
        else selectedStats.delete(m.id);
        try {
          localStorage.setItem("solaris.stats", JSON.stringify([...selectedStats]));
        } catch {}
        renderStats();
      });
      const span = document.createElement("span");
      span.textContent = m.label;
      lab.append(cb, span);
      statsMenu.appendChild(lab);
    }

    statsMenuBtn.addEventListener("click", (e) => {
      e.stopPropagation();
      const open = !statsMenu.hasAttribute("hidden");
      if (open) {
        statsMenu.setAttribute("hidden", "");
        statsMenuBtn.classList.remove("on");
      } else {
        statsMenu.removeAttribute("hidden");
        statsMenuBtn.classList.add("on");
      }
    });
    document.addEventListener("click", (e) => {
      if (!statsMenu.contains(e.target) && e.target !== statsMenuBtn) {
        statsMenu.setAttribute("hidden", "");
        statsMenuBtn.classList.remove("on");
      }
    });
    renderStats();
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
    attachStats();
    buildGraph();
    attachZoom();
    buildStateCards();
    startTimecode();
    startSSE();
  }

  window.addEventListener("DOMContentLoaded", init);
})();
