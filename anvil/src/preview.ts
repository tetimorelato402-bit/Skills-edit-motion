/** Preview: scrub and play the film against the real voice. */
import { build, render, css } from "./stage.js";
import { film, SECTION, VO } from "./timeline.js";

const style = document.createElement("style");
style.textContent = css + `
  body { display: grid; place-items: center; min-height: 100vh; gap: 14px;
         font: 12px/1.5 ui-monospace, monospace; color: #C3B49B; padding: 20px; }
  .stage { transform: scale(var(--fit)); transform-origin: top center; }
  .frame { height: calc(1080px * var(--fit)); }
  .bar { display: flex; gap: 12px; align-items: center; width: min(1200px, 92vw); }
  input[type=range] { flex: 1; accent-color: #A8895E; }
  button { background: #241C13; color: #F0E7D6; border: 1px solid #7C6342;
           border-radius: 8px; padding: 6px 14px; font: inherit; cursor: pointer; }
  .t { min-width: 118px; }
`;
document.head.append(style);

const section = SECTION.act23;
const root = document.getElementById("root")!;
build(root);

const vo = new Audio("../audio/vo_trimmed.wav");
const clang = new Audio("../audio/clang.wav");
clang.volume = 0.9;

let playing = false;
let t = section.from;
let started = 0;

const scrub = document.getElementById("scrub") as HTMLInputElement;
const label = document.getElementById("t")!;
const play = document.getElementById("play")!;
let clangFired = false;

function show(time: number) {
  t = time;
  render(film, t);
  label.textContent = `${t.toFixed(3)}s`;
  scrub.value = String(t);
}

function loop() {
  if (!playing) return;
  const now = section.from + (performance.now() - started) / 1000;
  if (now >= section.to) { stop(); show(section.to); return; }
  if (!clangFired && now >= VO.arrive.off) { clangFired = true; clang.currentTime = 0; clang.play(); }
  show(now);
  requestAnimationFrame(loop);
}

function start() {
  playing = true;
  clangFired = t > VO.arrive.off;
  started = performance.now() - (t - section.from) * 1000;
  vo.currentTime = t;
  vo.play();
  play.textContent = "pause";
  loop();
}
function stop() {
  playing = false; vo.pause(); play.textContent = "play";
}

play.addEventListener("click", () => (playing ? stop() : start()));
scrub.addEventListener("input", () => { stop(); show(Number(scrub.value)); });
addEventListener("keydown", (e) => {
  if (e.key === " ") { e.preventDefault(); playing ? stop() : start(); }
  if (e.key === "ArrowLeft") { stop(); show(Math.max(section.from, t - 1 / 30)); }
  if (e.key === "ArrowRight") { stop(); show(Math.min(section.to, t + 1 / 30)); }
});

const fit = () => document.body.style.setProperty(
  "--fit", String(Math.min(1, (innerWidth - 60) / 1920)));
addEventListener("resize", fit); fit();

scrub.min = String(section.from); scrub.max = String(section.to); scrub.step = "0.001";
show(section.from);
