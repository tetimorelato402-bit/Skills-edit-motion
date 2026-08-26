/**
 * ANVIL — the film as declarative beats. ALL timing lives in this file.
 *
 * Two clocks. `VO` holds speech onsets as measured in the trimmed voiceover
 * (audio/onset-map.md). `VO_AT` places that recording on the film clock, so
 * the film can open before the first word. `cue()` converts between them —
 * every beat below is written in film time, derived from a cue.
 *
 * Sync rule: a screen carrying a line is settled at `cue.on − LEAD`, so its
 * entrance starts at `cue.on − LEAD − duration`. The voice never moves to
 * accommodate a transition; transitions are cut to fit the voice.
 */

/* ------------------------------------------------- the voice, as measured */

export const VO = {
  name:     { on: 0.135, off: 1.051 },
  phone:    { on: 1.636, off: 4.038 },
  commit:   { on: 4.623, off: 5.659 },
  places:   { on: 6.095, off: 7.115 },
  home:     { on: 7.731, off: 8.541 },
  locked:   { on: 9.307, off: 10.388 },
  arrive:   { on: 10.943, off: 11.904 },
  opens:    { on: 12.730, off: 13.435 },
  proof:    { on: 13.931, off: 15.537 },
  circle:   { on: 15.987, off: 17.954 },
  compound: { on: 18.464, off: 20.355 },
} as const;

/** Where the trimmed VO sits on the film clock — the film's head. */
export const VO_AT = 1.00;

/** Every screen is settled this long before its line starts. */
export const LEAD = 0.25;

const cue = (k: keyof typeof VO) => ({ on: VO[k].on + VO_AT, off: VO[k].off + VO_AT });

const NAME = cue("name"), PHONE = cue("phone"), COMMIT = cue("commit");
const PLACES = cue("places"), HOME = cue("home"), LOCKED = cue("locked");
const ARRIVE = cue("arrive"), OPENS = cue("opens"), PROOF = cue("proof");
const CIRCLE = cue("circle"), COMPOUND = cue("compound");

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

/** The anvil strike, on the film clock. */
export const CLANG_AT = ARRIVE.off;

/* -------------------------------------------------------------- beat types */

export interface ElState { opacity: number; x: number; y: number; scale: number }

export type Track =
  | { k: "layer"; id: string; at: number; dur: number; via: "settleIn" | "revealUp";
      opts?: { distance?: number; from?: "below" | "above" }; note?: string }
  | { k: "cross"; out: string; in: string; at: number; dur: number; depth?: number;
      aperture?: { x: number; y: number; radius: number }; note?: string }
  /** a layer leaves with nothing replacing it */
  | { k: "exit"; id: string; at: number; dur: number; depth?: number; note?: string }
  | { k: "part"; id: string; at: number; dur: number; via: "settleIn" | "revealUp";
      opts?: { distance?: number; from?: "below" | "above" }; note?: string }
  | { k: "el"; id: string; at: number; dur: number;
      from: Partial<ElState>; to: Partial<ElState>; note?: string }
  /** children of one node, one at a time */
  | { k: "stagger"; ids: string[]; at: number; dur: number; step?: number;
      from: Partial<ElState>; to: Partial<ElState>; note?: string }
  | { k: "cam"; at: number; dur: number;
      to: { fx: number; fy: number; scale: number; center: number }; note?: string }
  | { k: "hold"; at: number; dur: number; note: string }
  | { k: "sfx"; at: number; src: string; gain: number; note?: string };

/* ---------------------------------------------------------- beat durations */

const HEAD      = 0.35;   // the beige world, before anything arrives
const OPEN_IN   = 0.535;
const CROSS_Q   = 0.32;   // Act 1 — quick, light, forward
const CROSS_T   = 0.18;   // Act 1's tightest gap
const CROSS_ACT = 0.34;   // into Act 2
const CROSS     = 0.44;   // Act 2 — the slow act
// Shorter than it looks: a shorter push buys a longer freeze, and the freeze
// is the point. At 0.60 s the camera is still travelling when she starts
// speaking and has stopped dead 0.75 s before she finishes.
const PUSH      = 0.60;
const TOAST_IN  = 0.26;
const SHACKLE   = 0.18;
const UNLOCK    = 0.396;
const CUT_PROOF = 0.24;   // Act 4 — the snap
const CUT_SEEN  = 0.20;
const CROSS_LONG= 0.26;

