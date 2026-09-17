import { describe, test } from "node:test";
import assert from "node:assert/strict";
import { pickCards, usedBy } from "./pick.ts";
import { DECKS, FREE, FREE_COUNT, MODES, PAID_PER_ROUND } from "./decks.ts";
import { MemoryStore } from "./store-memory.ts";
import { apply, view, type Game } from "./game.ts";

const modes = MODES.map(m => m.id);
const flat = (rs: string[][]) => rs.flat();

describe("the free five", () => {
  test("are one short round, the same for everyone, forever", () => {
    for (const m of modes) {
      const a = pickCards(m, "free", "one-seed");
      const b = pickCards(m, "free", "a-totally-different-seed");
      assert.deepEqual(a, [FREE[m]]);
      assert.deepEqual(a, b, "free games must never shuffle");
      assert.equal(flat(a).length, FREE_COUNT);
    }
  });

  test("never appear in a paid game, so buying is never what you already saw", () => {
    for (const m of modes) {
      const reserved = new Set(FREE[m]);
      for (const card of DECKS[m].flat()) {
        assert.ok(!reserved.has(card), `paid deck reuses a free card: ${card}`);
      }
    }
  });
});

describe("a paid deck", () => {
  test("is 21 cards, three rounds of seven", () => {
    for (const m of modes) {
      const rounds = pickCards(m, "paid", "seed-a");
      assert.deepEqual(rounds.map(r => r.length), [PAID_PER_ROUND, PAID_PER_ROUND, PAID_PER_ROUND]);
      assert.equal(new Set(flat(rounds)).size, 21, "a game must not deal the same card twice");
    }
  });

  test("keeps each round's cards in that round, so the game still builds", () => {
    for (const m of modes) {
      pickCards(m, "paid", "seed-b").forEach((round, i) => {
        for (const card of round) {
          assert.ok(DECKS[m][i].includes(card), `a round ${i + 1} slot was dealt a card from another round: ${card}`);
        }
      });
    }
  });

  test("deals a different order for a different game", () => {
    const a = flat(pickCards("exes", "paid", "game-one"));
    const b = flat(pickCards("exes", "paid", "game-two"));
    assert.notDeepEqual(a, b);
  });

  test("is the same deck for the same game, every time it is asked", () => {
    assert.deepEqual(pickCards("couples", "paid", "same-id"), pickCards("couples", "paid", "same-id"));
  });
});

describe("playing again", () => {
  test("skips every card the last game used", () => {
    // a pool big enough to deal twice: three rounds is 21 of the 21 on offer,
    // so widen the skip test to the rounds that can actually spare cards.
    const first = pickCards("exes", "paid", "game-one");
    const seen = flat(first);
    const second = pickCards("exes", "paid", "game-two", seen);
    second.forEach((round, i) => {
      const spare = DECKS.exes[i].filter(c => !seen.includes(c));
      if (spare.length < PAID_PER_ROUND) return; // exhausted: falls back on purpose
      for (const card of round) assert.ok(!seen.includes(card), `replay repeated: ${card}`);
    });
  });

  test("three games in a chain share not one card", () => {
    // 21 per round is exactly three fresh hands of seven. this is the promise
    // the go again button makes, so it is the one worth asserting hardest.
    for (const m of modes) {
      const seen: string[] = [];
      const hands: string[][] = [];
      for (let game = 1; game <= 3; game++) {
        const hand = flat(pickCards(m, "paid", `chain-${m}-${game}`, seen));
        assert.equal(hand.length, 21);
        for (const card of hand) {
          assert.ok(!seen.includes(card), `game ${game} of ${m} repeated: ${card}`);
        }
        hands.push(hand);
        seen.push(...hand);
      }
      assert.equal(new Set(seen).size, 63, `${m} should spend its whole pool over three games`);
      assert.equal(hands.length, 3);
    }
  });

  test("would rather repeat than end the game early", () => {
    // every card seen: the round cannot be filled fresh, so it refills instead
    const everything = DECKS.couples.flat();
    const rounds = pickCards("couples", "paid", "exhausted", everything);
    assert.deepEqual(rounds.map(r => r.length), [PAID_PER_ROUND, PAID_PER_ROUND, PAID_PER_ROUND]);
  });

  test("carries the chain forward: a child inherits what its parent spent", async () => {
    const store = new MemoryStore();
    const firstId = await store.create();
    const first = (await store.load(firstId)) as Game;
    const dealt = apply({ ...first, p1: "a", p2: "b", status: "playing" }, "p1", { type: "mode", mode: "exes" });
    assert.ok(dealt.ok);
    await store.save(firstId, first.version, dealt.patch);

    const childId = await store.create({ parent: firstId });
    const child = (await store.load(childId)) as Game;
    assert.equal(child.parent, firstId);
    assert.deepEqual(child.seen, usedBy((await store.load(firstId)) as Game));
    assert.equal(child.seen?.length, 21);
  });

  test("a free game is free, and a replay of it is paid unless asked otherwise", async () => {
    const store = new MemoryStore();
    const free = (await store.load(await store.create({ tier: "free" }))) as Game;
    const paid = (await store.load(await store.create())) as Game;
    assert.equal(free.tier, "free");
    assert.equal(paid.tier, "paid");
  });
});

describe("a free game, played through", () => {
  test("is over after five cards, not twenty-one", async () => {
    const store = new MemoryStore();
    const id = await store.create({ tier: "free" });
    let g: Game = { ...((await store.load(id)) as Game), p1: "a", p2: "b", status: "playing" };

    const picked = apply(g, "p1", { type: "mode", mode: "couples" });
    assert.ok(picked.ok);
    g = { ...g, ...picked.patch };

    const asked: string[] = [];
    for (let n = 1; n <= FREE_COUNT; n++) {
      const v = view(g, "p1");
      assert.equal(v.total, FREE_COUNT, "a free game should say it is five long");
      assert.equal(v.n, n);
      assert.ok(v.card, `card ${n} should exist`);
      asked.push(v.card!);
      const key = v.key;
      g = { ...g, answers: { ...g.answers, [key]: { p1: "x", p2: "y" } } };
      const next = apply(g, "p1", { type: "next", key });
      assert.ok(next.ok);
      g = { ...g, ...next.patch };
    }

    assert.equal(g.status, "done", "the sixth card must not exist");
    assert.deepEqual(asked, FREE.couples, "and they are the fixed five, in order");
  });
});
