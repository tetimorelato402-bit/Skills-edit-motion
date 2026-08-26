/**
 * ANVIL — motion system.
 *
 * Everything the film does is expressed as one of the primitives below.
 * No hand-authored keyframes live outside this file; timings live in
 * timeline.ts. Primitives are pure: given local progress they return the
 * state of one layer. Nothing here reads the clock.
 */

/* ------------------------------------------------------------------ easing */

/** Newton-solved cubic-bezier, the CSS timing function as a pure fn. */
export function cubicBezier(x1: number, y1: number, x2: number, y2: number) {
  const A = (a: number, b: number) => 1 - 3 * b + 3 * a;
  const B = (a: number, b: number) => 3 * b - 6 * a;
  const C = (a: number) => 3 * a;
  const calc = (t: number, a: number, b: number) => ((A(a, b) * t + B(a, b)) * t + C(a)) * t;
  const slope = (t: number, a: number, b: number) =>
    3 * A(a, b) * t * t + 2 * B(a, b) * t + C(a);

  return (x: number): number => {
    if (x <= 0) return 0;
    if (x >= 1) return 1;
    let t = x;
    for (let i = 0; i < 8; i++) {
      const d = slope(t, x1, x2);
      if (d === 0) break;
      const err = calc(t, x1, x2) - x;
      if (Math.abs(err) < 1e-6) break;
      t -= err / d;
    }
    return calc(t, y1, y2);
  };
}

/**
 * The film's one easing. Every move uses it unless a primitive documents
 * why it doesn't. There is no linear motion anywhere in this timeline.
 */
export const ease = cubicBezier(0.22, 1, 0.36, 1);

/**
 * The camera curve. The primary easing is built for UI response — it spends
 * 40% of its travel in the first 15% of its time, which on a 0.4 s dolly
 * reads as a snap, not a move. A camera needs mass: this one leaves slowly,
 * carries, and settles long. Still not linear anywhere.
 */
export const easeCamera = cubicBezier(0.42, 0.0, 0.22, 1);

export const clamp01 = (v: number) => (v < 0 ? 0 : v > 1 ? 1 : v);
export const lerp = (a: number, b: number, p: number) => a + (b - a) * p;

/** Local progress of a window [at, at+dur] at absolute time t. */
export const progress = (t: number, at: number, dur: number) =>
  dur <= 0 ? (t >= at ? 1 : 0) : clamp01((t - at) / dur);

/* ------------------------------------------------------------------- state */

export interface LayerState {
  opacity: number;
  /** px, stage space */
  x: number;
  y: number;
  scale: number;
  /** depth in px; negative pushes away from camera */
  z: number;
  /** 0…1 — drives the contact shadow's spread and alpha, never a hard drop */
  lift: number;
  /** 0…1 — how much of the layer is revealed from its bottom edge */
  reveal: number;
}

export const REST: LayerState = {
  opacity: 1, x: 0, y: 0, scale: 1, z: 0, lift: 1, reveal: 1,
};

export const HIDDEN: LayerState = { ...REST, opacity: 0 };

export interface CameraState {
  /** zoom factor about the focal point */
  scale: number;
  /** focal point in screen coordinates (430×932) */
  fx: number;
  fy: number;
  /** 0…1 — how far the focal point is pulled to frame centre */
  center: number;
}

export const CAMERA_REST: CameraState = { scale: 1, fx: 215, fy: 466, center: 0 };

/* -------------------------------------------------------------- primitives */

/**
 * settleIn — enters at 1.04 and settles to 1.0 through a slight overshoot.
 * The overshoot is in scale only: it passes 1.0, dips to 0.994, comes back.
 * Opacity resolves in the first 45% so the screen is never a ghost that
 * happens to be moving.
 */
export function settleIn(p: number): Partial<LayerState> {
  const e = ease(p);
  const overshoot = Math.sin(Math.PI * clamp01((p - 0.55) / 0.45)) * 0.006;
  return {
    opacity: ease(clamp01(p / 0.45)),
    scale: lerp(1.04, 1.0, e) - overshoot,
    lift: e,
  };
}

/**
 * revealUp — a mask reveal with the content travelling into it.
 * `from: "above"` runs the same gesture downward, for banners that
 * belong to the top edge of the screen.
 */
export function revealUp(
  p: number,
  { distance = 24, from = "below" as "below" | "above" } = {},
): Partial<LayerState> {
  const e = ease(p);
  const dir = from === "below" ? 1 : -1;
  return {
    opacity: ease(clamp01(p / 0.35)),
    y: lerp(distance * dir, 0, e),
    reveal: e,
  };
}

/**
 * crossDepth — the outgoing screen pushes back in z and fades; the incoming
 * one comes forward into the same space. Returns both halves so a transition
 * is authored as a single beat, not two that have to be kept in sync.
 */
