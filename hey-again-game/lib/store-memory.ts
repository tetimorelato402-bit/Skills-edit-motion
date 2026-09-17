// A faithful mirror of supabase/schema.sql, in memory. Used by the tests and by
// DEMO_MEMORY_DB for a local game with no Supabase project. Single process, and
// everything is lost on restart, so it is never right for a deployment.
import { newGame, type Claim, type NewGame, type Store } from "./store.ts";
import { usedBy } from "./pick.ts";
import type { Game } from "./game.ts";

const copy = (g: Game): Game => structuredClone(g);

export class MemoryStore implements Store {
  readonly games = new Map<string, Game>();
  readonly pings: { id: string; version: number }[] = [];
  readonly newId: () => string;
  // node's type stripping has no parameter properties, hence the long form
  constructor(newId: () => string = () => crypto.randomUUID()) {
    this.newId = newId;
  }

  // what the parent of a replay has already spent
  private inherited(parent?: string): string[] {
    const p = parent ? this.games.get(parent) : undefined;
    return p ? usedBy(p) : [];
  }

  async create(opts: NewGame = {}): Promise<string> {
    const id = this.newId();
    this.games.set(id, newGame(id, undefined, { ...opts, seen: this.inherited(opts.parent) }));
    return id;
  }

  async ensureForSession(sessionId: string, opts: NewGame = {}): Promise<void> {
    for (const g of this.games.values()) if (g.session_id === sessionId) return;
    const id = this.newId();
    this.games.set(id, newGame(id, sessionId, { ...opts, seen: this.inherited(opts.parent) }));
  }

  async findBySession(sessionId: string): Promise<string | null> {
    for (const g of this.games.values()) if (g.session_id === sessionId) return g.id;
    return null;
  }

  // mirrors claim_seat(uuid, text) exactly
  async claim(id: string, token: string): Promise<Claim> {
    const g = this.games.get(id);
    if (!g) return { seat: "none", claimed: false };
    if (g.p1 === token) return { seat: "p1", claimed: false };
    if (g.p2 === token) return { seat: "p2", claimed: false };
    if (g.p1 === null) { g.p1 = token; g.version++; return { seat: "p1", claimed: true }; }
    if (g.p2 === null) { g.p2 = token; g.status = "playing"; g.version++; return { seat: "p2", claimed: true }; }
    return { seat: "full", claimed: false };
  }

  async load(id: string): Promise<Game | null> {
    const g = this.games.get(id);
    return g ? copy(g) : null;
  }

  // mirrors update ... where id = $1 and version = $2
  async save(id: string, version: number, patch: Partial<Game>): Promise<Game | null> {
    const g = this.games.get(id);
    if (!g || g.version !== version) return null;
    Object.assign(g, patch, { version: version + 1 });
    return copy(g);
  }

  async ping(id: string, version: number): Promise<void> {
    this.pings.push({ id, version });
  }
}

// survives dev-server hot reloads
const g = globalThis as { __hgMemoryStore?: MemoryStore };
export const sharedMemoryStore = () => (g.__hgMemoryStore ??= new MemoryStore());
