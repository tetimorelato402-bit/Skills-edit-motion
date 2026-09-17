"use client";
import { useCallback, useEffect, useRef, useState } from "react";
import { client, channelFor } from "@/lib/supabase";
import { MODES, type Mode } from "@/lib/decks";
import { other, type Action, type Seat, type View } from "@/lib/game";

const POLL_MS = 4000;

function token() {
  let t = localStorage.getItem("hg_token");
  if (!t) { t = crypto.randomUUID(); localStorage.setItem("hg_token", t); }
  return t;
}

type Reply = { seat?: Seat | "full" | "none"; game?: View; error?: string };

export default function Play({ id, again, buy }: { id: string; again: string; buy: string }) {
  const [game, setGame] = useState<View | null>(null);
  const [seat, setSeat] = useState<Seat | "full" | "none" | null>(null);
  const [draft, setDraft] = useState("");
  const [pick, setPick] = useState<Mode | null>(null);
  const [busy, setBusy] = useState(false);
  const [note, setNote] = useState<string | null>(null);
  const me = useRef<string>("");

  const call = useCallback(async (action?: Action): Promise<Reply> => {
    const res = await fetch(`/api/game/${id}`, {
      method: action ? "POST" : "GET",
      headers: { "x-hg-token": me.current, ...(action ? { "content-type": "application/json" } : {}) },
      body: action ? JSON.stringify(action) : undefined,
      cache: "no-store",
    });
    const r: Reply = await res.json().catch(() => ({ error: "something broke" }));
    if (r.seat) setSeat(r.seat);
    if (r.game) setGame(g => (!g || r.game!.version >= g.version ? r.game! : g));
    return r;
  }, [id]);

  const refresh = useCallback(() => { call().catch(() => {}); }, [call]);

  useEffect(() => {
    me.current = token();
    refresh();
    // realtime: the server pings this channel after every change. polling covers the rest.
    const supabase = client();
    const ch = supabase?.channel(channelFor(id)).on("broadcast", { event: "ping" }, refresh).subscribe();
    const timer = setInterval(() => { if (document.visibilityState === "visible") refresh(); }, POLL_MS);
    document.addEventListener("visibilitychange", refresh);
    return () => { if (ch) supabase?.removeChannel(ch); clearInterval(timer); document.removeEventListener("visibilitychange", refresh); };
  }, [id, refresh]);

  const act = async (action: Action) => {
    setBusy(true); setNote(null);
    try { const r = await call(action); if (r.error) setNote(r.error); return !r.error; }
    catch { setNote("no connection. try again."); return false; }
    finally { setBusy(false); }
  };

  if (seat === "full") return <main className="wrap"><p className="q">this link already has its two people.</p><p className="small">A game is only ever two seats. Want your own? It's $2.99.</p><a className="btn" href="/">get a link</a></main>;
  if (seat === "none") return <main className="wrap"><p className="q">this link doesn't exist.</p><a className="btn ghost" href="/">home</a></main>;
  if (!game || !seat) return <main className="wrap"><p className="small">opening</p></main>;
  if (game.faded) return <main className="wrap"><p className="q">this game has faded.</p><p className="small">Links last seven days after the last card. Play again for $2.99.</p><a className="btn" href="/">get a link</a></main>;
  if (!game.ready) return <main className="wrap"><p className="q">waiting for them to open the link.</p><p className="small">Keep this open. The moment they tap it, you both start.</p></main>;

  if (!game.mode) return (
    <main className="wrap fade">
      <p className="q">what are you two?</p>
      <div>{MODES.map(m => <button key={m.id} className={"pill" + (pick === m.id ? " on" : "")} onClick={() => setPick(m.id)}>{m.label}</button>)}</div>
      <p className="small" style={{ marginTop: 14, minHeight: 24 }}>{MODES.find(m => m.id === pick)?.line ?? "either of you can choose. it can't be changed after."}</p>
      <button className="btn" disabled={!pick || busy} onClick={() => pick && act({ type: "mode", mode: pick })}>start</button>
      <Note text={note} />
    </main>
  );

  if (game.status === "done") {
    const mine = Object.entries(game.answers).map(([k, v]) => ({ k, a: v[seat] })).filter((x): x is { k: string; a: string } => !!x.a);
    return (
      <main className="wrap fade">
        <p className="q">that's the game.</p>
        <p className="small">Pick one of your answers to leave on the shared card. The rest stays between you two.</p>
        <div className="reveal">{mine.map(x => <button key={x.k} className="ans" disabled={busy} style={{ border: game.shared[seat] === x.a ? "3px solid #2E1C12" : "3px solid transparent" }} onClick={() => act({ type: "share", text: x.a })}>{x.a}</button>)}</div>
        {game.shared.p1 && game.shared.p2 ? <ShareCard a={game.shared.p1} b={game.shared.p2} /> : <p className="small" style={{ marginTop: 18 }}>{game.shared[seat] ? "waiting for their pick." : "pick yours."}</p>}
        <Again tier={game.tier} again={again} buy={buy} />
        <Note text={note} />
        <p className="progress">this link fades in seven days.</p>
      </main>
    );
  }

  const ans = game.answers[game.key] ?? {};
  const both = !!(ans.p1 && ans.p2);
  const card = game.card ?? "";
  const dare = card.startsWith("dare:");

  const submit = async () => {
    const text = draft.trim(); if (!text) return;
    if (await act({ type: "answer", key: game.key, text })) setDraft("");
  };

  return (
    <main className="wrap fade" key={game.key}>
      <p className="small" style={{ marginBottom: 18 }}>{game.roundName}</p>
      <h1 className="q">{card.replace(/^dare: /, "")}</h1>
      {!both && !ans[seat] && <>
        <textarea rows={3} maxLength={200} placeholder={dare ? "do it, then say you did" : "answer in secret"} value={draft} onChange={e => setDraft(e.target.value)} />
        <button className="btn" disabled={!draft.trim() || busy} onClick={submit}>lock it in</button>
      </>}
      {!both && ans[seat] && <p className="small">locked. waiting for them.</p>}
      {both && <>
        <div className="reveal">
          <div className="ans"><small>you</small>{ans[seat]}</div>
          <div className="ans"><small>them</small>{ans[other(seat)]}</div>
        </div>
        <button className="btn" disabled={busy} onClick={() => act({ type: "next", key: game.key })}>{game.n === game.total ? "finish" : "next card"}</button>
      </>}
      <Note text={note} />
      <p className="progress">{game.n} of {game.total}</p>
    </main>
  );
}

