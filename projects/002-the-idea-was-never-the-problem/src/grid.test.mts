import test from 'node:test';
import assert from 'node:assert/strict';
import {
  ACT_I,
  ACT_II,
  BAR,
  BEAT,
  EIGHTH,
  FPS,
  OFF_GRID,
  SIXTEENTH,
  THE_LINE,
  TOTAL_FRAMES,
  TURN,
  assertGrid,
  barline,
  bt,
} from './grid.ts';

test('the grid is whole frames all the way down', () => {
  assert.equal(FPS * 60 / 90, BEAT, '90 BPM at 60fps must be exactly 40 frames');
  assert.equal(BEAT, 40);
  assert.equal(EIGHTH, 20);
  assert.equal(SIXTEENTH, 10);
  assert.equal(BAR, 160);
  for (const unit of [BEAT, EIGHTH, SIXTEENTH, BAR]) {
    assert.ok(Number.isInteger(unit), `${unit} is not a whole frame count`);
  }
});

test('the film is nine bars exactly', () => {
  assert.equal(TOTAL_FRAMES, 1440);
  assert.equal(TOTAL_FRAMES / BAR, 9);
  assert.equal(TOTAL_FRAMES / FPS, 24);
});

test('sections tile the film with no gap and no overlap', () => {
  assert.equal(ACT_I.start, 0);
  assert.equal(ACT_I.end, TURN.start);
  assert.equal(TURN.end, ACT_II.start);
  assert.equal(ACT_II.end, THE_LINE.start);
  assert.equal(THE_LINE.end, TOTAL_FRAMES);
  for (const s of [ACT_I, TURN, ACT_II, THE_LINE]) {
    assert.equal(s.start % BAR, 0, 'every section starts on a bar line');
  }
});

test('bt and barline agree', () => {
  assert.equal(bt(0), 0);
  assert.equal(bt(4), BAR);
  assert.equal(barline(1), 0);
  assert.equal(barline(5), ACT_II.start);
  assert.equal(barline(9), THE_LINE.start);
});

test('assertGrid passes multiples of 5 and returns the frame', () => {
  assert.equal(assertGrid(0, 'zero'), 0);
  assert.equal(assertGrid(640, 'act ii'), 640);
  assert.equal(assertGrid(1435, 'late'), 1435);
});

test('assertGrid throws off the grid, and names the nearest legal frame', () => {
  assert.throws(() => assertGrid(37, 'x'), /off the grid/);
  assert.throws(() => assertGrid(37, 'x'), /nearest: 35/);
  assert.throws(() => assertGrid(-5, 'x'), /before the film starts/);
  assert.throws(() => assertGrid(12.5, 'x'), /not an integer frame/);
});

test('OFF_GRID is the exact inverse, and refuses to be rounded', () => {
  for (const f of [37, 113, 189, 266, 344]) {
    assert.equal(OFF_GRID(f, 'act i'), f);
  }
  assert.throws(() => OFF_GRID(40, 'x'), /is ON the grid/);
  assert.throws(() => OFF_GRID(0, 'x'), /is ON the grid/);
  assert.throws(() => OFF_GRID(-3, 'x'), /before the film starts/);
});

test('no frame is legal to both', () => {
  for (let f = 0; f < TOTAL_FRAMES; f++) {
    const onGrid = (() => {
      try {
        assertGrid(f, 't');
        return true;
      } catch {
        return false;
      }
    })();
    const offGrid = (() => {
      try {
        OFF_GRID(f, 't');
        return true;
      } catch {
        return false;
      }
    })();
    assert.notEqual(onGrid, offGrid, `frame ${f} passed both or neither`);
  }
});
