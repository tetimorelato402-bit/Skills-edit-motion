# The Room — a music visualiser

teti's first piece where **the sound drives the motion**, instead of the motion driving the
sound. Everything in `projects/001…003` is scored to a picture that was cut first. This is
the inverse, and that is the whole reason it exists.

It is a **fun project and page content**, not a study and not the offer. It should be
repeatable: the engine is pointed at a track, not written for one.

## The reference

teti brought two things: a photograph of a DJ set — fisheye, one amber lamp blowing out
behind the booth, a dark warm room, a crowd in silhouette — and **Cloonee, Prospa &
Tristan Henry, "Good Girl"** (Hellbent, 2026): **128 BPM, E minor**, bass-driven tech
house built on rolling low-end pressure.

The photograph is the look. The track is the clock.

## The rule that governs the export — the same one as 001

**The song is never burnt in.** Instagram licenses "Good Girl" only when it is added
inside the app; burning it into the MP4 risks a mute or a takedown and kills reach. The
export carries sound design only. The visual is built on a **128.000 BPM** grid so the
track locks to it when its start point is slid in the Reel editor, and stays locked —
both are metronomic, so even a 0.1 BPM error accumulates only ~15 ms over 30 s.

**The alignment instruction is one line: put the song's drop at 16.9 s.**

A tighter option stays open: if teti supplies the audio file, `analyse.py` turns it into
per-frame band energies and onsets and the room rides the actual record rather than the
grid. The export is still silent of it.

## The structure — 16 bars, 30.0 s exactly

A club visual is episodic by form: it changes every eight bars. That is what lets all five
of the directions teti chose live in one piece instead of fighting.

| Bars | Time | Section | What it is |
|---|---|---|---|
| 1–3 | 0.00–5.63 | **Booth** | fisheye on the CDJs, jog wheels turning, cue lights on the beat |
| 4–7 | 5.63–13.13 | **The room** | the wide room — haze, crowd, one amber lamp, camera shaking on the kick |
| 8–9 | 13.13–16.88 | **Specimen** | the annotation layer labels the build: SUB · KICK · RISER |
| 10–13 | 16.88–24.38 | **Drop → paint** | paint erupts from the lamp and the room is painted over, a stroke per kick |
| 14–16 | 24.38–30.00 | **Waveform** | the paint resolves into the waveform as architecture, and the camera flies down it |

## Load-bearing

- **WebGL 2 runs in this container** and a raymarched room with a real fisheye renders at
  **0.30 s/frame at 1080×1920** — 2.6× faster than 001's DOM engine. This is why the room
  is a shader and not CSS 3D. `renderFrame(t)` keeps the same contract as 001 and 003.
- **The fisheye is a lens, not a filter.** The barrel is applied to the ray direction
  before marching, so straight edges bend correctly and nothing is resampled. Post-warping
  a rectilinear render would soften the frame and crawl.
- **The palette is teti's, warm-family, and the reference photo is already in it.** Amber
  lamp, umber walls, oxblood accents. The one sanctioned exception is the paint section,
  which may use the 001 signal colour at full strength.
- **The camera shakes on the kick, the lens breathes on the sub.** Two separate channels,
  because shaking on everything reads as noise.

## Open

1. Which 30 s of the track — teti picks the section; the visual's drop is at 16.9 s.
2. Whether the specimen annotations earn their place, judged once the room exists.
