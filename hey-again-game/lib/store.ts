// The one thing the server needs from storage. Two implementations:
// store-supabase.ts (real) and store-memory.ts (tests, and DEMO_MEMORY_DB).
import type { Game, Seat, Tier } from "./game.ts";

export type Claim = { seat: Seat | "full" | "none"; claimed: boolean };

// a new game, optionally continuing a finished one: the chain is how a replay
// knows what it must not deal again.
export type NewGame = { tier?: Tier; parent?: string };

export interface Store {
  create(opts?: NewGame): Promise<string>;
  ensureForSession(sessionId: string, opts?: NewGame): Promise<void>;
  findBySession(sessionId: string): Promise<string | null>;
  claim(id: string, token: string): Promise<Claim>;
  load(id: string): Promise<Game | null>;
  // null means the row moved on: someone wrote before us, so re-read and retry
  save(id: string, version: number, patch: Partial<Game>): Promise<Game | null>;
  ping(id: string, version: number): Promise<void>;
}

export const newGame = (id: string, sessionId?: string, opts: NewGame & { seen?: string[] } = {}): Game => ({
  id,
  session_id: sessionId ?? null,
  mode: null,
  p1: null,
  p2: null,
  round: 0,
  idx: 0,
  answers: {},
  shared: {},
  status: "waiting",
  ends_at: null,
  version: 0,
  cards: null,
  tier: opts.tier ?? "paid",
  seen: opts.seen ?? [],
  parent: opts.parent ?? null,
});
