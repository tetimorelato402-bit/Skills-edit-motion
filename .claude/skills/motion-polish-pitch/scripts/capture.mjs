#!/usr/bin/env node
// Capture a site's motion: record a scroll + hover pass, inventory every
// transition/animation the page uses, and emit rule-based findings.
//
//   node capture.mjs <url> --out <dir> [--label before|after]
//                    [--polish polish.css] [--js polish.js]
//                    [--width 1440] [--height 900] [--mobile]
//                    [--max-hover 12] [--timeout 20000]
//
// Outputs in <out>/<label>/: video.webm, hero.png, full.png,
// inventory.json (raw computed-style data), findings.json (rule hits).

import { mkdirSync, readFileSync, renameSync, writeFileSync, existsSync } from 'node:fs';
import { join } from 'node:path';
import { execSync } from 'node:child_process';
import { pathToFileURL } from 'node:url';

// Resolve playwright from the project first, then the global npm root, so the
// script runs in a repo that never installed it (`npm i -g playwright` is enough).
const loadPlaywright = async () => {
  try { return await import('playwright'); } catch {}
  const root = execSync('npm root -g', { encoding: 'utf8' }).trim();
  for (const pkg of ['playwright', 'playwright-core', '@playwright/test']) {
    try { return await import(pathToFileURL(join(root, pkg, 'index.mjs')).href); } catch {}
  }
  console.error('playwright not found. Run: npm i -g playwright  (browsers: npx playwright install chromium)');
  process.exit(2);
};
const { chromium } = await loadPlaywright();

const argv = process.argv.slice(2);
const url = argv.find((a) => !a.startsWith('--'));
if (!url) {
  console.error('usage: capture.mjs <url> --out <dir> [--label before|after] [--polish file.css] [--js file.js]');
  process.exit(2);
}
const opt = (name, dflt) => {
  const i = argv.indexOf(`--${name}`);
  return i === -1 ? dflt : argv[i + 1];
};
const flag = (name) => argv.includes(`--${name}`);

const out = opt('out', 'capture');
const label = opt('label', 'before');
const polishCss = opt('polish', null);
const polishJs = opt('js', null);
const width = Number(opt('width', flag('mobile') ? 390 : 1440));
const height = Number(opt('height', flag('mobile') ? 844 : 900));
const maxHover = Number(opt('max-hover', 12));
const timeout = Number(opt('timeout', 20000));

const dir = join(out, label);
mkdirSync(dir, { recursive: true });

const launchOpts = { headless: true };
if (process.env.PLAYWRIGHT_CHROMIUM_PATH) launchOpts.executablePath = process.env.PLAYWRIGHT_CHROMIUM_PATH;

const browser = await chromium.launch(launchOpts);
const context = await browser.newContext({
  viewport: { width, height },
  deviceScaleFactor: 1,
  isMobile: flag('mobile'),
  hasTouch: flag('mobile'),
  recordVideo: { dir, size: { width, height } },
  colorScheme: 'light',
});
const page = await context.newPage();

const inject = async () => {
  if (polishCss) await page.addStyleTag({ content: readFileSync(polishCss, 'utf8') });
  if (polishJs) await page.addScriptTag({ content: readFileSync(polishJs, 'utf8') });
};

// Re-inject after any full navigation so the "after" pass survives redirects.
if (polishCss || polishJs) {
  page.on('framenavigated', (frame) => {
    if (frame === page.mainFrame()) inject().catch(() => {});
  });
}

const t0 = Date.now();
try {
  await page.goto(url, { waitUntil: 'domcontentloaded', timeout });
} catch (err) {
  const msg = String(err.message || err).split('\n')[0];
  console.error(`could not load ${url}: ${msg}`);
  console.error('(blocked headless browsers, a network policy, or a dead site — skip the prospect and note it in SKIPPED.md)');
  await browser.close();
  process.exit(1);
}
await page.waitForLoadState('networkidle', { timeout }).catch(() => {});
await inject();
await page.waitForTimeout(600);

await page.screenshot({ path: join(dir, 'hero.png') });

