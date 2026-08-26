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

/* ------------------------------------------------------------------- drift
 *
 * Nothing in this film is ever fully still. Two sine components at periods
 * that do not divide into each other, so the motion never resolves into a
 * loop the eye can catch, and an amplitude small enough that it is felt
 * rather than seen. Every drifting thing gets its own phase, which is what
 * stops a screen and its contents moving as one rigid sheet.
 */
export function drift(t: number, phase: number, amp: number,
                      p1 = 8.3, p2 = 13.7): number {
  return amp * (0.62 * Math.sin((2 * Math.PI * t) / p1 + phase) +
                0.38 * Math.sin((2 * Math.PI * t) / p2 + phase * 1.7));
}

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

/** Where the eye is being sent, and how hard the rest of the frame gives way. */
export interface FocusState {
  /** focal point in screen coordinates */
  x: number;
  y: number;
  /** radius of the in-focus region, screen px */
  radius: number;
  /** blur applied outside it, screen px */
  blur: number;
}

export const FOCUS_REST: FocusState = { x: 215, y: 466, radius: 1200, blur: 0 };

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
 * landIn — the heavy register. The film has two kinds of motion: the light
 * register (settleIn, crossDepth — things that glide) for setup, and this,
 * for consequence. The object FALLS to its rest position with accelerating
 * velocity, hits, compresses a few pixels past rest, and recovers. Mass
 * arriving, not drifting in. Used by the lock, the unlock's aftermath, and
 * the anvil mark — the things the film means.
 *
 * `drop: 0` gives pure landing absorption — no fall, just the compression —
 * for objects that are already in place when the impact reaches them.
 */
export function landIn(
  p: number, { drop = 30, compress = 2.5 } = {},
): { opacity: number; y: number; scaleMul: number } {
  // with no fall the impact IS the start: the whole duration is absorption
  const pc = drop > 0 ? 0.58 : 0;        // moment of contact
  if (p <= 0) return { opacity: drop > 0 ? 0 : 1, y: -drop, scaleMul: 1 };
  if (p < pc) {
    const q = p / pc;
    return {
      opacity: drop > 0 ? clamp01(q / 0.4) : 1,
      y: -drop * (1 - Math.pow(q, 1.9)),  // accelerating, not eased — it falls
      scaleMul: 1,
    };
  }
  const r = clamp01((p - pc) / (1 - pc));
  const ring = Math.sin(Math.PI * Math.min(r / 0.85, 1)) * Math.exp(-1.6 * r);
  return {
    opacity: 1,
    y: compress * ring,                   // past rest, downward, then back
    scaleMul: 1 - 0.014 * ring,           // the body absorbs the hit
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
export function cameraTransform(c: CameraState, t = 0, w = 430, h = 932): string {
  // the camera is never locked off: a slow breath on all three axes, under
  // the threshold of conscious notice but never absent
  const bx = drift(t, 0.0, 2.0, 11.3, 17.9);
  const by = drift(t, 1.9, 3.4, 9.7, 15.1);
  const bs = 1 + drift(t, 3.4, 0.0045, 12.9, 20.3);
  const dx = -c.scale * (c.fx - w / 2) * c.center + bx;
  const dy = -c.scale * (c.fy - h / 2) * c.center + by;
  return `translate(${dx.toFixed(3)}px, ${dy.toFixed(3)}px) scale(${(c.scale * bs).toFixed(4)})`;
}

/** Mask that keeps the focal region sharp and lets the rest go. */
export function focusMask(f: FocusState): string {
  if (f.blur < 0.05) return "none";
  const inner = Math.max(f.radius * 0.55, 8).toFixed(1);
  const outer = Math.max(f.radius, 12).toFixed(1);
  return `radial-gradient(circle ${outer}px at ${f.x.toFixed(1)}px ${f.y.toFixed(1)}px,` +
         ` #000 0px, #000 ${inner}px, transparent ${outer}px)`;
}

export function lerpFocus(a: FocusState, b: FocusState, p: number): FocusState {
  const e = easeCamera(p);
  return {
    x: lerp(a.x, b.x, e), y: lerp(a.y, b.y, e),
    radius: lerp(a.radius, b.radius, e), blur: lerp(a.blur, b.blur, e),
  };
}

export function layerTransform(s: LayerState): string {
  return `translate(${s.x.toFixed(3)}px, ${s.y.toFixed(3)}px) ` +
         `translateZ(${s.z.toFixed(3)}px) scale(${s.scale.toFixed(4)})`;
}
