# teti studio — working context

Personal repo of **teti**, a motion editor. Two things live here: the `.claude/skills/`
collection (forked from emilkowalski/skills, plus `big-video-project`), and `projects/` —
teti's own video work, one numbered study per directory.

Active branch: `claude/motion-editors-video-concept-fz6opf`.

## The one-line brief

`projects/001-why-motion-editors/` is teti's **first client-facing Instagram Reel**. Its
question — *"why do we need motion editors?"* — is the title of a study, answered by
demonstration and signed. It is a debut of craft, not an ad. Read `BRIEF.md` before
changing anything about its content; the framing was argued out carefully and the
rejected alternatives are recorded there with reasons.

## How the film is actually built

There is no NLE project. **The film is code.** `projects/001-why-motion-editors/source/`:

| File | What it is |
|---|---|
| `video.html` | The whole film. One deterministic `window.renderFrame(t)` positions every element for time `t`. No CSS animations — they are wall-clock based and would not render reproducibly. |
| `render.py` | Drives headless Chromium via Playwright, calling `renderFrame(i/fps)` and screenshotting each frame. |
| `paint.py` | Generates the oil-paint plates and canvas weave in `tex/`. |
| `../sound.py` | Synthesises the sound design as a WAV. Every hit is frame-exact. |

**Rebuild the film:**
```sh
python3 source/render.py --out frames120 --fps 120          # ~30 min, ~0.8 s/frame
ffmpeg -framerate 120 -i frames120/f%05d.png -i sound.wav \
  -filter_complex "[0:v]tmix=frames=3:weights='1 2 1',fps=30,noise=alls=2:allf=t+u,format=yuv420p[v]" \
  -map "[v]" -map 1:a -c:v libx264 -profile:v high -crf 17 -preset slow \
  -c:a aac -b:a 192k -movflags +faststart -shortest out.mp4
```
Rendering at 120 and averaging 3 frames down to 30 is what produces the motion blur —
a real 270° shutter, not a blur filter. Do not shortcut it to 30 fps.

Preview a few frames instead of the whole film while iterating:
`python3 source/render.py --out pv --times 4.9,9.7,14.6`

## Rules that are load-bearing

- **The generic brand post stays cold grey and crisp.** Everything teti draws is painted;
  the dead post is a flat digital object collaged onto canvas. That contrast carries the
  argument. Never warm it up or paint it.
- **The specimen band is ochre, not oxblood.** A full-frame saturated red field is the most
  recognisable thing about the reference (yuk.aji's *LILIUM*). Same grammar, different
  voice — that is the line between homage and copy. See `brand/PALETTE.md`.
- **Never burn the music in.** Instagram only licenses "Parisienne Walkways" when the track
  is added inside the app. The export carries sound design only. The guitar bend must land
  at **9.6 s**, where the ease curve is dragged. If a beat moves, that number moves with it —
  update `POSTING.md`.
- **The palette is derived, not chosen.** It was extracted from teti's oil portrait
  (`brand/portrait-source.png`) by k-means. Colour may move in *value*; it must not leave
  the warm family.

## Gotchas already paid for — do not rediscover these

- **`preserve-3d` + overwritten transforms.** In `buildCard`, each text layer is a wrapper
  (carrying the 3D depth) around the element that animates (carrying the 2D transform). If
  one element carries both, the animation transform replaces the `translate3d` and Chromium
  sorts the background layer *in front of* the text, which silently vanishes.
- **PIL thick lines have square ends.** Brush strokes are stamped ellipses along a path;
  `ImageDraw.line` with a wide stroke produces rectangles and reads as scratchy hatching.
- **Jitter colour in value only.** Perturbing R, G and B independently throws greens and
  purples into a warm painting.
- **Applying a filter to a whole scene is expensive.** The brush-edge displacement is applied
  to type elements only (`.pt`), never to a full-frame container.
- **Instagram render sizes are the real test.** 110 px on profile, 32 px in comments, ~390 px
  wide for a Reel. Check work at those sizes before judging it — several designs that looked
  good at full size failed there.
- **Image-based CSS masks do not render in headless Chromium.** `mask-image: url(x.png)`
  hides the element entirely, at every position, even though the PNG decodes and its alpha is
  valid. Gradient masks work. `paint.py` still writes `wipe_mask.png` — it is a usable matte
  in Resolve, just not here.
- **The paint wipe is a `clip-path: polygon()`, not a filter.** Two approaches were built and
  rejected first: a gradient mask displaced by `feDisplacementMap` bends the *content* as well
  as the edge (the band's edges wobble, then snap crisp when the filter drops), and a filter
  plus a mask on the same element runs the filter first, so it never reaches the mask edge.
  The bristled front is a fixed profile (`WIPE_EDGE`) slid across as a polygon — type stays
  crisp, no filter cost. The wrapper `s3inner` carries beat 3's own ground so the wipe
  reveals a whole painting, not a band floating over the cream page.
- **A thresholded-noise dissolve has a narrow live band.** `feTurbulence` values sit between
  ~0.15 and ~0.85, so with `slope=12` the `intercept` sweep that actually does anything is
  −9.8 → −1.2 (measured: coverage 0 → 1). The first version swept −12 → 1 and 60% of the
  window was spent invisible — the dissolve collapsed into a two-frame cut. Grain frequency
  0.14 was chosen at phone size: 0.34 read as a noisy crossfade, 0.07 as camouflage.
- **Transition overlaps are per scene.** `PRES[i]` — the grain dissolve (0.40 s) and the
  paint wipe (0.44 s) need longer than the default 0.26 s to be read as what they are.
  `renderFrame` passes each scene its entry progress `ein`; the scene decides what to do.
- **Full-frame filters cost ~0.4 s/frame while active.** Switch them to `none` the moment a
  transition lands (`s2.style.filter='none'`).
- **Re-render a range, not the film.** `render.py --start 438 --end 508` overwrites just those
  frames in place; a transition fix is ~1 minute instead of 40.
- **Big background images must be decoded before the first screenshot.** `render.py`
  decodes every texture in `tex/` explicitly; without that the 2 MB portrait rendered as an
  empty circle in the first frames it appeared.

## Fonts

The film needs **Inter** (400–900) plus ten families for the end-card type cycle:
Playfair Display, Anton, EB Garamond, IBM Plex Mono, Oswald, Caveat, Bodoni Moda,
Zilla Slab, DM Serif Display, Space Grotesk. They are referenced by family name and
resolved through fontconfig, so install them system-wide (`/usr/local/share/fonts/`
then `fc-cache -f`) before rendering. Missing families silently fall back to sans-serif
and the cycle stops reading as a cycle — check with `fc-list : family`.

## Open decisions

1. ~~Profile picture~~ — **decided: the portrait**, full colour, circular
   (`brand/pfp/opt1_portrait.png`, live on the account). The end card resolves into it,
   so the film and the profile now share a mark. The other seven options stay in
   `brand/pfp/` as a record.
2. **Hours and deadline** — never pinned down. Assume "ship soon" unless teti says otherwise.

## What a desktop session unlocks

This project was built in a cloud container, which cannot reach desktop apps. Running
locally adds:

- **DaVinci Resolve Studio** — see `projects/001-why-motion-editors/resolve/README.md` for
  setup and `build_timeline.py` (written, untested against a live Resolve).
- **Blender** — `bpy` is fully scriptable and runs headless, so scenes, sims and renders can
  be built in code and composited into the same pipeline.

See `HANDOFF.md` for what to build next and why.
