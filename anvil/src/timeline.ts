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

export type Format = "vertical" | "wide";

/**
 * Vertical is the master. The phone sits at ~68% of frame height so the
 * beige world survives above and below it rather than being cropped away;
 * the wide export is a secondary target and takes what fits.
 */
export const FORMATS = {
  vertical: { width: 1080, height: 1920, phoneScale: 1.40 },  // 1305 px tall, 68%
  wide:     { width: 1920, height: 1080, phoneScale: 0.92 },
} as const;

export const STAGE = { fps: 30 } as const;

/** The lock icon's centre in screen coordinates — the film's focal point. */
export const LOCK = { x: 215, y: 330 } as const;

/** What each line is about, in screen coordinates. Every spoken line has a
 *  visual subject; the frame is pointing at it before the line lands. */
export const SUBJECT = {
  nameField:   { x: 215, y: 317 },   // 01 — the input being typed into
  phoneField:  { x: 215, y: 231 },   // 02 — the number field
  chips:       { x: 215, y: 193 },   // 04 — the three chosen commitments
  placeField:  { x: 215, y: 465 },   // 05 — the focused place field
  commitments: { x: 215, y: 376 },   // 06_home — the commitments card
  lock:        { x: 215, y: 330 },   // 07 — the padlock
  banner:      { x: 215, y: -18 },   // the system notification, above the device
  viewfinder:  { x: 215, y: 340 },   // 09 — the open camera
  proofPhoto:  { x: 215, y: 230 },   // 11 — the posted proof itself
  maraRow:     { x: 215, y: 524 },   // 11 — the member who hasn't shown up
  friendRow:   { x: 215, y: 101 },   // 10 — "Jeff made it to the gym"
  friendList:  { x: 215, y: 376 },   // 10 — "and you see them": the shared commitments
  weekRow:     { x: 215, y: 176 },   // routine — the filled days
  streak:      { x: 213, y: 283 },   // routine — "Current streak 12"
} as const;

/** A value typed into a field: the reveal track plus one key per character
 *  that should sound (punctuation stays silent). */
const typeBeat = (id: string, at: number, dur: number, chars: number,
                  keys: number[], gain: number): Track[] => [
  { k: "type", id, at, dur, chars },
  ...keys.map((i): Track => ({ k: "sfx", at: at + (i * dur) / chars, src: "key", gain })),
];

/** The warm highlight that lands on a line's subject as the line begins. */
const bloom = (on: number, peak = 0.62): Track[] => [
  { k: "el", id: "focusBloom", at: on - 0.09, dur: 0.32,
    from: { opacity: 0, scale: 0.72 }, to: { opacity: peak, scale: 1 } },
  { k: "el", id: "focusBloom", at: on + 0.28, dur: 0.8,
    from: { opacity: peak }, to: { opacity: 0.1 } },
];

/* -------------------------------------------------------------- beat types */

export interface ElState { opacity: number; x: number; y: number; scale: number }

export type Track =
  | { k: "layer"; id: string; at: number; dur: number; via: "settleIn" | "revealUp";
      opts?: { distance?: number; from?: "below" | "above" }; note?: string }
  | { k: "cross"; out: string; in: string; at: number; dur: number; depth?: number;
      /** px the incoming screen travels through the cut — momentum, not a swap */
      travel?: number;
      aperture?: { x: number; y: number; radius: number }; note?: string }
  /** the heavy register: the object falls to rest, compresses, recovers.
      target "layer" applies the landing to a whole screen (drop 0 = pure
      absorption); default is a tagged element. */
  | { k: "land"; id: string; at: number; dur: number; drop?: number;
      compress?: number; target?: "el" | "layer"; note?: string }
  /** a value typed into a field: stepped character reveal on a tagged text
      element. The key sounds are separate sfx cues emitted by typeBeat(), so
      the mix hears exactly what the reveal shows. */
  | { k: "type"; id: string; at: number; dur: number; chars: number; note?: string }
  /** where the eye is being sent, and how far the rest of the frame gives way */
  | { k: "focus"; at: number; dur: number;
      to: { x?: number; y?: number; radius?: number; blur?: number }; note?: string }
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
// is the point. At 0.42 s the camera moves fast enough to feel pulled, and
// the stillness that follows is nearly a full second.
const PUSH      = 0.42;
const TOAST_IN  = 0.26;
// The release is three moves now, not two: the shackle lifts, the lock and
// its copy clear on the still-locked screen, and only then does the film cut.
const SHACKLE   = 0.15;
const CLEAR     = 0.15;
const OPEN      = 0.276;
const CUT_PROOF = 0.24;   // Act 4 — the snap
const CUT_SEEN  = 0.20;
const CROSS_LONG= 0.26;