/* ============================================================ ACT 1 — SETUP
 * Quick and light. 03_onboard_birthday is cut: birthday entry is compliance,
 * not product, and it explains nothing the film is here to explain.
 */

const openAt = HEAD;                                    // 0.350 → settled 0.885

export const act1: Track[] = [
  { k: "hold", at: 0, dur: HEAD, note: "the beige world, empty, before the voice" },
  { k: "layer", id: "name", at: openAt, dur: OPEN_IN, via: "settleIn",
    note: "01 settles at 0.885" },
  { k: "hold", at: openAt + OPEN_IN, dur: NAME.off - (openAt + OPEN_IN),
    note: "under 'It starts with your name.'" },

  { k: "cross", out: "name", in: "phone", at: NAME.off, dur: CROSS_Q, depth: 400 },
  { k: "hold", at: NAME.off + CROSS_Q, dur: PHONE.off - (NAME.off + CROSS_Q),
    note: "under the two-sentence verification line" },

  { k: "cross", out: "phone", in: "commit", at: PHONE.off, dur: CROSS_Q, depth: 400 },
  // The one stagger in the film, and the only motion under a line outside
  // Act 3: the three chosen commitments light one at a time while she says
  // "Choose what you're committing to." Act 1 is the light act; this is the
  // line describing itself.
  { k: "stagger", ids: ["chip0", "chip1", "chip2"], at: COMMIT.on + 0.077,
    dur: 0.28, step: 0.08,
    from: { opacity: 0.35, scale: 0.94 }, to: { opacity: 1, scale: 1 },
    note: "the commitments, one at a time, under their own line" },

  { k: "cross", out: "commit", in: "places", at: COMMIT.off, dur: CROSS_T, depth: 400,
    note: "0.18 s — the tightest gap in Act 1" },
  { k: "hold", at: COMMIT.off + CROSS_T, dur: PLACES.off - (COMMIT.off + CROSS_T),
    note: "under 'And exactly where you'll do it.'" },
];

/* ==================================================== ACT 2 — THE CONSTRAINT
 * The act slows down and then stops. The hold on the lock is the longest
 * stillness in the film by a wide margin — everything Act 4 releases from.
 */

const toHome   = PLACES.off;                            // 8.115
const homeIn   = toHome + CROSS_ACT;                    // 8.455 settled
const toLocked = HOME.off;                              // 9.541
const lockedIn = toLocked + CROSS;                      // 9.981 settled
const pushAt   = lockedIn + 0.04;                       // 10.021
const holdAt   = pushAt + PUSH;                         // 10.621
const toastAt  = ARRIVE.on - LEAD - TOAST_IN;           // 11.433

export const act2: Track[] = [
  { k: "cross", out: "places", in: "home", at: toHome, dur: CROSS_ACT, depth: 400,
    note: "into Act 2 — the film slows here" },
  { k: "hold", at: homeIn, dur: HOME.on - homeIn,
    note: "act boundary: the lead is the hold" },
  { k: "hold", at: HOME.on, dur: HOME.off - HOME.on,
    note: "still under 'This is your word.'" },

  { k: "cross", out: "home", in: "locked", at: toLocked, dur: CROSS, depth: 400,
    note: "06_home → 07_tab_camera" },

  { k: "cam", at: pushAt, dur: PUSH,
    to: { fx: LOCK.x, fy: LOCK.y, scale: 1.50, center: 0.68 },
    note: "focusPush into the lock — starts on silence, still moving at 10.307" },

  // 0.63 s of absolute stillness, landing while she is still speaking and
  // running past the end of the line. Nothing else in the film holds this
  // long. It is what the Act 4 snap releases from.
  { k: "hold", at: holdAt, dur: toastAt - holdAt,
    note: "the uncomfortable hold — 0.812 s, dead still at full push" },
];

