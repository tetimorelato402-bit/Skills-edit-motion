# Study 001 — how to finish and post

**Post `study-001-v10.mp4`** — 21.2s, 1080×1920, H.264, with its **complete soundtrack**
burnt in: a house beat, and every motion in the film cut to it. There is no music to add in
Instagram. **Note the runtime: 21.2s, not 19.2** — the film was re-cut to whole bars.
`study-001-v10-afro.mp4` is the same picture with an Afro House beat instead — an alternate
take, teti's call which one ships. `study-001-v4-painted.mp4` is kept as the earlier painted
cut; older versions are in git history.

Swap the beat without re-rendering: `python3 sound.py --afro`, then remux (see `../../CLAUDE.md`).

v10 is the film re-cut to a house beat, in the temperament of Kungs' "I Feel So Bad" feat.
Ephemerals (123 BPM, A minor) — teti's reference. It runs at 125 BPM, the same room, because
125 divides the film exactly: a beat is 0.48s, a bar 1.92s, and the film is eleven bars.

This is not a re-score. The picture was re-timed and re-rendered so that every motion in
focus lands on the beat: the caret blinks on the beat; MOTION falls on 2 and lands on 3; each
of the three studies gets a bar, the spacing chart drops a mark on every sixteenth, the ball
contacts on 2 and taps on 4, the seven bars stagger up the eighths; the setup plays one move
per beat — click, keyframe, keyframe, grab — and the ease is dragged onto the downbeat of bar
7, which is the drop, where the post comes apart and its five layers snap home on the
eighths; the hero line arrives one line per beat with MOVE. home on the next downbeat; the
type cycle plays sixteenths and lands on Inter on the last downbeat; MOVE. slides out on 3
and springs home on 4. Under that: four on the floor, clap on 2 and 4, offbeat open hats, an
A-minor bass vamp and a two-bar pluck riff, with the arrangement built to the film — bar 1 is
the intro, bar 6 empties out as the build, bar 7 is the drop, and the last bars thin to the
final hit before the loop.

v9 had made a five-note run into a hook; that and the jazz bed under v8 were both rejected.

v8 added the jazz bed teti asked for after hearing v7, kept very low: an upright bass walking
the six bars in quarter notes with three chromatic pickups, a Rhodes comping rootless jazz
voicings (Dm9, Gm9, C9, Bbmaj9, Em7b5, A7b9, Dm6/9) on pushed beats, brushes through the hero
line, and a soft ride marking the quarters while the hats moved onto the swung skip — so the
beat swings with the bed instead of fighting it. The harmony is one descending line home
(Dm — Gm — C — Bb — A7 — Dm) and the V resolves to the i on the downbeat of bar 4, which is
09.6: the bend now lands on a chord change, not just a beat.

v7 was the v6 picture with a new soundtrack. teti retired the licensed track, so the film now
carries its own score, synthesised in `sound.py`: a 75 BPM beat (the film turned out to be
exactly six bars — the cuts land a pushed sixteenth after the quarter, the same push every
time) and a sound for every motion — the caret, the grain of the dissolve, the brush of the
wipe, fifteen spacing ticks pitched by the head's speed, the ball's squash, the seven-note
stagger, the keyframes dropping, the layers snapping home, a felt hammer for every letter of
the hero line, a shutter for every typeface the name tries on, and a synth bend whose pitch
follows the exact ease being dragged from 09.32 to 09.96. Nothing is licensed, so the file
plays the same everywhere — Instagram, a portfolio site, a client send.

v6 added the signature and the transitions: "teti." cycles through eleven typefaces and
resolves into the circular portrait that is the profile picture, so film and profile share
one mark; STILL. breaks up into the study title through the tooth of the canvas (a grain
dissolve, not a fade); and the ochre band is revealed by a loaded brush dragged across the
frame (a paint wipe). Beat timings are unchanged — the bend still lands at 09.6.

v5 made the film perform the craft instead of naming it: three principles
played full-frame (a real spacing chart, a weight study with squash and
follow-through, a stagger), the dead post coming apart into its layers in 3D and
rebuilding with overshoot, per-character kinetic type on the payoff line, a
seamless loop, and the end card's joke — the cursor returns and MOVE. moves.

v4 rebuilt the film as a painted object — oil grounds with lit impasto,
linen weave through the whole frame, and hand-painted type edges (`source/paint.py`).
The generic brand post stays crisp and cold on purpose: a digital thing collaged
onto canvas. Earlier cuts (v2 blue, v3 flat warm, v5) are in git history.

v3 recoloured the film to the studio palette drawn from teti's oil portrait
(see `../../brand/PALETTE.md`): oxblood accents, an ochre specimen band, parchment
type on warm near-black. The generic brand post stays cold grey on purpose.

