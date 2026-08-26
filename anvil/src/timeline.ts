/**
 * ANVIL — the film as declarative beats. ALL timing lives in this file.
 *
 * Every absolute time is derived from the VO onset map (audio/onset-map.md),
 * so retiming means editing VO or LEAD/duration constants, never chasing
 * numbers through the renderer.
 *
 * Sync rule: a screen carrying a line is settled at `onset − LEAD`.
 * Its entrance therefore starts at `onset − LEAD − duration`.
 */

/* ------------------------------------------------- the voice, as measured */

/** Speech onsets in the trimmed VO (audio/vo_trimmed.wav, 20.550 s). */
export const VO = {
  name:    { on: 0.135, off: 1.051 },
  phone:   { on: 1.636, off: 4.038 },
  commit:  { on: 4.623, off: 5.659 },
  places:  { on: 6.095, off: 7.115 },
  home:    { on: 7.731, off: 8.541 },
  locked:  { on: 9.307, off: 10.388 },
  arrive:  { on: 10.943, off: 11.904 },
  opens:   { on: 12.730, off: 13.435 },
  proof:   { on: 13.931, off: 15.537 },
  circle:  { on: 15.987, off: 17.954 },
  compound:{ on: 18.464, off: 20.355 },
} as const;

/** Every screen is settled this long before its line starts. */
export const LEAD = 0.25;

/* ------------------------------------------------------------- stage setup */

export const STAGE = {
  width: 1920,
  height: 1080,
  fps: 30,
  /** phone is 430×932; this puts it at 857 px tall in a 1080 frame */
  phoneScale: 0.92,
} as const;

/** The lock icon's centre in screen coordinates — the film's focal point. */
export const LOCK = { x: 215, y: 330 } as const;

/* -------------------------------------------------------------- beat types */

export interface ElState { opacity: number; x: number; y: number; scale: number }

export type Track =
  /** a whole screen enters on its own */
  | { k: "layer"; id: string; at: number; dur: number; via: "settleIn" | "revealUp";
      opts?: { distance?: number; from?: "below" | "above" }; note?: string }
  /** outgoing pushes back in z, incoming comes forward — authored as one beat */
  | { k: "cross"; out: string; in: string; at: number; dur: number; depth?: number;
      aperture?: { x: number; y: number; radius: number }; note?: string }
  /** a child of a layer, with its own state (the arrival banner) */
  | { k: "part"; id: string; at: number; dur: number; via: "settleIn" | "revealUp";
      opts?: { distance?: number; from?: "below" | "above" }; note?: string }
  /** any DOM/SVG node by id */
  | { k: "el"; id: string; at: number; dur: number;
      from: Partial<ElState>; to: Partial<ElState>; note?: string }
  /** the camera */
  | { k: "cam"; at: number; dur: number;
      to: { fx: number; fy: number; scale: number; center: number }; note?: string }
  /** deliberate stillness, written down so retiming preserves it */
  | { k: "hold"; at: number; dur: number; note: string }
  | { k: "sfx"; at: number; src: string; gain: number; note?: string };

/* ================================================================ ACT 2 + 3
 *
 * Act 2 — THE CONSTRAINT.  06_home, then the locked camera. The lock is the
 * idea, so the camera goes to it and stops.
 * Act 3 — THE UNLOCK.  Arrival lands on the locked screen; the release runs
 * in the 0.826 s of silence before "Then it opens", so the line arrives on
 * the aftermath rather than narrating the event.
 */

const HOME_IN   = 0.62;                       // Act 2 is the slow act
const CROSS      = 0.44;
const PUSH       = 0.99;
const TOAST_IN   = 0.26;
const SHACKLE    = 0.18;
const UNLOCK     = 0.396;

/** 06_home settles at 7.481, a quarter second before "This is your word." */
const homeIn   = VO.home.on - LEAD - HOME_IN;          // 6.861
/** the crossDepth leaves on the last word of the line it is replacing */
const toLocked = VO.home.off;                           // 8.541
const lockedIn = toLocked + CROSS;                      // 8.981 — settled
/** the push starts in the 0.766 s gap, so the camera is already moving
 *  when "The camera stays locked." begins at 9.307 */
const pushAt   = lockedIn + 0.04;                       // 9.021
const holdAt   = pushAt + PUSH;                         // 10.011
/** the banner settles at 10.693, a quarter second before its line */
const toastAt  = VO.arrive.on - LEAD - TOAST_IN;        // 10.433
/** the release begins the instant the line ends, on silence */
const releaseAt = VO.arrive.off;                        // 11.904
const unlockAt  = releaseAt + SHACKLE;                  // 12.084
const opened    = unlockAt + UNLOCK;                    // 12.480 = opens.on − LEAD

