# STILL. — "The idea was never the problem"

Study 002. A 24.000s positioning film, 60fps, 1080×1920, built entirely in code.
No footage, no generation, no people. `BRIEF.md` is the spec and it is the
authority — read it before changing anything, the arguments in it were had already.

**Status: at the stop gate.** Act I is built and rendered. Nothing past frame 480
exists yet, on purpose.

---

## The stack

Remotion + TypeScript, not the HTML/Playwright pipeline that built study 001.
The reason is the brief's 60fps and its 1440-frame grid: Remotion's frame model
*is* an integer frame counter, so `useCurrentFrame()` and the grid in
`src/grid.ts` are the same number, and there is no seconds-to-frames conversion
anywhere to round the wrong way. Everything else about the house method carries
over — one deterministic function of `t`, no CSS animations, no wall-clock.

| File | What it is |
|---|---|
| `src/grid.ts` | 90 BPM at 60fps. `assertGrid` and its inverse `OFF_GRID`. Unit-tested. |
| `src/timeline.ts` | **Every event in the film, in frames.** The picture, the verifier and (later) the audio all read this one file, so they cannot drift. |
| `src/theme.ts` | Palette, the two type tokens, `LAYOUT`, easing, texture opacities. |
| `src/ActI.tsx` | The act. Seven rules of bad motion, and why each one may not be softened. |
| `src/components/` | `Square`, `Word`, `Eyebrow`, `TextureLayer` — all dumb, none owns timing. |
| `scripts/texture.py` | Generates the T1 plates in `public/tex/`. |
| `scripts/verify.mjs` | §12 of the brief. Fails the build. Reports unbuilt sections as PENDING, never PASS. |
| `scripts/contact-sheet.mjs` | One bundle, N stills, straight from source. |
| `scripts/measure-texture.py` | What the texture pass actually does to the ground, in 8-bit levels. |

## Build it

```sh
npm install
python3 scripts/texture.py                 # only after changing the texture
npm test                                   # the grid
npm run verify                             # §12
npm run act1                               # 480 frames, ~2m15s, -> outputs/
```

Iterating? Render stills instead of the act — one bundle, any frames:

```sh
node scripts/contact-sheet.mjs ActI 0 37 47 113 189 266 344 400 479
```

`npm run studio` opens Remotion Studio if a desktop session is available.

---

## Gotchas already paid for — do not rediscover these

- **Remotion will not launch Playwright's `chrome`.** It passes the old
  `--headless` flag, which the Chrome binary removed; the process exits with
  signal 1 and a message about new Headless mode. Use the *headless shell*:
  `/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell`.
- **Pass `browserExecutable` to `selectComposition` too, not just `renderStill`.**
  Miss it and Remotion tries to download its own Chrome from `remotion.media`,
  which is not in this container's egress allowlist — a 403 that reads like a
  network fault but is a missing argument.
- **A stacking context kills every blend mode underneath it.** The texture
  wrapper had `zIndex: 100`. That sealed the plates into their own group, where
  the backdrop is transparent rather than the film, so they composited as flat
  grey sheets and the BONE ground fell from 196 to 160 — it looked like fog.
  The wrapper must have no z-index, no opacity, no transform, no `isolation`.
  It is the last child; it is on top anyway.
- **A single mid-grey multiply plate cannot be a texture.** Multiply only ever
  takes light away, so any plate with enough contrast to be visible also drags
  the ground darker and BONE stops being BONE. One field split at zero into a
  dark plate (multiplied) and a light plate (screened) adds tooth with no net
  shift — and inverts itself on UMBER, so the same four plates work on both
  grounds with no second set.
- **Texture opacity is meaningless until the plate contrast is fixed.** The
  first build used the brief's percentages against low-contrast plates and the
  ground measured σ 0.16 levels — invisible. `scripts/measure-texture.py` is
  the arbiter: the pass currently sits at **σ ≈ 2.0 levels, peak-to-peak ~14, on
  a ground that still measures exactly BONE (199.4, 190.9, 170.3)**.
- **Low-frequency mottle must be held at about a third of the fibre strength.**
  A downscale to Reel size (390px wide) throws away the fibre and keeps the
  mottle, so a ground that looks right at 1080 reads as *dirty* on a phone.
  Judge the texture on the contact sheet, never at full size.
- **Playwright's ffmpeg is built with `--disable-everything`.** It can neither
  demux mp4 nor decode h264 — it exists to write webm screen recordings. There
  is no system ffmpeg either. Extract frames with `scripts/contact-sheet.mjs`,
  which goes through Remotion's renderer instead (and has no generation loss).
- **Node's type stripping does not do `.tsx`.** That is why the timings live in
  `src/timeline.ts` and not next to the component — `verify.mjs` imports the
  real constants rather than a transcription of them. Same reason `timeline.ts`
  imports `./grid.ts` *with* the extension: node's ESM resolver does not guess.
- **Fonts must be waited for explicitly.** `src/fonts.ts` holds a `delayRender`
  until `document.fonts.load()` resolves for both faces. Without it Chromium
  screenshots the first frames in a fallback sans and the 180px line silently
  changes width. The woff2 files are committed — a film that needs the network
  to look right is not reproducible.
- **CSS background images are invisible to Remotion's asset tracking.** The
  grain tiles have to be backgrounds (a 384px plate must *tile*; `object-fit`
  cannot), so eight zero-size `<Img>` tags sit alongside them purely to make the
  renderer wait. Without them the grain popped in three frames late, which on a
  ground this still is visible.

## Where this diverges from the brief, and why

- **Texture opacities.** §9 gives percentages (paper 6%, crumple 3%, grain 1.5%).
  Taken as literal CSS opacity against any plausible plate they produce nothing
  a viewer can see — the measured deviation was under a fifth of a level. They
  are implemented as the *result*: `TEXTURE` in `theme.ts`, calibrated with
  `measure-texture.py` to land in the range those percentages were reaching for.
  The look is the spec; the numbers were the estimate.
- **Vertical positions.** The brief fixes the square at 340×340 in the upper
  third and DISPLAY at 180px, but not where the block sits. `LAYOUT` puts the
  square at y=420 and the sentence at y=880, which clears the Reels chrome at
  the bottom of the frame by ~400px. Checked at phone size, not on a monitor.
- **Act I word gaps are 76/77/78 frames, not identical.** Those are the brief's
  own literal frames (37, 113, 189, 266, 344). The drift is under a sixteenth
  and reads as metronomic; `verify.mjs` asserts the spread stays under 10 frames
  so it can never quietly become rhythm.

## Next

The stop gate is real: Act I has to be approved as *lifeless* before anything is
built on top of it. After that, `BRIEF.md` §11 has the order — the turn, Act II,
the line, audio, the 1080×1080 variant. `src/timeline.ts` is where each new act's
frames go, and `verify.mjs` already has the pending checks written out.
