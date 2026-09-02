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
  teti retired "Parisienne Walkways" after v6 ("I don't like any music"). Two synthesised
  soundtracks were then rejected (a sparse motion score, then a jazz bed with a bespoke
  five-note hook — "I don't like it at all"). What landed is **house**, asked for by
  reference: Kungs' *I Feel So Bad* feat. Ephemerals (123 BPM, A minor).
- **The film is cut to a 125 BPM grid, and that is the load-bearing fact.** 125 is the same
  room as the reference and divides the film exactly: a beat is **0.48 s**, a bar **1.92 s**,
  and the film is **eleven bars = 21.12 s**, so the loop point lands on a downbeat. In
  `video.html` the grid is `BPM/BEAT/BAR` and `bt(n)` = beat n from frame 0; every section
  boundary and every motion is written in `bt()`, not in fractions of a scene. **Do not
  re-time anything to a value that is not a multiple of 0.12 s (a sixteenth).** The
  landings: MOTION on `bt(7)`, the ball on `bt(13)`/`bt(15)`, the seven-bar stagger up the
  eighths, the drag arriving on `bt(24)` (the drop), the five layers on the eighths after it,
  one hero line per beat with MOVE. home on `bt(32)`, the type cycle on sixteenths landing on
  Inter at `bt(40)`, MOVE. out on `bt(43)` and home on `bt(44)`.
- **`sound.py` mirrors that grid and must be re-run after any timing change.** Arrangement,
  both styles: bar 1 intro, bar 2 the beat lands, 3–5 the groove, 6 the build (parts pull
  out, a fill runs in), 7 THE DROP, 8–9 the hero, 10–11 the end card thinning to the last
  hit. The bend is a glide on the drag's exact easeInOut, `bt(23)→bt(24)`, landing with the
  drop.
- **Six styles share the grid; the motion cues are identical in all of them.**
  `python3 sound.py --style=NAME` writes `sound_NAME.wav` (`house` is the default and writes
  `sound.wav`). Only the `groove_*()` function differs, because the cues come from the film,
  not the genre — so **a style swap is a remux, never a re-render**, and adding a seventh
  style means writing one function.
  | style | what it is |
  |---|---|
  | `none` | no music — the film's own sound design, the baseline the rest must beat |
  | `house` | Kungs, *I Feel So Bad* — four on the floor, offbeat open hats, a pluck riff |
  | `afro` | HUGEL & SOLTO, *Jamaican (Bam Bam)* — conga tumbao, shaker sixteenths, marimba |
  | `boombap` | half-time, reads at ~62 — kick on 1, snare on 3, swung hats, vinyl |
  | `techno` | cold: a long kick, struck metal on the offbeats, one note of melody |
  | `trailer` | no groove — a drone, a slow pulse, low brass on the section lines |
  The variant wavs are gitignored: they regenerate in two seconds. `study-001-audio-options.mp4`
  is the A/B reel — the same four bars (the build, the drop, the hero) under each option.
- **Density and weight are the two axes that actually separate them**, measured over those
  four bars: onsets per bar runs 8 (`none`) → 36 (`afro`), and the low/high energy balance
  runs −10.5 dB (`none`, thin and bright) → +1.0 dB (`afro`, bass-forward). Pick on those,
  not on genre names.
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
  `ffmpeg -i study-001-v10.mp4 -i sound.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k
  -movflags +faststart -shortest out.mp4` swaps the track without touching the picture.
  Check loudness with `ffmpeg -i out.mp4 -af ebur128=peak=true -f null -`: the film sits at
  **−14.3 LUFS integrated, true peak −1.3 dBFS** — house sits louder than the earlier sparse
  cuts, and Reels normalise to about −14, so that is the target. Keep true peak under −1 dB
  or the AAC encode clips the kicks.
- **In `sound.py`, note names must not shadow the beats.** `B2`…`B6` are beat tuples, so a
  note constant may never reuse those names. (A jazz pass redefined `B2` as 123.47 Hz and
  every `B2[0]` downstream became "float is not subscriptable".)