/* ======================================================= ACT 3 — THE UNLOCK */

const releaseAt = ARRIVE.off;                           // 12.904
const unlockAt  = releaseAt + SHACKLE;                  // 13.084
const opened    = unlockAt + UNLOCK;                    // 13.480 = OPENS.on − LEAD

export const act3: Track[] = [
  { k: "part", id: "toast", at: toastAt, dur: TOAST_IN, via: "revealUp",
    opts: { distance: 30, from: "above" },
    note: "arrival banner drops onto the still-locked screen" },
  { k: "hold", at: toastAt + TOAST_IN, dur: releaseAt - (toastAt + TOAST_IN),
    note: "still under 'Until you actually arrive.'" },

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
  // viewfinder is already revealed from the middle outward.
  { k: "el", id: "warmGlow", at: unlockAt, dur: 0.52,
    from: { opacity: 0, scale: 0.4 }, to: { opacity: 1, scale: 1 },
    note: "warm light shift, blooming out of the lock" },
  { k: "el", id: "warmGlow", at: unlockAt + 0.52, dur: 0.83,
    from: { opacity: 1 }, to: { opacity: 0.32, scale: 1.16 },
    note: "and settling back — light that arrived, not a lamp left on" },
  { k: "cam", at: unlockAt, dur: UNLOCK,
    to: { fx: LOCK.x, fy: LOCK.y, scale: 1.06, center: 0.2 },
    note: "the frame opens up as the lock lets go" },
  { k: "cam", at: opened, dur: 0.82,
    to: { fx: 215, fy: 466, scale: 1.0, center: 0 },
    note: "the last of the pull-back, decelerating under the line" },

  { k: "hold", at: opened, dur: LEAD, note: "the aftermath — 09 settled at 13.480" },
  { k: "hold", at: OPENS.on, dur: OPENS.off - OPENS.on,
    note: "'Then it opens.' lands on a settled screen" },
];

/* ========================================================= ACT 4 — THE LOOP
 * Cut hard. 0.24 s and 0.20 s — seven and six frames. After Act 2's hold the
 * rhythm reads as a snap, which is the point: you arrive, the camera opens,
 * the proof is up. No breath anywhere in this act.
 */

export const act4: Track[] = [
  { k: "cross", out: "opened", in: "proof", at: OPENS.off, dur: CUT_PROOF, depth: 400,
    note: "the snap — 7 frames, no hold on either side" },
  { k: "hold", at: OPENS.off + CUT_PROOF, dur: PROOF.off - (OPENS.off + CUT_PROOF),
    note: "under 'Proof, not words.'" },

  { k: "cross", out: "proof", in: "seen", at: PROOF.off, dur: CUT_SEEN, depth: 400,
    note: "6 frames — the fastest cut in the film" },
  { k: "hold", at: PROOF.off + CUT_SEEN, dur: CIRCLE.off - (PROOF.off + CUT_SEEN),
    note: "under 'Your circle sees it. And you see them.'" },
];

/* ==================================================== ACT 5 — THE LONG GAME */

export const act5: Track[] = [
  { k: "cross", out: "seen", in: "routine", at: CIRCLE.off, dur: CROSS_LONG, depth: 400 },
  { k: "hold", at: CIRCLE.off + CROSS_LONG, dur: COMPOUND.off - (CIRCLE.off + CROSS_LONG),
    note: "under 'Show up enough, and it compounds.'" },
];

/* ====================================================== THE SILENT ENDING
 * The voice has stopped for good. Nothing here is scored; the room tone is
 * the only thing left, so the silence has texture instead of sounding like
 * the file gave out.
 */

