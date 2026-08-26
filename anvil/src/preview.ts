/** Preview: scrub and play the film against the real mix. */
import { build, render, css } from "./stage.js";
import { film, SECTION, duration } from "./timeline.js";

const style = document.createElement("style");
style.textContent = css + `
  body { display: grid; place-items: center; min-height: 100vh; gap: 14px;
         font: 12px/1.5 ui-monospace, monospace; color: #8B8475;
         background: #16140F; padding: 20px; }
  .stage { transform: scale(var(--fit)); transform-origin: top center; }
  .frame { height: calc(1080px * var(--fit)); }
  .bar { display: flex; gap: 12px; align-items: center; width: min(1200px, 92vw); }
  input[type=range] { flex: 1; accent-color: #A8895E; }
  button { background: #241C13; color: #F0E7D6; border: 1px solid #7C6342;
           border-radius: 8px; padding: 6px 14px; font: inherit; cursor: pointer; }
  .t { min-width: 150px; }
  .sec { display: flex; gap: 6px; }
`;
document.head.append(style);

build(document.getElementById("root")!);

const audio = new Audio("../audio/mix.wav");
let section = SECTION.full;
let playing = false;
let t = 0;
let started = 0;

const scrub = document.getElementById("scrub") as HTMLInputElement;
const label = document.getElementById("t")!;
const play = document.getElementById("play")!;

function show(time: number) {
  t = time;
  render(film, t);
  label.textContent = `${t.toFixed(3)}s / ${duration.toFixed(2)}s`;
  scrub.value = String(t);
}

function loop() {
  if (!playing) return;
  const now = section.from + (performance.now() - started) / 1000;
  if (now >= section.to) { stop(); show(section.to); return; }
  show(now);
  requestAnimationFrame(loop);
}

function start() {
  playing = true;
  started = performance.now() - (t - section.from) * 1000;
  audio.currentTime = t;
  audio.play();
  play.textContent = "pause";
  loop();
}
function stop() { playing = false; audio.pause(); play.textContent = "play"; }

play.addEventListener("click", () => (playing ? stop() : start()));
scrub.addEventListener("input", () => { stop(); show(Number(scrub.value)); });
addEventListener("keydown", (e) => {
  if (e.key === " ") { e.preventDefault(); playing ? stop() : start(); }
  if (e.key === "ArrowLeft") { stop(); show(Math.max(section.from, t - 1 / 30)); }
  if (e.key === "ArrowRight") { stop(); show(Math.min(section.to, t + 1 / 30)); }
});

const bar = document.querySelector(".sec")!;
for (const [name, s] of Object.entries(SECTION)) {
  const b = document.createElement("button");
  b.textContent = name;
  b.addEventListener("click", () => {
    stop(); section = s;
    scrub.min = String(s.from); scrub.max = String(s.to);
    show(s.from);
  });
  bar.append(b);
}

const fit = () => document.body.style.setProperty(
  "--fit", String(Math.min(1, (innerWidth - 60) / 1920)));
addEventListener("resize", fit); fit();

scrub.min = String(section.from); scrub.max = String(section.to); scrub.step = "0.001";
show(0);
