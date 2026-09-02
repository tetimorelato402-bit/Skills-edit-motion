# "It isn't moving yet" — build notes

**Status: at gate 1.** Two pieces exist. Runtime is **18 bars = 34.56s**.

- **Act I, the jar** — `source/blender/`, Blender 4.5 via `bpy`, Cycles on CPU. Eight
  bars: a dead poppy in a mason jar under a shaft of light, growing, blooming, and then
  the camera arcing over it and coming down into the petals until they own the screen. Stills and a
  low-res motion test render here; a full-resolution sequence does not (see below).
- **The bloom** — `source/video.html`, five beats of paint, erupting from the flower's
  black centre at (540, 963) — dead frame centre, because Act I now ends looking straight
  down the flower's throat. Origin and palette both come from `scripts/handoff.py`.

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
| `scripts/handoff.py` | Projects the flower head and its petal axes, and extracts its palette. |
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
- **`volume_bounces` defaults to ZERO in Cycles, and that means no scattering at all.**
  Not "no indirect volume light" — a camera ray crossing the beam can only be absorbed, so
  the shaft rendered as *nothing* through a correctly built, correctly lit, density-15
  cone. It looks exactly like a texture or a density bug and is neither. `configure()`
  sets it to 2.
- **A volume mesh must be a closed manifold.** The beam cone was built as a side wall with
  no caps; an open tube has no inside for Cycles to fill and renders as nothing at any
  density — the same symptom as the bounces bug, from a different cause.
- **A shaft is only a shaft if its edges are in frame.** At 19° the cone was 58cm across
  where the frame is 46cm wide, so the haze filled the whole frame and read as a general
  lift. The camera was inside the light. The beam also has to be *wider than the light
  cone* (5.5° of haze around a 3.5° spot), or the volume's own boundary becomes the visible
  edge and the beam renders as a bar with hard vertical sides.
- **The light and the subject must actually be in the same place.** The spot and cone sat
  at (0.05, 0.10) while the jar was at the origin, so the beam came down *beside* the
  flower and lit bare table next to it.
- **What photographs is the light a lamp CASTS, not the lamp.** A cool area fill laid two
  hard pale trapezoids across the table either side of the jar, and they read as flat cards
  standing behind the subject — set dressing, not a bug, which is why they survived several
  passes. `visible_camera = False` does not help, because the lamp itself was never the
  thing in shot. The fix is **light linking**: the rim spot is linked to the jar and the
  water alone (`light_linking.receiver_collection`) so it edges the glass and cannot touch
  the table. Hunting for a lamp position where the footprint hides is wasted time — the
  table is six metres wide.
- **Aim lights at a target, never by typed Euler angles.** The rim spot was set to
  (118°, 0, −141°) and lit nothing whatsoever, which is indistinguishable from an energy
  that is too low. `aim_at(ob, target)` builds the rotation from a direction vector, and a
  direction vector cannot be wrong that way.
- **A poppy sheds its sepals, and the birds-eye is why that matters.** Kept at full size
  they lie across the flower's face — invisible from the side, and from overhead a 6cm
  green blade covers the centre of the shot the whole act is building to. `scale *= (1 −
  opening)` is both botanically right and the fix.
- **Arcing overhead is not the same as getting a plan view.** The head is tilted 20°
  toward the lens, so a camera at 86° above it still yields a three-quarter. The flower
  has to straighten to meet the camera as it comes over — motivated (flowers turn to
  light) and it is what makes the shot read as looking down the throat.
- **The push needs two distances, not one.** Going straight to the final radius puts the
  lens INSIDE the flower, framing one sepal. Stop first at the distance where the whole
  bloom fills the frame — the rosette, which is the entire reason for going overhead — and
  only then come down into it.
- **Tilting the shaft has to be toward the camera.** Tilted away from the lens for the
  birds-eye, the poppy is backlit and goes dark at exactly the moment it should be at its
  brightest — correctly lit, and unusable.
## The five techniques

Bars 11–15, one bar each, in `video.html`. **Every one of them shows the same poppy** —
the Blender frame the film has been looking at since bar 7. That is the demonstration:
identical content, five languages. It is also what lets the film claim range without
becoming a showreel of five unrelated clips, and it carries the flower straight through
the back half.

