// End to end through the real server logic, against the in-memory mirror of
// supabase/schema.sql. Everything but the network to Supabase is exercised here.
import { test, describe } from "node:test";
import assert from "node:assert/strict";
import { MemoryStore } from "./store-memory.ts";
import { getGame, postGame } from "./server-game.ts";
import { CARDS_PER_ROUND, ROUND_COUNT, TOTAL, type Action } from "./game.ts";
import type { Game } from "./game.ts";

const P1 = "aaaaaaaaaaaaaaaaaaaa";
const P2 = "bbbbbbbbbbbbbbbbbbbb";
const P3 = "cccccccccccccccccccc";

const fresh = async () => {
  const store = new MemoryStore();
  const id = await store.create();
  return { store, id };
};

describe("seating", () => {
  test("first two tokens get the seats, everyone after is refused", async () => {
    const { store, id } = await fresh();
    assert.equal((await getGame(store, id, P1)).body.seat, "p1");
    assert.equal((await getGame(store, id, P2)).body.seat, "p2");
    const third = await getGame(store, id, P3);
    assert.equal(third.status, 403);
    assert.equal(third.body.seat, "full");
  });

  test("a returning token keeps its own seat", async () => {
    const { store, id } = await fresh();
    await getGame(store, id, P1);
    await getGame(store, id, P2);
    assert.equal((await getGame(store, id, P1)).body.seat, "p1");
    assert.equal((await getGame(store, id, P2)).body.seat, "p2");
  });

  test("an unknown link is not found", async () => {
    const { store } = await fresh();
    assert.equal((await getGame(store, "11111111-2222-3333-4444-555555555555", P1)).status, 404);
    assert.equal((await getGame(store, "not-a-uuid", P1)).status, 404);
  });

  test("p1 waits alone, then the second seat wakes them exactly once", async () => {
    const { store, id } = await fresh();
    const alone = await getGame(store, id, P1);
    assert.equal(alone.body.game!.ready, false);
    assert.equal(store.pings.length, 0);
    await getGame(store, id, P2);
    assert.equal(store.pings.length, 1);
    await getGame(store, id, P2); // polling must not keep pinging
    await getGame(store, id, P1);
    assert.equal(store.pings.length, 1);
  });

  test("nothing can be done from an empty second seat", async () => {
    const { store, id } = await fresh();
    await getGame(store, id, P1);
    assert.equal((await postGame(store, id, P1, { type: "mode", mode: "couples" })).status, 409);
  });
});

