import { NextResponse } from "next/server";
import { admin, ping, NotConfigured } from "@/lib/supabase-admin";
import { cookieName, seatToken } from "@/lib/seat";
import { apply, parseAction, view, type Game, type Seat } from "@/lib/game";

export const dynamic = "force-dynamic";

const UUID = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
const COOKIE_DAYS = 30;
type Ctx = { params: { id: string } };

const json = (body: unknown, status = 200) =>
  NextResponse.json(body, { status, headers: { "cache-control": "no-store" } });

// keep the seat in an httpOnly cookie too, so clearing site data in one place
// does not strand a player mid-game
function withSeatCookie(res: NextResponse, id: string, token: string) {
  res.cookies.set(cookieName(id), token, {
    httpOnly: true,
    sameSite: "lax",
    secure: process.env.NODE_ENV === "production",
    path: `/`,
    maxAge: COOKIE_DAYS * 24 * 3600,
  });
  return res;
}

type Open =
  | { res: NextResponse }
  | { db: ReturnType<typeof admin>; seat: Seat; token: string; claimed: boolean };

async function open(req: Request, id: string): Promise<Open> {
  const token = seatToken(req.headers.get("cookie"), req.headers.get("x-hg-token"), id);
  if (!token) return { res: json({ error: "missing token" }, 400) };
  if (!UUID.test(id)) return { res: json({ seat: "none" }, 404) };
  const db = admin();
  // first token becomes p1, second p2, anyone else is refused. atomic in sql.
  const { data, error } = await db.rpc("claim_seat", { gid: id, token });
  if (error) throw error;
  const seat = (data as { seat?: string } | null)?.seat;
  const claimed = !!(data as { claimed?: boolean } | null)?.claimed;
  if (seat === "none" || !seat) return { res: json({ seat: "none" }, 404) };
  if (seat === "full") return { res: json({ seat }, 403) };
  return { db, seat: seat as Seat, token, claimed };
}

async function load(db: ReturnType<typeof admin>, id: string): Promise<Game | null> {
  const { data, error } = await db.from("games").select("*").eq("id", id).maybeSingle();
  if (error) throw error;
  return (data as Game | null) ?? null;
}

async function handle(req: Request, id: string, run: (o: Extract<Open, { db: unknown }>) => Promise<NextResponse>) {
  try {
    const o = await open(req, id);
    if ("res" in o) return o.res;
    return withSeatCookie(await run(o), id, o.token);
  } catch (e) {
    if (e instanceof NotConfigured) return json({ error: "the game database isn't configured yet" }, 503);
    console.error("game route", e);
    return json({ error: "something broke on our side" }, 500);
  }
}

export async function GET(req: Request, { params }: Ctx) {
  return handle(req, params.id, async o => {
    const g = await load(o.db, params.id);
    if (!g) return json({ seat: "none" }, 404);
    // taking the second seat starts the game: wake the phone that was waiting
    if (o.claimed && o.seat === "p2") await ping(o.db, params.id, g.version);
    return json({ seat: o.seat, game: view(g, o.seat) });
  });
}

export async function POST(req: Request, { params }: Ctx) {
  const action = parseAction(await req.json().catch(() => null));
  if (!action) return json({ error: "bad action" }, 400);
  return handle(req, params.id, async o => {
    // optimistic concurrency: re-read and re-apply if the row moved under us
    for (let attempt = 0; attempt < 4; attempt++) {
      const g = await load(o.db, params.id);
      if (!g) return json({ seat: "none" }, 404);
      const r = apply(g, o.seat, action);
      if (!r.ok) return json({ error: r.error, seat: o.seat, game: view(g, o.seat) }, r.status);
      if (Object.keys(r.patch).length === 0) return json({ seat: o.seat, game: view(g, o.seat) });
      const { data, error } = await o.db
        .from("games")
        .update({ ...r.patch, version: g.version + 1 })
        .eq("id", params.id)
        .eq("version", g.version)
        .select()
        .maybeSingle();
      if (error) throw error;
      if (data) {
        const next = data as Game;
        await ping(o.db, params.id, next.version);
        return json({ seat: o.seat, game: view(next, o.seat) });
      }
    }
    return json({ error: "try again" }, 409);
  });
}
