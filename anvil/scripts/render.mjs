import { chromium } from "playwright";
import { LAUNCH } from "../src/chromium.mjs";
import { mkdirSync, rmSync, existsSync } from "node:fs";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import { serve } from "./serve.mjs";
import { FORMATS } from "../build/timeline.js";
import { execFileSync } from "node:child_process";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");
const arg = (k, d) => {
  const i = process.argv.indexOf(`--${k}`);
  return i === -1 ? d : process.argv[i + 1];
};

const from = Number(arg("from", 0));
const to = Number(arg("to", 26.25));
const fps = Number(arg("fps", 30));
const format = arg("format", "vertical");
const F = FORMATS[format];
if (!F) throw new Error(`unknown format ${format} — try vertical|wide`);
const height = Number(arg("height", F.height));
const name = arg("out", "anvil");
const scale = height / F.height;

const frames = join(ROOT, "build/frames");
rmSync(frames, { recursive: true, force: true });
mkdirSync(frames, { recursive: true });

const browser = await chromium.launch(LAUNCH);
const page = await browser.newPage({
  viewport: { width: Math.round(F.width * scale), height: Math.round(F.height * scale) },
  deviceScaleFactor: 1,
});
const { server, url } = await serve();
await page.goto(`${url}/build/frame.html?format=${format}`);
await page.waitForFunction(() => window.ready === true, null, { timeout: 20000 })
  .catch(() => {});
if (scale !== 1) {
  await page.addStyleTag({ content:
    `.stage{transform:scale(${scale});transform-origin:top left}
     html,body{width:${F.width * scale}px;height:${F.height * scale}px;overflow:hidden}` });
}

const total = Math.round((to - from) * fps);
process.stdout.write(`rendering ${total} frames @ ${fps}fps, ${format} ${Math.round(F.width * scale)}×${height}\n`);
for (let i = 0; i < total; i++) {
  const t = from + i / fps;
  await page.evaluate((tt) => window.setTime(tt), t);
  await page.screenshot({
    path: join(frames, `f${String(i).padStart(5, "0")}.png`),
    animations: "disabled",
  });
  if (i % 30 === 0) process.stdout.write(`  ${i}/${total}\r`);
}
await browser.close();
server.close();

/* ---- audio: slice the prebuilt mix, so picture and sound share one clock ---- */

const out = join(ROOT, `out/${name}.mp4`);
mkdirSync(join(ROOT, "out"), { recursive: true });

execFileSync("ffmpeg", [
  "-hide_banner", "-v", "error", "-y",
  "-framerate", String(fps), "-i", join(frames, "f%05d.png"),
  "-ss", String(from), "-t", String(to - from), "-i", join(ROOT, "audio/mix.wav"),
  "-map", "0:v", "-map", "1:a",
  "-c:v", "libx264", "-preset", "slow", "-crf", "17",
  "-pix_fmt", "yuv420p",
  "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709",
  "-c:a", "aac", "-b:a", "192k",
  "-shortest", out,
], { stdio: "inherit" });

console.log(`\nwrote ${out}`);
