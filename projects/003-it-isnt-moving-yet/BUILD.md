# "It isn't moving yet" — build notes

**Status: at gate 1.** Frame 0 (the cover) and the bloom (the hero) are built and
rendered. Nothing past `bt(5)` exists. `BRIEF.md` is the spec — read the REVISED section
at the top first, the premise changed after the interview.

## The stack

The **001 engine**, not 002's Remotion: `video.html` + `render.py`, one deterministic
`window.renderFrame(t)`, no CSS animation anywhere. The reason is the paint — `paint.py`
and the oil plates in `tex/` are what make this film teti's rather than anyone's, and
they already live in this pipeline. Same 125 BPM grid as 001, so `sound.py` transfers
with no conversion.

| File | What it is |
|---|---|
| `source/video.html` | The film. Frame 0 and the bloom, on the 125 BPM grid. |
| `source/render.py` | Headless Chromium, frame by frame. Fails loudly on a page error. |
| `source/paint.py` | The oil plates, from 001. `OUT` now writes next to itself. |
| `source/fonts/` | Inter + IBM Plex Mono, self-hosted. |
| `scripts/check-bloom.py` | Asserts the bloom only ever grows. Read why below. |

```sh
python3 source/render.py --out ../outputs/pv --times 0,0.96,1.32,1.86,2.40   # stills
python3 scripts/check-bloom.py outputs/pv                                     # regression
python3 source/render.py --out source/frames120 --fps 120                     # ~6 min
```

Then the house shutter — render at 120, average three frames down to 30. There is no
system ffmpeg in this container and Playwright's is useless (see below), so:

```sh
FF=$(python3 -c "import imageio_ffmpeg;print(imageio_ffmpeg.get_ffmpeg_exe())")
$FF -y -framerate 120 -i source/frames120/f%05d.png \
  -filter_complex "[0:v]tmix=frames=3:weights='1 2 1',fps=30,noise=alls=2:allf=t+u,format=yuv420p[v]" \
  -map "[v]" -c:v libx264 -profile:v high -crf 17 -preset slow \
  -movflags +faststart outputs/gate-bloom.mp4
```

---

## Gotchas already paid for — do not rediscover these

- **Chromium silently stops compositing past a layer budget, and the render still
  succeeds.** This is the worst bug in the project so far and it reports *nothing*. The
  first bloom gave each of 53 petals its own halo, and each of those 106 full-frame divs
  its own copy of a 1080×1920 oil plate plus a weave, plus `will-change: clip-path`.
  That is 212 promoted layers and roughly 900MB of compositor memory. Chromium does not
  error, does not warn, and does not fall back — it just stops applying style updates,
  and `page.screenshot()` returns an **arbitrary earlier state**. The bloom appeared to
  grow, then recede, and at 2.40s rendered as frame 0 with no paint on screen at all.
  Every individual still looked like a plausible frame of *something*, which is what
  makes it dangerous. **The paint skin is global, one layer over the whole bloom, and
  there is no `will-change` anywhere in this film.**
- **`scripts/check-bloom.py` exists because of that bug and must stay in the loop.** A
  bloom may only ever grow, so coverage across a rendered sequence must be monotonic.
  Only the *sequence* reveals the failure; no single frame does. Coverage is measured
  against frame 0, not against the palette's parchment — the woven ground already sits
  ~40 levels off `#EFE3CC`, so an absolute reference reports 100% before anything has
  happened.
- **`weave.png` is a 360px TILE.** Stretching it to 1080×1920 turns a canvas weave into
  gingham, and multiplied at 0.55 it drags the cream ground from 239 down to about 190 —
  the parchment stops being parchment and the whole film goes grey. Native size,
  `background-repeat: repeat`, at 001's recipe: multiply 0.30 for the shadow side, overlay
  0.14 for the tooth.
- **A petal's travel must stay well under its size.** Thrown 0.88 of the way to the far
  corner while only growing to 0.42 of it, a petal ends the bloom *outside* the frame —
  so the paint peaked halfway through and then visibly receded. `dist` now tops out at
  0.45 REACH against a 0.30 radius.
- **A halo behind a petal draws the frame's own border twice.** Any petal big enough to
  span the frame contributes a straight edge where the viewport clips it, and a halo a
  few percent larger contributes a second one just inside — which is what the horizontal
  bands across the middle of the early renders were. The fix is not a smaller halo, it is
  **more petals, each smaller**, so no single shape is large enough to show the border.
- **Bristle amplitude is relative to radius, so the same profile reads differently at
  different sizes.** A 0.15 lobe at frequency 3 on a 400px petal is a 60px scallop — at
  frame scale that is torn paper, not paint. The profile runs four octaves at 5/11/23/41
  and spends its deviation on bristle-scale detail instead of big geometric lobes.
- **Colour has to be assigned by petal size, not at random.** Left to chance, parchment
  drew a 500px petal in the middle of the frame and read as a *hole punched in the paint*
  rather than as paint. Light tones and cools go to small petals only; the warm eight
  take everything large.
- **Fonts are self-hosted via `@font-face`, never fontconfig.** 001 asks for "Inter" by
  family name, which silently falls back to sans-serif on any machine that has not
  installed it system-wide — this container is one — and then every measured line width
  in the film is wrong with no error. The woff2 files are committed in `source/fonts/`.
- **`getBoundingClientRect()` on a flex line returns the container width, not the text
  width.** The caret is positioned off the last line of the question; at full container
  width it landed 300px to the right of the text it follows. The line divs carry
  `width: fit-content` and that is load-bearing.
- **The bloom swallows the question — it does not cross-fade with it.** The paint is
  later in the DOM, so it occludes the type for free. The first pass *also* faded the
  type out over half a beat, and the result was a frame of empty parchment with a small
  paint cluster in the corner: the question had gone before the paint arrived to take it.
  There is no opacity on the type at all.
- **Playwright's bundled ffmpeg is built `--disable-everything`.** It exists to write
  webm screen recordings: it cannot demux mp4 and has no h264 decoder, so it fails on the
  repo's own renders with "Invalid data found when processing input" — which reads like a
  corrupt file and is not. `pip install imageio-ffmpeg` provides a full build with libx264
  and is what every encode in this project uses.

## Where the build diverges from the brief

- **The bloom is 38→66 small petals plus a base wash, not one expanding shape.** The
  brief just says "blooms with colour". The first build took that literally as nine
  concentric discs and produced four flat colour fields stacked like torn paper — no
  origin, no radiation, nothing that read as a detonation. What makes it paint thrown out
  of a button is that no single petal covers the frame.
- **Late petals are deliberately smaller** (`rad × (1 − 0.55·lag)`). The bloom used to own
  the frame by 1.50s and then had nine tenths of a second with nothing left to do.
