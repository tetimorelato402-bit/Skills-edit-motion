/** Proves the sync rule against the real module, not against a copy of it. */
import { VO, VO_AT, LEAD, LAYERS, film, duration } from "../build/timeline.js";

const cueOf = {
  name: "name", phone: "phone", commit: "commit", places: "places", home: "home",
  locked: "locked", opened: "opens", proof: "proof", seen: "circle", routine: "compound",
};
/** when does each layer finish arriving? */
const settled = {};
for (const t of film) {
  if (t.k === "cross") settled[t.in] = t.at + t.dur;
  if (t.k === "layer") settled[t.id] = t.at + t.dur;
  if (t.k === "part" && t.id === "toast") settled.toast = t.at + t.dur;
}
settled.opened = film.find((t) => t.k === "cross" && t.in === "opened").at
               + film.find((t) => t.k === "cross" && t.in === "opened").dur;

let bad = 0;
console.log("layer        settled    onset     lead");
for (const [layer, k] of Object.entries(cueOf)) {
  const onset = VO[k].on + VO_AT;
  const lead = onset - settled[layer];
  const flag = lead < LEAD - 1e-9 ? "  ** SHORT **" : "";
  if (flag) bad++;
  console.log(`${layer.padEnd(11)} ${settled[layer].toFixed(3).padStart(7)} ${onset.toFixed(3).padStart(8)} ${lead.toFixed(3).padStart(8)}${flag}`);
}
const toastOnset = VO.arrive.on + VO_AT;
const toastLead = toastOnset - settled.toast;
console.log(`${"toast".padEnd(11)} ${settled.toast.toFixed(3).padStart(7)} ${toastOnset.toFixed(3).padStart(8)} ${toastLead.toFixed(3).padStart(8)}`);
if (toastLead < LEAD - 1e-9) bad++;

/* Screens are what may not move at once. Camera, focus and bloom now run
   continuously and in parallel by design — the film is never locked off — so
   flagging those would be flagging the intent. Two SCREENS moving at once is
   still a mistake. */
const moves = film.filter((t) => ["layer", "cross", "exit"].includes(t.k) && t.dur > 0)
  .map((t) => ({ k: t.k, id: t.id ?? `${t.out}→${t.in}`, a: t.at, b: t.at + t.dur }))
  .sort((x, y) => x.a - y.a);
console.log("\nconcurrent screen moves:");
for (let i = 0; i < moves.length; i++)
  for (let j = i + 1; j < moves.length; j++)
    if (moves[j].a < moves[i].b - 1e-9)
      console.log(`  ${moves[i].a.toFixed(3)} ${moves[i].k}:${moves[i].id} || ${moves[j].k}:${moves[j].id}`);

/* the longest stillness in the film */
const holds = film.filter((t) => t.k === "hold" && t.dur > 0).sort((a, b) => b.dur - a.dur);
console.log(`\nlongest holds:`);
for (const h of holds.slice(0, 4)) console.log(`  ${h.dur.toFixed(3)}s @ ${h.at.toFixed(3)}  ${h.note}`);
console.log(`\nduration ${duration.toFixed(3)}s · ${bad} sync violations`);
process.exit(bad ? 1 : 0);
