import { chromium } from "playwright";
import { LAUNCH } from "../src/chromium.mjs";
import { serve } from "./serve.mjs";
const { server, url } = await serve();
const b = await chromium.launch(LAUNCH);
const p = await b.newPage({ viewport: { width: 1920, height: 1080 } });
await p.goto(`${url}/build/frame.html`);
await p.waitForFunction(() => window.ready === true, null, { timeout: 20000 }).catch(()=>{});
const times = process.argv.slice(2).map(Number);
const rows = await p.evaluate(async (ts) => {
  const { evaluate } = await import("./stage.js").catch(() => ({}));
  return null;
}, times);
// stage.js isn't a separate chunk; probe through the DOM instead
for (const t of times) {
  await p.evaluate((tt) => window.setTime(tt), t);
  const s = await p.evaluate(() => {
    const g = (id) => { const e = document.getElementById(id); return e && getComputedStyle(e); };
    const num = (m) => m ? [...m.matchAll(/-?[\d.]+/g)].map(Number) : null;
    const cam = num(g("camera").transform);
    return {
      camScale: cam ? +(cam[0]).toFixed(3) : null,
      locked: +(+g("layer-locked").opacity).toFixed(3),
      opened: +(+g("layer-opened").opacity).toFixed(3),
      lockOp: +(+g("lock").opacity).toFixed(3),
      finder: +(+g("finder").opacity).toFixed(3),
      glow: +(+g("warmGlow").opacity).toFixed(3),
    };
  });
  console.log(t.toFixed(3), JSON.stringify(s));
}
await b.close(); server.close();
