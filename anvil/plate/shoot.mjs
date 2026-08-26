import { chromium } from "playwright";
import { LAUNCH } from "../src/chromium.mjs";
import { serve } from "../scripts/serve.mjs";
const { server, url } = await serve();
const b = await chromium.launch(LAUNCH);
const p = await b.newPage({ viewport: { width: 1300, height: 2700 } });

await p.goto(`${url}/plate/assets.html`);
await p.waitForFunction(() => window.ready0 === true);
await p.evaluate(() => document.fonts.ready);
await p.locator("#tile").screenshot({ path: "plate/icon_tile.png", omitBackground: true });
await p.locator("#art").screenshot({ path: "plate/icon_art.png", omitBackground: true });

await p.goto(`${url}/plate/circle.html`);
await p.waitForFunction(() => window.ready0 === true);
await p.evaluate(() => document.fonts.ready);
await p.screenshot({ path: "plate/circle_full.png", clip: { x: 0, y: 0, width: 1180, height: 2556 } });

await b.close(); server.close();
console.log("assets shot");
