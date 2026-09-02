/**
 * PALETTE, TYPE AND EASING.
 *
 * The palette is sampled from study-001-v10 — the warm direction. Nothing here
 * is invented; if a colour is needed that is not in this file, the answer is
 * that it is not needed.
 */

export const C = {
  /** the light ground */
  BONE: '#C8BFAA',
  /** raised surfaces */
  BONE_LIGHT: '#D6CFBE',
  /** the dark ground */
  UMBER: '#220C06',
  /** panels on dark */
  UMBER_MID: '#3A2418',
  /** the accent — one word at a time, never two */
  RUST: '#A03A22',
  /** secondary accent, used twice in the whole film */
  OCHRE: '#B8843A',
  /** captions and the square */
  GREY: '#8B8475',
} as const;

/**
 * TWO SIZES. Nothing between 14px and 179px exists in this film — emotion comes
 * from scale and silence, never from switching typeface. verify.mjs enforces it.
 */
export const TYPE = {
  DISPLAY: {
    fontFamily: "'Inter', sans-serif",
    fontSize: 180,
    fontWeight: 800,
    // Large grotesk needs negative tracking to hold together, and it is what
    // lets "something" sit inside 1080 with real margins. Identical in both
    // acts, so it can never be the thing a viewer points at.
    letterSpacing: '-0.035em',
    lineHeight: 0.94,
  },
  MICRO: {
    fontFamily: "'IBM Plex Mono', monospace",
    fontSize: 13,
    fontWeight: 500,
    letterSpacing: '0.22em',
    textTransform: 'uppercase' as const,
    lineHeight: 1.4,
  },
} as const;

/**
 * LAYOUT — shared by both acts, byte for byte.
 *
 * §13 of the brief: the two halves must be pixel-identical in composition. That
 * is only guaranteed if there is exactly one source for these numbers, so both
 * acts import this object and neither is allowed a literal of its own.
 */
export const LAYOUT = {
  SQUARE: 340,
  /**
   * Top edge of the square. Sits in the upper third, and high enough that the
   * whole block — square plus four lines — clears the Reels chrome at the
   * bottom of the frame with ~400px to spare. Checked at phone size, not at
   * full size; several vertical positions that looked balanced on a monitor
   * put "new." underneath the caption.
   */
  SQUARE_TOP: 420,
  /** top of the first line of the sentence */
  TEXT_TOP: 880,
  /** distance from one baseline block to the next */
  LINE_STEP: 180 * 0.94,
  EYEBROW: {top: 78, left: 80},
} as const;

export const SENTENCE = ["We're", 'launching', 'something', 'new.'] as const;

export const EYEBROW_TEXT = 'STILL. — MOTION STUDIES';

/**
 * EASING.
 *
 * Act I gets `linear` and nothing else — that is the whole argument of the act,
 * and verify.mjs greps for any other curve inside ActI.tsx.
 */
export const EASE = {
  /** the default for Act II: a long, confident deceleration */
  OUT: [0.22, 1, 0.36, 1] as const,
  /** for anticipation — pulls back slowly, releases */
  IN_OUT: [0.65, 0, 0.35, 1] as const,
} as const;

/**
 * T1 TEXTURE PASS — plate opacities.
 *
 * The brief specifies these as percentages (paper 6%, crumple 3%, grain 1.5%).
 * Those numbers only mean something once the plate's own contrast is fixed, and
 * a percentage is not a look — so what is calibrated here is the *result*: the
 * deviation the pass produces on the flat BONE ground, measured off a rendered
 * frame with `scripts/measure-texture.py`. The brief's percentages are the
 * starting point and the target order of magnitude; these are what hits it.
 *
 * Each surface is a dark plate multiplied and a light plate screened, from one
 * field split at zero — see scripts/texture.py for why. On a light ground the
 * multiply side has roughly 3.6x the gain of the screen side, which is why the
 * screen numbers look large next to the multiply ones; on UMBER it inverts and
 * the same pair lifts the blacks with no second set of plates.
 */
export const TEXTURE = {
  PAPER_DARK: 0.1,
  PAPER_LIGHT: 0.18,
  CRUMPLE_DARK: 0.04,
  CRUMPLE_LIGHT: 0.07,
  GRAIN: 0.05,
} as const;
