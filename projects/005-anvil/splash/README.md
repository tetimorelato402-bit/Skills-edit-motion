# The launch animation

The anvil, arriving. Replaces the splash in the TestFlight build.

| | |
|---|---|
| `splash.html` | The animation. One deterministic `renderFrame(t)` draws every frame. |
| `render.py` | Screenshots it at 393 × 852 CSS px, deviceScaleFactor 3 → 1179 × 2556. |
| `AnvilSplash.swift` | The same thing in SwiftUI, to drop into the app. |
| `anvil-splash.mp4` | The reference render, 1.45 s. |
| `anvil-splash-compare.mp4` | Side by side with the TestFlight recording. |

```sh
python3 render.py --out frames --fps 120
FF=$(python3 -c "import imageio_ffmpeg;print(imageio_ffmpeg.get_ffmpeg_exe())")
"$FF" -y -framerate 120 -i frames/f%05d.png \
  -filter_complex "[0:v]tmix=frames=2:weights='1 1',fps=60,pad=1180:2556:0:0:color=0xE3DACD,format=yuv420p[v]" \
  -map "[v]" -c:v libx264 -profile:v high -crf 16 -preset slow -movflags +faststart anvil-splash.mp4
```

1179 is odd, and h264 in yuv420p will not take an odd width — hence the one-pixel
pad, which also makes the output exactly the size a screen recording of the
device is, so the two can be stacked without scaling either.

## The mark is traced, not drawn

The silhouette is the real logo. The artwork was read by scanline at 1 % of its
height and the half-width recorded; the seven entries in `PROF` are the points
where that half-width steps or changes slope. Everything between them is
straight, because in the artwork it is.

```
plate taper  0.4971 → 0.3480   over y 0 → 0.295
OVERHANG     steps in to 0.1579          at y 0.295
waist        0.1579 straight    to y 0.605
base flare   0.1579 → 0.2485    to y 0.940
FOOT         steps in to 0.0936          at y 0.940
```

The rendered resting frame was measured back against those numbers: **worst
edge error 1.7 px in 545, 0.31 %.** At rest the solid is face-on, so the only
thing on screen is its front cap — which is the logo, not an approximation of it
that would have to be cross-faded to the real one.

## What was wrong, and what each fix is

1. **It arrived at an angle the anvil cannot survive.** Past about 40° of yaw
   this mark loses its silhouette — it is a wide, flat object, so edge-on it is
   a sliver, and for the first half of the old animation it read as a boot. The
   turn now starts at 34° and the shape is legible on frame one. A logo
   animation that begins unrecognisable has spent its only asset.
2. **Nothing had weight.** It rotated in place, which is a sticker being skewed.
   An anvil is the heaviest object in any room it is in, so this one **falls**,
   lands, and compresses on the frame it lands. The idea of the mark, performed
   rather than decorated.
3. **The fall accelerates.** This is the fix that matters most. An out-curve
   decelerates into the landing, so the mark is already standing still before it
   arrives and the impact has nothing to absorb. Gravity is `u²` — it is moving
   at its fastest on the frame it lands.
4. **The turn is linear, and the floor stops it.** Nothing slows a spin in
   mid-air. An eased rotation left the mark square a tenth of a second before
   touchdown, which is two events — a turn, then a drop — when the whole point
   is that it is one. Constant angular velocity, cut dead at `T_LAND`.
5. **It was slow.** 2.95 s of logo before the app appeared. This is **1.45 s**,
   and it is doing more. There is no fade in either: iOS has already run its own
   app-open zoom to get here, and a second transition on top of it is the thing
   that makes a launch feel slow.
6. **The text is gone.** No wordmark, no tagline. Losing the wordmark removes
   what was *under* the mark; it does not move the mark, which still sits at
   0.455 of the screen height and still measures 176 pt wide.

## The sparks are gone, and that was a decision

The original had them. The first pass here rebuilt them properly — off the base
rather than off the top, because this anvil is *landing* and not being *struck*,
and sideways as streaks rather than falling as confetti. At phone size fourteen
gold scratches under the mark still read as dirt on the lens rather than as
force. The impact is now carried by the two things that are actually the object:
it **compresses about its foot**, and a **shadow snaps in underneath** and then
leaves, so what is left at the end is the logo on a bone page with nothing under
it. Putting them back is about ten lines; the git history has the version.

## Numbers

| | |
|---|---|
| logo width | 176 pt |
| centre | 0.455 × screen height |
| extrusion depth | 0.260 × width |
| camera | 3.4 width-units |
| yaw / pitch / roll | −34° / −16° / −4° → 0 |
| drop | 76 pt |
| scale | 1.075 → 1.00 |
| land | 0.44 s |
| compression | to 0.955 of height, about the foot, out by 0.60 s |
| hold | 0.60 → 1.05 s |
| hand over | 1.05 → 1.35 s |
| total | 1.45 s |

Pitch is **negative**, which tips the top toward the camera. Positive tips it
away and puts the viewer underneath looking up at the base — the one angle where
the plate, the most recognisable thing about the mark, is hidden.

## Gotchas paid for

- **Wall quads must be wound `F,B,B,F` and not `F,F,B,B`.** `OUT` runs down the
  right side and back up the left, and model y increases downward, so the front
  cap has a +z normal — which means the obvious wall order gives every side an
  **inward** normal. It culls exactly the wrong half of the solid and shades
  what survives from the wrong side. Nothing errors; it comes back as a mangled
  silhouette.
- **Tag the front cap, never infer it.** Testing `normal.z > 0.999` only holds at
  identity rotation, so for the whole of the fall the logo was being painted in
  the wall colour and the mark turned gold mid-air.
- **The walls have to separate from the face.** Run ink → gold, not ink → a
  slightly lighter ink. A first pass had every wall within a few values of the
  front cap and the solid read as a flat shape being skewed — the exact failure
  the extrusion exists to avoid.
- **Depth is 0.26 of the width, not 0.15.** An anvil is a deep object. At 0.15
  the side wall projected to about 8 % of the mark and the turn still read as a
  skew.
- **Painter's algorithm, not culling alone.** This profile is concave at the
  overhang and at the foot, so culling by itself lets the plate's underside
  paint over the waist.

## Porting notes

`AnvilSplash.swift` is a line-for-line port — same profile, same constants, same
curves — so `anvil-splash.mp4` is what it draws rather than an impression of it.
It is written against the artboard in `005-anvil/source/screens.html`, so every
number above is a number you can type in without scaling anything.

It draws into a `Canvas` and **not** `rotation3DEffect`, which takes a flat view
and skews it in perspective — a sticker turning, and precisely the thing being
fixed. Reduce Motion gets the mark, held, and the same handover: a splash is not
worth a vestibular problem, and a logo that simply *is* there is a perfectly good
splash.

It has not been through a Swift compiler — there is no toolchain in this
container — so treat the first build as a proofread.
