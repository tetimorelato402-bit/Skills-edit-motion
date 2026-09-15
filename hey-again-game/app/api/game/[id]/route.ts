import { NextResponse } from "next/server";
import { storeFor } from "@/lib/store-for";
import { cookieName, seatToken } from "@/lib/seat";
import { getGame, postGame, type Outcome } from "@/lib/server-game";
import { parseAction } from "@/lib/game";

export const dynamic = "force-dynamic";

const COOKIE_DAYS = 30;
type Ctx = { params: { id: string } };

const json = (body: unknown, status = 200) =>
  NextResponse.json(body, { status, headers: { "cache-control": "no-store" } });

function respond(o: Outcome, id: string, token: string) {
  const res = json(o.body, o.status);
  // keep the seat in an httpOnly cookie too, so clearing site data in one place
  // does not strand a player mid-game
  if (o.seat) {
    res.cookies.set(cookieName(id), token, {
      httpOnly: true,
      sameSite: "lax",
      secure: process.env.NODE_ENV === "production",
      path: "/",
      maxAge: COOKIE_DAYS * 24 * 3600,
    });
  }
  return res;
}

async function handle(req: Request, id: string, run: (token: string) => Promise<Outcome>) {
  const token = seatToken(req.headers.get("cookie"), req.headers.get("x-hg-token"), id);
  if (!token) return json({ error: "missing token" }, 400);
  try {
    return respond(await run(token), id, token);
  } catch (e) {
    console.error("game route", e);
    return json({ error: "something broke on our side" }, 500);
  }
}

export async function GET(req: Request, { params }: Ctx) {
  const store = storeFor();
  if (!store) return json({ error: "the game database isn't configured yet" }, 503);
  return handle(req, params.id, token => getGame(store, params.id, token));
}

export async function POST(req: Request, { params }: Ctx) {
  const store = storeFor();
  if (!store) return json({ error: "the game database isn't configured yet" }, 503);
  const action = parseAction(await req.json().catch(() => null));
  if (!action) return json({ error: "bad action" }, 400);
  return handle(req, params.id, token => postGame(store, params.id, token, action));
}
