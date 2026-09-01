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
| `../sound.py` | **The whole soundtrack**, synthesised: a 75 BPM beat and a sound for every motion. Cue times are derived from the film's own constants and easing curves, so they are frame-exact by construction. |

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
- **There is no music. The film carries its own score; nothing is added in Instagram.**
  teti retired "Parisienne Walkways" after v6 ("I don't like any music"). The soundtrack is
  synthesised in `sound.py`: a beat, and a sound for every motion. The beat is **75 BPM from
  frame 0** — the film is exactly six bars of 4/4, the snap (1.6), the drag (9.6), the name
  (16.0) and the loop point sit on quarter notes, and every cut lands one sixteenth after a
  quarter, the same push each time. The guitar bend became a **synth glide whose pitch follows
  the exact easeInOut of the drag (9.32→9.96 s)**. Drums sit on the grid; every other cue sits
  on its motion. If a beat moves in `video.html`, mirror the constant in `sound.py` and re-run
  it — the cues follow.
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
- **A sound change is a remux, not a render.** `python3 sound.py` takes two seconds; then
  `ffmpeg -i study-001-v7.mp4 -i sound.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k
  -movflags +faststart -shortest out.mp4` swaps the track without touching the picture.
  Check loudness with `ffmpeg -i out.mp4 -af ebur128=peak=true -f null -`: the film sits at
  **−16.8 LUFS integrated, true peak −0.9 dBFS**. Reels normalise to about −14, so do not
  chase loudness; do keep true peak under −1 dB or the AAC encode clips the kicks.
- **Two transients closer than ~35 ms fuse; 100–250 ms apart they flam.** When a drum hit
  and a motion cue nearly coincide, put the drum exactly on the motion (the bar-3 downbeat
  *is* the ball's second bounce at 6.417) rather than on the grid next to it.
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
