import { admin } from "@/lib/supabase";
import Link from "next/link";
import Copy from "./copy";
export const dynamic = "force-dynamic";
async function gameFor(sessionId?: string) {
  const db = admin();
  if (sessionId) {
    for (let i = 0; i < 10; i++) { // webhook can land a second after redirect
      const { data } = await db.from("games").select("id").eq("session_id", sessionId).maybeSingle();
      if (data) return data.id as string;
      await new Promise(r => setTimeout(r, 700));
    }
    return null;
  }
  if (process.env.DEV_FREE !== "true") return null;
  const { data } = await db.from("games").insert({}).select("id").single();
  return data!.id as string;
}
export default async function Start({ searchParams }: { searchParams: { session_id?: string } }) {
  const id = await gameFor(searchParams.session_id);
  if (!id) return <main className="wrap"><p className="q">we couldn't find your game yet.</p><p className="small">If you just paid, wait a few seconds and refresh. Still nothing? Email us with your receipt.</p><Link className="btn ghost" href="/">back</Link></main>;
  const url = `${process.env.NEXT_PUBLIC_SITE_URL}/play/${id}`;
  return (
    <main className="wrap fade">
      <h1 className="q">this is your link. send it to one person.</h1>
      <p className="small">The first phone that opens it becomes the other player. After that it locks. Open it yourself too, that's your seat.</p>
      <div className="link">{url}</div>
      <Copy url={url} />
      <Link className="btn ghost" href={`/play/${id}`}>open my seat</Link>
    </main>
  );
}