| Bar | Technique | Accent | What it does |
|---|---|---|---|
| 11 | T5 white space editorial | rust | One petal at twice frame height crossing an otherwise empty frame. The technique is the imbalance. |
| 12 | T6 modular grid | signal blue | The frame becomes 3×5 cells and the flower is dealt across them, quantised to sixteenths; a blue block crosses and occludes. |
| 13 | T3 torn collage | hot red | Seven torn fragments slam in at 6–14°, tape, and the red block wipes the whole frame twice inside the bar. |
| 14 | T9 ink on one colour | mustard | Black line on flat mustard, drawn on with `stroke-dashoffset`. |
| 15 | T7 painted frame | the paint engine | A bristled brush wipe reveals the painting, which keeps breathing after it lands. |
| 16 | all five at once | — | Five horizontal bands, one technique each, sliding in **alternating** directions. Five bands drifting the same way is a texture scrolling; five opposing each other is five things happening at once. |
| 17 | the question returns | — | Each line rises out of its own clipped box, one per eighth, and then the bar holds. **Nothing is added.** |
| 18 | `teti.` and the loop | rust | The name lands, the dot arrives a beat later and is the only rust on screen, then the film **cuts** back to the dark jar. |

**Each entry transition is the technique announcing itself** — the grid arrives as tiles
snapping, the collage as a torn wipe, the ink as a flood. A generic dissolve between them
would make the five read as clips; a transition built from the technique's own grammar is
one film changing voice.

**Bar 16 rebuilds its five bands rather than reusing the scenes.** A technique scaled down
to a fifth of the frame stops being the technique — T5's entire character is a shape too
big for its frame, and shrunk into a band it is just a small picture. Each band is its
technique's *signature* at band scale.

**The loop is a cut, not a crossfade.** Dissolving a parchment end card into a frame that
is 95% black passes through a washed grey for half a beat and reads as a fade to nothing.
The film cuts — the shutter does, and so does this: two sixteenths of the dark jar, so the
last frame is the first frame.

**T9 was the scheduling risk and it is solved.** The brief flagged ink-on-one-colour as
the only asset code teti already owns could not produce, because it needs hand-drawn line
work. The line is instead generated from the flower's own geometry — the same petal
profile and the same six projected axes the paint bloom uses — and drawn on with
`stroke-dashoffset`. It is hand-drawn in the sense that matters: nothing was traced, and
it is the same flower.

## Making it read as ONE flower

The film asks a viewer to follow a single object through a growth, a camera arc, a cut and
a change of medium. Three things break that reading, and all three are fixed rather than
hoped about:

- **Exposure.** The camera closes from 3.2x the framing distance to 0.36m and the pool it
  travels into gets brighter the whole way, so the poppy rendered dim at 13s and blazing
  at 15s. It is one continuous shot of one flower, but a colour that swings that far reads
  as two different objects. The key pulls back 42% across the arc and the push so the
  petals hold the same vermilion from the moment they open to the moment the paint takes
  them.
- **The petal axes.** `handoff.py` projects the six real petals' screen directions
  (48.2°, 110.3°, 172.0°, 231.5°, 289.8°, 348.3°) and the paint's first six petals launch
  along exactly those, first, before the rest. For the opening frames the paint is not
  merely erupting from where the flower was — it is continuing the flower's own geometry
  outward. This is the single strongest continuity cue in the film and it costs nothing.
- **The backdrop must be regenerated whenever the lighting changes.** `act1_last.png` is
  Act I's final lit frame and the ground the paint erupts over. Change the Blender
  exposure and the 2D clip is butting against a frame that no longer exists — the join
  jumps in brightness at exactly the cut you spent the whole act hiding. **Re-run
  `handoff.py` after ANY change to the camera or the lights**, and re-render the 2D side
  after it.

The clips also butt with nothing to trim: Act I runs `bt(0)`–`bt(32)` and ends on a
sixteenth of black; `video.html`'s local time 0 IS `bt(32)`, the frame the shutter opens on.

---

- **Every scene must outlive its own bar by an eighth.** Each technique enters through a
  bristled wipe of its own colour, and a wipe reveals the incoming picture *over* the
  outgoing one. Cutting the previous scene at its last frame leaves the wipe uncovering
  the bare page, so between every pair of techniques the film flashed empty parchment —
  which reads as a missing scene rather than as a bug, and is easy to stare straight past.
- **A texture at full strength eats its own subject.** T7's brush plate at 0.78 overlay
  turned the painted poppy into an abstract fire: the flower was still there and nobody
  could see it. The paint is a SURFACE (0.20 / 0.16 / 0.18 with the weave under it); the
  poppy is the subject.
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
