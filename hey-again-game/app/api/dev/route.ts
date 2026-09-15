import { NextResponse } from "next/server";
import { storeFor } from "@/lib/store-for";
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
  const store = storeFor();
  if (!store) return NextResponse.json({ error: "database not configured" }, { status: 503 });
  try {
    return NextResponse.json({ id: await store.create() });
  } catch (e) {
    console.error("dev route", e);
    return NextResponse.json({ error: "could not create a game" }, { status: 500 });
  }
}
