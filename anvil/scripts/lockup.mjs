import { chromium } from "playwright";
import { LAUNCH } from "../src/chromium.mjs";
import { serve } from "./serve.mjs";
const { server, url } = await serve();
const b = await chromium.launch(LAUNCH);
const p = await b.newPage({ viewport: { width: 1920, height: 1080 } });
await p.goto(`${url}/build/frame.html`);
await p.waitForFunction(() => window.ready === true, null, {timeout:20000}).catch(()=>{});
await p.evaluate(() => window.setTime(25.0));
console.log(await p.evaluate(() => {
  const box = (id) => { const r = document.getElementById(id).getBoundingClientRect();
    return { x: Math.round(r.x), r: Math.round(r.right), y: Math.round(r.y), b: Math.round(r.bottom) }; };
  const m = box("mark"), w = box("wordmark"), t = box("tagline");
  return { mark: m, word: w, tag: t,
           lockupSpan: [m.x, w.r], lockupCentre: Math.round((m.x + w.r) / 2),
           gap: w.x - m.r, frameCentre: 960 };
}));
await b.close(); server.close();
