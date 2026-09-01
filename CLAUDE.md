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

## Open decisions

1. **Profile picture** — eight options rendered in `brand/pfp/`. Recommended: `duotone`.
   Not yet produced at final size or applied.
2. **Hours and deadline** — never pinned down. Assume "ship soon" unless teti says otherwise.

## What a desktop session unlocks

This project was built in a cloud container, which cannot reach desktop apps. Running
locally adds:

- **DaVinci Resolve Studio** — see `projects/001-why-motion-editors/resolve/README.md` for
  setup and `build_timeline.py` (written, untested against a live Resolve).
- **Blender** — `bpy` is fully scriptable and runs headless, so scenes, sims and renders can
  be built in code and composited into the same pipeline.

See `HANDOFF.md` for what to build next and why.
