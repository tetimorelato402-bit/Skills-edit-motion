#!/usr/bin/env python3
"""Build the contact sheet page from a manifest of uploaded asset URLs.

manifest.json: {"reels": {deck: url}, "slides": {deck: [url x7]}}
"""
import json, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from decks import DECKS

SP = os.path.dirname(os.path.abspath(__file__))
M = json.load(open(f"{SP}/manifest.json"))
CAT = {"couple": "couple", "ex": "ex", "general": "general"}
SLIDE_LABEL = ["theme", "q1", "q2", "q3", "q4", "q5", "cta"]

cards = []
for d in DECKS:
    k = d["key"]
    reel = M["reels"][k]
    slides = M["slides"][k]
    thumbs = "".join(
        f'''<figure class="sl">
          <button class="shot" data-u="{u}" data-n="heyagain_{k}_{i + 1}_{SLIDE_LABEL[i]}.png"
                  title="download slide {i + 1}">
            <img src="{u}" alt="{k} slide {i + 1}" loading="lazy">
            <figcaption><span>{i + 1}</span>{SLIDE_LABEL[i]}</figcaption>
          </button></figure>'''
        for i, u in enumerate(slides))
    qs = "".join(f"<li>{q}</li>" for q in d["questions"])
    cards.append(f'''
    <section class="deck" id="{k}" data-cat="{d['cat']}">
      <header class="dh">
        <div class="dt">
          <span class="cat cat-{d['cat']}">{CAT[d['cat']]}</span>
          <h2>{d['lead']} <b>{d['subject']}</b></h2>
        </div>
        <div class="acts">
          <button class="btn" data-one="{reel}" data-n="heyagain_{k}_reel.mp4">reel .mp4</button>
          <button class="btn ghost" data-zip="{k}">7 slides .zip</button>
        </div>
      </header>
      <div class="body">
        <div class="reel">
          <video src="{reel}" controls preload="metadata" playsinline></video>
        </div>
        <div class="slides">{thumbs}</div>
      </div>
      <details class="qs"><summary>the five questions</summary><ol>{qs}</ol></details>
    </section>''')

manifest_js = json.dumps({k: M["slides"][k] for k in M["slides"]})
labels_js = json.dumps(SLIDE_LABEL)
all_files = json.dumps(
    [{"u": M["reels"][d["key"]], "n": f"reels/heyagain_{d['key']}_reel.mp4"} for d in DECKS]
    + [{"u": u, "n": f"slides/{d['key']}/heyagain_{d['key']}_{i + 1}_{SLIDE_LABEL[i]}.png"}
       for d in DECKS for i, u in enumerate(M["slides"][d["key"]])])

