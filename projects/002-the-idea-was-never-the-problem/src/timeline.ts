// Explicit extension: scripts/verify.mjs imports this file directly through
// node's type stripping, and node's ESM resolver does not guess extensions.
import {ACT_I, OFF_GRID} from './grid.ts';

/**
 * EVERY EVENT IN THE FILM, IN FRAMES.
 *
 * Kept out of the components on purpose. Three things read these numbers — the
 * picture, the verification script and (once it exists) the audio — and if any
 * of them held its own copy they would drift. The soundtrack is frame-exact
 * only because it is derived from this file rather than transcribed from it.
 */

/**
 * ACT I — deliberately between the beats.
 *
 * The ticks in the audio sit on 90 BPM and these do not, so sound and picture
 * never agree and the viewer feels wrong without being able to name it.
 * OFF_GRID throws on anything divisible by 5, so a well-meaning future edit
 * that rounds these to the grid fails loudly instead of quietly deleting the
 * point of the act.
 */
export const A1 = {
  SQUARE: OFF_GRID(37, 'Act I square in'),
  WORDS: [
    OFF_GRID(113, "Act I: We're"),
    OFF_GRID(189, 'Act I: launching'),
    OFF_GRID(266, 'Act I: something'),
    OFF_GRID(344, 'Act I: new.'),
  ],
  SQUARE_FADE: 20,
  WORD_FADE: 12,
  /** everything has arrived; from here the frame does not change */
  SETTLED: 400,
} as const;

export const ACT_I_DURATION = ACT_I.end - ACT_I.start; // 480
