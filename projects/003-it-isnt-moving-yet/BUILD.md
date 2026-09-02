# "It isn't moving yet" — build notes

**Status: at gate 1.** Two pieces exist. Runtime is **17 bars = 32.64s**.

- **Act I, the jar** — `source/blender/`, Blender 4.5 via `bpy`, Cycles on CPU. Seven
  bars of a dead plant in a mason jar growing in the dark and blooming. Stills and a
  low-res motion test render here; a full-resolution sequence does not (see below).
- **The bloom** — `source/video.html`, five beats of paint. Built with its origin at a
  send button that no longer exists; **its origin must move to the flower head.**

The chat-box opening was cut when the jar replaced it. `frame 0` as built is retired. `BRIEF.md` is the spec — read the REVISED section
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
| `source/blender/plant.py` | Act I. Builds the scene, and `set_time(t)` moves it. |
| `source/blender/render_plant.py` | Cycles CPU, stills or a range. |
| `scripts/handoff.py` | Projects the flower head and extracts its palette. |
| `scripts/brushplate.py` | The grayscale brush plate the bloom is textured with. |

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

## Act I — Blender in this container

```sh
pip install bpy==4.5.13
python3 source/blender/render_plant.py --times 0,3.4,7.2,10.6,12.5,13.44 --res 360 --samples 24
```

**There are no keyframes.** `plant.py` builds the scene once and `set_time(t)` positions
everything for time `t` — the same contract as `renderFrame(t)` in `video.html`, and for
the same reason: Blender's animation system would be a second source of truth to keep in
sync with the 125 BPM grid, and a pure function of `t` is not.

**What this container can and cannot do.** There is no GPU — `/dev/dri` does not exist.

- **Cycles CPU works** and is the only real path. 360×640 at 20 samples is ~3.3s/frame
  on 4 cores.
- **EEVEE is a dead end here.** It needs `libEGL`, which is not installed by default;
  `apt-get install libegl1 libglx-mesa0` plus `LIBGL_ALWAYS_SOFTWARE=1
  EGL_PLATFORM=surfaceless` does get it running — and it then took **40s for a default
  cube at 540×960**, far slower than Cycles, because llvmpipe is software rasterisation
  and EEVEE Next leans on a lot of GPU passes. Do not spend time on it.
- **A full-resolution Act I is a desktop job, and here is the measured number.** One
  frame at 1080×1920 / 96 samples took **104.3 seconds** on these four cores. Seven bars
  is 403 frames at 30fps and 1613 at 120 — so **11.7 hours** for a flat 30fps pass and
  **46.7 hours** for the house 120→`tmix`→30 shutter. Approve the act here as stills and
  low-res motion tests; render it where there is a GPU. `CLAUDE.md` already lists Blender
  as a desktop unlock and this is what it meant.

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
- **Frame the camera by solving for it, not by eye.** The first pass put the camera 0.86m
  from the jar on an 85mm lens. That covers 24cm of subject height — so the jar filled the
  bottom of the frame, the stem ran off the top, and the flower, the entire point of the
  act, was never in shot. `_camera()` now solves the distance from the lens, the sensor
  and the subject height.
- **A petal's "closed" is a HIGH pitch, not a low one.** The blade is generated along +Y
  and pitch rotates about X, so 90° stands a petal upright into a bud and 0° lays it flat
  and open. Writing it the intuitive way round ran the whole bloom backwards — the flower
  was wide open at 12.5s and a tight bud at 13.4s. It also must not go past about 18°:
  taken all the way to flat the petals reflex and the flower reads as a parasol.
- **A jar has to be mostly empty to read as glass.** 13cm of water in a 24cm jar made the
  body an opaque black cylinder that looked like a tin can. A finger of water — 4cm — lets
  the key light through the body, which is the only reason to use glass at all.
- **Four modelled petals do not make a poppy on camera.** A real poppy has four. Modelled
  as four, a front-on camera sees two face-on and two edge-on, and the open flower reads
  as a pair of blades sticking out sideways instead of a bowl. Six wide, heavily
  overlapping petals give the silhouette a poppy actually has. Botany loses to the camera.
- **The head must lift to about −20°, not to level.** The camera sits below the flower, so
  a head that comes fully upright presents the open bowl edge-on and the poppy reads as a
  flat squashed disc. Leaning it toward the lens is also what a real flower does.
- **A low-contrast paper plate does nothing over saturated colour.** The bloom's first
  texture pass reused 001's paper and ochre plates as overlays; on the cream ground of the
  old opening that worked, but over vermilion there is no value range left to push and at
  1:1 the paint was flat vector fill with a faint weave on it. `scripts/brushplate.py`
  builds a neutral-grey plate carrying **only value** (σ 53), so in `overlay` it carves
  brush strokes into any hue without shifting it — the palette rule expressed as a
  texture.
- **One full-frame plate over fifty overlapping petals reads as WOOD.** Every petal gets
  the same grain in the same place, so the striations run the whole height of the frame.
  A second copy at 1.6× and mirrored breaks it up. Petals also take a per-petal value
  jitter (never hue), because two overlapping petals drawn from the same eight-entry list
  are otherwise an identical flat fill and their shared edge vanishes.
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
- **Every petal has its own fixed duration** (`dur`, 0.45–0.90s), rather than all of them
  ending when the bloom ends. This is what let the bloom stretch from 1.44s to 2.4s
  without going soft: with a shared end time, the earliest petals have the LONGEST window
  and so lengthening the bloom slows the initial impact instead of increasing it. A fixed
  throw per petal keeps every one snapping out at the same speed, and length then buys
  more waves rather than slower ones.
- **Throw distance is a fraction of the room available along each petal's own heading**
  (`roomAlong(ang)`), not a fixed fraction of the frame. The button sits low and right, so
  a uniform cap meant nothing ever travelled into the top third — it stayed a flat field
  of wash for the entire second half of the bloom.