describe("a whole game", () => {
  test("21 cards, both answers each, revealed together, then a shared card", async () => {
    const { store, id } = await fresh();
    await getGame(store, id, P1);
    await getGame(store, id, P2);

    assert.equal((await postGame(store, id, P1, { type: "mode", mode: "exes" })).status, 200);
    assert.equal((await postGame(store, id, P2, { type: "mode", mode: "couples" })).status, 409); // one mode only

    const mine: string[] = [];
    for (let n = 1; n <= TOTAL; n++) {
      const before = (await getGame(store, id, P1)).body.game!;
      assert.equal(before.n, n, `card ${n}`);
      assert.equal(typeof before.card, "string");
      const key = before.key;

      const a = `p1 says ${n}`, b = `p2 says ${n}`;
      mine.push(a);
      assert.equal((await postGame(store, id, P1, { type: "answer", key, text: a })).status, 200);

      // p1 has locked; p2 must not be able to see it yet
      const p2Peek = (await getGame(store, id, P2)).body.game!;
      assert.equal(p2Peek.answers[key], undefined);
      // and p1 cannot answer twice or advance alone
      assert.equal((await postGame(store, id, P1, { type: "answer", key, text: "changed" })).status, 409);
      assert.equal((await postGame(store, id, P1, { type: "next", key })).status, 409);

      const both = await postGame(store, id, P2, { type: "answer", key, text: b });
      assert.equal(both.status, 200);
      assert.deepEqual(both.body.game!.answers[key], { p1: a, p2: b });
      assert.deepEqual((await getGame(store, id, P1)).body.game!.answers[key], { p1: a, p2: b });

      assert.equal((await postGame(store, id, P1, { type: "next", key })).status, 200);
    }

    const end = (await getGame(store, id, P1)).body.game!;
    assert.equal(end.status, "done");
    assert.equal(new Date(end.faded ? 0 : Date.now()) instanceof Date, true);
    assert.equal(end.faded, false);

    // the shared card: only your own answers, one each, changeable
    assert.equal((await postGame(store, id, P1, { type: "share", text: "p2 says 1" })).status, 400);
    assert.equal((await postGame(store, id, P1, { type: "share", text: mine[0] })).status, 200);
    assert.equal((await postGame(store, id, P2, { type: "share", text: "p2 says 3" })).status, 200);
    const final = (await getGame(store, id, P1)).body.game!;
    assert.deepEqual(final.shared, { p1: "p1 says 1", p2: "p2 says 3" });
  });

  test("the rounds run in order and the deck does not repeat a card", async () => {
    const { store, id } = await fresh();
    await getGame(store, id, P1);
    await getGame(store, id, P2);
    await postGame(store, id, P1, { type: "mode", mode: "strangers" });

    const seen: string[] = [], names: string[] = [];
    for (let n = 1; n <= TOTAL; n++) {
      const v = (await getGame(store, id, P1)).body.game!;
      seen.push(v.card!);
      if (!names.includes(v.roundName)) names.push(v.roundName);
      await postGame(store, id, P1, { type: "answer", key: v.key, text: "a" });
      await postGame(store, id, P2, { type: "answer", key: v.key, text: "b" });
      await postGame(store, id, P1, { type: "next", key: v.key });
    }
    assert.deepEqual(names, ["before", "between", "again"]);
    assert.equal(new Set(seen).size, TOTAL);
    assert.equal(seen.length, ROUND_COUNT * CARDS_PER_ROUND);
  });
});

describe("two phones at once", () => {
  const playTo = async (store: MemoryStore, id: string) => {
    await getGame(store, id, P1);
    await getGame(store, id, P2);
    await postGame(store, id, P1, { type: "mode", mode: "couples" });
    await postGame(store, id, P1, { type: "answer", key: "0-0", text: "a" });
    await postGame(store, id, P2, { type: "answer", key: "0-0", text: "b" });
  };

  test("both tapping next advances exactly one card", async () => {
    const { store, id } = await fresh();
    await playTo(store, id);
    const next: Action = { type: "next", key: "0-0" };
    const [a, b] = await Promise.all([postGame(store, id, P1, next), postGame(store, id, P2, next)]);
    assert.equal(a.status, 200);
    assert.equal(b.status, 200);
    assert.equal((await getGame(store, id, P1)).body.game!.n, 2);
  });

  test("a lost write is retried against the fresh row", async () => {
    class Flaky extends MemoryStore {
      misses = 1;
      async save(gid: string, version: number, patch: Partial<Game>) {
        if (this.misses-- > 0) return null; // pretend another phone wrote first
        return super.save(gid, version, patch);
      }
    }
    const store = new Flaky();
    const id = await store.create();
    await playTo(store, id);
    const r = await postGame(store, id, P1, { type: "next", key: "0-0" });
    assert.equal(r.status, 200);
    assert.equal(r.body.game!.n, 2);
  });

  test("a row that never settles gives up instead of spinning", async () => {
    class Stuck extends MemoryStore {
      async save() { return null; }
    }
    const store = new Stuck();
    const id = await store.create();
    await getGame(store, id, P1);
    await getGame(store, id, P2);
    const r = await postGame(store, id, P1, { type: "mode", mode: "couples" });
    assert.equal(r.status, 409);
    assert.equal(r.body.error, "try again");
  });
});

describe("checkout plumbing", () => {
  test("a session id maps to exactly one game, and the webhook is idempotent", async () => {
    const store = new MemoryStore();
    assert.equal(await store.findBySession("cs_test_1"), null);
    await store.ensureForSession("cs_test_1");
    const id = await store.findBySession("cs_test_1");
    assert.equal(typeof id, "string");
    await store.ensureForSession("cs_test_1"); // stripe retried
    assert.equal(await store.findBySession("cs_test_1"), id);
    assert.equal(store.games.size, 1);
  });
});
