import { test, describe } from "node:test";
import assert from "node:assert/strict";
import { apply, view, parseAction, isFaded, TOTAL, CARDS_PER_ROUND, ROUND_COUNT, type Game } from "./game.ts";

const NOW = Date.UTC(2026, 0, 1);
const base = (over: Partial<Game> = {}): Game => ({
  id: "00000000-0000-0000-0000-000000000000",
  mode: "couples",
  p1: "tok-1",
  p2: "tok-2",
  round: 0,
  idx: 0,
  answers: {},
  shared: {},
  status: "playing",
  ends_at: null,
  version: 3,
  ...over,
});
const ok = (r: ReturnType<typeof apply>) => { assert.equal(r.ok, true, r.ok ? "" : r.error); return (r as { ok: true; patch: Partial<Game> }).patch; };
const err = (r: ReturnType<typeof apply>, status: number) => { assert.equal(r.ok, false); assert.equal((r as { status: number }).status, status); };

describe("view", () => {
  test("never exposes seat tokens", () => {
    const v = view(base(), "p1", NOW) as unknown as Record<string, unknown>;
    assert.equal(v.p1, undefined);
    assert.equal(v.p2, undefined);
    assert.equal(JSON.stringify(v).includes("tok-"), false);
  });

  test("hides the other answer until both exist", () => {
    const g = base({ answers: { "0-0": { p2: "theirs" }, "0-1": { p1: "a", p2: "b" } } });
    const v1 = view(g, "p1", NOW);
    assert.deepEqual(v1.answers["0-0"], undefined);
    assert.deepEqual(v1.answers["0-1"], { p1: "a", p2: "b" });
    const v2 = view(g, "p2", NOW);
    assert.deepEqual(v2.answers["0-0"], { p2: "theirs" });
  });

  test("describes the current card", () => {
    const v = view(base({ round: 1, idx: 2 }), "p2", NOW);
    assert.equal(v.key, "1-2");
    assert.equal(v.n, 1 * CARDS_PER_ROUND + 3);
    assert.equal(v.total, TOTAL);
    assert.equal(v.roundName, "between");
    assert.equal(typeof v.card, "string");
    assert.equal(v.ready, true);
    assert.equal(v.faded, false);
  });

  test("has no card before a mode is picked", () => {
    const v = view(base({ mode: null }), "p1", NOW);
    assert.equal(v.mode, null);
    assert.equal(v.card, null);
  });
});

describe("mode", () => {
  test("waits for the second seat", () => err(apply(base({ mode: null, p2: null, status: "waiting" }), "p1", { type: "mode", mode: "exes" }, NOW), 409));
  test("either seat can pick once", () => {
    assert.deepEqual(ok(apply(base({ mode: null }), "p2", { type: "mode", mode: "exes" }, NOW)), { mode: "exes" });
    err(apply(base(), "p1", { type: "mode", mode: "exes" }, NOW), 409);
  });
  test("rejects unknown modes", () => err(apply(base({ mode: null }), "p1", { type: "mode", mode: "friends" as never }, NOW), 400));
});

describe("answer", () => {
  test("locks a trimmed answer for the current card", () => {
    const p = ok(apply(base(), "p1", { type: "answer", key: "0-0", text: "  hey  " }, NOW));
    assert.deepEqual(p.answers, { "0-0": { p1: "hey" } });
  });
  test("keeps the other seat's answer", () => {
    const p = ok(apply(base({ answers: { "0-0": { p2: "b" } } }), "p1", { type: "answer", key: "0-0", text: "a" }, NOW));
    assert.deepEqual(p.answers, { "0-0": { p1: "a", p2: "b" } });
  });
  test("cannot be changed after locking", () => err(apply(base({ answers: { "0-0": { p1: "a" } } }), "p1", { type: "answer", key: "0-0", text: "b" }, NOW), 409));
  test("must be for the current card", () => err(apply(base(), "p1", { type: "answer", key: "0-1", text: "a" }, NOW), 409));
  test("rejects empty and oversized text", () => {
    err(apply(base(), "p1", { type: "answer", key: "0-0", text: "   " }, NOW), 400);
    err(apply(base(), "p1", { type: "answer", key: "0-0", text: "x".repeat(201) }, NOW), 400);
  });
  test("needs a mode", () => err(apply(base({ mode: null }), "p1", { type: "answer", key: "0-0", text: "a" }, NOW), 409));
});

