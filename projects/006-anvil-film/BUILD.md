# Building the Anvil film

Everything is code. There is no NLE project and no timeline to open.

| file | what it is |
|---|---|
| `source/video.html` | The whole film. One deterministic `window.renderFrame(t)` positions every element for time `t`. No CSS animations — they are wall-clock based and would not render reproducibly. |
| `source/render.py` | Drives headless Chromium via Playwright, calling `renderFrame(i/fps)` and screenshotting each frame. |
| `sound.py` | The whole soundtrack, synthesised. Every cue is a motion in the film, derived from the same 120 BPM grid. |
| `scripts/check-sync.py` | Proves `sound.py` and `video.html` are still cut to the same grid. |
| `scripts/fillplate.py` | Builds `source/ui/fill.png`, the duotone plate that fills the type. |

## Rebuild

```sh
python3 scripts/check-sync.py                       # must pass before anything else
python3 sound.py                                    # 2 s -> anvil.wav
python3 source/render.py --out source/frames --fps 60    # 53 s, 840 frames

FF=$(python3 -c "import imageio_ffmpeg;print(imageio_ffmpeg.get_ffmpeg_exe())")
"$FF" -y -framerate 60 -i source/frames/f%05d.png -i anvil.wav \
  -filter_complex "[0:v]tmix=frames=2:weights='1 1',fps=30,format=yuv420p[v]" \
  -map "[v]" -map 1:a -c:v libx264 -profile:v high -crf 17 -preset slow \
  -c:a aac -b:a 256k -movflags +faststart -shortest anvil-v4.mp4
```

Rendering at 60 and averaging pairs down to 30 is what produces the motion blur — a real
**180° shutter**, not a blur filter. Do not shortcut it to 30 fps: every hard cut in this
film would then land with no shutter at all.

Preview instead of rendering the film while iterating:

```sh
python3 source/render.py --out source/pv --times 2.70,7.82,9.02,9.95,10.90,13.40
python3 source/render.py --start 560 --end 640      # re-render a range in place
```

**A sound change is a remux, not a render:**

```sh
"$FF" -i anvil-v4.mp4 -i anvil.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 256k \
  -movflags +faststart -shortest out.mp4
```

## Delivery targets

- **1080×1920, 30 fps, 14.0 s.**
- **−14.3 LUFS integrated, −1.7 dBFS true peak.** Reels normalise to about −14, and true
  peak must stay under −1 dB or the AAC encode clips the transients. Check with
  `"$FF" -i anvil-v4.mp4 -af ebur128=peak=true -f null -`.
- **No grain.** Adding 001's `noise=alls=2` costs 5 MB and softens a film whose brief is
  *crisp*. Grain belongs to the painted world, not to this one.

## Assets

`source/screens/` holds nine full screens of the app at 590×1279. **The film no longer
draws any of them** — rule 4 retired the whole-phone shots — but they are where the proof
photographs in `source/ui/` were cropped from, and where every word on the UI cards was
read off. They are provenance, not payload; delete them and the next person has no way to
check that a card is quoting the product rather than inventing it.

`source/ui/fill.png` is generated — `python3 scripts/fillplate.py` — and the three
`proof_*.png` beside it are hand crops of the check-in photographs.

## Gotchas already paid for — do not rediscover these

- **A `<div>` is block-level, so measuring a line returns the container's width.** The
  auto-fit measured line boxes and got 4000 px every time, so every page fitted to 23 px —
  with no error anywhere. Fit measures the sum of the **inline spans**.
- **Never fire the negative on a rust flash frame.** `mix-blend-mode: difference` against
  warm white turns rust into teal, so bone tinted 24 % rust inverted to a flat green
  (measured `(46,53,43)`; clean bone gives `(28,15,2)`). Two edits that are each correct
  can compose into a colour that belongs to neither.
- **Subtracting a global mean writes DC into the silence.** `out -= out.mean()` put a
  −53 dBFS constant into the one place the film has to be a hole (absmax == mean, so it
  was a flat line). `dcblock()` is a centred box high-pass: zero in, zero out.
- **Chasing the limiter ceiling down made the delivered true peak WORSE.** The figure being
  measured was the AAC's quantisation noise on near-Nyquist click energy, not the mix.
  A 15 kHz roof (`lowpass()`) fixed the cause, and the same master then measured 2.6 LU
  louder *and* 3 dB safer. Tune the ceiling against the delivered **mp4**, never the wav.
- **A list name can shadow a constant silently.** `BARS` was the film's length in bars
  before it was reassigned to the letterbox times. `DUR` had already been computed so
  nothing rendered wrong — only the log lied. Same failure as 001's `B2`.
- **`document.fonts.ready` resolves without a face that nothing has used yet.** A typeface
  first set at second 9 is still swapping in when it is screenshotted. `render.py` calls
  `document.fonts.load()` for every family by name, and `video.html` also carries a hidden
  warm-up node — belt and braces, because the failure is a silent fallback.
- **Check the whole timeline for JS errors before committing to a render.** Driving
  `renderFrame` across all 840 frames in a headless page takes under a second and catches
  a throw that a preview still would miss.
- **Palette constants must be declared at the top of the file.** The type is built before
  the distraction layer, so a `const` declared down there is in the temporal dead zone when
  the instruction line asks for `INK` — and the file then fails to define `renderFrame` at
  all, which looks exactly like a render hang rather than like an error.
- **An `<img>` assigned mid-render paints nothing on the frame it appears on.** `render.py`
  decodes every photo explicitly before the first screenshot; a cut landing on a
  half-decoded image is invisible in the log.
- **Pills have no corner to crop against.** Bleeding a rounded chip off the frame edge
  slices the VERIFIED diamond in half and reads as a mistake rather than as a crop; those
  cards are held to the slots that sit inside the frame.
- **A page turn is not a place to put another edit.** `GO+4.5` was carrying a letterbox
  slam, a zoom punch, the photo-in-type and a new page at once, which is not four edits,
  it is one mess. Density late in the film is the design; density on a page turn is noise.
