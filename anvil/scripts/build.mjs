import { readFileSync, writeFileSync, mkdirSync, existsSync } from "node:fs";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import * as esbuild from "esbuild";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");
const SCREENS = join(ROOT, "assets/screens");
const OUT = join(ROOT, "build");
mkdirSync(OUT, { recursive: true });

/* ---------- fonts: the SVGs ship Georgia / Courier stand-ins ---------- */

const FONT_SWAP = [
  [/font-family="Georgia, 'Times New Roman', serif"/g,
   `font-family="Fraunces, Georgia, serif"`],
  [/font-family="Inter, Helvetica, Arial, sans-serif"/g,
   `font-family="Inter, system-ui, sans-serif"`],
  [/font-family="'DM Mono','Courier New',monospace"/g,
   `font-family="'DM Mono', ui-monospace, monospace"`],
];
const swapFonts = (s) => FONT_SWAP.reduce((a, [re, to]) => a.replace(re, to), s);

/* ---------- a tiny tokenizer: these SVGs are flat, generated markup ---------- */

function parse(svg) {
  const open = svg.indexOf(">") + 1;
  const head = svg.slice(0, open);
  const body = svg.slice(open, svg.lastIndexOf("</svg>"));
  const toks = [];
  let i = 0;
  while (i < body.length) {
    if (body[i] !== "<") { i++; continue; }
    const tag = /^<([a-zA-Z]+)/.exec(body.slice(i))[1];
    const close = body.indexOf(">", i);
    if (body[close - 1] === "/") {
      toks.push({ tag, raw: body.slice(i, close + 1) });
      i = close + 1;
    } else {
      // balanced search for the matching end tag
      let depth = 1, j = close + 1;
      while (depth > 0) {
        const nextOpen = body.indexOf(`<${tag}`, j);
        const nextClose = body.indexOf(`</${tag}>`, j);
        if (nextOpen !== -1 && nextOpen < nextClose) { depth++; j = nextOpen + 1; }
        else { depth--; j = nextClose + tag.length + 3; }
      }
      toks.push({ tag, raw: body.slice(i, j) });
      i = j;
    }
  }
  return { head, toks };
}

const find = (toks, needle, from = 0) => {
  const i = toks.findIndex((t, k) => k >= from && t.raw.includes(needle));
  if (i === -1) throw new Error(`build: no element matching ${JSON.stringify(needle)}`);
  return i;
};

/** wrap toks[a..b] in <g id=…>, in place */
function group(toks, a, b, id, attrs = "") {
  const inner = toks.slice(a, b + 1).map((t) => t.raw).join("");
  toks.splice(a, b - a + 1, { tag: "g", raw: `<g id="${id}"${attrs ? " " + attrs : ""}>${inner}</g>` });
}
const tag = (toks, i, id) => {
  toks[i].raw = toks[i].raw.replace(/^<([a-zA-Z]+)/, `<$1 id="${id}"`);
};
const serialize = ({ head, toks }) => head + toks.map((t) => t.raw).join("") + "</svg>";

/* ---------- derive the variants the timeline animates ---------- */

const src = (n) => swapFonts(readFileSync(join(SCREENS, `${n}.svg`), "utf8"));
const out = {};

// 06_home — commitment rows become stagger children
{
  const doc = parse(src("06_home"));
  const t = doc.toks;
  tag(t, find(t, `<rect x="18" y="112"`), "cardTop");
  tag(t, find(t, `<rect x="18" y="310"`), "cardCommitments");
  tag(t, find(t, `<rect x="18" y="488"`), "cardMarks");
  out["06_home"] = serialize(doc);
}

// 04_onboard_commitments — the three chosen chips are the film's one stagger
{
  const doc = parse(src("04_onboard_commitments"));
  const t = doc.toks;
  let at = find(t, `<rect x="34" y="172"`);
  for (let i = 0; i < 3; i++) {
    group(t, at, at + 1, `chip${i}`);   // each chip is a rect + its label
    at += 1;
  }
  out["04_onboard_commitments"] = serialize(doc);
}

// 07_tab_camera — the lock is the idea, so it gets handles
{
  const doc = parse(src("07_tab_camera"));
  const t = doc.toks;
  tag(t, find(t, `>LOCKED<`), "statusLabel");
  tag(t, find(t, `<rect x="18" y="112"`), "card");
  const ring = find(t, `<circle cx="215.0" cy="330" r="34"`);
  tag(t, ring, "lockRing");
  tag(t, ring + 1, "lockBody");               // padlock rect
  tag(t, ring + 2, "lockShackle");            // shackle path
  group(t, ring, ring + 2, "lock");
  const copy = find(t, `>Not there yet<`);
  group(t, copy, copy + 2, "lockCopy");
  out["07_locked"] = serialize(doc);
}

