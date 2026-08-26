# ANVIL — animated product walkthrough

A ~26 s vector walkthrough built from the 15 production SVG screens and the
supplied voiceover. Screens stay SVG end to end — they are inlined into the
DOM and rasterised only by the renderer, at whatever resolution you ask for.

**Built so far: Act 2 (the constraint) and Act 3 (the unlock).**
Acts 1, 4, 5 and the silent ending are scaffolded in `src/timeline.ts` but
not yet authored.

## Layout

```
assets/screens/     the 15 source SVGs, untouched
assets/audio/       the source VO and anvil clang, untouched
assets/fonts/       Fraunces / Inter / DM Mono, vendored for offline renders
audio/              derived: vo_trimmed.wav (the working master), clang.wav
                    onset-map.md — the trim, the onsets, the line assignment
src/motion.ts       easing and the six primitives. No timings.
src/timeline.ts     the film as declarative beats. ALL timings.
src/stage.ts        builds the DOM, maps a time to a picture. No clock.
scripts/            build, preview server, renderer, onset detection
build/              generated — bundles, tagged SVGs, stills
out/                rendered MP4s
```

## Preview

```bash
npm run build
node scripts/serve.mjs        # → http://127.0.0.1:5173/build/preview.html
```

Space plays against the real voice; ← → step one frame; the scrubber covers
the section set in `SECTION.act23`.

## Render

```bash
node scripts/render.mjs --from 6.861 --to 13.90 --fps 30 --height 1080 --out act2-3
```

| flag | default | notes |
|---|---|---|
| `--from` `--to` | `0` `13.9` | seconds on the film clock (= trimmed-VO clock) |
| `--fps` | `30` | |
| `--height` | `1080` | `720`, `1440`, `2160` all work — the stage is scaled, not upsampled, so the SVGs re-rasterise sharp at every size |
| `--out` | `act2-3` | writes `out/<name>.mp4` |
| `--clang` | `11.904` | absolute time of the anvil strike |

Rendering is deterministic: the page exposes `setTime(t)` and holds no clock
of its own, so frame *n* is identical on every run and on every machine.

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
| `apertureOpen` | used once — see below |

`holdBeat` is written into the timeline as a real beat rather than left as
whatever gap the neighbouring beats happen to leave. Holds survive retiming.