/* ============================================================ ACT 1 — SETUP
 * Quick and light, but never a slideshow: every line's subject is framed
 * before the line lands, the name and number and place are TYPED rather than
 * shown, and each cut is a button press — a tap, then the whoosh it causes.
 * 03_onboard_birthday is cut: compliance, not product.
 */

const filmOpensAt = HEAD;                               // 0.350 → settled 0.885

export const act1: Track[] = [
  { k: "hold", at: 0, dur: HEAD, note: "the beige world, empty, before the voice" },
  { k: "layer", id: "name", at: filmOpensAt, dur: OPEN_IN, via: "settleIn",
    note: "01 settles at 0.885" },
  { k: "focus", at: 0.60, dur: 0.55, to: { ...SUBJECT.nameField, radius: 240, blur: 1.9 },
    note: "the frame is on the input before the first word" },
  { k: "cam", at: 0.95, dur: 1.00,
    to: { fx: SUBJECT.nameField.x, fy: SUBJECT.nameField.y, scale: 1.045, center: 0.32 } },
  ...bloom(NAME.on),
  // the name arrives as it is spoken about
  { k: "el", id: "namePlaceholder", at: 1.24, dur: 0.10,
    from: { opacity: 1 }, to: { opacity: 0 } },
  ...typeBeat("nameValue", 1.28, 0.63, 7, [1, 2, 3, 4, 5, 6, 7], 0.26),
  { k: "hold", at: filmOpensAt + OPEN_IN, dur: NAME.off - (filmOpensAt + OPEN_IN),
    note: "under 'It starts with your name.'" },

  { k: "sfx", at: NAME.off - 0.07, src: "ui_tap", gain: 0.34, note: "Continue" },
  { k: "cross", out: "name", in: "phone", at: NAME.off, dur: CROSS_Q, depth: 400, travel: 64 },
  { k: "sfx", at: NAME.off, src: "whoosh_a", gain: 0.26 },
  { k: "cam", at: NAME.off, dur: CROSS_Q, to: { fx: 215, fy: 300, scale: 1.005, center: 0.15 },
    note: "the camera passes through the cut, not around it" },
  { k: "focus", at: 2.30, dur: 0.45, to: { ...SUBJECT.phoneField, radius: 240, blur: 1.9 } },
  { k: "cam", at: 2.60, dur: 1.30,
    to: { fx: SUBJECT.phoneField.x, fy: SUBJECT.phoneField.y, scale: 1.05, center: 0.35 } },
  ...bloom(PHONE.on),
  // "(305) 555-1234" — the digits sound, the punctuation doesn't
  ...typeBeat("phoneValue", 2.95, 1.05, 14, [2, 3, 4, 7, 8, 9, 10, 11, 12, 13, 14], 0.20),
  { k: "hold", at: NAME.off + CROSS_Q, dur: PHONE.off - (NAME.off + CROSS_Q),
    note: "under the two-sentence verification line" },

  { k: "sfx", at: PHONE.off - 0.07, src: "ui_tap", gain: 0.32, note: "Send code" },
  { k: "cross", out: "phone", in: "commit", at: PHONE.off, dur: CROSS_Q, depth: 400, travel: 64 },
  { k: "sfx", at: PHONE.off, src: "whoosh_b", gain: 0.22 },
  { k: "cam", at: PHONE.off, dur: CROSS_Q, to: { fx: 215, fy: 260, scale: 1.01, center: 0.18 } },
  { k: "focus", at: 5.30, dur: 0.40, to: { ...SUBJECT.chips, radius: 230, blur: 1.9 } },
  { k: "cam", at: 5.45, dur: 0.85,
    to: { fx: SUBJECT.chips.x, fy: SUBJECT.chips.y, scale: 1.05, center: 0.40 } },
  ...bloom(COMMIT.on),
  // the one stagger in the film: the commitments light as she names them,
  // each with the tap that chose it
  { k: "stagger", ids: ["chip0", "chip1", "chip2"], at: COMMIT.on + 0.077,
    dur: 0.28, step: 0.08,
    from: { opacity: 0.35, scale: 0.94 }, to: { opacity: 1, scale: 1 } },
  { k: "sfx", at: 5.72, src: "ui_tap", gain: 0.30 },
  { k: "sfx", at: 5.80, src: "ui_tap", gain: 0.30 },
  { k: "sfx", at: 5.88, src: "ui_tap", gain: 0.30 },

  { k: "sfx", at: COMMIT.off - 0.07, src: "ui_tap", gain: 0.30, note: "Set 3 places" },
  // no whoosh on this one — just the tap. The silences between moves are
  // what let the whooshes that remain actually land.
  { k: "cross", out: "commit", in: "places", at: COMMIT.off, dur: CROSS_T, depth: 400, travel: 56,
    note: "0.18 s — the tightest gap in Act 1, cut on the tap alone" },
  { k: "cam", at: COMMIT.off, dur: CROSS_T, to: { fx: 215, fy: 350, scale: 1.01, center: 0.20 } },
  { k: "focus", at: 6.85, dur: 0.40, to: { ...SUBJECT.placeField, radius: 240, blur: 1.9 } },
  { k: "cam", at: 7.00, dur: 0.90,
    to: { fx: SUBJECT.placeField.x, fy: SUBJECT.placeField.y, scale: 1.045, center: 0.35 } },
  ...bloom(PLACES.on),
  ...typeBeat("placeValue", 7.30, 0.70, 13, [2, 4, 6, 8, 10, 12, 13], 0.16),
  { k: "hold", at: COMMIT.off + CROSS_T, dur: PLACES.off - (COMMIT.off + CROSS_T),
    note: "under 'And exactly where you'll do it.'" },
  { k: "sfx", at: PLACES.off - 0.07, src: "ui_tap", gain: 0.32, note: "Enter Anvil" },
];