html = f'''<!doctype html>
<html lang="en"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Social Template Assets</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
:root{{
  --orange:#D8652B; --orange-d:#B44F1E; --cream:#F4EEE4;
  --bg:#FBF7F1; --card:#FFFFFF; --ink:#22160F; --muted:#6F5C4E;
  --line:rgba(34,22,15,.12); --shadow:0 1px 2px rgba(34,22,15,.06),0 8px 24px rgba(34,22,15,.07);
}}
:root:not([data-theme="light"]){{
  @media (prefers-color-scheme: dark){{
    --bg:#140E09; --card:#1E1611; --ink:#F4EEE4; --muted:#B49C89;
    --line:rgba(244,238,228,.14); --shadow:0 1px 2px rgba(0,0,0,.4),0 8px 24px rgba(0,0,0,.35);
  }}
}}
:root[data-theme="dark"]{{
  --bg:#140E09; --card:#1E1611; --ink:#F4EEE4; --muted:#B49C89;
  --line:rgba(244,238,228,.14); --shadow:0 1px 2px rgba(0,0,0,.4),0 8px 24px rgba(0,0,0,.35);
}}
*{{box-sizing:border-box}}
html,body{{margin:0}}
body{{background:var(--bg);color:var(--ink);
  font:400 16px/1.55 Inter,system-ui,-apple-system,sans-serif;
  -webkit-font-smoothing:antialiased}}
.wrap{{max-width:1180px;margin:0 auto;padding:0 16px 96px}}

.hero{{background:var(--orange);color:var(--cream);margin-bottom:40px}}
.hero .in{{max-width:1180px;margin:0 auto;padding:56px 16px 48px}}
.hero h1{{margin:0;font-size:clamp(30px,6vw,52px);font-weight:600;letter-spacing:-.025em;line-height:1.05}}
.hero h1 .dot{{display:inline-block;width:.30em;height:.30em;border-radius:50%;
  background:radial-gradient(circle at 36% 30%,#fff 0%,#fff 45%,#F3EADD 80%,#E3D6C2 100%);
  vertical-align:baseline;margin-left:.06em}}
.hero p{{margin:14px 0 0;max-width:62ch;opacity:.9;font-size:clamp(15px,2.2vw,18px)}}
.stats{{display:flex;flex-wrap:wrap;gap:10px;margin-top:26px}}
.stat{{background:rgba(255,255,255,.14);border:1px solid rgba(255,255,255,.22);
  border-radius:999px;padding:7px 15px;font-size:13.5px;font-weight:500}}
.hero .btn{{margin-top:26px;background:var(--cream);color:var(--orange-d);border-color:transparent;font-weight:600}}

.bar{{position:sticky;top:0;z-index:20;background:color-mix(in srgb,var(--bg) 88%,transparent);
  backdrop-filter:blur(12px);border-bottom:1px solid var(--line);margin-bottom:32px}}
.bar .in{{max-width:1180px;margin:0 auto;padding:11px 16px;display:flex;gap:8px;
  align-items:center;flex-wrap:wrap}}
.bar span{{font-size:13px;color:var(--muted);margin-right:2px}}
.chip{{border:1px solid var(--line);background:transparent;color:var(--ink);
  border-radius:999px;padding:6px 14px;font:500 13.5px Inter,sans-serif;cursor:pointer}}
.chip[aria-pressed="true"]{{background:var(--orange);border-color:var(--orange);color:#fff}}

.deck{{background:var(--card);border:1px solid var(--line);border-radius:18px;
  box-shadow:var(--shadow);padding:22px;margin-bottom:26px}}
.deck[hidden]{{display:none}}
.dh{{display:flex;gap:16px;align-items:flex-start;justify-content:space-between;
  flex-wrap:wrap;margin-bottom:20px}}
.dt h2{{margin:8px 0 0;font-size:clamp(20px,3.4vw,27px);font-weight:400;
  letter-spacing:-.02em;color:var(--muted)}}
.dt h2 b{{font-weight:600;color:var(--ink)}}
.cat{{display:inline-block;font:600 11px/1 Inter,sans-serif;letter-spacing:.09em;
  text-transform:uppercase;padding:5px 10px;border-radius:6px}}
.cat-couple{{background:rgba(216,101,43,.14);color:var(--orange-d)}}
.cat-ex{{background:rgba(120,72,160,.14);color:#7848A0}}
.cat-general{{background:rgba(42,110,120,.14);color:#2A6E78}}
:root[data-theme="dark"] .cat-ex,:root:not([data-theme="light"]) .cat-ex{{color:#C09BE0}}
:root[data-theme="dark"] .cat-general,:root:not([data-theme="light"]) .cat-general{{color:#78C4CE}}
:root[data-theme="dark"] .cat-couple,:root:not([data-theme="light"]) .cat-couple{{color:#F09264}}
@media (prefers-color-scheme: light){{
  :root:not([data-theme="dark"]) .cat-ex{{color:#7848A0}}
  :root:not([data-theme="dark"]) .cat-general{{color:#2A6E78}}
  :root:not([data-theme="dark"]) .cat-couple{{color:var(--orange-d)}}
}}

.acts{{display:flex;gap:8px;flex-wrap:wrap}}
.btn{{display:inline-flex;align-items:center;gap:7px;background:var(--orange);color:#fff;
  border:1px solid var(--orange);border-radius:10px;padding:9px 16px;
  font:500 14px Inter,sans-serif;text-decoration:none;cursor:pointer;white-space:nowrap}}
.btn:hover{{background:var(--orange-d);border-color:var(--orange-d)}}
.btn.ghost{{background:transparent;color:var(--ink);border-color:var(--line)}}
.btn.ghost:hover{{background:rgba(216,101,43,.09);border-color:var(--orange)}}

.body{{display:grid;grid-template-columns:232px 1fr;gap:22px;align-items:start}}
.reel video{{width:100%;aspect-ratio:9/16;border-radius:12px;background:var(--orange);display:block}}
.slides{{display:grid;grid-template-columns:repeat(auto-fill,minmax(122px,1fr));gap:12px}}
.sl{{margin:0}}
.shot{{display:block;width:100%;padding:0;border:0;background:none;
  color:inherit;font:inherit;cursor:pointer;text-align:left}}
.sl img{{width:100%;aspect-ratio:4/5;object-fit:cover;border-radius:9px;display:block;
  background:var(--orange);border:1px solid var(--line);transition:transform .14s ease}}
.shot:hover img{{transform:translateY(-2px)}}
.shot:focus-visible img{{outline:2px solid var(--orange);outline-offset:2px}}
.sl figcaption{{display:flex;gap:6px;align-items:center;margin-top:7px;
  font-size:12px;color:var(--muted)}}
.sl figcaption span{{background:var(--line);border-radius:4px;padding:1px 5px;
  font-weight:600;font-size:11px;color:var(--ink)}}

.qs{{margin-top:20px;border-top:1px solid var(--line);padding-top:14px}}
.qs summary{{cursor:pointer;font-size:13.5px;color:var(--muted);font-weight:500}}
.qs ol{{margin:12px 0 0;padding-left:22px;color:var(--ink)}}
.qs li{{margin:5px 0;font-size:15px}}

.note{{color:var(--muted);font-size:13.5px;margin:34px 0 0;text-align:center}}
.nodl{{margin:14px 0 0;font-size:13.5px;background:rgba(0,0,0,.18);
  border-radius:9px;padding:9px 13px;max-width:52ch}}
.btn:disabled{{opacity:.7;cursor:progress}}
#toast{{position:fixed;left:50%;bottom:26px;transform:translateX(-50%);z-index:60;
  background:var(--ink);color:var(--bg);border-radius:10px;padding:10px 18px;
  font-size:14px;font-weight:500;box-shadow:0 8px 28px rgba(0,0,0,.25)}}
#toast[hidden]{{display:none}}
@media (max-width:760px){{
  .body{{grid-template-columns:1fr}}
  .reel{{max-width:220px}}
  .dh{{flex-direction:column;gap:12px}}
}}
</style></head><body>

<div class="hero"><div class="in">
  <h1>hey again<span class="dot"></span></h1>
  <p>The social template: eight decks, each as a vertical reel and a seven-slide
     carousel. Orange field, cream Inter, the dot as the full stop. Every asset below
     downloads at full resolution.</p>
  <div class="stats">
    <div class="stat">8 reels · 1080×1920 · 30fps</div>
    <div class="stat">56 slides · 2160×2700</div>
    <div class="stat">40 questions</div>
    <div class="stat">3 categories</div>
  </div>
  <button class="btn" id="dl-all">Download everything · .zip</button>
  <p class="nodl" id="nodl" hidden>Saving files isn’t available in this view — open the
     artifact in its own tab to download.</p>
</div></div>

<div class="bar"><div class="in">
  <span>filter</span>
  <button class="chip" aria-pressed="true" data-f="all">all 8</button>
  <button class="chip" aria-pressed="false" data-f="couple">couple</button>
  <button class="chip" aria-pressed="false" data-f="ex">ex</button>
  <button class="chip" aria-pressed="false" data-f="general">general</button>
</div></div>

<main class="wrap">
{''.join(cards)}
  <p class="note">Click any slide to save that PNG. Batches arrive as a single .zip, so
     you confirm once instead of once per file.</p>
</main>
<div id="toast" hidden></div>

<script>
const SLIDES = {manifest_js};
const LABELS = {labels_js};
const ALL = {all_files};

/* The artifact viewer never grants a page a plain download link, so every save goes
   through the downloads capability. One prompt per file would mean 64 prompts for the
   whole set, so anything more than a single file is zipped here first and offered once. */
async function dl(){{
  try {{ return window.claude?.use ? await window.claude.use('downloads') : null; }}
  catch {{ return null; }}
}}

const CRC = (() => {{
  const t = new Uint32Array(256);
  for (let n = 0; n < 256; n++){{
    let c = n;
    for (let k = 0; k < 8; k++) c = (c & 1) ? (0xEDB88320 ^ (c >>> 1)) : (c >>> 1);
    t[n] = c >>> 0;
  }}
  return t;
}})();
function crc32(u8){{
  let c = 0xFFFFFFFF;
  for (let i = 0; i < u8.length; i++) c = CRC[(c ^ u8[i]) & 0xFF] ^ (c >>> 8);
  return (c ^ 0xFFFFFFFF) >>> 0;
}}

/* Store-only zip: PNG and MP4 are already compressed, so deflating them would cost time
   and save nothing. No zip64 — the whole set is under 10 MB. */
function zipStore(files){{
  const enc = new TextEncoder(), parts = [], central = [];
  const d = new Date();
  const time = ((d.getHours() << 11) | (d.getMinutes() << 5) | (d.getSeconds() >> 1)) & 0xFFFF;
  const date = (((d.getFullYear() - 1980) << 9) | ((d.getMonth() + 1) << 5) | d.getDate()) & 0xFFFF;
  let off = 0;
  for (const f of files){{
    const nb = enc.encode(f.name), crc = crc32(f.data), sz = f.data.length;
    const lh = new DataView(new ArrayBuffer(30));
    lh.setUint32(0, 0x04034b50, true); lh.setUint16(4, 20, true);
    lh.setUint16(6, 0x0800, true);     lh.setUint16(8, 0, true);
    lh.setUint16(10, time, true);      lh.setUint16(12, date, true);
    lh.setUint32(14, crc, true);       lh.setUint32(18, sz, true);
    lh.setUint32(22, sz, true);        lh.setUint16(26, nb.length, true);
    lh.setUint16(28, 0, true);
    parts.push(new Uint8Array(lh.buffer), nb, f.data);

    const ch = new DataView(new ArrayBuffer(46));
    ch.setUint32(0, 0x02014b50, true); ch.setUint16(4, 20, true);
    ch.setUint16(6, 20, true);         ch.setUint16(8, 0x0800, true);
    ch.setUint16(10, 0, true);         ch.setUint16(12, time, true);
    ch.setUint16(14, date, true);      ch.setUint32(16, crc, true);
    ch.setUint32(20, sz, true);        ch.setUint32(24, sz, true);
    ch.setUint16(28, nb.length, true); ch.setUint32(42, off, true);
    central.push(new Uint8Array(ch.buffer), nb);
    off += 30 + nb.length + sz;
  }}
  const cd = central.reduce((a, b) => a + b.length, 0);
  const eo = new DataView(new ArrayBuffer(22));
  eo.setUint32(0, 0x06054b50, true);   eo.setUint16(8, files.length, true);
  eo.setUint16(10, files.length, true); eo.setUint32(12, cd, true);
  eo.setUint32(16, off, true);
  return new Blob([...parts, ...central, new Uint8Array(eo.buffer)], {{type: 'application/zip'}});
}}

function toast(msg){{
  const t = document.getElementById('toast');
  t.textContent = msg; t.hidden = false;
  clearTimeout(t._h); t._h = setTimeout(() => {{ t.hidden = true; }}, 2200);
}}
function busy(btn, txt){{
  if (!btn) return toast(txt);                    // thumbnails report through the toast
  if (btn.dataset.label === undefined) btn.dataset.label = btn.textContent;
  btn.textContent = txt; btn.disabled = true;
}}
function done(btn, txt){{
  if (!btn) return txt ? toast(txt) : undefined;
  const back = btn.dataset.label;
  btn.disabled = false;
  if (txt){{ btn.textContent = txt; setTimeout(() => {{ btn.textContent = back; }}, 1800); }}
  else btn.textContent = back;
}}
function why(e){{
  const c = e && e.code;
  if (c === 'declined') return null;                       // the viewer said no; stay quiet
  if (c === 'rate_limited') return 'busy — try again';
  if (c === 'too_large') return 'file too large';
  if (c === 'unavailable' || c === 'not_granted') return 'unavailable here';
  return 'failed';
}}

async function saveOne(url, name, btn){{
  const d = await dl();
  if (!d) return done(btn, 'unavailable');
  busy(btn, 'preparing…');
  try {{
    const r = await fetch(url);
    if (!r.ok) throw new Error(r.status);
    await d.save({{filename: name.split('/').pop(), data: await r.blob()}});
    done(btn, 'saved');
  }} catch (e) {{ done(btn, why(e)); }}
}}

async function saveZip(items, zipName, btn){{
  const d = await dl();
  if (!d) return done(btn, 'unavailable');
  busy(btn, '0 / ' + items.length);
  try {{
    const files = [];
    for (let i = 0; i < items.length; i++){{
      const r = await fetch(items[i].u);
      if (!r.ok) throw new Error(r.status);
      files.push({{name: items[i].n, data: new Uint8Array(await r.arrayBuffer())}});
      busy(btn, (i + 1) + ' / ' + items.length);
    }}
    busy(btn, 'zipping…');
    await d.save({{filename: zipName, data: zipStore(files)}});
    done(btn, 'saved');
  }} catch (e) {{ done(btn, why(e)); }}
}}

document.querySelectorAll('[data-one]').forEach(b => b.addEventListener('click',
  () => saveOne(b.dataset.one, b.dataset.n, b)));
document.querySelectorAll('.shot').forEach(b => b.addEventListener('click',
  () => saveOne(b.dataset.u, b.dataset.n, null)));
document.querySelectorAll('[data-zip]').forEach(b => b.addEventListener('click', () => {{
  const k = b.dataset.zip;
  saveZip(SLIDES[k].map((u, i) => ({{u, n: `heyagain_${{k}}_${{i + 1}}_${{LABELS[i]}}.png`}})),
          `heyagain_${{k}}_slides.zip`, b);
}}));
document.getElementById('dl-all').addEventListener('click',
  e => saveZip(ALL, 'heyagain_social_template.zip', e.currentTarget));

/* If the viewer cannot save at all, say so once rather than leaving dead buttons. */
dl().then(d => {{ if (!d) document.getElementById('nodl').hidden = false; }});

const chips = document.querySelectorAll('.chip');
chips.forEach(c => c.addEventListener('click', () => {{
  chips.forEach(o => o.setAttribute('aria-pressed', String(o === c)));
  const f = c.dataset.f;
  document.querySelectorAll('.deck').forEach(d => {{
    d.hidden = f !== 'all' && d.dataset.cat !== f;
  }});
}}));
</script>
</body></html>'''

open(f"{SP}/contact_sheet.html", "w").write(html)
print(f"ok contact_sheet.html  {len(html) // 1024} KB")