const voiceEnds  = COMPOUND.off;            // 21.355
const beat       = voiceEnds + 0.545;       // 21.900
const receded    = beat + 0.60;             // 22.500
const markAt     = receded + 0.32;          // 22.820 — empty beige, held
const markDone   = markAt + 0.58;           // 23.400
const wordAt     = markDone + 0.12;         // 23.520
const wordDone   = wordAt + 0.54;           // 24.060
const tagAt      = wordDone + 0.14;         // 24.200
const tagDone    = tagAt + 0.60;            // 24.800
const fadeAt     = tagDone + 0.90;          // 25.700
const filmEnds   = fadeAt + 0.55;           // 26.250

export const ending: Track[] = [
  { k: "hold", at: voiceEnds, dur: beat - voiceEnds,
    note: "hold on the routine screen — the voice is gone and the film knows it" },
  { k: "exit", id: "routine", at: beat, dur: receded - beat, depth: 520,
    note: "everything recedes" },
  // the warm light lives in the phone's space; it leaves when the phone does,
  // or it sits in the empty frame behind the lockup as a stain
  { k: "el", id: "warmGlow", at: beat, dur: (receded - beat) * 0.7,
    from: { opacity: 0.32 }, to: { opacity: 0 } },
  { k: "hold", at: receded, dur: markAt - receded,
    note: "the beige space alone, 0.32 s — the silence is the ending" },

  { k: "layer", id: "logo", at: markAt, dur: 0, via: "settleIn",
    note: "the lockup layer opens; its parts arrive one at a time" },
  { k: "el", id: "mark", at: markAt, dur: markDone - markAt,
    from: { opacity: 0, y: 26, scale: 0.96 }, to: { opacity: 1, y: 0, scale: 1 },
    note: "the anvil mark forms, alone" },
  { k: "hold", at: markDone, dur: wordAt - markDone, note: "" },
  { k: "el", id: "wordmark", at: wordAt, dur: wordDone - wordAt,
    from: { opacity: 0, x: -18 }, to: { opacity: 1, x: 0 },
    note: "ANVIL settles beside it" },
  { k: "hold", at: wordDone, dur: tagAt - wordDone, note: "" },
  { k: "el", id: "tagline", at: tagAt, dur: tagDone - tagAt,
    from: { opacity: 0, y: 10 }, to: { opacity: 1, y: 0 },
    note: "the tagline fades in below" },

  { k: "hold", at: tagDone, dur: fadeAt - tagDone,
    note: "0.90 s. Let the silence sit." },
  { k: "el", id: "filmFade", at: fadeAt, dur: filmEnds - fadeAt,
    from: { opacity: 0 }, to: { opacity: 1 },
    note: "out to ink — warm, not black" },
];

/* --------------------------------------------------------------- assembly */

export interface LayerDef { space: "phone" | "stage"; screens: string[] }

/** Which SVGs compose each layer, bottom to top, and where it lives. */
export const LAYERS: Record<string, LayerDef> = {
  name:    { space: "phone", screens: ["01_onboard_name"] },
  phone:   { space: "phone", screens: ["02_onboard_phone"] },
  commit:  { space: "phone", screens: ["04_onboard_commitments"] },
  places:  { space: "phone", screens: ["05_onboard_places"] },
  home:    { space: "phone", screens: ["06_home"] },
  locked:  { space: "phone", screens: ["07_locked", "08_toast"] },
  opened:  { space: "phone", screens: ["09_unlocked"] },
  proof:   { space: "phone", screens: ["11_circle_live"] },
  seen:    { space: "phone", screens: ["10_friend_arrived"] },
  routine: { space: "phone", screens: ["07_tab_routine"] },
  logo:    { space: "stage", screens: ["logo"] },
};

export const film: Track[] = [...act1, ...act2, ...act3, ...act4, ...act5, ...ending];

export const SECTION = {
  full:  { from: 0, to: filmEnds },
  act1:  { from: 0, to: HOME.on },
  act23: { from: PLACES.off, to: OPENS.off },
  act45: { from: OPENS.off, to: voiceEnds },
  end:   { from: voiceEnds - 0.6, to: filmEnds },
};

export const duration = filmEnds;
