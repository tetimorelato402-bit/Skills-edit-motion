"use client";
import { useState } from "react";
export default function Copy({ url }: { url: string }) {
  const [done, setDone] = useState(false);
  const go = async () => {
    if (navigator.share) { try { await navigator.share({ title: "hey again.", text: "play this with me.", url }); return; } catch {} }
    await navigator.clipboard.writeText(url); setDone(true); setTimeout(() => setDone(false), 2000);
  };
  return <button className="btn" onClick={go}>{done ? "copied" : "send the link"}</button>;
}