function Note({ text }: { text: string | null }) {
  return text ? <p className="small" role="status" style={{ marginTop: 14 }}>{text}</p> : null;
}

// A free game ends five cards in, on purpose: it exists to teach the mechanic.
// A paid one ends offering another, and the link carries this game forward so
// the next 21 are cards neither of them has answered.
function Again({ tier, again, buy }: { tier: "free" | "paid"; again: string; buy: string }) {
  if (tier === "free") {
    return (
      <div style={{ marginTop: 26 }}>
        <p className="q" style={{ fontSize: "1.1rem" }}>that was the shallow end.</p>
        <p className="small">Those five are the same five everyone gets. The full game is 21, it goes somewhere else, and you never get the same ones twice.</p>
        {buy ? <a className="btn" href={buy}>play the whole thing, $2.99</a> : null}
      </div>
    );
  }
  if (!again) return null;
  return (
    <div style={{ marginTop: 26 }}>
      <a className="btn ghost" href={again}>hey again — 21 new cards, $2.99</a>
      <p className="small">Nothing you just answered comes back.</p>
    </div>
  );
}

function ShareCard({ a, b }: { a: string; b: string }) {
  const download = () => {
    const c = document.createElement("canvas"); c.width = 1080; c.height = 1350; const x = c.getContext("2d")!;
    x.fillStyle = "#D8652B"; x.fillRect(0, 0, 1080, 1350); x.fillStyle = "#F4EEE4"; x.textAlign = "center"; x.font = "500 52px Inter, sans-serif";
    const wrap = (t: string, y: number) => { const w: string[] = []; let line = ""; for (const word of t.split(" ")) { if (x.measureText(line + " " + word).width > 900) { w.push(line); line = word; } else line = (line + " " + word).trim(); } w.push(line); w.forEach((l, i) => x.fillText(l, 540, y + i * 66)); return y + w.length * 66; };
    let y = wrap(a, 420); y = wrap(b, y + 120);
    x.font = "500 40px Inter, sans-serif"; x.fillText("hey again.", 540, 1240);
    const l = document.createElement("a"); l.download = "hey-again.png"; l.href = c.toDataURL(); l.click();
  };
  return <button className="btn" onClick={download}>save the shared card</button>;
}
