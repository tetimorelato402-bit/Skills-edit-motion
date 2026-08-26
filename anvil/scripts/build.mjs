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
  toks.splice(a, b - a + 1, { tag: "g", raw: `<g data-el="${id}"${attrs ? " " + attrs : ""}>${inner}</g>` });
}
const tag = (toks, i, id) => {
  toks[i].raw = toks[i].raw.replace(/^<([a-zA-Z]+)/, `<$1 data-el="${id}"`);
};
const serialize = ({ head, toks }) => head + toks.map((t) => t.raw).join("") + "</svg>";

/* ---------- depth banding ----------
 * A screen that drifts as one rigid sheet reads as a picture of an app, not
 * as an app. These wrap each screen's contents into bands that drift
 * independently: the header and the tab bar barely move (they are chrome,
 * attached to the device), and each card group moves on its own phase at its
 * own depth. Bands carry no transform attribute of their own, so the
 * renderer's CSS transform has nothing to fight.
 */

const yOf = (raw) => {
  const m = /\sy="(-?[\d.]+)"/.exec(raw) ?? /\scy="(-?[\d.]+)"/.exec(raw)
        ?? /\sy1="(-?[\d.]+)"/.exec(raw) ?? /translate\([\d.-]+,\s*(-?[\d.]+)\)/.exec(raw);
  return m ? parseFloat(m[1]) : null;
};
/** a wide rounded rect, or a mono section label — both start a new card group */
const startsGroup = (raw) => {
  const w = /\swidth="([\d.]+)"/.exec(raw);
  if (raw.startsWith("<rect") && /\srx="/.test(raw) && w && +w[1] >= 300) return true;
  return raw.startsWith("<text") && /letter-spacing="2"/.test(raw) && /DM Mono/.test(raw);
};

function band(toks, a, b, depth, phase) {
  if (b < a) return 0;
  const inner = toks.slice(a, b + 1).map((t) => t.raw).join("");
  toks.splice(a, b - a + 1, { tag: "g",
    raw: `<g data-depth="${depth}" data-phase="${phase.toFixed(2)}">${inner}</g>` });
  return 1;
}

/** Wrap a phone screen's tokens into chrome / card-group / chrome bands. */
function depthBands(doc) {
  const t = doc.toks;
  // tab bar: the dark pill near the bottom and everything after it
  let tab = t.findIndex((x) => /<rect[^>]*\sy="848"/.test(x.raw));
  if (tab === -1) tab = t.length;
  // header: everything above the divider line at y=56
  let head = t.findIndex((x) => /<line[^>]*\sy1="56"/.test(x.raw));
  head = head === -1 ? -1 : head;

  if (tab < t.length) band(t, tab, t.length - 1, 0.30, 4.1);
  const bodyEnd = (tab < t.length ? tab : t.length) - 1;

  // card groups, bottom-up so indices stay valid
  const starts = [];
  for (let i = head + 1; i <= bodyEnd; i++) if (startsGroup(t[i].raw)) starts.push(i);
  for (let k = starts.length - 1; k >= 0; k--) {
    const a = starts[k];
    const b = (k === starts.length - 1 ? bodyEnd : starts[k + 1] - 1);
    band(t, a, b, 0.86 + 0.24 * (k % 4), 1.7 * k + 0.4);
  }
  if (head > 0) band(t, 0, head, 0.34, 2.6);
  return doc;
}

/**
 * The arrival banner, rebuilt rather than relocated. The asset ships it as an
 * in-app card sized to the screen's gutters; a system notification is a
 * different object — wider than the app, rounder, and hung across the top
 * edge of the device rather than laid inside it. Only the strings survive.
 */
const TOAST_SVG = (title, sub) =>
  `<svg xmlns="http://www.w3.org/2000/svg" width="462" height="116" viewBox="0 0 462 116">` +
  `<g data-el="toast">` +
  `<rect x="6" y="16" width="450" height="84" rx="26" fill="#241C13"/>` +
  `<circle cx="54" cy="58" r="21" fill="#A8895E"/>` +
  `<text x="54" y="65" font-family="Fraunces, Georgia, serif" font-size="18" font-weight="700" fill="#E7E0D2" text-anchor="middle">A</text>` +
  `<text x="90" y="52" font-family="Fraunces, Georgia, serif" font-size="18" font-weight="700" fill="#E7E0D2">${title}</text>` +
  `<text x="90" y="76" font-family="'DM Mono', ui-monospace, monospace" font-size="12" fill="#C3B49B">${sub}</text>` +
  `<text x="428" y="52" font-family="'DM Mono', ui-monospace, monospace" font-size="12" fill="#8B8475" text-anchor="end">now</text>` +
  `</g></svg>`;

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
  out["06_home"] = serialize(depthBands(doc));
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
  out["04_onboard_commitments"] = serialize(depthBands(doc));
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
  out["07_locked"] = serialize(depthBands(doc));
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
  out["08_arrived"] = serialize(depthBands(doc));
  const text = (needle) => {
    const m = new RegExp(`>([^<]*${needle}[^<]*)<`).exec(toast);
    if (!m) throw new Error(`build: banner text ${needle} not found`);
    return m[1];
  };
  out["08_toast"] = TOAST_SVG(text("made it"), text("camera"));
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
  out["09_unlocked"] = serialize(depthBands(doc));
}

// everything else passes through with fonts swapped only
for (const n of ["01_onboard_name", "02_onboard_phone",
                 "05_onboard_places", "07_tab_routine", "07_tab_circle",
                 "10_friend_arrived", "11_circle_live", "12_notification"]) {
  out[n] = serialize(depthBands(parse(src(n))));
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
<g transform="translate(772,457)"><g data-el="mark"><g transform="scale(2.6) translate(-40,-32)">${ANVIL_MARK}</g></g></g>
<text data-el="wordmark" x="896" y="502" font-family="Fraunces, Georgia, serif" font-size="92" font-weight="700" letter-spacing="16" fill="#15130E">ANVIL</text>
<text data-el="tagline" x="960" y="596" font-family="Inter, system-ui, sans-serif" font-size="29" fill="#8B8475" text-anchor="middle">Sharpen iron with iron.</text>
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
