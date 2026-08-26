import { chromium } from "playwright";
import { LAUNCH } from "../src/chromium.mjs";
import { mkdirSync, rmSync, existsSync } from "node:fs";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import { serve } from "./serve.mjs";
import { execFileSync } from "node:child_process";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");
const arg = (k, d) => {
  const i = process.argv.indexOf(`--${k}`);
  return i === -1 ? d : process.argv[i + 1];
};

const from = Number(arg("from", 0));
const to = Number(arg("to", 13.9));
const fps = Number(arg("fps", 30));
const height = Number(arg("height", 1080));
const name = arg("out", "act2-3");
const scale = height / 1080;

const frames = join(ROOT, "build/frames");
rmSync(frames, { recursive: true, force: true });
mkdirSync(frames, { recursive: true });

const browser = await chromium.launch(LAUNCH);
const page = await browser.newPage({
  viewport: { width: Math.round(1920 * scale), height: Math.round(1080 * scale) },
  deviceScaleFactor: 1,
});
const { server, url } = await serve();
await page.goto(`${url}/build/frame.html`);
await page.waitForFunction(() => window.ready === true, null, { timeout: 20000 })
  .catch(() => {});
if (scale !== 1) {
  await page.addStyleTag({ content:
    `.stage{transform:scale(${scale});transform-origin:top left}
     html,body{width:${1920 * scale}px;height:${1080 * scale}px;overflow:hidden}` });
}

const total = Math.round((to - from) * fps);
process.stdout.write(`rendering ${total} frames @ ${fps}fps, ${Math.round(1920 * scale)}×${height}\n`);
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

/* ---- audio bed for this section: VO slice + the clang, placed absolutely ---- */

const clangAt = Number(arg("clang", 11.904));
const dur = to - from;
const out = join(ROOT, `out/${name}.mp4`);
mkdirSync(join(ROOT, "out"), { recursive: true });

const hasClang = clangAt >= from && clangAt < to;
const filter = hasClang
  ? `[1:a]atrim=start=${from}:end=${to},asetpts=N/SR/TB[vo];` +
    `[2:a]adelay=${Math.round((clangAt - from) * 1000)}|${Math.round((clangAt - from) * 1000)},` +
    `pan=mono|c0=0.5*c0+0.5*c1[cl];` +
    `[vo][cl]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.97[a]`
  : `[1:a]atrim=start=${from}:end=${to},asetpts=N/SR/TB,alimiter=limit=0.97[a]`;

execFileSync("ffmpeg", [
  "-hide_banner", "-v", "error", "-y",
  "-framerate", String(fps), "-i", join(frames, "f%05d.png"),
  "-i", join(ROOT, "audio/vo_trimmed.wav"),
  ...(hasClang ? ["-i", join(ROOT, "audio/clang.wav")] : []),
  "-filter_complex", filter,
  "-map", "0:v", "-map", "[a]",
  "-c:v", "libx264", "-preset", "slow", "-crf", "17",
  "-pix_fmt", "yuv420p", "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709",
  "-c:a", "aac", "-b:a", "192k",
  "-t", String(dur), out,
], { stdio: "inherit" });

console.log(`\nwrote ${out}`);
