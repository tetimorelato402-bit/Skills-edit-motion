// What the /api/game/[id] route does, with storage behind an interface so the
// whole flow can be tested without a database. HTTP lives in the route.
import { apply, view, type Action, type Seat, type View } from "./game.ts";
import type { Store } from "./store.ts";

const UUID = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
const RETRIES = 4;

export type Outcome = {
  status: number;
  body: { seat?: Seat | "full" | "none"; game?: View; error?: string };
  seat?: Seat;
};

const out = (status: number, body: Outcome["body"], seat?: Seat): Outcome => ({ status, body, seat });

type Seated = { ok: true; seat: Seat; claimed: boolean } | { ok: false; res: Outcome };

async function seatOf(store: Store, id: string, token: string): Promise<Seated> {
  if (!UUID.test(id)) return { ok: false, res: out(404, { seat: "none" }) };
  const { seat, claimed } = await store.claim(id, token);
  if (seat === "none") return { ok: false, res: out(404, { seat: "none" }) };
  if (seat === "full") return { ok: false, res: out(403, { seat: "full" }) };
  return { ok: true, seat, claimed };
}

export async function getGame(store: Store, id: string, token: string): Promise<Outcome> {
  const c = await seatOf(store, id, token);
  if (!c.ok) return c.res;
  const g = await store.load(id);
  if (!g) return out(404, { seat: "none" });
  // taking the second seat starts the game: wake the phone that was waiting
  if (c.claimed && c.seat === "p2") await store.ping(id, g.version);
  return out(200, { seat: c.seat, game: view(g, c.seat) }, c.seat);
}

export async function postGame(store: Store, id: string, token: string, action: Action): Promise<Outcome> {
  const c = await seatOf(store, id, token);
  if (!c.ok) return c.res;

  // optimistic concurrency: re-read and re-apply if the row moved under us
  for (let attempt = 0; attempt < RETRIES; attempt++) {
    const g = await store.load(id);
    if (!g) return out(404, { seat: "none" });
    const r = apply(g, c.seat, action);
    if (!r.ok) return out(r.status, { error: r.error, seat: c.seat, game: view(g, c.seat) }, c.seat);
    if (Object.keys(r.patch).length === 0) return out(200, { seat: c.seat, game: view(g, c.seat) }, c.seat);
    const saved = await store.save(id, g.version, r.patch);
    if (saved) {
      await store.ping(id, saved.version);
      return out(200, { seat: c.seat, game: view(saved, c.seat) }, c.seat);
    }
  }
  return out(409, { error: "try again", seat: c.seat }, c.seat);
}
