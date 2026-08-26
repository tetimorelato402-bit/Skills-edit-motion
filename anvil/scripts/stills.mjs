import { chromium } from "playwright";
import { LAUNCH } from "../src/chromium.mjs";
import { mkdirSync } from "node:fs";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import { serve } from "./serve.mjs";
const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");
const outDir = join(ROOT, "build/stills");
mkdirSync(outDir, { recursive: true });
const times = process.argv.slice(2).map(Number);
const b = await chromium.launch(LAUNCH);
const fmt = process.env.FMT ?? "vertical";
const dim = fmt === "wide" ? [1920,1080] : [1080,1920];
const p = await b.newPage({ viewport: { width: dim[0], height: dim[1] } });
const { server, url } = await serve();
await p.goto(`${url}/build/frame.html?format=${fmt}`);
await p.waitForFunction(() => window.ready === true, null, { timeout: 20000 }).catch(()=>{});
for (const t of times) {
  await p.evaluate((tt) => window.setTime(tt), t);
  await p.screenshot({ path: join(outDir, `t${t.toFixed(3)}.png`) });
}
await b.close();
server.close();
console.log("stills:", times.join(", "));
