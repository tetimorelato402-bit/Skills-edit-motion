# ANVIL — animated product walkthrough

A ~26 s vector walkthrough built from the 15 production SVG screens and the
supplied voiceover. Screens stay SVG end to end — they are inlined into the
DOM and rasterised only by the renderer, at whatever resolution you ask for.

**Complete.** 26.25 s, five acts and the silent ending.
`03_onboard_birthday` is cut: birthday entry is compliance, not product.

## Layout

```
assets/screens/     the 15 source SVGs, untouched
assets/audio/       the source VO and anvil clang, untouched
assets/fonts/       Fraunces / Inter / DM Mono, vendored for offline renders
audio/              derived: vo_trimmed.wav (the working master), clang.wav,
                    room.wav (generated), mix.wav (the film's whole bed)
                    onset-map.md — the trim, the onsets, the line assignment
src/motion.ts       easing and the six primitives. No timings.
src/timeline.ts     the film as declarative beats. ALL timings.
src/stage.ts        builds the DOM, maps a time to a picture. No clock.
scripts/            build, preview server, renderer, mix, onset detection,
                    checkSync.mjs — proves the sync rule against the timeline
build/              generated — bundles, tagged SVGs, stills
out/                rendered MP4s
```

## Preview

```bash
npm run build
node scripts/mix.mjs          # builds audio/mix.wav — needed by preview and render
node scripts/serve.mjs        # → http://127.0.0.1:5173/build/preview.html
```

Space plays against the real mix; ← → step one frame; the buttons under the
scrubber jump to a section (`full`, `act1`, `act23`, `act45`, `end`).

## Render

```bash
node scripts/mix.mjs
node scripts/render.mjs                                    # the whole film, 1080p
node scripts/render.mjs --height 2160 --out anvil-4k       # 4K
node scripts/render.mjs --from 12.9 --to 14.5 --out unlock # one beat
```

| flag | default | notes |
|---|---|---|
| `--from` `--to` | `0` `26.25` | seconds on the film clock |
| `--fps` | `30` | |
| `--height` | `1080` | `720`, `1440`, `2160` all work — the stage is scaled, not upsampled, so the SVGs re-rasterise sharp at every size |
| `--out` | `anvil` | writes `out/<name>.mp4` |

Rendering is deterministic: the page exposes `setTime(t)` and holds no clock
of its own, so frame *n* is identical on every run and on every machine.

## Sound

The mix is dry: voice, one anvil strike, and room tone. No music. Anything
else would be decorating a film whose argument is that proof does not need
decorating.

`scripts/mix.mjs` assembles the whole bed once, so picture and sound share
one clock and the renderer only ever slices it:

| layer | level | notes |
|---|---|---|
| VO | 0 dB, master reference | placed at `VO_AT`; never stretched, pitched or ducked |
| anvil clang | −1 dB, on the unlock | sits on top, never ducked |
| room tone | −46 dBFS | generated, not sampled — see below |

The film has long silences by design, and digital zero does not read as
quiet, it reads as playback having stopped. `scripts/roomtone.py` generates
a pink-noise floor band-limited to roughly 45 Hz–3.5 kHz, seeded so it is
identical on every render. It is audible as texture in the gaps and gone
under speech, and it fades out with the picture rather than after it.

## Retiming

Every absolute time in the film is derived, in `src/timeline.ts`, from two
things: the measured VO onsets in `VO`, and `LEAD` (how long a screen is
settled before its line starts). Nothing downstream hard-codes a time.

- **The voice changed.** Re-run `python3 scripts/onsets.py audio/vo_trimmed.wav
  audio/onsets.json`, then `python3 scripts/linemap.py`, and paste the new
  onsets into `VO`. Every beat moves with them.
- **A beat feels rushed.** Change its duration constant (`HOME_IN`, `CROSS`,
  `PUSH`, `TOAST_IN`, `SHACKLE`, `UNLOCK`). Entrances are computed backwards
  from the line they serve, so a longer entrance starts earlier — it never
  pushes into the narration.