export function crossDepth(p: number, { depth = 220, aperture = false } = {}) {
  const e = ease(p);
  // With an aperture the incoming screen is revealed geometrically, so neither
  // layer moves in z: a receding outgoing layer would show the stage through
  // the corners the circle has not reached yet, and the depth cue would be
  // fighting the reveal for the same beat. The camera supplies the motion.
  if (aperture) {
    const still: Partial<LayerState> = { opacity: 1, z: 0, lift: 1 };
    return { out: still, in: { ...still } };
  }
  return {
    // The outgoing screen holds full opacity until the incoming one covers
    // it. Fading both at once shows the stage through the middle of every
    // transition and washes the picture out — a light screen becoming a dark
    // one goes grey. It recedes in z the whole time; only its cover changes.
    // Opacity is eased like everything else. A linear ramp holds the incoming
    // screen near half-transparent through the middle of the beat, which is
    // what turns a dissolve into a double exposure; eased, it is effectively
    // opaque two frames in and the rest of the beat is depth, not blending.
    // The incoming screen resolves in the first quarter of the beat. Two
    // text-dense screens held at half opacity against each other read as a
    // double exposure, not as depth; the cover has to happen fast and the
    // rest of the duration is the new screen settling forward. The outgoing
    // one only starts fading once it is already hidden underneath.
    out: {
      opacity: 1 - ease(clamp01((p - 0.35) / 0.35)),
      z: lerp(0, -depth, e),
      lift: 1 - e,
    } as Partial<LayerState>,
    in: {
      opacity: aperture ? 1 : ease(clamp01(p / 0.30)),
      z: lerp(depth * 0.5, 0, e),
      lift: e,
    } as Partial<LayerState>,
  };
}

/**
 * recede — a layer leaves with nothing replacing it. crossDepth's outgoing
 * half is wrong here: it is tuned to disappear under something that covers
 * it, so on its own it blinks out in a fifth of the beat. This holds, then
 * drifts away, on the camera curve — the ending has time and should use it.
 */
export function recede(p: number, { depth = 520 } = {}): Partial<LayerState> {
  const e = easeCamera(p);
  return { opacity: 1 - e, z: lerp(0, -depth, e), lift: 1 - e };
}

/**
 * apertureOpen — the incoming screen is revealed by a circle growing from a
 * point rather than by a fade. Used once, on the unlock: the viewfinder opens
 * out of the lock's own centre, which is the thing the film is about.
 * Returns the clip radius in screen px.
 */
export function apertureOpen(p: number, radius: number): number {
  // easeCamera, not the primary curve: on the primary the circle clears the
  // lock in 60 ms and the release is over before it reads.
  return radius * easeCamera(p);
}

/**
 * focusPush — the camera moves, the screen does not. `center` says how much
 * of the focal point's offset from frame centre is taken up as the push
 * lands; 1 puts the subject dead centre, which is usually too literal.
 */
export function focusPush(
  p: number,
  from: CameraState,
  to: Partial<CameraState> & { fx: number; fy: number; scale: number },
): CameraState {
  const e = easeCamera(p);
  return {
    scale: lerp(from.scale, to.scale, e),
    fx: lerp(from.fx, to.fx, e),
    fy: lerp(from.fy, to.fy, e),
    center: lerp(from.center, to.center ?? 1, e),
  };
}

/**
 * holdBeat — deliberate stillness. It exists as a primitive so that a hold
 * is written into the timeline as an element with a duration, and survives
 * retiming instead of being whatever gap the neighbouring beats leave behind.
 */
export function holdBeat(_p: number): Partial<LayerState> {
  return {};
}

/**
 * stagger — child index → its own local progress, 80 ms apart by default.
 */
export function stagger(
  t: number, at: number, dur: number, count: number, step = 0.08,
): number[] {
  return Array.from({ length: count }, (_, i) => progress(t, at + i * step, dur));
}

/* ---------------------------------------------------------------- composing */

export function apply(base: LayerState, ...parts: Partial<LayerState>[]): LayerState {
  return Object.assign({ ...base }, ...parts);
}

/** Screen-space → CSS. The camera scales about the phone's centre, then
 *  translates so the focal point drifts toward frame centre by `center`. */
export function cameraTransform(c: CameraState, w = 430, h = 932): string {
  const dx = -c.scale * (c.fx - w / 2) * c.center;
  const dy = -c.scale * (c.fy - h / 2) * c.center;
  return `translate(${dx.toFixed(3)}px, ${dy.toFixed(3)}px) scale(${c.scale.toFixed(4)})`;
}

export function layerTransform(s: LayerState): string {
  return `translate(${s.x.toFixed(3)}px, ${s.y.toFixed(3)}px) ` +
         `translateZ(${s.z.toFixed(3)}px) scale(${s.scale.toFixed(4)})`;
}
