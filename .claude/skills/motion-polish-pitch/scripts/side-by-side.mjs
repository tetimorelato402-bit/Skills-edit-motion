#!/usr/bin/env node
// Compose before/after recordings into one labelled side-by-side clip, with no
// ffmpeg dependency: a headless Chromium page plays both videos in sync and
// Playwright records it. If a full ffmpeg (with libx264) is on PATH the result
// is also transcoded to MP4 for Instagram/X/LinkedIn upload.
//
//   node side-by-side.mjs <capture-dir> [--title "acme.com"] [--height 720]
// Expects <capture-dir>/before/video.webm and <capture-dir>/after/video.webm.
// Writes <capture-dir>/before-after.webm (and .mp4 when possible).

import { existsSync, renameSync, writeFileSync } from 'node:fs';
import { join, resolve } from 'node:path';
import { execSync, spawnSync } from 'node:child_process';
import { pathToFileURL } from 'node:url';

const argv = process.argv.slice(2);
const dir = argv.find((a) => !a.startsWith('--'));
if (!dir) { console.error('usage: side-by-side.mjs <capture-dir> [--title text] [--height 720]'); process.exit(2); }
const opt = (n, d) => { const i = argv.indexOf(`--${n}`); return i === -1 ? d : argv[i + 1]; };
const title = opt('title', '');
const H = Number(opt('height', 720));

const loadPlaywright = async () => {
  try { return await import('playwright'); } catch {}
  const root = execSync('npm root -g', { encoding: 'utf8' }).trim();
  for (const pkg of ['playwright', 'playwright-core', '@playwright/test']) {
    try { return await import(pathToFileURL(join(root, pkg, 'index.mjs')).href); } catch {}
  }
  console.error('playwright not found. Run: npm i -g playwright');
  process.exit(2);
};
const { chromium } = await loadPlaywright();

const abs = resolve(dir);
for (const side of ['before', 'after']) {
  if (!existsSync(join(abs, side, 'video.webm'))) { console.error(`missing ${side}/video.webm`); process.exit(1); }
}

// Both source videos share the viewport aspect; compute the composite width.
const probe = await chromium.launch();
const pp = await probe.newPage();
await pp.goto(pathToFileURL(join(abs, 'before', 'video.webm')).href).catch(() => {});
const dims = await pp.evaluate(() => new Promise((res) => {
  const v = document.querySelector('video'); if (!v) return res({ w: 1440, h: 900 });
  const done = () => res({ w: v.videoWidth || 1440, h: v.videoHeight || 900 });
  v.readyState >= 1 ? done() : v.addEventListener('loadedmetadata', done, { once: true });
}));
await probe.close();
const paneW = Math.round((dims.w / dims.h) * H);
const W = paneW * 2 + 24;

const html = `<!doctype html><meta charset="utf-8"><style>
html,body{margin:0;background:#0a0a0a;width:${W}px;height:${H + (title ? 56 : 0)}px;overflow:hidden;font-family:system-ui,-apple-system,sans-serif}
.row{display:flex;gap:24px}.pane{position:relative;width:${paneW}px;height:${H}px;background:#000}
video{width:100%;height:100%;display:block;object-fit:cover}
.tag{position:absolute;top:16px;left:16px;padding:8px 14px;border-radius:999px;font:600 18px/1 system-ui;color:#fff;background:rgba(0,0,0,.6);letter-spacing:.04em}
.tag.after{background:#16a34a}
.title{height:56px;display:flex;align-items:center;justify-content:center;color:#a3a3a3;font:500 18px system-ui}
</style>
<div class="row">
 <div class="pane"><video id="a" muted playsinline preload="auto" src="before/video.webm"></video><span class="tag">BEFORE</span></div>
 <div class="pane"><video id="b" muted playsinline preload="auto" src="after/video.webm"></video><span class="tag after">AFTER</span></div>
</div>${title ? `<div class="title">${title.replace(/</g, '&lt;')} — motion polish preview</div>` : ''}
<script>
 const a=document.getElementById('a'),b=document.getElementById('b');
 window.__ended=false;
 Promise.all([a,b].map(v=>new Promise(r=>v.readyState>=3?r():v.addEventListener('canplaythrough',r,{once:true})))).then(async()=>{
   await Promise.all([a.play(),b.play()]);
   const check=()=>{ if(a.ended||b.ended){ a.pause(); b.pause(); window.__ended=true; } else requestAnimationFrame(check); };
   check();
 });
</script>`;
writeFileSync(join(abs, 'composite.html'), html);

const browser = await chromium.launch();
const context = await browser.newContext({
  viewport: { width: W, height: H + (title ? 56 : 0) },
  recordVideo: { dir: abs, size: { width: W, height: H + (title ? 56 : 0) } },
});
const page = await context.newPage();
await page.goto(pathToFileURL(join(abs, 'composite.html')).href);
await page.waitForFunction(() => window.__ended === true, null, { timeout: 180000 });
await page.waitForTimeout(400);
const video = page.video();
await context.close();
const out = join(abs, 'before-after.webm');
renameSync(await video.path(), out);
await browser.close();

let mp4 = null;
const ff = spawnSync('ffmpeg', ['-hide_banner', '-encoders'], { encoding: 'utf8' });
if (ff.status === 0 && /libx264/.test(ff.stdout)) {
  mp4 = join(abs, 'before-after.mp4');
  const r = spawnSync('ffmpeg', ['-y', '-loglevel', 'error', '-i', out, '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', '-crf', '22', mp4]);
  if (r.status !== 0) mp4 = null;
}
console.log(JSON.stringify({ webm: out, mp4, width: W, height: H + (title ? 56 : 0) }, null, 2));