describe("next", () => {
  const both = { "0-0": { p1: "a", p2: "b" } };
  test("needs both answers", () => err(apply(base({ answers: { "0-0": { p1: "a" } } }), "p1", { type: "next", key: "0-0" }, NOW), 409));
  test("advances within a round", () => assert.deepEqual(ok(apply(base({ answers: both }), "p2", { type: "next", key: "0-0" }, NOW)), { round: 0, idx: 1 }));
  test("wraps into the next round", () => {
    const g = base({ round: 0, idx: CARDS_PER_ROUND - 1, answers: { [`0-${CARDS_PER_ROUND - 1}`]: { p1: "a", p2: "b" } } });
    assert.deepEqual(ok(apply(g, "p1", { type: "next", key: `0-${CARDS_PER_ROUND - 1}` }, NOW)), { round: 1, idx: 0 });
  });
  test("finishes after the last card and fades seven days later", () => {
    const key = `${ROUND_COUNT - 1}-${CARDS_PER_ROUND - 1}`;
    const g = base({ round: ROUND_COUNT - 1, idx: CARDS_PER_ROUND - 1, answers: { [key]: { p1: "a", p2: "b" } } });
    const p = ok(apply(g, "p1", { type: "next", key }, NOW));
    assert.equal(p.status, "done");
    assert.equal(p.ends_at, new Date(NOW + 7 * 864e5).toISOString());
    assert.equal(isFaded({ ends_at: p.ends_at! }, NOW + 8 * 864e5), true);
    assert.equal(isFaded({ ends_at: p.ends_at! }, NOW + 6 * 864e5), false);
  });
  test("is a no-op when the other player already advanced", () => {
    assert.deepEqual(ok(apply(base({ idx: 1, answers: both }), "p1", { type: "next", key: "0-0" }, NOW)), {});
  });
});

describe("share", () => {
  const done = base({ status: "done", answers: { "0-0": { p1: "a", p2: "b" }, "0-1": { p1: "c", p2: "d" } } });
  test("only after the game", () => err(apply(base({ answers: done.answers }), "p1", { type: "share", text: "a" }, NOW), 409));
  test("only one of your own answers", () => {
    err(apply(done, "p1", { type: "share", text: "b" }, NOW), 400);
    err(apply(done, "p1", { type: "share", text: "nope" }, NOW), 400);
  });
  test("can be changed", () => {
    assert.deepEqual(ok(apply(done, "p1", { type: "share", text: "c" }, NOW)), { shared: { p1: "c" } });
    assert.deepEqual(ok(apply({ ...done, shared: { p1: "c", p2: "d" } }, "p1", { type: "share", text: "a" }, NOW)), { shared: { p1: "a", p2: "d" } });
  });
});

describe("faded games", () => {
  const past = new Date(NOW - 1000).toISOString();
  test("refuse every action", () => {
    err(apply(base({ status: "done", ends_at: past }), "p1", { type: "share", text: "a" }, NOW), 410);
    assert.equal(view(base({ status: "done", ends_at: past }), "p1", NOW).faded, true);
  });
});

describe("parseAction", () => {
  test("accepts well-formed bodies", () => {
    assert.deepEqual(parseAction({ type: "mode", mode: "strangers" }), { type: "mode", mode: "strangers" });
    assert.deepEqual(parseAction({ type: "answer", key: "0-0", text: "hi" }), { type: "answer", key: "0-0", text: "hi" });
    assert.deepEqual(parseAction({ type: "next", key: "0-0" }), { type: "next", key: "0-0" });
    assert.deepEqual(parseAction({ type: "share", text: "hi" }), { type: "share", text: "hi" });
  });
  test("rejects junk", () => {
    assert.equal(parseAction(null), null);
    assert.equal(parseAction("next"), null);
    assert.equal(parseAction({ type: "reset" }), null);
    assert.equal(parseAction({ type: "mode", mode: "friends" }), null);
  });
});
