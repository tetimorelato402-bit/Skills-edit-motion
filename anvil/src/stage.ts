/**
 * ANVIL — the stage. Builds the DOM once, then maps a time to a picture.
 * It owns no timing of its own: everything it does is a function of t and
 * the tracks in timeline.ts.
 */
import {
  ease, progress, settleIn, revealUp, crossDepth, focusPush, apertureOpen, recede,
  cameraTransform, layerTransform, lerp, drift, focusMask, lerpFocus,
  REST, HIDDEN, CAMERA_REST, FOCUS_REST,
  type LayerState, type CameraState, type FocusState,
} from "./motion.js";
import { LAYERS, FORMATS, type Format, type Track, type ElState } from "./timeline.js";
import { SCREENS } from "../build/screens.js";

const EL_REST: ElState = { opacity: 1, x: 0, y: 0, scale: 1 };
const PHONE_W = 430, PHONE_H = 932, RADIUS = 44;

export interface Frame {
  layers: Record<string, LayerState>;
  els: Record<string, ElState>;
  clips: Record<string, string>;
  /** clip-paths on tagged elements — the stepped character reveals */
  elClips: Record<string, string>;
  camera: CameraState;
  focus: FocusState;
  t: number;
}

/* ------------------------------------------------------------- evaluation */

export function evaluate(tracks: Track[], t: number): Frame {
  const layers: Record<string, LayerState> = {};
  for (const id of Object.keys(LAYERS)) layers[id] = { ...HIDDEN };
  const els: Record<string, ElState> = {};
  for (const tr of tracks) {
    if (tr.k === "el" && !(tr.id in els)) els[tr.id] = { ...EL_REST, ...tr.from };
    if (tr.k === "stagger")
      for (const id of tr.ids) if (!(id in els)) els[id] = { ...EL_REST, ...tr.from };
  }
  const clips: Record<string, string> = {};
  // typed values are hidden until their reveal opens — seeded, not defaulted,
  // so a field never flashes its finished value before the typing starts
  const elClips: Record<string, string> = {};
  for (const tr of tracks)
    if (tr.k === "type") elClips[tr.id] = "inset(0 100% 0 0)";

  /**
   * Camera and focus are chained by DECLARATION, not by the clock: each move
   * starts from the previous move's declared target. Advancing the chain on
   * `p >= 1` looks equivalent and is not — when one move ends exactly where
   * the next begins, `(13.48 − 13.204) / 0.276` comes out as 0.9999999999999993,
   * the chain never advances, and the next move starts from a stale position.
   * That produced a one-frame snap backwards in the middle of the unlock.
   */
  let camera: CameraState = { ...CAMERA_REST };
  {
    let from: CameraState = { ...CAMERA_REST };
    for (const tr of tracks.filter((x) => x.k === "cam").sort((a, b) => a.at - b.at)) {
      const to: CameraState = { fx: tr.to.fx, fy: tr.to.fy, scale: tr.to.scale, center: tr.to.center };
      if (t >= tr.at) camera = focusPush(progress(t, tr.at, tr.dur), from, to);
      from = to;
    }
  }

  let focus: FocusState = { ...FOCUS_REST };
  {
    let from: FocusState = { ...FOCUS_REST };
    for (const tr of tracks.filter((x) => x.k === "focus").sort((a, b) => a.at - b.at)) {
      const to: FocusState = { ...from, ...tr.to };
      if (t >= tr.at) focus = lerpFocus(from, to, progress(t, tr.at, tr.dur));
      from = to;
    }
  }

  for (const tr of [...tracks].sort((a, b) => a.at - b.at)) {
    if (tr.k === "stagger") {
      const step = tr.step ?? 0.08;
      tr.ids.forEach((id, i) => {
        const q = ease(progress(t, tr.at + i * step, tr.dur));
        const from = { ...EL_REST, ...tr.from };
        const to = { ...from, ...tr.to };
        els[id] = { opacity: lerp(from.opacity, to.opacity, q), x: lerp(from.x, to.x, q),
                    y: lerp(from.y, to.y, q), scale: lerp(from.scale, to.scale, q) };
      });
      continue;
    }
    if (t < tr.at) continue;
    const p = progress(t, tr.at, tr.dur);

    switch (tr.k) {
      case "type": {
        // stepped, not eased: characters arrive whole, the way typing does
        const n = Math.min(tr.chars, Math.floor(p * tr.chars + 1e-6));
        const frac = n / tr.chars;
        elClips[tr.id] = frac >= 1 ? "none"
          : `inset(0 ${(100 * (1 - frac)).toFixed(2)}% 0 0)`;
        break;
      }

      case "el": {
        const e = ease(p);
        const from = { ...(els[tr.id] ?? EL_REST), ...tr.from };
        const to = { ...from, ...tr.to };
        els[tr.id] = { opacity: lerp(from.opacity, to.opacity, e), x: lerp(from.x, to.x, e),
                       y: lerp(from.y, to.y, e), scale: lerp(from.scale, to.scale, e) };
        break;
      }
      case "layer":
        layers[tr.id] = p >= 1 ? { ...REST } : {
          ...REST,
          ...(tr.via === "settleIn" ? settleIn(p) : revealUp(p, tr.opts)),
        };
        break;

      case "cross": {
        const c = crossDepth(p, { depth: tr.depth, aperture: !!tr.aperture });
        layers[tr.out] = p >= 1 ? { ...HIDDEN } : { ...REST, ...c.out };
        layers[tr.in] = p >= 1 ? { ...REST } : { ...REST, ...c.in };
        // the incoming screen arrives FROM somewhere: it carries momentum
        // through the cut instead of materialising in its final position
        if (tr.travel && p < 1) layers[tr.in].y = lerp(tr.travel, 0, ease(p));
        if (tr.travel && p < 1) layers[tr.out].y = lerp(0, -tr.travel * 0.45, ease(p));
        if (tr.aperture && p < 1) {
          const r = apertureOpen(p, tr.aperture.radius);
          clips[tr.in] = `circle(${r.toFixed(2)}px at ${tr.aperture.x}px ${tr.aperture.y}px)`;
        } else if (tr.aperture) delete clips[tr.in];
        break;
      }

      case "exit":
        layers[tr.id] = p >= 1 ? { ...HIDDEN }
                               : { ...REST, ...recede(p, { depth: tr.depth }) };
        break;

      case "cam":
      case "focus":
        break;   // resolved above, as a chain

      case "hold":
      case "sfx":
        break;
    }
  }
  return { layers, els, clips, elClips, camera, focus, t };
}