// ---------- Inventory: what does this page do with motion? ----------
const inventory = await page.evaluate(({ maxHover }) => {
  const SELECTORS = 'a, button, [role="button"], input, select, textarea, summary, [tabindex], [class*="card"], [class*="Card"], nav li, [class*="btn"], [class*="Button"]';
  const els = Array.from(document.querySelectorAll(SELECTORS));
  const visible = (el) => {
    const r = el.getBoundingClientRect();
    const s = getComputedStyle(el);
    return r.width > 4 && r.height > 4 && s.visibility !== 'hidden' && s.display !== 'none' && s.opacity !== '0';
  };
  const pick = (el) => {
    const s = getComputedStyle(el);
    return {
      transitionProperty: s.transitionProperty,
      transitionDuration: s.transitionDuration,
      transitionTimingFunction: s.transitionTimingFunction,
      animationName: s.animationName,
      animationDuration: s.animationDuration,
      animationTimingFunction: s.animationTimingFunction,
      animationIterationCount: s.animationIterationCount,
      transform: s.transform,
      boxShadow: s.boxShadow,
      border: s.border,
      outline: s.outline,
      willChange: s.willChange,
    };
  };
  const describe = (el) => {
    const tag = el.tagName.toLowerCase();
    const id = el.id ? `#${el.id}` : '';
    const cls = typeof el.className === 'string' && el.className.trim() ? '.' + el.className.trim().split(/\s+/).slice(0, 3).join('.') : '';
    const text = (el.innerText || el.value || el.getAttribute('aria-label') || '').trim().replace(/\s+/g, ' ').slice(0, 40);
    return `${tag}${id}${cls}${text ? ` "${text}"` : ''}`;
  };

  const seen = new Set();
  const items = [];
  for (const el of els) {
    if (!visible(el)) continue;
    const key = describe(el);
    if (seen.has(key)) continue; // collapse repeated components
    seen.add(key);
    const r = el.getBoundingClientRect();
    items.push({
      selector: key,
      rect: { x: Math.round(r.x + window.scrollX), y: Math.round(r.y + window.scrollY), w: Math.round(r.width), h: Math.round(r.height) },
      styles: pick(el),
    });
    if (items.length >= 60) break;
  }

  // Stylesheet-level signals (same-origin sheets only; cross-origin throws).
  let cssText = '';
  for (const sheet of Array.from(document.styleSheets)) {
    try {
      for (const rule of Array.from(sheet.cssRules)) cssText += rule.cssText + '\n';
    } catch {}
  }
  const sheet = {
    readableSheets: Array.from(document.styleSheets).filter((s) => { try { return !!s.cssRules; } catch { return false; } }).length,
    totalSheets: document.styleSheets.length,
    hasReducedMotionQuery: /prefers-reduced-motion/.test(cssText),
    easeInCount: (cssText.match(/\bease-in\b(?!-out)/g) || []).length,
    transitionAllCount: (cssText.match(/transition\s*:\s*all\b/g) || []).length,
    keyframeCount: (cssText.match(/@keyframes/g) || []).length,
    viewTransitionCount: (cssText.match(/view-transition/g) || []).length,
    springLibrary: !!(window.motion || window.Motion || window.gsap || window.anime || window.Framer || document.querySelector('[data-framer-name]')),
  };

  return {
    url: location.href,
    title: document.title,
    viewport: { w: innerWidth, h: innerHeight },
    pageHeight: document.documentElement.scrollHeight,
    hoverCandidates: items.slice(0, maxHover).map((i) => i.selector),
    items,
    sheet,
  };
}, { maxHover });

// ---------- Hover pass: measure what actually changes on hover ----------
const hovered = [];
for (const item of inventory.items.slice(0, maxHover)) {
  const { x, y, w, h } = item.rect;
  try {
    await page.mouse.move(x + w / 2, y + h / 2 - (await page.evaluate(() => window.scrollY)), { steps: 8 });
  } catch { continue; }
  await page.waitForTimeout(350);
  const after = await page.evaluate((sel) => {
    const el = document.querySelector(':hover');
    const deepest = (() => { let e = document.querySelector(':hover'); while (e && e.querySelector(':hover')) e = e.querySelector(':hover'); return e; })();
    if (!deepest) return null;
    const s = getComputedStyle(deepest);
    return { transform: s.transform, boxShadow: s.boxShadow, backgroundColor: s.backgroundColor, color: s.color, transitionDuration: s.transitionDuration, transitionTimingFunction: s.transitionTimingFunction, transitionProperty: s.transitionProperty, cursor: s.cursor };
  }, item.selector);
  hovered.push({ selector: item.selector, rest: item.styles, hover: after });
  await page.waitForTimeout(150);
}
await page.mouse.move(5, 5);

// ---------- Scroll pass (this is what the video shows) ----------
const pageHeight = inventory.pageHeight;
const steps = Math.min(14, Math.max(4, Math.ceil(pageHeight / height)));
for (let i = 1; i <= steps; i++) {
  await page.evaluate((y) => window.scrollTo({ top: y, behavior: 'smooth' }), Math.round((pageHeight - height) * (i / steps)));
  await page.waitForTimeout(700);
}
await page.evaluate(() => window.scrollTo({ top: 0, behavior: 'smooth' }));
await page.waitForTimeout(900);
await page.screenshot({ path: join(dir, 'full.png'), fullPage: true }).catch(() => {});

