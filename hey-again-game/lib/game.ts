// the rules of the game, as pure functions. no i/o here.
// the server (app/api/game/[id]/route.ts) loads a row, calls apply(), writes the patch.
// the browser only ever sees what view() returns for its own seat.
import { DECKS, FREE_COUNT, MODES, PAID_PER_ROUND, ROUNDS, type Mode, type Tier } from "./decks.ts";
import { pickCards } from "./pick.ts";

export type { Mode, Tier };
export type Seat = "p1" | "p2";
export type Status = "waiting" | "playing" | "done";
export type Answers = Record<string, Partial<Record<Seat, string>>>;
export type Shared = Partial<Record<Seat, string>>;

// one row of the games table
export type Game = {
  id: string;
  session_id: string | null;
  mode: string | null;
  p1: string | null;
  p2: string | null;
  round: number;
  idx: number;
  answers: Answers;
  shared: Shared;
  status: Status;
  ends_at: string | null;
  version: number;
  // dealt when the mode is picked, because the deck depends on it. rows written
  // before the shuffle existed have none, and fall back to the old fixed deck.
  cards?: string[][] | null;
  tier?: Tier | null;
  // every card this chain has already spent, so a replay deals something else
  seen?: string[] | null;
  parent?: string | null;
};

// what a seat is allowed to know
export type View = {
  seat: Seat;
  status: Status;
  mode: Mode | null;
  ready: boolean; // both seats taken
  faded: boolean;
  tier: Tier;
  round: number;
  roundName: string;
  idx: number;
  key: string;
  card: string | null;
  n: number; // 1-based card number
  total: number;
  answers: Answers; // the other seat's answer is only present once both exist
  shared: Shared;
  version: number;
};

export type Action =
  | { type: "mode"; mode: Mode }
  | { type: "answer"; key: string; text: string }
  | { type: "next"; key: string }
  | { type: "share"; text: string };

export type Result = { ok: true; patch: Partial<Game> } | { ok: false; error: string; status: number };

// the shape of a paid game, which is what these always described
export const CARDS_PER_ROUND = PAID_PER_ROUND;
export const ROUND_COUNT = 3;
export const TOTAL = CARDS_PER_ROUND * ROUND_COUNT;
export const LINK_DAYS = 7;
export const MAX_ANSWER = 200;

export const cardKey = (round: number, idx: number) => `${round}-${idx}`;
export const other = (s: Seat): Seat => (s === "p1" ? "p2" : "p1");
export const isMode = (m: unknown): m is Mode => MODES.some(x => x.id === m);
export const isSeat = (s: unknown): s is Seat => s === "p1" || s === "p2";

export function isFaded(g: Pick<Game, "ends_at">, now = Date.now()) {
  return !!g.ends_at && new Date(g.ends_at).getTime() < now;
}

export function shape(g: Pick<Game, "cards" | "tier">): number[] {
  if (g.cards?.length) return g.cards.map(r => r.length);
  if (g.tier === "free") return [FREE_COUNT];
  return Array(ROUND_COUNT).fill(CARDS_PER_ROUND);
}

export const totalCards = (g: Pick<Game, "cards" | "tier">): number =>
  shape(g).reduce((a, b) => a + b, 0);

export function card(g: Pick<Game, "mode" | "round" | "idx" | "cards">): string | null {
  if (g.cards?.length) return g.cards[g.round]?.[g.idx] ?? null;
  // a game dealt before decks were stored on the row: read the fixed deck
  if (!isMode(g.mode)) return null;
  return DECKS[g.mode][g.round]?.[g.idx] ?? null;
}

