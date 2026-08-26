/**
 * ANVIL — the stage. Builds the DOM once, then maps a time to a picture.
 * It owns no timing of its own: everything it does is a function of t and
 * the tracks in timeline.ts.
 */
import {
  ease, progress, settleIn, revealUp, crossDepth, focusPush, apertureOpen, recede,
  cameraTransform, layerTransform, lerp,
  REST, HIDDEN, CAMERA_REST, type LayerState, type CameraState,
} from "./motion.js";
import { LAYERS, STAGE, type Track, type ElState } from "./timeline.js";
import { SCREENS } from "../build/screens.js";

const EL_REST: ElState = { opacity: 1, x: 0, y: 0, scale: 1 };

export interface Frame {
  layers: Record<string, LayerState>;
  parts: Record<string, LayerState>;
  els: Record<string, ElState>;
  /** layer id → clip-path, while an aperture is mid-open */
  clips: Record<string, string>;
  camera: CameraState;
}

/* ------------------------------------------------------------- evaluation */

export function evaluate(tracks: Track[], t: number): Frame {
  const layers: Record<string, LayerState> = {};
  for (const id of Object.keys(LAYERS)) layers[id] = { ...HIDDEN };
  const parts: Record<string, LayerState> = {};
  for (const def of Object.values(LAYERS))
    for (const k of def.screens) parts[k.replace(/^\d+_/, "")] = { ...REST };
  const els: Record<string, ElState> = {};
  // every animated node starts at the `from` of the first track that owns it
  for (const tr of tracks) {
    if (tr.k === "el" && !(tr.id in els)) els[tr.id] = { ...EL_REST, ...tr.from };
    if (tr.k === "stagger")
      for (const id of tr.ids) if (!(id in els)) els[id] = { ...EL_REST, ...tr.from };
  }
  const clips: Record<string, string> = {};
  let camera: CameraState = { ...CAMERA_REST };
  let camFrom: CameraState = { ...CAMERA_REST };

  for (const tr of tracks) if (tr.k === "part") parts[tr.id] = { ...HIDDEN };

  const ordered = [...tracks].sort((a, b) => a.at - b.at);

  for (const tr of ordered) {
    if (tr.k === "stagger") {
      const step = tr.step ?? 0.08;
      tr.ids.forEach((id, i) => {
        const q = ease(progress(t, tr.at + i * step, tr.dur));
        const from = { ...EL_REST, ...tr.from };
        const to = { ...from, ...tr.to };
        els[id] = {
          opacity: lerp(from.opacity, to.opacity, q),
          x: lerp(from.x, to.x, q),
          y: lerp(from.y, to.y, q),
          scale: lerp(from.scale, to.scale, q),
        };
      });
      continue;
    }
    if (tr.k === "el") {
      if (t < tr.at) continue;
      const p = progress(t, tr.at, tr.dur);
      const e = ease(p);
      const base = els[tr.id] ?? EL_REST;
      const from = { ...base, ...tr.from };
      const to = { ...from, ...tr.to };
      els[tr.id] = {
        opacity: lerp(from.opacity, to.opacity, e),
        x: lerp(from.x, to.x, e),
        y: lerp(from.y, to.y, e),
        scale: lerp(from.scale, to.scale, e),
      };
      continue;
    }
    if (t < tr.at) continue;
    const p = progress(t, tr.at, tr.dur);

    switch (tr.k) {
      case "layer":
        layers[tr.id] = p >= 1 ? { ...REST } : {
          ...REST,
          ...(tr.via === "settleIn" ? settleIn(p) : revealUp(p, tr.opts)),
        };
        break;

      case "part":
        parts[tr.id] = p >= 1 ? { ...REST } : {
          ...REST,
          ...(tr.via === "settleIn" ? settleIn(p) : revealUp(p, tr.opts)),
        };
        break;

      case "cross": {
        const c = crossDepth(p, { depth: tr.depth, aperture: !!tr.aperture });
        layers[tr.out] = p >= 1 ? { ...HIDDEN } : { ...REST, ...c.out };
        layers[tr.in] = p >= 1 ? { ...REST } : { ...REST, ...c.in };
        if (tr.aperture && p < 1) {
          const r = apertureOpen(p, tr.aperture.radius);
          clips[tr.in] = `circle(${r.toFixed(2)}px at ${tr.aperture.x}px ${tr.aperture.y}px)`;
        } else if (tr.aperture) {
          delete clips[tr.in];
        }
        break;
      }

      case "cam":
        camera = focusPush(p, camFrom, tr.to);
        if (p >= 1) camFrom = { ...camera };
        break;

      case "exit":
        layers[tr.id] = p >= 1 ? { ...HIDDEN }
                               : { ...REST, ...recede(p, { depth: tr.depth }) };
        break;

      case "hold":
      case "sfx":
        break;
    }
  }
  return { layers, parts, els, clips, camera };
}

/* ----------------------------------------------------------------- the DOM */

const PHONE_RADIUS = 44;

