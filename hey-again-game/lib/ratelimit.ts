// smallest thing that works: a fixed window per key, in memory. one server
// instance only, so it slows a bored stranger, not a botnet. the free-game
// routes are the only callers and they are off in production anyway.
export type Bucket = { n: number; resetAt: number };
export type Limit = { ok: boolean; retryAfter: number };

export function hit(store: Map<string, Bucket>, key: string, max: number, windowMs: number, now = Date.now()): Limit {
  const b = store.get(key);
  if (!b || b.resetAt <= now) {
    store.set(key, { n: 1, resetAt: now + windowMs });
    if (store.size > 5000) for (const [k, v] of store) if (v.resetAt <= now) store.delete(k);
    return { ok: true, retryAfter: 0 };
  }
  b.n++;
  if (b.n > max) return { ok: false, retryAfter: Math.ceil((b.resetAt - now) / 1000) };
  return { ok: true, retryAfter: 0 };
}

// behind vercel/any proxy the first x-forwarded-for entry is the client
export function callerKey(req: Request): string {
  const fwd = req.headers.get("x-forwarded-for") ?? "";
  return (fwd.split(",")[0] || req.headers.get("x-real-ip") || "unknown").trim();
}
