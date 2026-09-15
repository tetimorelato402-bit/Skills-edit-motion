import { NextResponse } from "next/server";
import { admin, NotConfigured } from "@/lib/supabase-admin";
import { devFree } from "@/lib/env";
import { hit, callerKey, type Bucket } from "@/lib/ratelimit";

export const dynamic = "force-dynamic";

const buckets = new Map<string, Bucket>();
const MAX = 5, WINDOW_MS = 60 * 60 * 1000;

// creates a free game for testing. disabled unless DEV_FREE=true
export async function POST(req: Request) {
  if (!devFree()) return NextResponse.json({ error: "off" }, { status: 403 });
  const limit = hit(buckets, callerKey(req), MAX, WINDOW_MS);
  if (!limit.ok) {
    return NextResponse.json({ error: "slow down" }, { status: 429, headers: { "retry-after": String(limit.retryAfter) } });
  }
  try {
    const { data, error } = await admin().from("games").insert({}).select("id").single();
    if (error) throw error;
    return NextResponse.json({ id: data.id });
  } catch (e) {
    if (e instanceof NotConfigured) return NextResponse.json({ error: "database not configured" }, { status: 503 });
    console.error("dev route", e);
    return NextResponse.json({ error: "could not create a game" }, { status: 500 });
  }
}
