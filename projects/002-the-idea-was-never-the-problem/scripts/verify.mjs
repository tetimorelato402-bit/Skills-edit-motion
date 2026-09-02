/**
 * VERIFICATION — §12 of the brief.
 *
 * The build fails on any of these. Several checks are inverted on purpose: Act I
 * must be OFF the grid and must contain no easing but linear, and a well-meaning
 * "fix" to either is the most likely way this film quietly stops working.
 *
 * Checks for sections that do not exist yet report PENDING, not PASS. A green
 * report on an unbuilt film would be worse than no report.
 *
 *   node --experimental-strip-types scripts/verify.mjs
 */
import {readFileSync, existsSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
import {dirname, join} from 'node:path';
import {TOTAL_FRAMES, FPS} from '../src/grid.ts';
import {TYPE, C} from '../src/theme.ts';
import {A1, ACT_I_DURATION} from '../src/timeline.ts';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
const read = (p) => readFileSync(join(ROOT, p), 'utf8');

const results = [];
const check = (name, fn) => {
  try {
    const note = fn();
    results.push({state: 'PASS', name, note: note ?? ''});
  } catch (e) {
    results.push({state: 'FAIL', name, note: e.message});
  }
};
const pending = (name, why) => results.push({state: 'PEND', name, note: why});
const assert = (cond, msg) => {
  if (!cond) throw new Error(msg);
};

// ---------------------------------------------------------------- the grid

check('the film is 1440 frames / 24.000s', () => {
  assert(TOTAL_FRAMES === 1440, `TOTAL_FRAMES is ${TOTAL_FRAMES}`);
  assert(TOTAL_FRAMES / FPS === 24, 'not 24.000s');
  return '1440 @ 60fps';
});

check('Act I events are all OFF the grid (inverted on purpose)', () => {
  const events = [A1.SQUARE, ...A1.WORDS];
  for (const f of events) {
    assert(f % 5 !== 0, `frame ${f} is on the grid — Act I must not agree with the beat`);
  }
  return events.join(', ');
});

check('Act I spans exactly three bars', () => {
  assert(ACT_I_DURATION === 480, `Act I is ${ACT_I_DURATION} frames`);
  const last = Math.max(...A1.WORDS) + A1.WORD_FADE;
  assert(last < A1.SETTLED, `last word lands at ${last}, after the settle at ${A1.SETTLED}`);
  assert(ACT_I_DURATION - A1.SETTLED === 80, 'the held silence is not 80 frames');
  return `settles at ${last}, holds ${ACT_I_DURATION - A1.SETTLED} frames`;
});

check('Act I word spacing is uniform (no rhythm)', () => {
  const gaps = A1.WORDS.slice(1).map((f, i) => f - A1.WORDS[i]);
  const spread = Math.max(...gaps) - Math.min(...gaps);
  // 76/77/78: within a sixteenth of each other, so it reads as metronomic.
  assert(spread < 10, `word gaps ${gaps.join('/')} vary by ${spread} frames — that is rhythm`);
  return `gaps ${gaps.join('/')} frames`;
});

// ----------------------------------------------------------------- the type

check('no type between 14px and 179px', () => {
  for (const [token, spec] of Object.entries(TYPE)) {
    const s = spec.fontSize;
    assert(!(s > 14 && s < 180), `${token} is ${s}px, inside the forbidden band`);
  }
  return `${TYPE.MICRO.fontSize}px and ${TYPE.DISPLAY.fontSize}px, nothing between`;
});

check('exactly two faces in the whole film', () => {
  const families = new Set(
    Object.values(TYPE).map((t) => t.fontFamily.split(',')[0].trim()),
  );
  assert(families.size === 2, `${families.size} faces: ${[...families].join(', ')}`);
  return [...families].join(' + ');
});

// ------------------------------------------------------------------- Act I

check('Act I uses no easing but linear', () => {
  const src = read('src/ActI.tsx');
  const code = src.replace(/\/\*[\s\S]*?\*\/|\/\/.*$/gm, ''); // prose may name them
  for (const banned of ['Easing', 'spring(', 'cubic-bezier', 'bezier', 'EASE']) {
    assert(!code.includes(banned), `ActI.tsx references "${banned}"`);
  }
  assert(code.includes('interpolate('), 'Act I does not interpolate anything');
  return 'linear only';
});

check('Act I animates opacity and nothing else', () => {
  const code = read('src/ActI.tsx').replace(/\/\*[\s\S]*?\*\/|\/\/.*$/gm, '');
  for (const prop of ['dy=', 'blur=', 'scale=']) {
    assert(!code.includes(prop), `ActI.tsx drives "${prop}" — Act I is opacity only`);
  }
  return 'opacity only';
});

check('RUST never appears in Act I', () => {
  const code = read('src/ActI.tsx').replace(/\/\*[\s\S]*?\*\/|\/\/.*$/gm, '');
  assert(!code.includes('RUST'), 'Act I uses the accent — it is saved for Act II');
  assert(C.RUST === '#A03A22', 'RUST has been altered');
  return 'accent unspent';
});

check('both acts share one layout source', () => {
  const theme = read('src/theme.ts');
  assert(theme.includes('LAYOUT'), 'no LAYOUT block in theme.ts');
  for (const file of ['src/components/Square.tsx', 'src/components/Word.tsx']) {
    const code = read(file).replace(/\/\*[\s\S]*?\*\/|\/\/.*$/gm, '');
    assert(code.includes('LAYOUT.'), `${file} does not read LAYOUT`);
    assert(
      !/top:\s*\d{3}/.test(code),
      `${file} hard-codes a position — the two acts must not be able to drift`,
    );
  }
  return 'LAYOUT is the only source of position';
});

// ---------------------------------------------------------------- not built

pending('every Act II / The Line event on a multiple of 5', 'Act II not built — stop gate');
pending('RUST on at most one word per frame', 'the RUST word lives in Act II');
pending('audio RMS is exactly zero, frames 480–560', 'audio not built');
pending('frame 400 and frame 1000 are the same image', 'Act II not built');

// ------------------------------------------------------------------ report

const w = Math.max(...results.map((r) => r.name.length));
const lines = results.map((r) => `  ${r.state}  ${r.name.padEnd(w)}  ${r.note}`);
const failed = results.filter((r) => r.state === 'FAIL').length;
const passed = results.filter((r) => r.state === 'PASS').length;
const pend = results.filter((r) => r.state === 'PEND').length;
const report = [
  'STILL. — "The idea was never the problem"',
  'verification report — Act I stop gate',
  '',
  ...lines,
  '',
  `${passed} passed, ${failed} failed, ${pend} pending`,
].join('\n');

console.log(report);
if (existsSync(join(ROOT, 'outputs'))) {
  const {writeFileSync} = await import('node:fs');
  writeFileSync(join(ROOT, 'outputs/idea-verify-report.txt'), report + '\n');
}
process.exit(failed > 0 ? 1 : 0);