- **A line of type must sweep in a fixed time, not a fixed time per letter.** The hero lines
  are 7 to 13 characters; with a constant per-letter step the long lines were still filling in
  when MOVE. landed. The step is `(BEAT/2)/(nchars-1)`, so every line is home one beat after
  it starts, whatever its length.
- **Check the whole timeline for JS errors before committing to a 38-minute render.** Driving
  `renderFrame` across all 2534 frames in a headless page takes ~40 s and catches a throw or a
  console error that a preview still would miss.
- **Two transients closer than ~35 ms fuse; 100–250 ms apart they flam.** When a drum hit
  and a motion cue nearly coincide, put the drum exactly on the motion (the bar-3 downbeat
  *is* the ball's second bounce at 6.417) rather than on the grid next to it.
- **Big background images must be decoded before the first screenshot.** `render.py`
  decodes every texture in `tex/` explicitly; without that the 2 MB portrait rendered as an
  empty circle in the first frames it appeared.

## Study 002 — STILL., "The idea was never the problem"

`projects/002-the-idea-was-never-the-problem/` is a second, separate film and a
**different stack**: Remotion + TypeScript at 60fps, not the HTML/Playwright pipeline
above. Its own `BRIEF.md` is the spec and its `BUILD.md` has the commands and the bugs
already paid for. Nothing in it shares code with study 001 — read those two files, not
this section, before working on it.

It shows the same sentence and the same grey square twice: once with dead template
motion, once with real motion, and nothing added in between. **It is at a stop gate** —
Act I (frames 0–480) is built and rendered and must be approved as *lifeless* before
anything past frame 480 is written. `npm run verify` reports the unbuilt sections as
PENDING rather than PASS, on purpose.

(`HANDOFF.md` proposed ARC-in-Blender as study 002. This took the slot because it is
what got briefed; ARC is still the strongest 3D move whenever it is picked up.)

## The pitch film — "It isn't moving yet"

`projects/003-it-isnt-moving-yet/` is **at gate 1**, and it is the one project here with
**two stacks in one film**: Act I is Blender/Cycles (`source/blender/`), everything after
the bloom is the 001 HTML engine (`source/video.html`). It is **not a numbered study** —
the directory is numbered for ordering only; the studies are the craft, this is the offer.
Read its `BRIEF.md` first.

**It is the master** — teti's current skill level on display, with no post date, no
deadline and no call to action. An earlier brief had it as a conversion ad; that was
withdrawn, and `BRIEF.md` records what was pulled and why so it does not creep back.

The question is **"how do you make ideas that aren't alive, alive?"** and it is never
answered on screen.

Load-bearing for it, if it gets built:

- **The ground never leaves the warm family; the accent may.** Five techniques each get
  their own accent colour, which is the only sanctioned exception to the palette rule
  above — bone and umber stay constant under all five, as do the oil-plate surface and the
  125 BPM grid. That is what stops five palettes reading as five different films.
- **Same 125 BPM grid as 001**, so `sound.py` and the beat helpers transfer directly.
  **18 bars = 34.56s**. Act I is eight bars; the bloom is five beats.
- **Act I is a dead POPPY in a mason jar, in the dark, growing and blooming** — seven
  bars, `bt(0)`–`bt(28)`. The poppy is chosen for camera reasons, not botanical ones: its
  bud reads as dead, its head lifts before it opens (anticipation performed by the plant),
  and its petals emerge creased and open by uncreasing. It is modelled with six
  overlapping petals, not four — four gives a front-on camera two blades instead of a bowl. It makes the film's question literal rather than metaphorical.
  **The chat box was cut entirely**; there is no interface anywhere in the film, which is
  what disposes of the "I asked AI to..." risk. The question appears as pure type.
- **The transition is a camera arc, and it is the best structural idea in the film.**
  After the poppy opens, the camera rises over it to a birds-eye and comes down into the
  petals until they cover the screen. A poppy from above is petals radiating from a dark
  centre — the same image as the paint detonation — so the two worlds are one picture in
  two media and the cut becomes a SUBSTITUTION rather than a transition. Two distances:
  stop at the rosette, then push in. Then one sixteenth of black, and the paint.
- **The paint bloom erupts out of the flower head, and the join is extracted, never typed.**
  `scripts/handoff.py` projects the head through Act I's real camera and k-means clusters
  the rendered poppy for the palette, lifting it **in value only** — the same method that
  produced 001's palette from the oil portrait. Re-run it after any change to the Blender
  camera or lighting, or the paint silently starts in the wrong place in the wrong colour.
  The 3D act is not cut away from, it is covered; the two worlds share exactly one frame.
- **The bloom is textured with `scripts/brushplate.py`, a neutral-grey plate carrying only
  value.** 001's paper plates do nothing over saturated colour — there is no value range
  left to push, and the paint reads as flat vector fill. A grey plate in `overlay` carves
  strokes into any hue without shifting it: the palette rule expressed as a texture.
- **Act I is lit by ONE beam from above** landing on the floor as a pool, with the camera
  starting across a dark room and travelling into it. **The lights cut to black on
  `bt(27)`** — two frames, a switch not a fade — so the film holds on nothing for a beat
  and the bloom detonates out of a hole rather than out of a lit frame.
- **In Blender, aim lights with `aim_at(ob, target)` and never by typed Euler angles**, and
  remember that `volume_bounces` defaults to 0 — which is no scattering at all, so a beam
  renders as nothing. Both failures look exactly like "the value is too low". A lamp's
  footprint on the table is also what photographs, not the lamp: use light linking rather
  than hunting for a position where the spill hides.
- **`plant.py` has no keyframes.** It builds the scene once and `set_time(t)` moves it,
  the same contract as `renderFrame(t)`, so the 125 BPM grid stays the only clock.
- **The question returns unchanged at the end and the viewer supplies the answer.**
  Putting a line under it is the one edit that breaks the film.
- **Every bloom petal has its own fixed duration**, rather than all of them ending when
  the bloom does. Otherwise the earliest petals take the longest to grow and lengthening
  the bloom makes the impact softer instead of bigger.
- **Throw distance is a fraction of the room available along each petal's heading**, not
  a fixed fraction of the frame. The button sits low and right; a uniform cap meant
  nothing ever travelled into the top third and it stayed a flat field for half the bloom.
- **No `will-change`, and one paint skin over the whole bloom, never one per petal.**
  Past a layer budget Chromium stops applying style updates *silently* — no error, no
  warning — and screenshots come back showing arbitrary earlier states.
  `scripts/check-bloom.py` asserts coverage is monotonic and is what catches it.

## Blender in this container

`pip install bpy==4.5.13` gives Blender as a Python module and **Cycles on CPU works**
(~3.3s/frame at 360x640, 20 samples, 4 cores). Two things to know before spending time:

- **There is no GPU** — `/dev/dri` does not exist. EEVEE needs `libEGL` (not installed;
  `apt-get install libegl1 libglx-mesa0` plus `LIBGL_ALWAYS_SOFTWARE=1
  EGL_PLATFORM=surfaceless` does get it running) and then renders a *default cube* at
  540x960 in 40s — far slower than Cycles, because llvmpipe is software rasterisation.
  EEVEE is a dead end here; do not retry it.
- **Full-resolution Blender sequences are a desktop job.** Approve the act here as stills
  and low-res motion tests, render it where there is a GPU.

## ffmpeg in this container

There is no system ffmpeg, and Playwright's bundled one is built `--disable-everything`:
it cannot demux mp4 or decode h264, so it fails on this repo's own renders with an error
that reads like file corruption. `pip install imageio-ffmpeg` gives a full build with
libx264 — `python3 -c "import imageio_ffmpeg;print(imageio_ffmpeg.get_ffmpeg_exe())"`.
This is what makes the 120fps → `tmix` → 30 house shutter runnable here at all.

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