/* ==================================================== ACT 2 — THE CONSTRAINT
 * The act slows down and then stops. The hold on the lock is the longest
 * stillness in the film — though "stillness" here means the drift and the
 * camera's breath and nothing else. Nothing is ever locked off.
 */

const toHome   = PLACES.off;                            // 8.115
const homeIn   = toHome + CROSS_ACT;                    // 8.455 settled
const toLocked = HOME.off;                              // 9.541
const lockedIn = toLocked + CROSS;                      // 9.981 settled
const pushAt   = lockedIn + 0.04;                       // 10.021
const holdAt   = pushAt + PUSH;                         // 10.441
/** the camera starts easing out just before the banner does — the
 *  notification is what pulls the frame back off the lock */
const pullAt   = 11.420;
const toastAt  = ARRIVE.on - LEAD - TOAST_IN;           // 11.433

export const act2: Track[] = [
  { k: "cross", out: "places", in: "home", at: toHome, dur: CROSS_ACT, depth: 400,
    travel: 70, note: "into Act 2 — the film slows here" },
  { k: "sfx", at: toHome, src: "whoosh_up", gain: 0.34 },
  { k: "cam", at: toHome, dur: CROSS_ACT, to: { fx: 215, fy: 400, scale: 1.03, center: 0.20 } },
  { k: "cam", at: 8.55, dur: 0.85,
    to: { fx: SUBJECT.commitments.x, fy: SUBJECT.commitments.y, scale: 1.07, center: 0.42 },
    note: "settling onto the commitments before 'This is your word.'" },
  { k: "focus", at: homeIn - 0.2, dur: 0.55,
    to: { ...SUBJECT.commitments, radius: 250, blur: 2.4 },
    note: "the frame is on the commitments before 'This is your word.' lands" },
  { k: "el", id: "focusBloom", at: HOME.on - 0.09, dur: 0.34,
    from: { opacity: 0, scale: 0.7 }, to: { opacity: 0.85, scale: 1 } },
  { k: "el", id: "focusBloom", at: HOME.on + 0.25, dur: 0.7,
    from: { opacity: 0.85 }, to: { opacity: 0.16 } },
  { k: "hold", at: HOME.on, dur: HOME.off - HOME.on,
    note: "under 'This is your word.' — drift only" },

  { k: "cross", out: "home", in: "locked", at: toLocked, dur: CROSS, depth: 400,
    travel: 96, note: "06_home → 07_tab_camera, travelling through the space" },
  // the camera pushes through the cut rather than cutting between two
  // stationary positions
  { k: "cam", at: toLocked, dur: CROSS,
    to: { fx: 215, fy: 560, scale: 1.10, center: 0.30 }, note: "through the cut" },
  { k: "sfx", at: toLocked - 0.07, src: "ui_tap", gain: 0.32, note: "the Camera tab" },
  { k: "sfx", at: toLocked, src: "whoosh_down", gain: 0.38 },
  // The lock LANDS. The screen glides in on the light register while the
  // lock falls onto it in the heavy one, hitting just before the screen
  // settles — the catch is the sound of that landing, not set dressing.
  { k: "land", id: "lock", at: 9.64, dur: 0.42, drop: 30, compress: 2.5,
    note: "contact at 9.884, at rest 10.06 — lead 0.247 on the line" },
  { k: "sfx", at: 9.884, src: "lock_catch", gain: 0.68,
    note: "the sound of the lock landing" },

  // 1.95× fills the whole frame with the phone — no beige left, no exit.
  // Standing at a closed door.
  { k: "cam", at: pushAt, dur: PUSH,
    to: { ...SUBJECT.lock, fx: SUBJECT.lock.x, fy: SUBJECT.lock.y, scale: 1.95, center: 0.90 },
    note: "focusPush into the lock — starts on silence, still moving at 10.307" },
  { k: "focus", at: pushAt, dur: PUSH + 0.16,
    to: { ...SUBJECT.lock, radius: 120, blur: 5.2 },
    note: "the rest of the screen gives way; only the lock stays sharp" },
  { k: "el", id: "focusBloom", at: LOCKED.on - 0.10, dur: 0.36,
    from: { opacity: 0, scale: 0.66 }, to: { opacity: 0.7, scale: 1 } },
  { k: "el", id: "focusBloom", at: LOCKED.on + 0.30, dur: 0.9,
    from: { opacity: 0.7 }, to: { opacity: 0.2 } },

  // The hold. Drift and breath only — 0.79 s of it, landing while she is
  // still speaking and running past the end of the line.
  { k: "hold", at: holdAt, dur: pullAt - holdAt,
    note: "the uncomfortable hold — 0.979 s at full push, drift only, the " +
          "room tone sinking out from under it" },
];

