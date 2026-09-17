import { NextResponse } from "next/server";
import { storeFor } from "@/lib/store-for";
import { SITE_URL } from "@/lib/env";
import { hit, callerKey, type Bucket } from "@/lib/ratelimit";

export const dynamic = "force-dynamic";

// the free game is a real product, not a testing backdoor, so it is always on.
// the cap is only here so one person cannot fill the table.
const buckets = new Map<string, Bucket>();
const MAX = 5, WINDOW_MS = 60 * 60 * 1000;

const home = (req: Request, error?: string) =>
  new URL(error ? `/?error=${error}` : "/", SITE_URL || req.url);

export async function POST(req: Request) {
  const limit = hit(buckets, callerKey(req), MAX, WINDOW_MS);
  if (!limit.ok) return NextResponse.redirect(home(req, "toomany"), 303);

  const store = storeFor();
  if (!store) return NextResponse.redirect(home(req, "free"), 303);
  try {
    const id = await store.create({ tier: "free" });
    return NextResponse.redirect(new URL(`/start?game=${id}`, SITE_URL || req.url), 303);
  } catch (e) {
    console.error("free route", e);
    return NextResponse.redirect(home(req, "free"), 303);
  }
}
