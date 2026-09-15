import { NextResponse } from "next/server";
import { admin, channelFor } from "@/lib/supabase";
import { apply, parseAction, view, type Game, type Seat } from "@/lib/game";

export const dynamic = "force-dynamic";

const UUID = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
const TOKEN = /^[A-Za-z0-9_-]{16,64}$/;
type Ctx = { params: { id: string } };

const json = (body: unknown, status = 200) => NextResponse.json(body, { status, headers: { "cache-control": "no-store" } });

async function open(req: Request, id: string) {
  const token = req.headers.get("x-hg-token") ?? "";
  if (!TOKEN.test(token)) return { res: json({ error: "missing token" }, 400) };
  if (!UUID.test(id)) return { res: json({ seat: "none" }, 404) };
  const db = admin();
  // first token becomes p1, second p2, anyone else is refused. atomic in sql.
  const { data: seat, error } = await db.rpc("claim_seat", { gid: id, token });
  if (error) throw error;
  if (seat === "none") return { res: json({ seat }, 404) };
  if (seat === "full") return { res: json({ seat }, 403) };
  return { db, seat: seat as Seat };
}

async function load(db: ReturnType<typeof admin>, id: string): Promise<Game | null> {
  const { data, error } = await db.from("games").select("*").eq("id", id).maybeSingle();
  if (error) throw error;
  return data as Game | null;
}

// wake the other phone. the payload carries nothing private; clients refetch their own view.
async function ping(db: ReturnType<typeof admin>, id: string, version: number) {
  try { await db.channel(channelFor(id)).send({ type: "broadcast", event: "ping", payload: { version } }); }
  catch { /* realtime is a nicety; polling covers it */ }
}

export async function GET(req: Request, { params }: Ctx) {
  const o = await open(req, params.id);
  if ("res" in o) return o.res;
  const g = await load(o.db, params.id);
  if (!g) return json({ seat: "none" }, 404);
  if (g.p2 && g.version <= 1) await ping(o.db, params.id, g.version); // second seat just joined: wake the first
  return json({ seat: o.seat, game: view(g, o.seat) });
}

export async function POST(req: Request, { params }: Ctx) {
  const action = parseAction(await req.json().catch(() => null));
  if (!action) return json({ error: "bad action" }, 400);
  const o = await open(req, params.id);
  if ("res" in o) return o.res;

  // optimistic concurrency: re-read and re-apply if the row moved under us
  for (let attempt = 0; attempt < 4; attempt++) {
    const g = await load(o.db, params.id);
    if (!g) return json({ seat: "none" }, 404);
    const r = apply(g, o.seat, action);
    if (!r.ok) return json({ error: r.error, seat: o.seat, game: view(g, o.seat) }, r.status);
    if (Object.keys(r.patch).length === 0) return json({ seat: o.seat, game: view(g, o.seat) });
    const { data, error } = await o.db.from("games").update({ ...r.patch, version: g.version + 1 }).eq("id", params.id).eq("version", g.version).select().maybeSingle();
    if (error) throw error;
    if (data) {
      const next = data as Game;
      await ping(o.db, params.id, next.version);
      return json({ seat: o.seat, game: view(next, o.seat) });
    }
  }
  return json({ error: "try again" }, 409);
}