/* ======================================================= ACT 3 — THE UNLOCK
 *
 * The banner is the TRIGGER, not a caption. It arrives while the screen is
 * still visibly locked; the lock then releases on that screen, in place; only
 * then does the film cut to the open camera. Announcing the unlock over a
 * stale locked state was the bug this sequence exists to fix.
 */

const releaseAt = ARRIVE.off;                           // 12.904 — the shackle
const clearAt   = releaseAt + SHACKLE;                  // 13.054 — the lock clears
const openAt    = clearAt + CLEAR;                      // 13.204 — the cut
const opened    = openAt + OPEN;                        // 13.480 = OPENS.on − LEAD

export const act3: Track[] = [
  // 1 — the frame comes off the lock to receive a system notification
  { k: "cam", at: pullAt, dur: 0.40,
    to: { fx: 215, fy: 120, scale: 1.12, center: 0.5 },
    note: "the notification pulls the camera off the lock and up" },
  { k: "focus", at: pullAt, dur: 0.44,
    to: { ...SUBJECT.banner, radius: 270, blur: 2.2 } },
  { k: "layer", id: "toast", at: toastAt, dur: TOAST_IN, via: "revealUp",
    opts: { distance: 46, from: "above" },
    note: "the banner drops over the top edge of the device — settled 11.693" },
  { k: "sfx", at: toastAt + 0.06, src: "arrival", gain: 0.5 },
  { k: "hold", at: toastAt + TOAST_IN, dur: 12.55 - (toastAt + TOAST_IN),
    note: "under 'Until you actually arrive.' — the screen is still locked" },

  // 2 — the frame returns to the lock before the release, not after
  { k: "cam", at: 12.55, dur: 0.36,
    to: { ...SUBJECT.lock, fx: SUBJECT.lock.x, fy: SUBJECT.lock.y, scale: 1.44, center: 0.78 },
    note: "back to the lock while she is still speaking, so the eye is there first" },
  { k: "focus", at: 12.55, dur: 0.36,
    to: { ...SUBJECT.lock, radius: 165, blur: 3.8 } },

  // 3 — the lock releases, on the locked screen, in place
  { k: "sfx", at: releaseAt, src: "unlock", gain: 1.0,
    note: "the biggest sound in the film — the catch giving way, then air" },
  { k: "el", id: "lockShackle", at: releaseAt, dur: SHACKLE,
    from: { y: 0 }, to: { y: -9 },
    note: "the shackle lifts — the only thing moving" },
  { k: "el", id: "lock", at: clearAt, dur: CLEAR,
    from: { opacity: 1, scale: 1 }, to: { opacity: 0, scale: 0.84 } },
  { k: "el", id: "lockCopy", at: clearAt, dur: CLEAR,
    from: { opacity: 1, y: 0 }, to: { opacity: 0, y: 8 },
    note: "'Not there yet' clears — the screen is no longer claiming to be locked" },
  { k: "el", id: "statusLabel", at: clearAt, dur: CLEAR,
    from: { opacity: 1 }, to: { opacity: 0 } },
  { k: "el", id: "toast", at: clearAt, dur: CLEAR + 0.1,
    from: { opacity: 1, y: 0 }, to: { opacity: 0, y: -22 },
    note: "the notification has done its job and withdraws" },

  // 4 — and only then, the cut
  { k: "cross", out: "locked", in: "opened", at: openAt, dur: OPEN, depth: 150,
    aperture: { x: SUBJECT.lock.x, y: SUBJECT.lock.y, radius: 660 },
    note: "07 → 09, opening out of the lock's own centre" },
  { k: "el", id: "warmGlow", at: openAt, dur: 0.5,
    from: { opacity: 0, scale: 0.4 }, to: { opacity: 1, scale: 1 } },
  { k: "el", id: "warmGlow", at: openAt + 0.5, dur: 0.8,
    from: { opacity: 1 }, to: { opacity: 0.3, scale: 1.16 } },
  { k: "cam", at: openAt, dur: OPEN,
    to: { ...SUBJECT.viewfinder, fx: SUBJECT.viewfinder.x, fy: SUBJECT.viewfinder.y,
          scale: 1.08, center: 0.24 },
    note: "the frame opens up as the lock lets go" },
  { k: "focus", at: openAt, dur: OPEN + 0.42,
    to: { ...SUBJECT.viewfinder, radius: 330, blur: 1.5 },
    note: "depth opens with it, but the viewfinder keeps the eye" },
  { k: "cam", at: opened, dur: 0.86,
    to: { fx: 215, fy: 466, scale: 1.0, center: 0 },
    note: "the last of the pull-back, decelerating under the line" },

  { k: "land", id: "opened", target: "layer", at: opened, dur: 0.30, drop: 0, compress: 3.5,
    note: "the open camera absorbs its own arrival — weight, not float" },
  { k: "hold", at: opened, dur: LEAD, note: "the aftermath — 09 settled at 13.480" },
  { k: "el", id: "focusBloom", at: OPENS.on - 0.10, dur: 0.38,
    from: { opacity: 0, scale: 0.7 }, to: { opacity: 0.66, scale: 1 } },
  { k: "el", id: "focusBloom", at: OPENS.on + 0.3, dur: 0.9,
    from: { opacity: 0.66 }, to: { opacity: 0 } },
  { k: "hold", at: OPENS.on, dur: OPENS.off - OPENS.on,
    note: "'Then it opens.' lands on a settled screen" },
];