- **The whole film should breathe more.** Raise `LEAD`.
- **The film needs a longer head.** Raise `VO_AT`; the whole voice track moves
  with it, because `scripts/mix.mjs` reads the same constant.

Run `node scripts/checkSync.mjs` after any retime. It reads the built
timeline — not a copy of the numbers — and fails if any screen carrying a
line settles less than `LEAD` before it. It also prints every pair of moves
that overlap, so an accidental second animation in a beat shows up as a
line of output rather than as something you have to catch by eye.

## Motion system

One easing everywhere: `cubic-bezier(0.22, 1, 0.36, 1)`. Nothing is linear,
including opacity ramps — a linear fade is what turns a dissolve into a
double exposure.

The one documented exception is `easeCamera`, `cubic-bezier(0.42, 0, 0.22, 1)`.
The primary curve spends 40 % of its travel in the first 15 % of its time,
which is right for UI response and wrong for a camera: on a 0.4 s dolly it
reads as a snap. The camera curve leaves slowly, carries, and settles long.

| primitive | behaviour |
|---|---|
| `settleIn` | enters at 1.04, settles to 1.0 through a slight overshoot |
| `revealUp` | mask reveal with the content travelling into it; `from: "above"` for banners |
| `crossDepth` | outgoing recedes in z, incoming comes forward and covers fast |
| `focusPush` | the camera moves into a region; the screen does not move |
| `holdBeat` | stillness with a duration, so retiming preserves it |
| `stagger` | children 80 ms apart |
| `recede` | a layer leaves with nothing replacing it |
| `apertureOpen` | used once, on the unlock |

`crossDepth`'s outgoing half is tuned to vanish under something covering it,
so it blinks out in a fifth of its beat. `recede` exists because the ending
has nothing to cover it with and needs the screen to drift away instead.

`apertureOpen` is the film's one bespoke gesture: on the unlock the incoming
viewfinder is revealed by a circle growing from the lock's own centre rather
than by a fade. The padlock is the first thing the circle consumes and the
viewfinder ring is the first thing it reveals — the same coordinates, one
continuous opening. A dissolve there cross-faded a light card into a dark one
and went grey through the middle.

`holdBeat` is written into the timeline as a real beat rather than left as
whatever gap the neighbouring beats happen to leave. Holds survive retiming.

## The shape

| act | screens | what the motion is doing |
|---|---|---|
| 1 — setup | 01, 02, 04, 05 | quick and light; 0.18–0.32 s cuts. The one `stagger` in the film lights the three chosen commitments under their own line. |
| 2 — the constraint | 06, 07 | the film slows and then stops. 3.10 s on the locked screen — the longest single-screen dwell — with 0.81 s of absolute stillness at full push. |
| 3 — the unlock | 08 banner, 09 | the release runs in the 0.826 s of silence after the line: the shackle lifts alone, then the viewfinder opens out of the lock while the camera pulls back. "Then it opens." lands on the aftermath. |
| 4 — the loop | 11, 10 | 0.24 s and 0.20 s. Seven frames and six. No breath anywhere. |
| 5 — the long game | 07_tab_routine | one cut, then 2.14 s still under the last line. |
| ending | — | silent. The screen recedes, the beige holds empty, the mark forms, ANVIL settles beside it, the tagline arrives, and the frame goes to ink. |

Act 2 and Act 4 are the film's whole argument in its rhythm: the longest
hold, then the fastest cuts. The tightness of Act 4 is not a compromise
forced by the voice — it is what the product does.

## What is not here

- **No music.** By decision, not omission — see **Sound**.
- **`03_onboard_birthday`** is cut.
- **`07_tab_circle` and `12_notification`** are unused. `12_notification`
  reads "Joe arrived at the gym", which belongs to Act 4's friend beat, but
  Act 4 is cut too fast to carry a floating overlay as well.
- **`08_arrival_toast`'s body** is unused; only its banner is. The asset's
  screen is already unlocked, so playing it whole would kill the lock a
  second before "Then it opens." The banner rides over the still-locked 07.
