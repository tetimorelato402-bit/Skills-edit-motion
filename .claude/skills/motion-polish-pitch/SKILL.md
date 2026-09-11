---
name: motion-polish-pitch
description: Turn any live website URL into a sellable motion-polish pitch — record the site, inventory every transition and animation it uses, grade it against Emil Kowalski's standards, inject a drop-in polish stylesheet that fixes the motion, render a labelled before/after video of the prospect's own site, and write the cold DM and offer. Use when asked to pitch, prospect, audit a live URL for outreach, make a before/after clip of a site's animations, or cold-sell motion polish on social media. For auditing your own codebase use improve-animations; for building an animation from scratch use animate.
---

# Motion Polish Pitch

A productized-service skill. It does ONE thing: take a prospect's live URL and produce, in minutes, the three things a cold pitch needs — proof (a before/after video of *their* site), a deliverable (the drop-in `polish.css` that made the "after"), and the message. It does not redesign pages, write copy, audit a codebase (that's `improve-animations`), or build new animations (that's `animate`).

Why this is the one to sell: a human design engineer can produce two or three personalised before/after clips a day and each takes taste they can't delegate. This skill produces one every few minutes, for any site on the internet, at the same standard every time, and the prospect sees *their own product* moving better before they've replied. Nothing about the pitch is generic, and nothing about it scales linearly with your hours.

## Operating Posture

You are a senior design engineer with **restraint**, selling to founders and small product teams. Three rules override everything else:

1. **Show, don't claim.** The DM contains a clip and three plain-English findings. It never contains a conversion number, a "studies show", or a promise about revenue. Motion polish makes a product feel faster and more considered; that is the whole pitch and it is enough.
2. **Only fix what's there.** The "after" side is the prospect's site with its existing motion corrected — faster hovers, right curves, no layout thrash, reduced-motion respected. No added scroll reveals, no parallax, no hero entrance sequence. If the clip looks like "more things moving", the layer is wrong. See [POLISH-LAYER.md](POLISH-LAYER.md).
3. **One human, one message.** The pipeline scales the *production*; sending is still a person choosing to message another person. Never automate sending, never bulk-DM, never message the same prospect twice without a reply beyond the single follow-up in [PITCH.md](PITCH.md).

Everything you produce is judged against `../review-animations/STANDARDS.md` and `../improve-animations/AUDIT.md`. Cite their exact values; never approximate.

## Requirements

- Node 18+ with Playwright and Chromium: `npm i -g playwright && npx playwright install chromium`. The scripts resolve Playwright from the project or the global npm root.
- No ffmpeg needed. The side-by-side clip is recorded in Chromium. If a full `ffmpeg` with `libx264` is on PATH you also get an `.mp4`; otherwise ship the `.webm` (X and LinkedIn accept it; for Instagram convert once on your machine).

## Pipeline

Work through every step in order. Steps 2–6 are mechanical and run unattended; steps 1, 3 and 7 are the judgment the fee is for.

### 1. Qualify (30 seconds, before any capture)

Open the URL and answer these. Any "no" means skip the prospect and say why in one line.

- Is it a product or service they own (SaaS, app, agency's own site, e-commerce store)? Skip: personal blogs, template demos, Fortune-500 sites, sites obviously built by a big agency with a motion team.
- Does the page have interactive surfaces — nav, buttons, cards, menus, pricing toggles? A static one-pager has nothing to polish.
- Can you find the person to message (founder, design lead, head of product) on the platform you'll pitch on?
- Is the *motion* the weak part? If the layout, type or colour is the real problem, motion polish is lipstick. Not a prospect for this skill.

### 2. Capture "before"

```bash
node .claude/skills/motion-polish-pitch/scripts/capture.mjs https://example.com \
  --out pitches/example.com --label before
```

Add `--mobile` for a 390×844 pass when the product is mobile-first. Output in `pitches/example.com/before/`: `video.webm` (a hover pass over the first twelve interactive elements, then a scroll through the page), `hero.png`, `full.png`, `inventory.json` (computed transition/animation styles per element, rest vs hover), and `findings.json` (mechanical rule hits with severity).

The script only hovers and scrolls. It never clicks, submits, or leaves the page.

### 3. Judge the findings

Read `findings.json` and `inventory.json`. The rules are mechanical — you decide what matters. Pick **the three findings a founder will see in the video**, in this priority:

1. The primary CTA's hover/press (`hover-too-slow`, `ease-in-on-ui`, `hover-scale-too-big` on `.btn`-like elements). This is what they click in their own product daily.
2. Navigation and cards — anything hit tens of times a session (`transition-all`, `too-slow`, `layout-property-animated`).
3. Page-level hygiene (`no-reduced-motion`, `infinite-animation` on decoration).

Findings you cannot show on video (a stylesheet-level rule with no visible surface) go in the written audit you deliver after they buy, not in the DM. If there are fewer than three visible findings of `high` severity, the site is already decent: skip, or pitch only if step 1 said the surfaces are rich enough that the improvement is still obvious on screen.

Note that `ease-in-in-css`, `transition-all-in-css` and `no-reduced-motion` are read from the stylesheet text and persist in the "after" findings until the patch is merged into their CSS; the injected layer overrides them at the cascade level, which is what the video shows.

### 4. Write the polish layer

Create `pitches/example.com/polish.css` from the skeleton in [POLISH-LAYER.md](POLISH-LAYER.md), using the prospect's real selectors from `inventory.json`. Keep it under ~60 lines. It must be pasteable into their codebase unchanged — that is the product.

### 5. Capture "after" and verify

```bash
node .claude/skills/motion-polish-pitch/scripts/capture.mjs https://example.com \
  --out pitches/example.com --label after --polish pitches/example.com/polish.css
```

Compare `after/findings.json` to `before/findings.json`. Element-level `high` findings should be zero. If any remain, the selector didn't match — fix the layer, don't loosen the standard. Look at both `hero.png` files side by side: nothing but motion may differ.

### 6. Compose the clip

```bash
node .claude/skills/motion-polish-pitch/scripts/side-by-side.mjs pitches/example.com --title "example.com"
```

Produces `before-after.webm` (and `.mp4` if ffmpeg is available): both recordings playing in sync with BEFORE / AFTER tags. Watch it once before it goes anywhere. Both panes must show the same hover targets at the same time; if the page redirected or a cookie banner covered the hero on one side, recapture.

### 7. Write the pitch

Follow [PITCH.md](PITCH.md) exactly: a DM under 60 words, the three findings in plain words with the exact values from the standards, the offer, and the clip. Save it as `pitches/example.com/PITCH.md` next to the assets.

## Batch mode

Given a list of URLs, run steps 1–6 for each in sequence (Chromium is heavy; don't parallelise beyond two) and stop at step 7 for each prospect until a human has watched the clip. A `pitches/` directory with one folder per domain is the queue; a `SKIPPED.md` listing the domains rejected at step 1 or 3 with the one-line reason is the record. Throughput on a laptop is roughly one prospect every 3–5 minutes end-to-end, which is the point: fifty personalised pitches in an afternoon, each one real.

## Etiquette and limits

- Public pages only. Never capture behind a login, never fill a form, never bypass a paywall or a bot check. If a site blocks headless browsers, skip it.
- Never claim affiliation with the prospect or with Emil Kowalski. The standards are his published philosophy; the work is yours.
- If a prospect asks you to stop, stop. Record it in `SKIPPED.md` so batch mode never resurfaces them.
- The before/after clip is critique of a public interface for the purpose of offering a service. Do not post a prospect's clip publicly without their consent; the public "portfolio" format in PITCH.md is for clients who agreed, or for your own demo sites.

## Deliverable layout

```
pitches/
└── example.com/
    ├── before/   video.webm hero.png full.png inventory.json findings.json
    ├── after/    video.webm hero.png full.png inventory.json findings.json
    ├── polish.css
    ├── before-after.webm  (+ .mp4 when ffmpeg is available)
    └── PITCH.md
```

When the prospect buys, the polish patch is delivered as a pull request to their repository (or the stylesheet plus a one-page install note if they have no repo access to give), with the findings written up per `../improve-animations/AUDIT.md`. That is the "Patch" tier in PITCH.md; the larger tiers are ordinary `animate` / `improve-animations` work scoped from the same audit.

## Output

End every run with this summary:

```
Prospect: example.com — QUALIFIED | SKIPPED (reason)
Before: N findings (H high / M medium / L low) · After: N findings
Top 3 shown in clip:
  1. <element> — <what's wrong> → <what the layer does, with the exact value>
  2. …
  3. …
Assets: pitches/example.com/before-after.webm · polish.css (NN lines)
Pitch: pitches/example.com/PITCH.md — ready to send / needs human review because …
```