/* ----------------------------------------------------------------- the DOM */

let bandCache: { node: HTMLElement; depth: number; phase: number }[] = [];

export function build(root: HTMLElement, format: Format = "vertical") {
  const F = FORMATS[format];
  root.innerHTML = "";
  root.className = "stage";
  root.style.width = `${F.width}px`;
  root.style.height = `${F.height}px`;

  const forge = document.createElement("div");
  forge.className = "forge";
  root.append(forge);

  const wrap = document.createElement("div");
  wrap.className = "phoneWrap";
  wrap.style.transform = `translate(-50%, -50%) scale(${F.phoneScale})`;
  const cam = document.createElement("div");
  cam.className = "camera";
  cam.dataset.el = "camera";
  wrap.append(cam);
  root.append(wrap);

  const stageSpace = document.createElement("div");
  stageSpace.className = "stageSpace";
  stageSpace.style.width = `${F.width}px`;
  stageSpace.style.height = `${F.height}px`;
  root.append(stageSpace);

  const svgOf = (key: string) => {
    const host = document.createElement("div");
    host.className = "part";
    host.innerHTML = SCREENS[key];
    const svg = host.querySelector("svg")!;
    svg.removeAttribute("width");
    svg.removeAttribute("height");
    return host;
  };

  for (const [id, def] of Object.entries(LAYERS)) {
    const layer = document.createElement("div");
    layer.className = "layer" + (def.space === "stage" ? " stageLayer" : "")
                    + (def.box ? " boxed" : "");
    layer.dataset.layer = id;
    if (def.box) {
      layer.style.left = `${def.box.x}px`; layer.style.top = `${def.box.y}px`;
      layer.style.width = `${def.box.w}px`; layer.style.height = `${def.box.h}px`;
    }

    if (def.space === "phone") {
      // two copies: one soft, one sharp and masked to wherever the eye is
      // being sent. Both carry the same bands, so drift stays in register.
      const blur = document.createElement("div");
      blur.className = "dof dofBlur";
      const sharp = document.createElement("div");
      sharp.className = "dof dofSharp";
      for (const key of def.screens) { blur.append(svgOf(key)); sharp.append(svgOf(key)); }
      layer.append(blur, sharp);
    } else {
      for (const key of def.screens) layer.append(svgOf(key));
    }
    (def.space === "stage" ? stageSpace : cam).append(layer);
  }

  for (const [cls, el] of [["warmGlow", "warmGlow"], ["focusBloom", "focusBloom"]] as const) {
    const d = document.createElement("div");
    d.className = cls; d.dataset.el = el;
    cam.append(d);
  }

  const fade = document.createElement("div");
  fade.className = "filmFade"; fade.dataset.el = "filmFade";
  root.append(fade);

  bandCache = [...root.querySelectorAll<HTMLElement>("[data-depth]")].map((node) => ({
    node, depth: +node.dataset.depth!, phase: +node.dataset.phase!,
  }));
  return root;
}

