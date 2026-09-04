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

**One Blender film.** `plant.py` builds the whole scene once — the dark room, the plant,
the jar, the beam, and a studio (cyclorama, a four-light rig, five looks' materials, the
question as 3D type) that is hidden and unlit until `bt(44)` — and `set_time(t)` moves
everything for time `t`. There are no keyframes; the 129 BPM grid is the only clock.
`render_plant.py` drives Cycles a frame at a time. The 2D half that used to carry the
back half (`video.html`, the paint bloom, `handoff.py`'s join) is in `source/attic/` with
a README saying why; nothing calls it.

| File | What it is |
|---|---|
| `source/blender/plant.py` | The film. Builds the scene, and `set_time(t)` moves it — lights, camera, materials, type. |
| `source/blender/render_plant.py` | Cycles CPU/GPU, stills (`--times`) or a range (`--start/--end`). |
| `source/question.html` + `source/render_overlay.py` | The question, typeset in Chromium and composited over Act I's frames. Self-hosted Inter. |
| `source/fonts/` | Inter + IBM Plex Mono, `.woff2` for the overlay and `.ttf` for Blender's FONT objects. |
| `build.sh` | The whole build, resumable, single-instance. `RES` and `SAMPLES` from the environment. |
| `assemble.sh` | Conform to 1080x1920/30, cut the track under it from 46.555 s, loudnorm, decode check. |
| `scripts/verify-film.py` | Frames present, lit where lit, loop pixel-exact, mp4 decodes, silence under the fall, contact sheet. |
| `scripts/track.py` | Measured the tempo and found the two silences. `audio/README.md` has the numbers. |
| `scripts/brushplate.py` | The grey brush plate the painted look's impasto is built on. |
| `scripts/handoff.py`, `scripts/check-bloom.py` | Retired with the 2D half. They still run; nothing needs them. |

```sh
pip install bpy==4.5.13 imageio-ffmpeg pillow numpy playwright && playwright install chromium
python3 source/blender/render_plant.py --res 540 --samples 24 --out outputs/pv \
    --times 12.5,20.0,23.7,25.6,26.5,32.8,47.0            # stills at the moments that matter
bash build.sh                                             # 540 px / 24 samples: ~4-5 h on four CPU cores
RES=1080 SAMPLES=64 bash build.sh                         # the desktop, on a GPU: well under an hour
python3 scripts/verify-film.py                            # before believing any of it
```

`build.sh` renders to `outputs/film/`, composites the question, and calls `assemble.sh`,
which writes `outputs/it-isnt-moving-yet.mp4`. Every stage resumes from the first frame
actually missing, and the frame directory carries a signature of `plant.py` + `RES/SAMPLES`
— change any of them and the directory is cleared rather than resumed into. To re-render a
range after a change that only touches one section, delete those frames and run
`build.sh` again; it fills the gap and nothing else.

## Rendering on the desktop (Windows, an RTX card)

The same scripts, on the card. `render_plant.py` picks OptiX/CUDA when a GPU is
present and says so (`cycles device: OPTIX`); `build.sh` and `assemble.sh` find
whichever python this OS has; the overlay uses Playwright's own Chromium when the
container's is not there; `.gitattributes` pins the scripts to LF so a Windows
checkout does not hand bash a `\r` on every line. Everything below runs in
**Git Bash** (installed with Git for Windows) — not PowerShell, not cmd.

```sh
winget install Git.Git Python.Python.3.11              # once; then open a NEW Git Bash
# A SLIM clone: the repo carries ~300 MB of finished mp4s from every study and
# a full clone dropped twice on a home connection. This fetches only this film's
# sources (~9 MB) — blobs on demand, one branch, no outputs/ — and builds fine.
git clone --filter=blob:none --depth 1 --single-branch \
    --branch claude/motion-editors-video-concept-fz6opf --no-checkout \
    https://github.com/tetimorelato402-bit/skills-edit-motion.git
cd skills-edit-motion
# CONE mode, listing the subdirectories wanted. Cone mode pulls in each
# listed directory recursively plus the plain files of every parent, so this
# gets build.sh, BUILD.md, source/, scripts/, audio/ — and NOT outputs/, the
# sibling with 70 MB of old mp4s. (A no-cone pattern set that excluded /*/ and
# re-included the project fetched nothing but the root files on Git for
# Windows; re-including under an excluded parent is not portable.)
git sparse-checkout init --cone
git sparse-checkout set projects/003-it-isnt-moving-yet/source \
    projects/003-it-isnt-moving-yet/scripts projects/003-it-isnt-moving-yet/audio
git checkout claude/motion-editors-video-concept-fz6opf
cd projects/003-it-isnt-moving-yet
py -3.11 -m venv .venv && source .venv/Scripts/activate   # bpy 4.5 needs 3.11 EXACTLY
pip install bpy==4.5.13 imageio-ffmpeg pillow numpy playwright && playwright install chromium
cp /c/Users/<you>/Downloads/gracias_a_ti_beat_129bpm_luifer.mp3 audio/gracias-a-ti-129.mp3
python source/blender/render_plant.py --res 540 --samples 24 --out outputs/pv --times 23.7   # must print "cycles device: OPTIX"
RES=1080 SAMPLES=64 bash build.sh
python scripts/verify-film.py
```

Things that bite on Windows and are already handled, in case one of them comes
back: `python3` in Git Bash is frequently the Microsoft Store stub, which opens
a shop window instead of Python — the scripts prefer `python` on Windows and
`PY=/path/to/python.exe` overrides them; `flock` does not exist there, so the
one-build-at-a-time lock is skipped rather than failing; a venv on Windows makes
`python.exe`, not `python3.exe`; `bpy` wheels exist for 3.11 only, so 3.12/3.13
gives "no matching distribution" and the fix is the 3.11 venv, not a newer bpy.
The audio track is gitignored and has to be copied in by hand. Blender 5.2
installed on the machine is NOT what renders — the pip `bpy` 4.5 module is,
same as the container, so the two renders match.

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
- **`set_time` has to aim the key BACK, not just forward.** The follow-spot is re-aimed at
  the falling petal from `DETACH` onward — and the first version never aimed it home again,
  so the lamp's rotation depended on which times had already been evaluated. A sequential
  render never notices, because `t` only increases. `handoff.py` does not render
  sequentially: it evaluates the end of the act to project the petal, then goes back to the
  open flower to shoot the poppy plate, and got a **96% black frame** — the beam was still
  pointing at the patch of table where the petal lands thirteen beats later. Anything that
  evaluates out of order hits this: a re-rendered range, a preview at scattered times, an
  extraction script. `set_time` being a pure function of `t` is the whole reason this file
  has no keyframes; that has to include the lights.
- **Two builds racing produce an mp4 that PROBES fine and will not decode.** Two instances
  of `build.sh` overlapped once and both wrote `outputs/it-isnt-moving-yet.mp4`. The result
  reported a correct 50.23s duration and two valid streams to `ffprobe` — and threw
  `Invalid NAL unit size` / `Error splitting the input into NAL units` the moment anything
  tried to decode it. The frame stages are individually safe (they resume, and rewriting a
  frame with the same frame is harmless); the ENCODE is not, because two writers share one
  output path. `build.sh` takes an exclusive `flock` and refuses to start a second run.
- **Verify a render by DECODING it, not by probing it.** `ffprobe`-style header checks
  passed on a file that was structurally broken all the way through. `ffmpeg -v error -i
  out.mp4 -f null -` walks every frame and prints nothing when the file is sound.
- **Put the assertion in the watcher, not in your head.** This was caught because the
  monitor waiting on the plate measured how much of it came back dark and printed
  `dark 96% (want ~10%)`. The render succeeded, wrote a valid PNG, and reported nothing
  wrong. Every long-running job in this project that produces an image should be watched
  by something that knows what the image is supposed to look like.
- **An overlay authored at 1080 will silently CROP onto a 540 frame.** Act I renders at
  540x960 and `question.html` is laid out for 1080x1920; PIL's `alpha_composite` pastes at
  1:1 from the top-left and takes no view about the size difference, so the first pass
  composited the top-left QUARTER of the type at double scale, running off the right of
  every frame. It reads exactly like a font that is too big — which sent me to `fc-list`
  and a font install before the image dimensions. `render_overlay.py` resamples the
  overlay to whatever the plate actually is; the design stays at 1080 because that is the
  frame it was laid out for.
- **The overlay passes self-host their fonts, because the container loses them.** This
  session's container restarted mid-build and came back with no Inter installed, so a
  132px 800-weight line would have fallen back to DejaVu. `video.html` has always carried
  its own `@font-face` off `source/fonts/inter.woff2` and was never exposed;
  `question.html` and `glitch.html` were relying on a system install and now do the same.
  `fc-list` is a check somebody has to remember to run. An `@font-face` is not.
- **Resume from the first MISSING frame, not from the file count.** Counting files and
  starting at the count is only correct if they are contiguous, and a container restart
  does not promise that: this one came back having lost frames 118-167 while keeping
  everything after them. The count said 168, the render resumed at 168, and it spent an
  hour extending a sequence with a fifty-frame hole in the middle of the stem's growth.
  ffmpeg does not care — it would have produced a two-second jump cut and no warning.
  `build.sh` now finds the first missing index in each leg's range and, importantly, the
  END of that missing run, so it fills the 50-frame gap instead of re-rendering the 312
  frames that follow it.
- **A resumable render will happily finish somebody else's film.** Every stage of
  `build.sh` resumes by counting the frames already on disk, which cannot distinguish
  "already rendered" from "rendered under a DIFFERENT timeline". The first run after the
  re-cut found 369 Act I frames and 2304 studio frames left from the 18-bar version at 125
  BPM, counted them as progress, and set about completing a film half of which was the
  previous edit. Nothing errors; every stale frame is a valid PNG of a plausible picture,
  and it would have surfaced as "the first half looks wrong somehow" after three hours.
  Each frame directory now carries a **signature of the timeline constants** that produced
  it, and a mismatch wipes the directory instead of resuming into it. The same reasoning
  covers the extracted textures: `build.sh` copies `act1_last.png` and `poppy.png` into
  `source/tex/` itself rather than trusting that somebody remembered to.
- **check-bloom.py measures the BLOOM, and nothing after it.** Pointed at a full
  2304-frame render it reported ~1500 frames "went backwards" and meant none of it:
  coverage is measured against frame 0, and once the five techniques start cutting, each
  has its own composition and its own crop of the poppy, so it rises and falls for
  entirely healthy reasons. The script truncates to the first 289 frames now (`bt(5)` at
  120fps) and says so; `--all` overrides. The trap was easy to walk into precisely
  because the output looks like the catastrophic bug it was written to catch.
- **The bloom check needed a tolerance, and that is not a weakening.** The failure it
  guards is a CLIFF — a 90%-covered frame coming back as frame 0 — but its threshold was
  0.005, and once the bloom plateaus near full frame the paint skin and the petals' own
  edges move coverage half a point either way. It failed a completely healthy render five
  times, which is how a regression check stops being run. It is 0.05 now, still an order
  of magnitude below anything the compositor failure has produced.
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

## The flower carries the palette

Three things tie the five techniques' accents back to the flower itself, so the colour in
the back half is not five arbitrary choices but something the flower was already doing.

- **The stem glitches through the five accents while it climbs.** `ACCENTS` in `plant.py`
  is the same five hexes as `AC` in `video.html`, converted sRGB→linear (Blender's inputs
  are linear; pasting the hex straight in renders about 40% too bright and washes the
  colours toward pastel). The stem picks one at random on a **thirty-second** grid — fast
  enough to strobe, slow enough to read as discrete colours rather than as noise — and the
  hit density decays `(1 - progress) ** 1.6` across the first 3.2 bars, so it is violent
  when the plant is dead and gone by the time the bud forms. Measured over the render:
  **48% of frames carry a hit in the first third, 16% in the middle, 5% in the last.** The
  randomness is a hashed frame index, not `random()` — `set_time(t)` has to stay a pure
  function of `t` or a re-render of a range comes back different from the first pass.
- **Each technique tints the poppy to its own accent, and the tint is `mix-blend-mode:
  color`.** `tint()` in `video.html` lays the accent over the scene taking hue and
  saturation from the tint and **luminance from the source**, so every fold, edge and
  brush stroke in the flower survives the recolour. A flat `background` at low opacity, or
  `multiply` alone, buries exactly the detail the recolour exists to show. The second
  `multiply` layer at 0.22 of the strength is only there to keep the darks from going
  chalky. Six call sites: the five techniques and the bar-16 bands.
- **A bounce light, linked to the plant alone.** One warm area light low and to camera
  right, `light_linking.receiver_collection` set to the plant collection, lifting the
  shadow side of the stem and the undersides of the petals so the glitch colours are
  visible at all in a scene lit by one hard beam from above. Linked, because unlinked it
  puts a second pool on the table and the beam stops being the only light in the room.

### Four things that only show up once the flower is rendered big

Act I ends on six petals filling a 1080-wide frame. Everything below looked fine at 300px
and was a defect at 540, and the last lit frame is also the ground the ENTIRE 2D half is
composited over (`POPPY` in `video.html` is `act1_last.png`, used by all five techniques),
so a defect here is a defect in every shot of the film.

- **A smooth transmissive shell is moulded plastic, whatever the lighting.** The petals
  carry a procedural crumple bump and a roughness variation off the same noise — matte in
  the folds, silkier on the ridges — and the roughness half is the one that reads as
  tissue. Coordinates are **Generated**, not Object: Generated is normalised over the mesh
  bounding box in local space and so is unaffected by the petal's scale animating 0→1
  during the bloom. Object coordinates swim.
- **Veining and sheen both backfire.** A second bump stretched 26:1 base-to-tip made
  parallel streaks down each petal, and with `Sheen Weight` glinting off them the birds-eye
  read as brushed satin ribbing — a worse material than the plastic it replaced. Both were
  removed. Petal veins are a shading detail at this size and barely even that.
- **One crimp wave at six samples per period is a balloon.** `blade()`'s crease was a single
  2.5-period standing wave and `nv=15`, which is a perfectly smooth lobe six times over —
  the open flower read as a ring of inflated tubes. A 7-period harmonic at 0.30 of the
  amplitude, with `nv=27` to resolve it, is creased tissue from the same silhouette.
- **From directly above, an upright cylinder is a disc.** 52 identical stamens at 13° off
  vertical on one radius rendered as a bead necklace in the birds-eye — the shot the whole
  act builds toward. They splay 26–44° now and present their length to the camera as a
  radiating fringe, which is also the paint bloom's figure one shot early. Thin and short
  (r 0.42mm, 19–30mm): the first splayed pass was 0.62mm and 26–42mm and read as a scribble
  of black bars over the petals. All the jitter comes from a **hashed index, never
  `random()`** — a resumed render chunk rebuilds the scene from scratch and has to get the
  same flower.
- **Near-black under a broad specular lobe reads GREY at full-frame size**, because the
  highlight covers the whole sphere. The boss is `Roughness 0.88 / Specular IOR Level 0.22`
  — velvet — and only then is it the dark hole the brief says the paint comes out of.

**Cycles cost, measured on these four cores at 540x960:** 24 samples 11.1s/frame, 48
samples 19.9s/frame on a smooth petal. The creased petal costs about **three times** that
— bump plus transmission is a lot of rays — and a close-up measured 50.7s at 24 samples,
so the shading above turns a 68-minute act into a three-hour one. Adaptive sampling is what
buys it back: `adaptive_threshold = 0.02` with a 6-sample floor spends nothing on the dark
two-thirds of a frame lit by a single beam, where variance is already under what the
denoiser finishes anyway. `volume_step_rate = 8.0` sharpens the beam's edge for free; it is
a stepping change, not a sample change.

---

## The studio — five looks, in Blender, on the flower

The back half is no longer a cut to 2D. `plant.py`'s `_studio()` builds a cyclorama, a
four-light rig, a material per look, a font object per word, tape and the voxel modifiers —
all dark, hidden or disabled until `bt(44)` — and `_set_time_studio()` dresses the room per
look. `source/attic/` holds the retired 2D half; nothing calls it.

What each look actually is, mechanically:

| look | material | rig | geometry | type |
|---|---|---|---|---|
| editorial | the petal's own | soft key + fill + wash | — | `how`, Inter Black, 1.35 units, upright behind the flower, dollying |
| grid | flat signal blue | key + fill + wash, flat | **Solidify → Remesh BLOCKS**, `octree_depth` stepping 4/5/3/6 on the sixteenths | `do you`, flat on the floor |
| collage | flat hot-red paper | **one hard key**, size 0.35 | petals leave the head, hang at hashed angles, 8 tape strips placed off each petal's `matrix_world` | `make`, cut-out white, rotated −7° |
| ink | paper-white, opaque | fill + wash, shadowless | **Freestyle**: silhouette + border + crease, on a collection of the plant alone | `ideas that aren't`, Inter Regular, small |
| painted | plum with the brush plate as bump *and* roughness | raking key from the side | — | `alive,`, placed in world space on whichever face of petal 3 the camera can see |

**Gotchas already paid for in the studio:**

- **Size type to the FRAME, not the room.** A 65 mm lens on a vertical-fit 24 mm sensor in
  9:16 gives a frame only **0.21 × distance** wide: 30 cm across at the flower, 23 cm at the
  grid's floor label. Every word was first placed in scene-metres — a 1.1 m floor label, a
  caption 42 cm off-axis in a ±15 cm frame, a petal word twice the length of its petal — and
  none of it was in shot. Three rounds of "the type isn't rendering" were the type rendering
  perfectly, out of frame. Only *how* stays deliberately wider than the frame, because it
  crosses.
- **The word on the petal was in frame and invisible five times, for five different
  reasons, and every one was found by measuring rather than guessing.** Projected through the
  camera it was at (0.46, 0.61) in frame at depth 0.93 — with two petals in front of it at
  0.87: chosen by *best-facing*, which picked the back petal's inner face. Then, on the front
  petal, at mid-blade 1.8 cm off the mean plane — inside a crimp that is ±3.2 cm there, so the
  petal passed through it. Then at the tip, but flipped onto the outer face about X, which
  mirrors text. It lives on the **nearest petal that faces the lens**, at **86% of the blade**
  where the crimp is a third, turned about **Y**, and spun upright against the camera's own
  up vector. Five renders would have been fifty without `world_to_camera_view` in a probe.
- **The petal that carries the word is found every frame, not chosen.** Petal 3 was a guess
  and turned out to sit under the bowl with two petals over it. The front petal is whichever
  has its blade midpoint nearest the lens, and it changes as the painted look's camera pushes
  in.
- **`STUDIO_GAIN` exists because the film's exposure was set for one 620 W spot in a black
  room.** Four soft sources at 500–900 W plus a cyc bouncing all of it back put every look
  about a stop and a half over: plum rendered as dusty pink, signal blue as powder, the
  mustard field as peach. The rig values are the *ratios* between lamps and they were
  right; one scalar (0.36) sets how bright the room is.
- **The collage moves petals, so every pose must restore their LOCATION, not just their
  rotation.** The first `_pose_open()` reset rotation only, and the flower rendered torn
  apart through ink, painted, the strobe and the break. Same class of bug as the key aim.
- **A sheet cannot be remeshed.** Remesh in BLOCKS mode on the open petal mesh produced
  nothing; it needs volume, so Solidify (6 mm) goes first.
- **Freestyle draws only the plant.** `select_by_collection` on an `ink_only` collection —
  otherwise the cyc's cove and the jar's silhouette get inked too and the drawing loses its
  subject.
- **Type on a petal is placed in world space, not parented.** The blade's cupped face is on
  local −Z; parented text at +Z vanished behind it. The word is set a hair off the surface on
  whichever of the two faces is nearer the camera, with the petal's rotation.
- **Type on the floor needs a camera that can see the floor.** At 12° down the grid label was
  a sliver; the grid's camera sits at 1.05 m looking down ~30°, which is also the right view
  for a systematic look.
- **Transparent petals under the ink line were a tangle** — every overlapping outline showed
  through every other. Opaque paper-white under a black line is a drawing.
- **The studio is cheap.** 3–8 s/frame at 360 px on four cores, against 10–40 s for Act I:
  no haze, no transmission, flat materials. Freestyle is the only cost that shows.

## The studio turns — a full 360°, on the beat, with a real kit around it

teti asked for the camera to go all the way round the flower like it really was a studio,
for the words (still barely legible at the time) to be fixed, and for detail around the
flower rather than an empty cyc. All three turned out to be one change: `studio_az(t)` in
`plant.py` is a pure function of `t` that returns the camera's azimuth in radians, built
from the same `bt()`/`BEAT` grid as everything else — a beat is a "kick" (`_kicked()`,
`ease_out` inside the beat) that advances the turn 18° in STATED, 18°/beat then 9°/eighth
in CUTTING, a full 72°/eighth in ALLFIVE (a quarter-turn on every cut of the strobe — the
fastest the room ever moves, for the loudest the claim ever gets), then eases back to
exactly the axis Act I stood on across COLLAPSE. By the time it lands there the camera has
done just over **five full revolutions**. Every look, every word, and every fixture in the
rig is placed with `_place()`/`Rz(az)` in the CAMERA's frame, not the world's, so a look
reads identically from every angle — the set turns, not the subject.

`_dressing()` builds a full kit around the flower — softbox on a stand, C-stand with a
flag, fresnel with barn doors, a boom carrying the Act I lamp itself, a tripod with a
second camera looking back, apple boxes and a slate, a reflector, a hanging roll of paper,
a stool and a sandbag, cables, floor tape, and the card the ink look's caption sits on —
all built once in `_studio()`, all `hide_render=True` until the room is lit, matching every
other studio asset's contract.

**Gotchas from this pass:**

- **A generic "beam returns" camera position was overwriting every look's own framing,
  every frame, for the whole collapse — not just the last one.** The comment said "over the
  last look"; the code ran unconditionally. Grid, collage, ink and painted each place their
  word for THEIR OWN camera, and all four were rendering from one fixed fallback position
  instead — which is a real, worse version of "the words are hard to see" than any sizing
  issue. Gated to `if li == 0` (the actual last span) and blended from wherever that look's
  own camera already was.
- **A tiny floor mark can be a bigger on-screen problem than a huge one.** A 14×2 cm tape
  T-mark placed right by the jar looked harmless at the distances every OTHER shot uses —
  and then REVEAL's opening pull-back starts almost on top of the just-landed petal, close
  enough that the mark filled the frame as a huge soft diagonal bar. Distance to camera
  matters more than an object's absolute size; the kit is now hidden entirely until REVEAL
  ends and the wide is actually established, and nothing is placed inside the radius that
  opening shot passes through.
- **A camera standing on the R-frame's own axis (local x=0) makes "place the word at local
  (0, y, z)" centre it for free; a camera dollying off that axis does not.** The strobe and
  most looks sit at local x=0 and look straight down their own y-axis, so any word at
  local x=0 lands centre-frame at every az. Painted's camera carries a persistent x-offset
  (0.30→0.18) while still `aim_at`-ing the flower head off that axis, and the same trick put
  a word's centre at ndc.x≈1.0 — off the right edge — at the closest push-in. The fix is
  geometric, not a bigger safety margin: place the word ON THE CAMERA'S OWN RAY through the
  aim point (`camv + k*(H-camv)`), which is centre-frame by construction for *any* camera
  offset, because `aim_at` already points the lens at every point on that line.
- **Measure on-screen extent with `world_to_camera_view`, not by eye at a 480 px preview** —
  the collage word overflowed the right edge by 10% of frame width and read as "mak" with an
  ‘e’ ghosting off-screen at a glance; the number (`ndc.x` to 1.10) made it unambiguous and
  gave a real target to fit back inside.
- **That same measurement is unreliable near the edge of the lens's own view cone.** A
  bounding-box NDC sweep flagged cables and floor kit at width > 1.0 — apparently spanning
  more than the whole frame — for objects that, rendered, are a thin stand leg politely
  visible at a corner. A point near 90° off the camera's forward axis is where perspective
  projection blows up, and a small object straddling that boundary produces a huge, mostly
  meaningless bounding box. The words (near frame centre, never near that boundary) are
  where this check is trustworthy; anything peripheral has to be judged by an actual render.
- **`ALLFIVE` clears `self.words` but there is now a second dict.** Painted's word a phone
  can read lives in `self.words_big`, added after the strobe's own clearing loop was
  written — so `alive,` kept showing, off-centre, under the strobing `alive?` until that
  loop was updated to clear both dicts. Any state that lives outside the one dict the
  original contract clears is state a later look can inherit.
- **Bezier handles on procedural geometry: prefer `VECTOR` to `AUTO`.** `AUTO` solves a
  smooth tangent from neighbouring points and can overshoot badly on a sparse, non-collinear
  run — cosmetic on paper, but this is exactly the kind of thing the peripheral NDC check
  above can't be trusted to catch, so `VECTOR` (straight segments, never overshoot) is the
  safer default for anything procedural and unreviewed by eye.
- **Check every word at 390 px, and check it against the flower, not the frame.** The
  strobe's `alive?` was in frame, in front of the crossing `how`, at the right size — and
  invisible for all eight beats, because at head height the flower hides the middle of a
  0.32 m word and only an `a` and a `?` poked out of the petals. It now sits below the head,
  behind the stem, at 88% of the frame width, and every look's own word is parked while it
  holds (rust `how` behind a rust `alive?` ate its baseline). The ink caption at any
  single-line size a phone can read ran under the stem and lost its last word; it is two
  lines, like a museum label. The test is `render_plant.py --res 390 --times …` on the type
  moments (`bt(51)`, `bt(55)`, `bt(57)`, `bt(70.5)`), not a still at 1080.

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

The clips also butt with nothing to trim: Act I runs `bt(0)`-`bt(32)` and ends on a
sixteenth of black; `video.html`'s local time 0 IS `bt(32)`, the frame the shutter opens on.

**Assembling the two acts.** They are rendered at different sizes and different rates, so
each is conformed separately and then concatenated — never filtered together:

```sh
FF=$(python3 -c "import imageio_ffmpeg;print(imageio_ffmpeg.get_ffmpeg_exe())")
# Act I: 540x960 at 24 -> 1080x1920 at 30, blended (it has no rendered motion blur)
$FF -y -framerate 24 -i outputs/plant_hi/f%05d.png \
  -vf "scale=1080:1920:flags=lanczos,framerate=fps=30:interp_start=0:interp_end=255,\
noise=alls=2:allf=t+u,setsar=1,format=yuv420p" -t 15.36 \
  -c:v libx264 -profile:v high -crf 16 -preset slow act1.mp4
# Act II: 1080x1920 at 120 -> the house 270-degree shutter -> 30
$FF -y -framerate 120 -i source/frames120/f%05d.png \
  -filter_complex "[0:v]tmix=frames=3:weights='1 2 1',fps=30,noise=alls=2:allf=t+u,\
setsar=1,format=yuv420p[v]" -map "[v]" \
  -c:v libx264 -profile:v high -crf 16 -preset slow act2.mp4
$FF -y -f concat -safe 0 -i list.txt -c copy outputs/it-isnt-moving-yet.mp4
```

`setsar=1` on **both** legs or `concat` refuses them (a scaled leg comes out 1600:1599 and
an unscaled one 0:1). `framerate=` rather than `fps=` on Act I: `fps` duplicates frames and
a 24→30 pulldown judders on the camera arc, where `framerate` blends and stands in for the
motion blur Cycles was not asked to compute. The grain is applied to **both** legs at the
same strength — a clean 3D leg butting a grained 2D one is a visible change of stock at the
one cut the film exists to hide.

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