v2 added: synthesised sound design (`sound.py` — every hit is frame-exact), real 270° motion
blur (rendered at 120fps, shutter-averaged down to 30), light film grain, and two match cuts —
the specimen band folds into the graph panel at 8.2s, and the ease curve you drag grows out
of the editor to fill the frame at 12.2s.
Source of truth is `source/video.html` — the whole film is code; `source/render.py` turns it into frames.

## 1. Sound — there is nothing to add

The soundtrack is in the file. Do **not** add a track in the Reel editor: the film's beat is
its own, and anything Instagram lays over it will fight the 75 BPM grid.

1. New Reel → upload `study-001-v10.mp4`.
2. If the editor suggests audio, decline it. In the mixer, **original audio at 100%**, no music.
3. Leave the volume alone — the mix sits at −14.3 LUFS, which is where Instagram normalises.
4. Check on the phone speaker before posting: the beat landing at 01.9, the ball's contact at
   06.2 and the drop at 11.5 should all read without headphones. The intro (00.0–01.9) is
   deliberately near-empty — a filtered kick on 1 and 3, and the caret.
5. If a beat is ever re-timed, re-run `sound.py` (cue times follow the film) and remux — see
   `../../CLAUDE.md`. The picture does not need re-rendering for a sound change.

## 2. Cover

Use `study-001-v10-cover.png` (the first frame — "STILL." with the selection handles). It reads as
intentional, not broken, and it is the reason someone stops.

## 3. Caption

First line does the work (it is the second hook):

> Someone has to decide how things move.
>
> Study 001 — the anatomy of motion: timing, spacing, easing, weight, rhythm.
> New study every week.
>
> I'm teti, a motion editor — I decide how things move.

Hashtag bridge (the title "motion editor" is not the searched term, so bridge to the ones that are):
`#motiondesign #motiongraphics #animation #graphicdesign #davinciresolve #motiondesigner #kineticstype`

## 4. If you want changes

Everything is parametric — say the word and it re-renders in ~3 minutes:

| Change | Where |
|---|---|
| Signal colour | `--signal` in `video.html` `:root`, or `render.py --signal "#C6F000"` |
| Any wording | the `el(...)` text argument for that beat |
| Beat lengths | the `B1…B6` arrays at the top of the script |
| Runtime | change the beat arrays; frames = 30 × duration |
| Any sound | `sound.py` — instruments at the top, the beat and every motion cue below; re-run and remux, no re-render |

Re-render: the exact commands are in `../../CLAUDE.md` (render at 120 fps, shutter-average
down to 30 — that is where the motion blur comes from, so do not shortcut it).

## 5. Taking it into DaVinci Resolve instead

The MP4 is post-ready as is. If you'd rather finish it yourself in Resolve:

- Import `study-001-v10.mp4` as a base layer and work on top — it's a clean 1080×1920 30p H.264.
- Or rebuild any single beat in Fusion following `BUILD.md`, and cut it against the rendered version.
- The beat most worth re-shooting yourself is **beat 4 (08.2–12.2s)**: a real screen recording of you
  dragging a real ease curve in Resolve's Spline editor is more honest than the simulated UI here,
  and it is literally footage of you doing the job. Swap it in and the video gets stronger.

## Beat map (for trimming and alignment)

| Beat | Bars | In | Out | What |
|---|---|---|---|---|
| 1 | 1 | 00.00 | 01.92 | STILL. — the cover frame; the caret blinks on the beat; grain-dissolves out |
| 2 | 2 | 01.92 | 03.84 | Study title; MOTION falls on 2, **lands on 3 (02.88)**; paint wipe out |
| 3 | 3–5 | 03.84 | 09.60 | The anatomy — one study per bar: spacing on sixteenths, weight contacting on 2 and 4, the stagger up the eighths |
| 4 | 6–7 | 09.60 | 13.44 | The editor's hand — one move per beat, **the drag lands on the drop (11.52)**, the layers snap home on the eighths |
| 5 | 8–9 | 13.44 | 17.28 | Someone has to decide how things move — one line per beat, **MOVE. home on 15.36** |
| 6 | 10–11 | 17.28 | 21.12 | teti. — the type cycle lands on Inter at 19.20, the mark opens, then MOVE. moves (out 20.16, home 20.64) |

125 BPM from frame 0: a beat is 0.48 s, a bar 1.92 s, and the film is eleven bars exactly, so
the loop point is a downbeat. Bar lines: 00.00, 01.92, 03.84, 05.76, 07.68, 09.60, 11.52,
13.44, 15.36, 17.28, 19.20. Every cut is on a downbeat and every landing is on a beat.