/* ========================================================= ACT 4 — THE LOOP
 * Cut hard. 0.24 s and 0.20 s — seven and six frames. After Act 2's hold the
 * rhythm reads as a snap, which is the point: you arrive, the camera opens,
 * the proof is up. The frame is still directed inside the snap: each cut
 * lands already pointed at its line's subject.
 */

export const act4: Track[] = [
  { k: "sfx", at: OPENS.off, src: "shutter", gain: 0.5, note: "the proof posts" },
  { k: "cross", out: "opened", in: "proof", at: OPENS.off, dur: CUT_PROOF, depth: 400, travel: 46,
    note: "the snap — 7 frames, no hold on either side" },
  { k: "cam", at: OPENS.off, dur: CUT_PROOF,
    to: { fx: SUBJECT.proofPhoto.x, fy: SUBJECT.proofPhoto.y, scale: 1.07, center: 0.35 } },
  { k: "focus", at: OPENS.off, dur: CUT_PROOF + 0.02,
    to: { ...SUBJECT.proofPhoto, radius: 230, blur: 2.6 } },
  ...bloom(PROOF.on),
  { k: "cam", at: 14.95, dur: 0.38,
    to: { fx: SUBJECT.proofPhoto.x, fy: SUBJECT.proofPhoto.y, scale: 1.10, center: 0.45 },
    note: "a short push into the photo under 'Proof,'" },
  // THE SHADOW. "Proof," is the photo; "not words." is Mara, who said she
  // would come and hasn't. The frame drops to her row and just sits there —
  // no bloom, no commentary. The app shows who didn't show up.
  { k: "focus", at: 15.35, dur: 0.42, to: { ...SUBJECT.maraRow, radius: 150, blur: 3.2 },
    note: "arrives at 15.77, before 'not words.' lands at 15.816" },
  { k: "cam", at: 15.35, dur: 0.50,
    to: { fx: SUBJECT.maraRow.x, fy: SUBJECT.maraRow.y, scale: 1.12, center: 0.50 },
    note: "0.77 s on 'Mara — not yet' before the cut" },
  { k: "hold", at: OPENS.off + CUT_PROOF, dur: PROOF.off - (OPENS.off + CUT_PROOF),
    note: "under 'Proof, not words.'" },

  { k: "cross", out: "proof", in: "seen", at: PROOF.off, dur: CUT_SEEN, depth: 400, travel: 40,
    note: "6 frames — the fastest cut in the film" },
  { k: "sfx", at: PROOF.off, src: "whoosh_c", gain: 0.20 },
  { k: "cam", at: PROOF.off, dur: CUT_SEEN,
    to: { fx: SUBJECT.friendRow.x, fy: SUBJECT.friendRow.y, scale: 1.06, center: 0.40 } },
  { k: "focus", at: PROOF.off, dur: CUT_SEEN + 0.02,
    to: { ...SUBJECT.friendRow, radius: 200, blur: 2.6 } },
  ...bloom(CIRCLE.on),
  // "Your circle sees it." is the banner; "And you see them." is the list —
  // the frame moves between the line's two halves, arriving before the second
  { k: "focus", at: 17.90, dur: 0.40, to: { ...SUBJECT.friendList, radius: 260, blur: 2.2 } },
  { k: "cam", at: 17.90, dur: 0.55,
    to: { fx: SUBJECT.friendList.x, fy: SUBJECT.friendList.y, scale: 1.05, center: 0.35 } },
  ...bloom(VO.circle.on + VO_AT + 1.321, 0.4),   // 18.308 — the second half lands
  { k: "hold", at: PROOF.off + CUT_SEEN, dur: CIRCLE.off - (PROOF.off + CUT_SEEN),
    note: "under 'Your circle sees it. And you see them.'" },
];