/* ------------------------------------------------------------------ paint */

export function paint(frame: Frame) {
  const t = frame.t;
  const cam = document.querySelector<HTMLElement>('[data-el="camera"]')!;
  cam.style.transform = cameraTransform(frame.camera, t);

  for (const [id, s] of Object.entries(frame.layers)) {
    const el = document.querySelector<HTMLElement>(`[data-layer="${id}"]`);
    if (!el) continue;
    const vis = s.opacity > 0.001;
    el.style.visibility = vis ? "visible" : "hidden";
    if (!vis) continue;
    el.style.opacity = String(s.opacity);
    // every screen drifts, always, even at rest — never a locked-off plate
    const dx = s.x + drift(t, id.length * 0.9, 1.3, 10.1, 16.3);
    const dy = s.y + drift(t, id.length * 1.4 + 0.6, 2.9, 8.9, 14.7);
    el.style.transform = layerTransform({ ...s, x: dx, y: dy });
    el.style.clipPath = frame.clips[id] ?? "none";
    if (!el.classList.contains("stageLayer") && !el.classList.contains("boxed")) {
      const spread = 26 + 34 * s.lift;
      el.style.boxShadow = `0 ${(10 + 26 * s.lift).toFixed(1)}px ${spread.toFixed(1)}px ` +
                           `rgba(44, 33, 20, ${(0.10 + 0.13 * s.lift).toFixed(3)})`;
    }
  }

  // bands move independently of the screen that contains them
  for (const b of bandCache) {
    const bx = drift(t, b.phase, 1.1 * b.depth, 9.3, 15.9);
    const by = drift(t, b.phase + 0.8, 2.6 * b.depth, 7.7, 12.1);
    b.node.style.transform = `translate(${bx.toFixed(2)}px, ${by.toFixed(2)}px)`;
  }

  for (const [id, s] of Object.entries(frame.els)) {
    for (const el of document.querySelectorAll<HTMLElement>(`[data-el="${id}"]`)) {
      el.style.opacity = String(s.opacity);
      el.style.transform =
        `translate(${s.x.toFixed(2)}px, ${s.y.toFixed(2)}px) scale(${s.scale.toFixed(4)})`;
    }
  }

  for (const [id, clip] of Object.entries(frame.elClips))
    for (const el of document.querySelectorAll<HTMLElement>(`[data-el="${id}"]`))
      el.style.clipPath = clip;

  // selective depth of field, and the bloom that sits on the subject
  const f = frame.focus;
  const mask = focusMask(f);
  for (const el of document.querySelectorAll<HTMLElement>(".dofSharp")) {
    el.style.maskImage = mask;
    (el.style as any).webkitMaskImage = mask;
  }
  for (const el of document.querySelectorAll<HTMLElement>(".dofBlur")) {
    el.style.filter = f.blur < 0.05 ? "none" : `blur(${f.blur.toFixed(2)}px)`;
  }
  const bloom = document.querySelector<HTMLElement>('[data-el="focusBloom"]')!;
  bloom.style.left = `${f.x}px`;
  bloom.style.top = `${f.y}px`;
}

