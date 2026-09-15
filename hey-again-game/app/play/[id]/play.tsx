"use client";
import { useEffect, useRef, useState } from "react";
import { client, type Game } from "@/lib/supabase";
import { DECKS, MODES, ROUNDS, type Mode } from "@/lib/decks";

const TOTAL = 21;
function token() {
  let t = localStorage.getItem("hg_token");
  if (!t) { t = crypto.randomUUID(); localStorage.setItem("hg_token", t); }
  return t;
}

export default function Play({ id }: { id: string }) {
  const supabase = client();
  const [game, setGame] = useState<Game | null>(null);
  const [seat, setSeat] = useState<"p1" | "p2" | "full" | "none" | null>(null);
  const [draft, setDraft] = useState("");
  const [pick, setPick] = useState<string | null>(null);
  const me = useRef<string>("");

  useEffect(() => {
    me.current = token();
    (async () => {
      const { data: s } = await supabase.rpc("claim_seat", { gid: id, token: me.current });
      setSeat(s as any);
      const { data } = await supabase.from("games").select("*").eq("id", id).single();
      setGame(data as Game);
    })();
    const ch = supabase.channel("g" + id).on("postgres_changes", { event: "UPDATE", schema: "public", table: "games", filter: `id=eq.${id}` }, p => setGame(p.new as Game)).subscribe();
    return () => { supabase.removeChannel(ch); };
  }, [id]);

  const patch = async (p: Partial<Game>) => { const { data } = await supabase.from("games").update(p).eq("id", id).select().single(); if (data) setGame(data as Game); };

  if (seat === "full") return <main className="wrap"><p className="q">this link already has its two people.</p><p className="small">A game is only ever two seats. Want your own? It's $2.99.</p><a className="btn" href="/">get a link</a></main>;
  if (seat === "none") return <main className="wrap"><p className="q">this link doesn't exist.</p><a className="btn ghost" href="/">home</a></main>;
  if (!game || !seat) return <main className="wrap"><p className="small">opening</p></main>;
  if (game.ends_at && new Date(game.ends_at) < new Date()) return <main className="wrap"><p className="q">this game has faded.</p><p className="small">Links last seven days after the last card. Play again for $2.99.</p><a className="btn" href="/">get a link</a></main>;

  const other = seat === "p1" ? "p2" : "p1";
  const mode = game.mode as Mode | null;

  if (!game.p2) return <main className="wrap"><p className="q">waiting for them to open the link.</p><p className="small">Keep this open. The moment they tap it, you both start.</p></main>;

  if (!mode) return (
    <main className="wrap fade">
      <p className="q">what are you two?</p>
      <div>{MODES.map(m => <button key={m.id} className={"pill" + (pick === m.id ? " on" : "")} onClick={() => setPick(m.id)}>{m.label}</button>)}</div>
      <p className="small" style={{ marginTop: 14, minHeight: 24 }}>{MODES.find(m => m.id === pick)?.line ?? "either of you can choose. it can't be changed after."}</p>
      <button className="btn" disabled={!pick} onClick={() => patch({ mode: pick })}>start</button>
    </main>
  );

  if (game.status === "done") {
    const mine = Object.entries(game.answers).map(([k, v]) => ({ k, a: v[seat] })).filter(x => x.a);
    return (
      <main className="wrap fade">
        <p className="q">that's the game.</p>
        <p className="small">Pick one of your answers to leave on the shared card. The rest stays between you two.</p>
        <div className="reveal">{mine.map(x => <button key={x.k} className={"ans"} style={{ border: game.shared[seat] === x.a ? "3px solid #2E1C12" : "3px solid transparent" }} onClick={() => patch({ shared: { ...game.shared, [seat]: x.a } })}>{x.a}</button>)}</div>
        {game.shared.p1 && game.shared.p2 && <ShareCard a={game.shared.p1} b={game.shared.p2} />}
        <p className="progress">this link fades in seven days.</p>
      </main>
    );
  }

  const card = DECKS[mode][game.round][game.idx];
  const key = `${game.round}-${game.idx}`;
  const ans = game.answers[key] || {};
  const n = game.round * 7 + game.idx + 1;
  const both = ans.p1 && ans.p2;

  const submit = async () => {
    const t = draft.trim(); if (!t) return;
    const { data: fresh } = await supabase.from("games").select("answers").eq("id", id).single();
    const answers = { ...(fresh?.answers || {}), [key]: { ...((fresh?.answers || {})[key] || {}), [seat]: t } };
    await patch({ answers }); setDraft("");
  };
  const next = async () => {
    let r = game.round, i = game.idx + 1;
    if (i >= 7) { r++; i = 0; }
    if (r >= 3) { await patch({ status: "done", ends_at: new Date(Date.now() + 7 * 864e5).toISOString() }); return; }
    await patch({ round: r, idx: i });
  };

  return (
    <main className="wrap fade" key={key}>
      <p className="small" style={{ marginBottom: 18 }}>{ROUNDS[game.round]}</p>
      <h1 className="q">{card.replace(/^dare: /, "")}</h1>
      {!both && !ans[seat] && <>
        <textarea rows={3} maxLength={200} placeholder={card.startsWith("dare:") ? "do it, then say you did" : "answer in secret"} value={draft} onChange={e => setDraft(e.target.value)} />
        <button className="btn" disabled={!draft.trim()} onClick={submit}>lock it in</button>
      </>}
      {!both && ans[seat] && <p className="small">locked. waiting for them.</p>}
      {both && <>
        <div className="reveal">
          <div className="ans"><small>you</small>{ans[seat]}</div>
          <div className="ans"><small>them</small>{ans[other]}</div>
        </div>
        <button className="btn" onClick={next}>{n === TOTAL ? "finish" : "next card"}</button>
      </>}
      <p className="progress">{n} of {TOTAL}</p>
    </main>
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