/* ==================================================== ACT 5 — THE LONG GAME */

export const act5: Track[] = [
  { k: "sfx", at: CIRCLE.off - 0.06, src: "ui_tap", gain: 0.30, note: "the Routine tab" },
  { k: "cross", out: "seen", in: "routine", at: CIRCLE.off, dur: CROSS_LONG, depth: 400, travel: 48 },
  { k: "sfx", at: CIRCLE.off, src: "whoosh_down", gain: 0.24 },
  { k: "cam", at: CIRCLE.off, dur: CROSS_LONG, to: { fx: 215, fy: 250, scale: 1.02, center: 0.25 } },
  { k: "focus", at: 19.10, dur: 0.35, to: { ...SUBJECT.weekRow, radius: 230, blur: 2.4 } },
  { k: "cam", at: 19.25, dur: 0.70,
    to: { fx: SUBJECT.weekRow.x, fy: SUBJECT.weekRow.y, scale: 1.08, center: 0.50 } },
  ...bloom(COMPOUND.on),
  // the filled days pop one at a time, a small ascending tick under each —
  // "Show up enough" drawn as marks landing
  { k: "stagger", ids: ["day0", "day1", "day2", "day3"], at: 19.55, dur: 0.30, step: 0.17,
    from: { opacity: 0.25, scale: 0.55 }, to: { opacity: 1, scale: 1 } },
  { k: "sfx", at: 19.58, src: "tick0", gain: 0.45 },
  { k: "sfx", at: 19.75, src: "tick1", gain: 0.45 },
  { k: "sfx", at: 19.92, src: "tick2", gain: 0.45 },
  { k: "sfx", at: 20.09, src: "tick3", gain: 0.45 },
  // "…and it compounds." — the frame drops to the streak as the words land
  { k: "focus", at: 20.15, dur: 0.40, to: { ...SUBJECT.streak, radius: 200, blur: 2.6 } },
  { k: "cam", at: 20.15, dur: 0.55,
    to: { fx: SUBJECT.streak.x, fy: SUBJECT.streak.y, scale: 1.10, center: 0.55 } },
  ...bloom(20.485, 0.5),
  { k: "hold", at: CIRCLE.off + CROSS_LONG, dur: COMPOUND.off - (CIRCLE.off + CROSS_LONG),
    note: "under 'Show up enough, and it compounds.'" },
];