// strip everything a seat must not see: tokens, and the other seat's answer before both exist
export function view(g: Game, seat: Seat, now = Date.now()): View {
  const sizes = shape(g);
  const total = sizes.reduce((a, b) => a + b, 0);
  const answers: Answers = {};
  for (const [k, a] of Object.entries(g.answers ?? {})) {
    const mine = a?.[seat];
    const theirs = a?.[other(seat)];
    if (mine && theirs) answers[k] = { p1: a.p1, p2: a.p2 };
    else if (mine) answers[k] = { [seat]: mine };
  }
  return {
    seat,
    status: g.status,
    mode: isMode(g.mode) ? g.mode : null,
    ready: !!(g.p1 && g.p2),
    faded: isFaded(g, now),
    tier: g.tier === "free" ? "free" : "paid",
    round: g.round,
    roundName: ROUNDS[g.round] ?? ROUNDS[ROUNDS.length - 1],
    idx: g.idx,
    key: cardKey(g.round, g.idx),
    card: card(g),
    n: Math.min(sizes.slice(0, g.round).reduce((a, b) => a + b, 0) + g.idx + 1, total),
    total,
    answers,
    shared: g.shared ?? {},
    version: g.version,
  };
}

const fail = (status: number, error: string): Result => ({ ok: false, error, status });

export function apply(g: Game, seat: Seat, action: Action, now = Date.now()): Result {
  if (isFaded(g, now)) return fail(410, "this game has faded");
  if (!g.p1 || !g.p2) return fail(409, "waiting for the other seat");
  const key = cardKey(g.round, g.idx);

  switch (action.type) {
    case "mode": {
      if (g.mode) return fail(409, "mode is already set");
      if (!isMode(action.mode)) return fail(400, "unknown mode");
      // the deck depends on the mode, so this is the first moment it can be dealt
      const cards = pickCards(action.mode, g.tier === "free" ? "free" : "paid", g.id, g.seen ?? []);
      return { ok: true, patch: { mode: action.mode, cards } };
    }

    case "answer": {
      if (g.status !== "playing" || !isMode(g.mode)) return fail(409, "not playing");
      if (action.key !== key) return fail(409, "that card has moved on");
      const text = (action.text ?? "").trim();
      if (!text) return fail(400, "say something");
      if (text.length > MAX_ANSWER) return fail(400, `keep it under ${MAX_ANSWER} characters`);
      const cur = g.answers?.[key] ?? {};
      if (cur[seat]) return fail(409, "you already locked this one");
      return { ok: true, patch: { answers: { ...g.answers, [key]: { ...cur, [seat]: text } } } };
    }

    case "next": {
      if (g.status !== "playing" || !isMode(g.mode)) return fail(409, "not playing");
      // both players tap next; the second tap sees the card already advanced. that's fine.
      if (action.key !== key) return { ok: true, patch: {} };
      const cur = g.answers?.[key] ?? {};
      if (!cur.p1 || !cur.p2) return fail(409, "both answers first");
      const sizes = shape(g);
      let round = g.round, idx = g.idx + 1;
      if (idx >= (sizes[round] ?? 0)) { round++; idx = 0; }
      if (round >= sizes.length) {
        return { ok: true, patch: { status: "done", ends_at: new Date(now + LINK_DAYS * 864e5).toISOString() } };
      }
      return { ok: true, patch: { round, idx } };
    }

    case "share": {
      if (g.status !== "done") return fail(409, "finish the game first");
      const text = (action.text ?? "").trim();
      const mine = Object.values(g.answers ?? {}).map(a => a?.[seat]).filter(Boolean);
      if (!mine.includes(text)) return fail(400, "pick one of your own answers");
      return { ok: true, patch: { shared: { ...g.shared, [seat]: text } } };
    }

    default:
      return fail(400, "unknown action");
  }
}

export function parseAction(body: unknown): Action | null {
  if (!body || typeof body !== "object") return null;
  const b = body as Record<string, unknown>;
  const str = (v: unknown) => (typeof v === "string" ? v : "");
  switch (b.type) {
    case "mode": return isMode(b.mode) ? { type: "mode", mode: b.mode } : null;
    case "answer": return { type: "answer", key: str(b.key), text: str(b.text).slice(0, MAX_ANSWER * 4) };
    case "next": return { type: "next", key: str(b.key) };
    case "share": return { type: "share", text: str(b.text).slice(0, MAX_ANSWER * 4) };
    default: return null;
  }
}