// 08_arrival_toast — split the banner off from the screen underneath it
{
  const doc = parse(src("08_arrival_toast"));
  const t = doc.toks;
  const a = find(t, `<rect x="46" y="70"`);
  const toast = t.slice(a, a + 5).map((x) => x.raw).join("");
  t.splice(a, 5);
  tag(t, find(t, `>UNLOCKED · AT LIFT<`), "statusLabel");
  tag(t, find(t, `<rect x="18" y="112"`), "card");
  const f = find(t, `<circle cx="215.0" cy="330" r="46"`);
  group(t, f, f + 1, "finder");
  tag(t, find(t, `>YOU ARE HERE<`), "hereLabel");
  out["08_arrived"] = serialize(doc);
  // the banner ships inset from the card gutter and clips the status label
  // behind it; align it to the card (x=18, w=394) and it reads as one system
  const aligned = toast.replace('<rect x="46" y="70" width="338"', '<rect x="46" y="70" width="394"');
  out["08_toast"] = `${doc.head}<g id="toast" transform="translate(-28,0)">${aligned}</g></svg>`;
}

// 09_camera_unlocked
{
  const doc = parse(src("09_camera_unlocked"));
  const t = doc.toks;
  tag(t, find(t, `>UNLOCKED · AT LIFT<`), "statusLabel");
  tag(t, find(t, `<rect x="18" y="112"`), "card");
  const f = find(t, `<circle cx="215.0" cy="330" r="46"`);
  group(t, f, f + 2, "finder");               // 2 circles + the lens hood path
  tag(t, find(t, `>YOU ARE HERE<`), "hereLabel");
  const c = find(t, `<rect x="46" y="524"`);
  group(t, c, c + 1, "capture");
  out["09_unlocked"] = serialize(doc);
}

// everything else passes through with fonts swapped only
for (const n of ["01_onboard_name", "02_onboard_phone",
                 "05_onboard_places", "07_tab_routine", "07_tab_circle",
                 "10_friend_arrived", "11_circle_live", "12_notification"]) {
  out[n] = src(n);
}

/* ---------- the closing lockup, in stage space ---------- */

// Shifted +30 from a naive centring: the wordmark's letter-spacing adds a
// trailing gap after the L that the bounding box counts and the eye does not,
// so measured-centre and optical-centre differ by half a letter-space.
// The positioning transform lives on an OUTER group: an animated node must
// not carry a transform attribute of its own, because the CSS transform the
// renderer writes replaces it outright and snaps the element to the origin.
const ANVIL_MARK =
  `<path d="M8 20 L72 20 L62 30 L50 30 L50 40 L56 52 L24 52 L30 40 L30 30 L18 30 Z" fill="#15130E"/>` +
  `<rect x="34" y="40" width="12" height="14" fill="#15130E"/>`;

out["logo"] = `<svg xmlns="http://www.w3.org/2000/svg" width="1920" height="1080" viewBox="0 0 1920 1080">
<g transform="translate(772,457)"><g id="mark"><g transform="scale(2.6) translate(-40,-32)">${ANVIL_MARK}</g></g></g>
<text id="wordmark" x="896" y="502" font-family="Fraunces, Georgia, serif" font-size="92" font-weight="700" letter-spacing="16" fill="#15130E">ANVIL</text>
<text id="tagline" x="960" y="596" font-family="Inter, system-ui, sans-serif" font-size="29" fill="#8B8475" text-anchor="middle">Sharpen iron with iron.</text>
</svg>`;

writeFileSync(join(OUT, "screens.js"),
  `export const SCREENS = ${JSON.stringify(out)};\n`);

/* ---------- pages ---------- */

const FONTS = `<link rel="stylesheet" href="../assets/fonts/fonts.css">`;

writeFileSync(join(OUT, "frame.html"), `<!doctype html>
<meta charset="utf-8"><title>ANVIL frame</title>
${FONTS}
<style>html,body{margin:0;background:#E7E0D2}</style>
<div id="root"></div>
<script type="module" src="./frame.js"></script>
`);

writeFileSync(join(OUT, "preview.html"), `<!doctype html>
<meta charset="utf-8"><title>ANVIL — preview</title>
${FONTS}
<div class="frame"><div id="root"></div></div>
<div class="bar">
  <button id="play">play</button>
  <input id="scrub" type="range">
  <span class="t" id="t">0.000s</span>
</div>
<div class="sec"></div>
<script type="module" src="./preview.js"></script>
`);

/* ---------- bundle ---------- */

for (const [entry, name] of [["src/preview.ts", "preview.js"], ["src/frame.ts", "frame.js"],
                             ["src/timeline.ts", "timeline.js"]]) {
  if (!existsSync(join(ROOT, entry))) continue;
  await esbuild.build({
    entryPoints: [join(ROOT, entry)],
    bundle: true, format: "esm", target: "es2022",
    outfile: join(OUT, name), logLevel: "warning",
  });
}

console.log(`build: ${Object.keys(out).length} screens, bundles written to build/`);