/* ====================================================== THE SILENT ENDING
 * The voice has stopped for good. Nothing here is scored; the room tone is
 * the only thing left, so the silence has texture instead of sounding like
 * the file gave out. The frame lets go of everything it was holding — depth
 * of field clears, the camera returns to rest, the screen recedes.
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
  { k: "focus", at: 21.40, dur: 0.85, to: { x: 215, y: 466, radius: 1200, blur: 0 },
    note: "depth of field lets go with the voice" },
  { k: "cam", at: 21.42, dur: 0.95, to: { fx: 215, fy: 466, scale: 1.0, center: 0 },
    note: "the camera returns to rest" },
  { k: "el", id: "focusBloom", at: 21.35, dur: 0.5, from: {}, to: { opacity: 0 } },
  { k: "hold", at: voiceEnds, dur: beat - voiceEnds,
    note: "hold on the routine screen — the voice is gone and the film knows it" },
  { k: "exit", id: "routine", at: beat, dur: receded - beat, depth: 520,
    note: "everything recedes" },
  { k: "el", id: "warmGlow", at: beat, dur: (receded - beat) * 0.7,
    from: { opacity: 0.3 }, to: { opacity: 0 } },
  { k: "hold", at: receded, dur: markAt - receded,
    note: "the beige space alone, 0.32 s — the silence is the ending" },

  { k: "layer", id: "logo", at: markAt, dur: 0, via: "settleIn",
    note: "the lockup layer opens; its parts arrive one at a time" },
  // an anvil does not fade in. It lands — silently; the ending stays unscored
  { k: "land", id: "mark", at: markAt, dur: markDone - markAt, drop: 40, compress: 3,
    note: "the mark falls into place, compresses, and is still" },
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

export interface LayerDef {
  space: "phone" | "camera" | "stage";
  screens: string[];
  /** camera-space layers are hung at an explicit box in phone coordinates */
  box?: { x: number; y: number; w: number; h: number };
}

/** Which SVGs compose each layer, bottom to top, and where it lives. */
export const LAYERS: Record<string, LayerDef> = {
  name:    { space: "phone", screens: ["01_onboard_name"] },
  phone:   { space: "phone", screens: ["02_onboard_phone"] },
  commit:  { space: "phone", screens: ["04_onboard_commitments"] },
  places:  { space: "phone", screens: ["05_onboard_places"] },
  home:    { space: "phone", screens: ["06_home"] },
  locked:  { space: "phone", screens: ["07_locked"] },
  opened:  { space: "phone", screens: ["09_unlocked"] },
  proof:   { space: "phone", screens: ["11_circle_live"] },
  seen:    { space: "phone", screens: ["10_friend_arrived"] },
  routine: { space: "phone", screens: ["07_tab_routine"] },
  // The arrival banner is a SYSTEM notification, so it is hung across the top
  // edge of the device — wider than the device, outside its clip, and above
  // every app layer. Inside the frame it read as a caption on the app's own
  // state, which is the one thing it must not be.
  toast:   { space: "camera", screens: ["08_toast"],
             box: { x: -16, y: -78, w: 462, h: 116 } },
  logo:    { space: "stage", screens: ["logo"] },
};

export const film: Track[] = [...act1, ...act2, ...act3, ...act4, ...act5, ...ending];

export const SECTION = {
  full:  { from: 0, to: filmEnds },
  act1:  { from: 0, to: HOME.on },
  act23: { from: 8.00, to: 14.40 },
  act45: { from: OPENS.off, to: voiceEnds },
  end:   { from: voiceEnds - 0.6, to: filmEnds },
};

export const duration = filmEnds;
