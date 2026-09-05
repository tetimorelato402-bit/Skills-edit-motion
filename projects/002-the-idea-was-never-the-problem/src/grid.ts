/**
 * THE GRID — 90 BPM at 60fps.
 *
 * The whole point of choosing 90 at 60fps is that every subdivision is a whole
 * number of frames. Nothing in this film is ever timed in seconds or in
 * fractions of a scene; everything is written in frames off this grid, so a
 * timing change is an integer change and the audio can be derived from the same
 * constants.
 */

export const FPS = 60;
export const BPM = 90;

/** 60 fps * 60 s / 90 bpm = 40 frames per beat. */
export const BEAT = 40;
export const EIGHTH = BEAT / 2; // 20
export const SIXTEENTH = BEAT / 4; // 10
export const BAR = BEAT * 4; // 160

/** 9 bars exactly. 1440 frames = 24.000s. */
export const TOTAL_FRAMES = BAR * 9; // 1440

export const WIDTH = 1080;
export const HEIGHT = 1920;
export const SQUARE_FORMAT = 1080;

/** Section boundaries, in frames. Every one is a bar line. */
export const ACT_I = {start: 0, end: BAR * 3} as const; // 0 – 480
export const TURN = {start: BAR * 3, end: BAR * 4} as const; // 480 – 640
export const ACT_II = {start: BAR * 4, end: BAR * 8} as const; // 640 – 1280
export const THE_LINE = {start: BAR * 8, end: BAR * 9} as const; // 1280 – 1440

/** Frame of beat `n` counted from frame 0 of the film. */
export const bt = (n: number): number => n * BEAT;

/** Frame of bar `n` (1-indexed, the way a musician counts). */
export const barline = (n: number): number => (n - 1) * BAR;

/**
 * Every event in the Turn, Act II and The Line lands on a multiple of 5 — a
 * thirty-second note. Call this on every literal frame number those sections
 * use, so a mistyped constant fails at module load rather than in the render.
 */
export const assertGrid = (frame: number, label: string): number => {
  if (!Number.isInteger(frame)) {
    throw new Error(`assertGrid: "${label}" is ${frame}, not an integer frame`);
  }
  if (frame < 0) {
    throw new Error(`assertGrid: "${label}" is ${frame}, before the film starts`);
  }
  if (frame % 5 !== 0) {
    throw new Error(
      `assertGrid: "${label}" is frame ${frame}, which is off the grid. ` +
        `Events must land on a multiple of 5 (nearest: ${Math.round(frame / 5) * 5}).`,
    );
  }
  return frame;
};

/**
 * The escape hatch, and the only one. Act I is deliberately off the grid: the
 * ticks in the audio are on 90 BPM and the picture is not, so sound and image
 * never agree and the viewer feels wrong without being able to name it.
 *
 * This throws on anything that IS on the grid, which is the inverse of
 * assertGrid — it exists so that "fixing" an Act I timing to a round number
 * fails loudly instead of quietly destroying the effect.
 */
export const OFF_GRID = (frame: number, label: string): number => {
  if (!Number.isInteger(frame)) {
    throw new Error(`OFF_GRID: "${label}" is ${frame}, not an integer frame`);
  }
  if (frame < 0) {
    throw new Error(`OFF_GRID: "${label}" is ${frame}, before the film starts`);
  }
  if (frame % 5 === 0) {
    throw new Error(
      `OFF_GRID: "${label}" is frame ${frame}, which is ON the grid. ` +
        `Act I must not agree with the beat — this is deliberate, do not round it.`,
    );
  }
  return frame;
};