export function render(tracks: Track[], t: number) {
  paint(evaluate(tracks, t));
}

export const css = `
  * { margin: 0; padding: 0; box-sizing: border-box; }
  html, body { background: #16140F; }
  .stage { position: relative; overflow: hidden; background: #E7E0D2; }
  /* the beige world reaches every edge; the forge sits low in frame */
  .forge {
    position: absolute; inset: 0;
    background:
      radial-gradient(115% 46% at 50% 112%,
        rgba(168,137,94,0.38) 0%, rgba(168,137,94,0.14) 40%, rgba(168,137,94,0) 70%),
      radial-gradient(90% 34% at 50% -6%,
        rgba(21,19,14,0.05) 0%, rgba(21,19,14,0) 62%);
  }
  .phoneWrap {
    position: absolute; left: 50%; top: 50%;
    width: ${PHONE_W}px; height: ${PHONE_H}px;
    perspective: 2400px;
  }
  .camera { position: absolute; inset: 0; transform-origin: 50% 50%; transform-style: preserve-3d; }
  .layer {
    position: absolute; inset: 0;
    border-radius: ${RADIUS}px; overflow: hidden;
    transform-origin: 50% 50%; will-change: transform, opacity;
  }
  .layer.boxed {
    inset: auto; border-radius: 0; overflow: visible;
    /* follows the banner's alpha, so the shadow is the pill's, not the box's */
    filter: drop-shadow(0 16px 34px rgba(44, 33, 20, 0.26));
  }
  .stageSpace { position: absolute; inset: 0; }
  .stageLayer { border-radius: 0; overflow: visible; }
  .dof { position: absolute; inset: 0; }
  .dofBlur { will-change: filter; }
  .part { position: absolute; inset: 0; transform-origin: 50% 50%; }
  .part svg { width: 100%; height: 100%; display: block; }
  [data-el="lock"], [data-el="lockShackle"], [data-el="lockCopy"], [data-el="finder"],
  [data-el="capture"], [data-el="statusLabel"], [data-el="chip0"], [data-el="chip1"],
  [data-el="chip2"], [data-el="mark"], [data-el="wordmark"], [data-el="tagline"],
  [data-el="toast"], [data-el="nameValue"], [data-el="phoneValue"],
  [data-el="placeValue"], [data-el="day0"], [data-el="day1"], [data-el="day2"],
  [data-el="day3"], [data-el="namePlaceholder"] {
    transform-box: fill-box; transform-origin: center;
  }
  .warmGlow {
    position: absolute; left: 215px; top: 330px;
    width: 620px; height: 620px; margin: -310px 0 0 -310px;
    pointer-events: none; opacity: 0; mix-blend-mode: screen;
    background: radial-gradient(circle at 50% 50%,
      rgba(214,176,116,0.62) 0%, rgba(168,137,94,0.30) 34%, rgba(168,137,94,0) 66%);
  }
  /* the brief highlight that lands on whatever the line is about */
  .focusBloom {
    position: absolute; width: 460px; height: 460px; margin: -230px 0 0 -230px;
    pointer-events: none; opacity: 0; mix-blend-mode: screen;
    background: radial-gradient(circle at 50% 50%,
      rgba(226,192,138,0.50) 0%, rgba(190,155,104,0.22) 38%, rgba(168,137,94,0) 70%);
  }
  .filmFade { position: absolute; inset: 0; background: #15130E; opacity: 0; pointer-events: none; }
`;
