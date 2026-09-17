import Link from "next/link";
import { headers } from "next/headers";
import { storeFor } from "@/lib/store-for";
import { devFree, SITE_URL } from "@/lib/env";
import { hit, type Bucket } from "@/lib/ratelimit";
import Copy from "./copy";

export const dynamic = "force-dynamic";

const buckets = new Map<string, Bucket>();
const MAX_FREE = 5, WINDOW_MS = 60 * 60 * 1000;

type Outcome = { id: string } | { error: "notfound" | "unconfigured" | "throttled" };

async function gameFor(sessionId?: string, gameId?: string): Promise<Outcome> {
  const store = storeFor();
  if (!store) return { error: "unconfigured" };

  try {
    // a free game we just created: it already exists, just show its link
    if (gameId) return (await store.load(gameId)) ? { id: gameId } : { error: "notfound" };

    if (sessionId) {
      for (let i = 0; i < 10; i++) { // the webhook can land a second after the redirect
        const id = await store.findBySession(sessionId);
        if (id) return { id };
        await new Promise(r => setTimeout(r, 700));
      }
      return { error: "notfound" };
    }

    if (!devFree()) return { error: "notfound" };
    const ip = (headers().get("x-forwarded-for") ?? "").split(",")[0].trim() || "unknown";
    if (!hit(buckets, ip, MAX_FREE, WINDOW_MS).ok) return { error: "throttled" };
    return { id: await store.create() };
  } catch (e) {
    console.error("start", e);
    return { error: "notfound" };
  }
}

const COPY = {
  notfound: ["we couldn't find your game yet.", "If you just paid, wait a few seconds and refresh. Still nothing? Email us with your receipt."],
  unconfigured: ["this game isn't plugged in yet.", "The database keys are missing. If this is your site, fill in .env and restart."],
  throttled: ["that's a lot of free games.", "Testing has a limit. Wait an hour, or turn DEV_FREE off and use a real checkout."],
} as const;

export default async function Start({ searchParams }: { searchParams: { session_id?: string; game?: string } }) {
  const out = await gameFor(searchParams.session_id, searchParams.game);

  if ("error" in out) {
    const [title, body] = COPY[out.error];
    return (
      <main className="wrap">
        <p className="q">{title}</p>
        <p className="small">{body}</p>
        <Link className="btn ghost" href="/">back</Link>
      </main>
    );
  }

  const url = `${SITE_URL}/play/${out.id}`;
  return (
    <main className="wrap fade">
      <h1 className="q">this is your link. send it to one person.</h1>
      <p className="small">The first phone that opens it becomes the other player. After that it locks. Open it yourself too, that&apos;s your seat.</p>
      <div className="link">{url}</div>
      <Copy url={url} />
      <Link className="btn ghost" href={`/play/${out.id}`}>open my seat</Link>
      <p className="progress">save this link. it&apos;s the only one you get.</p>
    </main>
  );
}