export function build(root: HTMLElement, sectionLayers = Object.keys(LAYERS)) {
  root.innerHTML = "";
  root.className = "stage";

  const forge = document.createElement("div");
  forge.className = "forge";
  root.append(forge);

  const wrap = document.createElement("div");
  wrap.className = "phoneWrap";
  const cam = document.createElement("div");
  cam.className = "camera";
  cam.id = "camera";
  wrap.append(cam);
  root.append(wrap);

  // stage-space layers sit in the frame itself, not inside the phone
  const stageSpace = document.createElement("div");
  stageSpace.className = "stageSpace";
  root.append(stageSpace);

  for (const id of sectionLayers) {
    const def = LAYERS[id];
    const layer = document.createElement("div");
    layer.className = def.space === "stage" ? "layer stageLayer" : "layer";
    layer.id = `layer-${id}`;
    for (const key of def.screens) {
      const part = document.createElement("div");
      part.className = "part";
      // "08_toast" → part id "toast", so the timeline names it as content
      part.id = `part-${key.replace(/^\d+_/, "")}`;
      part.innerHTML = SCREENS[key];
      const svg = part.querySelector("svg")!;
      svg.removeAttribute("width");
      svg.removeAttribute("height");
      layer.append(part);
    }
    (def.space === "stage" ? stageSpace : cam).append(layer);
  }

  const glow = document.createElement("div");
  glow.id = "warmGlow";
  glow.className = "warmGlow";
  cam.append(glow);

  const fade = document.createElement("div");
  fade.id = "filmFade";
  fade.className = "filmFade";
  root.append(fade);

  return root;
}

/* ------------------------------------------------------------------ paint */

export function paint(frame: Frame) {
  const cam = document.getElementById("camera")!;
  cam.style.transform = cameraTransform(frame.camera);

  for (const [id, s] of Object.entries(frame.layers)) {
    const el = document.getElementById(`layer-${id}`);
    if (!el) continue;
    el.style.opacity = String(s.opacity);
    el.style.transform = layerTransform(s);
    el.style.visibility = s.opacity <= 0.001 ? "hidden" : "visible";
    el.style.clipPath = frame.clips[id] ?? "none";
    // depth reads as a soft contact shadow that grows with lift — never hard
    if (!el.classList.contains("stageLayer")) {
      const spread = 26 + 34 * s.lift;
      el.style.boxShadow =
        `0 ${(10 + 26 * s.lift).toFixed(1)}px ${spread.toFixed(1)}px ` +
        `rgba(44, 33, 20, ${(0.10 + 0.13 * s.lift).toFixed(3)})`;
    }
  }

  for (const [id, s] of Object.entries(frame.parts)) {
    const el = document.getElementById(`part-${id}`);
    if (!el) continue;
    el.style.opacity = String(s.opacity);
    el.style.transform = layerTransform(s);
    const hidden = ((1 - s.reveal) * 100).toFixed(2);
    el.style.clipPath = s.reveal >= 1 ? "none" : `inset(0 0 ${hidden}% 0)`;
  }

  for (const [id, s] of Object.entries(frame.els)) {
    const el = document.getElementById(id);
    if (!el) continue;
    el.style.opacity = String(s.opacity);
    el.style.transform =
      `translate(${s.x.toFixed(2)}px, ${s.y.toFixed(2)}px) scale(${s.scale.toFixed(4)})`;
  }
}

export function render(tracks: Track[], t: number) {
  paint(evaluate(tracks, t));
}

export const css = `
  * { margin: 0; padding: 0; box-sizing: border-box; }
  html, body { background: #0b0a08; }
  .stage {
    position: relative; overflow: hidden;
    width: ${STAGE.width}px; height: ${STAGE.height}px;
    background: #E7E0D2;
  }
  /* a faint warm forge glow, low in frame — the world, not a vignette */
  .forge {
    position: absolute; inset: 0;
    background:
      radial-gradient(120% 70% at 50% 118%,
        rgba(168,137,94,0.34) 0%, rgba(168,137,94,0.13) 38%, rgba(168,137,94,0) 68%),
      radial-gradient(80% 55% at 50% 6%,
        rgba(21,19,14,0.045) 0%, rgba(21,19,14,0) 60%);
  }
  .phoneWrap {
    position: absolute; left: 50%; top: 50%;
    width: 430px; height: 932px;
    transform: translate(-50%, -50%) scale(${STAGE.phoneScale});
    perspective: 2400px;
  }
  .camera {
    position: absolute; inset: 0;
    transform-origin: 50% 50%;
    transform-style: preserve-3d;
  }
  .layer {
    position: absolute; inset: 0;
    border-radius: ${PHONE_RADIUS}px;
    overflow: hidden;
    transform-origin: 50% 50%;
    will-change: transform, opacity;
  }
  .stageSpace {
    position: absolute; inset: 0;
    width: ${STAGE.width}px; height: ${STAGE.height}px;
  }
  .stageLayer { border-radius: 0; overflow: visible; }
  .part { position: absolute; inset: 0; transform-origin: 50% 50%; }
  .part svg { width: 100%; height: 100%; display: block; }
  #lock, #lockShackle, #lockCopy, #finder, #capture, #statusLabel,
  #chip0, #chip1, #chip2, #mark, #wordmark, #tagline {
    transform-box: fill-box; transform-origin: center;
  }
  /* out to ink — warm, not black */
  .filmFade {
    position: absolute; inset: 0; background: #15130E;
    opacity: 0; pointer-events: none;
  }
  .warmGlow {
    position: absolute; left: 215px; top: 330px;
    width: 620px; height: 620px; margin: -310px 0 0 -310px;
    pointer-events: none; opacity: 0;
    mix-blend-mode: screen;
    background: radial-gradient(circle at 50% 50%,
      rgba(214,176,116,0.62) 0%, rgba(168,137,94,0.30) 34%, rgba(168,137,94,0) 66%);
  }
`;