export const act2: Track[] = [
  { k: "layer", id: "home", at: homeIn, dur: HOME_IN, via: "settleIn",
    note: "06_home settles at 7.481" },
  { k: "hold", at: homeIn + HOME_IN, dur: VO.home.off - (homeIn + HOME_IN),
    note: "still under 'This is your word.'" },

  { k: "cross", out: "home", in: "locked", at: toLocked, dur: CROSS, depth: 400,
    note: "06_home → 07_tab_camera" },

  { k: "cam", at: pushAt, dur: PUSH,
    to: { fx: LOCK.x, fy: LOCK.y, scale: 1.50, center: 0.68 },
    note: "focusPush into the lock — starts on silence, still moving at 9.307" },
  { k: "hold", at: holdAt, dur: toastAt - holdAt,
    note: "0.42 s dead still on the lock, carrying past the end of the line" },
];

export const act3: Track[] = [
  { k: "part", id: "toast", at: toastAt, dur: TOAST_IN, via: "revealUp",
    opts: { distance: 30, from: "above" },
    note: "arrival banner drops onto the still-locked screen" },
  { k: "hold", at: toastAt + TOAST_IN, dur: releaseAt - (toastAt + TOAST_IN),
    note: "still under 'Until you actually arrive.'" },

  // --- the release. One gesture, in two moves. ---
  { k: "sfx", at: releaseAt, src: "clang", gain: 0.9, note: "the strike, on top, never ducked" },
  { k: "el", id: "lockShackle", at: releaseAt, dur: SHACKLE,
    from: { y: 0 }, to: { y: -7 },
    note: "the shackle lifts — the only thing moving" },

  { k: "el", id: "lock", at: unlockAt, dur: UNLOCK,
    from: { opacity: 1, scale: 1 }, to: { opacity: 0, scale: 0.86 } },
  { k: "el", id: "lockCopy", at: unlockAt, dur: UNLOCK * 0.6,
    from: { opacity: 1 }, to: { opacity: 0 } },
  { k: "cross", out: "locked", in: "opened", at: unlockAt, dur: UNLOCK, depth: 150,
    aperture: { x: LOCK.x, y: LOCK.y, radius: 660 },
    note: "07 → 09, opening out of the lock's own centre; the banner rides " +
          "out with the layer it belongs to" },
  // no track on #finder: the aperture opens out of the lock's centre, so the
  // viewfinder is already revealed from the middle outward. Scaling it as well
  // would be a second animation on the same object in the same beat.
  { k: "el", id: "warmGlow", at: unlockAt, dur: 0.52,
    from: { opacity: 0, scale: 0.4 }, to: { opacity: 1, scale: 1 },
    note: "warm light shift, blooming out of the lock" },
  { k: "el", id: "warmGlow", at: unlockAt + 0.52, dur: 0.9,
    from: { opacity: 1 }, to: { opacity: 0.32, scale: 1.16 },
    note: "and settling back — light that arrived, not a lamp left on" },
  { k: "cam", at: unlockAt, dur: UNLOCK,
    to: { fx: LOCK.x, fy: LOCK.y, scale: 1.06, center: 0.2 },
    note: "the frame opens up as the lock lets go" },

  { k: "hold", at: opened, dur: LEAD, note: "the aftermath — 09 settled at 12.480" },
  { k: "cam", at: opened, dur: 0.82,
    to: { fx: 215, fy: 466, scale: 1.0, center: 0 },
    note: "the last of the pull-back, decelerating under the line" },
  { k: "hold", at: VO.opens.on, dur: VO.opens.off - VO.opens.on,
    note: "'Then it opens.' lands on a settled screen" },
];

/* --------------------------------------------------------------- assembly */

/** Which SVGs compose each layer, bottom to top. */
export const LAYERS: Record<string, string[]> = {
  home:   ["06_home"],
  locked: ["07_locked", "08_toast"],   // the banner is a part of this layer
  opened: ["09_unlocked"],
};

/** Layers that start visible at t = 0 for a given section. */
export const film: Track[] = [...act2, ...act3];

export const SECTION = {
  /** Act 2 + Act 3, for review before the rest is built. */
  act23: { from: 6.60, to: 13.90, first: [] as string[] },
};

export const duration = 13.90;