// ---------- Findings: mechanical rule hits (judgment comes later) ----------
const ms = (s) => (s || '').split(',').map((v) => v.trim()).map((v) => (v.endsWith('ms') ? parseFloat(v) : parseFloat(v) * 1000)).filter((n) => !Number.isNaN(n));
const findings = [];
const add = (rule, selector, evidence, severity = 'medium') => findings.push({ rule, selector, evidence, severity });

for (const it of inventory.items) {
  const s = it.styles;
  const durs = ms(s.transitionDuration);
  const props = (s.transitionProperty || '').split(',').map((p) => p.trim());
  const timing = s.transitionTimingFunction || '';
  const hasTransition = durs.some((d) => d > 0) && props.some((p) => p && p !== 'none');
  if (!hasTransition) continue;
  if (props.includes('all')) add('transition-all', it.selector, `transition-property: all (${s.transitionDuration})`, 'medium');
  if (/(^|,)\s*ease-in\s*(,|$)/.test(timing) || /cubic-bezier\(0\.4[2-9]?,\s*0,\s*1,\s*1\)/.test(timing)) add('ease-in-on-ui', it.selector, `timing: ${timing}`, 'high');
  if (durs.some((d) => d > 400)) add('too-slow', it.selector, `transition-duration: ${s.transitionDuration}`, 'high');
  const layoutProps = props.filter((p) => /^(width|height|top|left|right|bottom|margin|padding|font-size)/.test(p));
  if (layoutProps.length) add('layout-property-animated', it.selector, `animates ${layoutProps.join(', ')}`, 'high');
  if (/\b(ease|ease-in-out|linear)\b/.test(timing) && !/cubic-bezier/.test(timing) && durs.some((d) => d >= 250)) add('weak-builtin-curve', it.selector, `timing: ${timing} at ${s.transitionDuration}`, 'low');
  if (ms(s.animationDuration).some((d) => d > 0) && s.animationIterationCount === 'infinite') add('infinite-animation', it.selector, `animation ${s.animationName} runs forever`, 'medium');
}
for (const h of hovered) {
  if (!h.hover) continue;
  const durs = ms(h.hover.transitionDuration);
  const changed = ['transform', 'boxShadow', 'backgroundColor', 'color'].filter((k) => h.hover[k] !== h.rest[k === 'backgroundColor' ? 'backgroundColor' : k] && h.rest[k] !== undefined);
  if (changed.length && durs.some((d) => d > 200)) add('hover-too-slow', h.selector, `hover changes ${changed.join(', ')} over ${h.hover.transitionDuration}`, 'high');
  if (h.hover.transform && h.hover.transform !== 'none' && /matrix\(1\.(0[6-9]|[1-9])/.test(h.hover.transform)) add('hover-scale-too-big', h.selector, `hover transform ${h.hover.transform}`, 'medium');
  if (h.hover.cursor !== 'pointer' && /^(a|button|\[role)/.test(h.selector)) add('no-pointer-cursor', h.selector, `cursor: ${h.hover.cursor}`, 'low');
}
if (!inventory.sheet.hasReducedMotionQuery && inventory.sheet.readableSheets > 0 && (inventory.sheet.keyframeCount > 0 || findings.length > 0)) {
  add('no-reduced-motion', 'stylesheet', `${inventory.sheet.keyframeCount} @keyframes, 0 prefers-reduced-motion queries across ${inventory.sheet.readableSheets} readable sheets`, 'high');
}
if (inventory.sheet.transitionAllCount > 0) add('transition-all-in-css', 'stylesheet', `${inventory.sheet.transitionAllCount} × "transition: all"`, 'medium');
if (inventory.sheet.easeInCount > 0) add('ease-in-in-css', 'stylesheet', `${inventory.sheet.easeInCount} × ease-in`, 'high');
if (inventory.items.length > 0 && !inventory.items.some((i) => ms(i.styles.transitionDuration).some((d) => d > 0))) {
  add('no-transitions-at-all', 'page', `${inventory.items.length} interactive elements, none transition on hover/press`, 'medium');
}

const summary = {
  url: inventory.url,
  title: inventory.title,
  label,
  capturedAt: new Date().toISOString(),
  elapsedMs: Date.now() - t0,
  interactiveElements: inventory.items.length,
  findings: findings.length,
  bySeverity: { high: findings.filter((f) => f.severity === 'high').length, medium: findings.filter((f) => f.severity === 'medium').length, low: findings.filter((f) => f.severity === 'low').length },
  sheet: inventory.sheet,
};

writeFileSync(join(dir, 'inventory.json'), JSON.stringify({ ...inventory, hovered }, null, 2));
writeFileSync(join(dir, 'findings.json'), JSON.stringify({ summary, findings }, null, 2));

const video = page.video();
await context.close();
if (video) {
  const p = await video.path();
  if (existsSync(p)) renameSync(p, join(dir, 'video.webm'));
}
await browser.close();

console.log(JSON.stringify(summary, null, 2));
