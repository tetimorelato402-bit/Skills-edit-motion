// Choosing the cards for one game. Pure, and deterministic: the same seed and
// the same pool always deal the same hand, so a deck can be reasoned about in a
// test instead of being watched for a while and hoped about.
import { DECKS, FREE, FREE_COUNT, PAID_PER_ROUND, type Mode, type Tier } from "./decks.ts";

// mulberry32 over an fnv-1a hash of the seed. not cryptographic: it only has to
// be stable across machines and spread evenly, and Math.random is neither.
function rng(seed: string): () => number {
  let h = 2166136261;
  for (let i = 0; i < seed.length; i++) {
    h ^= seed.charCodeAt(i);
    h = Math.imul(h, 16777619);
  }
  let a = h >>> 0;
  return () => {
    a = (a + 0x6d2b79f5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

function shuffled<T>(xs: readonly T[], next: () => number): T[] {
  const out = xs.slice();
  for (let i = out.length - 1; i > 0; i--) {
    const j = Math.floor(next() * (i + 1));
    [out[i], out[j]] = [out[j], out[i]];
  }
  return out;
}

// Free games are the same five for everyone, in a fixed order, forever: they
// exist to teach the mechanic, not to be a small paid game.
//
// Paid games draw seven per round, skipping every card the player has already
// seen earlier in this chain, so buying again is never the game you just played.
// Rounds are drawn separately on purpose. The rounds escalate (before, between,
// again), so dealing from one flat pool would let a round three card land first
// and the build the whole game depends on would be gone.
export function pickCards(
  mode: Mode,
  tier: Tier,
  seed: string,
  seen: readonly string[] = [],
): string[][] {
  if (tier === "free") return [FREE[mode].slice(0, FREE_COUNT)];
  const skip = new Set(seen);
  const next = rng(seed);
  return DECKS[mode].map(pool => {
    const fresh = pool.filter(c => !skip.has(c));
    // a long chain eventually exhausts a round. dealing short would end the game
    // early, so fall back to the whole pool and repeat rather than break.
    const from = fresh.length >= PAID_PER_ROUND ? fresh : pool;
    return shuffled(from, next).slice(0, PAID_PER_ROUND);
  });
}

// what this game has now used up, for the next game in the chain to skip
export const usedBy = (g: { cards?: string[][] | null; seen?: string[] | null }): string[] =>
  [...(g.seen ?? []), ...(g.cards ?? []).flat()];
