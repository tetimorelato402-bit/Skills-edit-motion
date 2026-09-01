# Study 001 — how to finish and post

**Post `study-001-v6.mp4`** — 19.2s, 1080×1920, H.264, with burnt-in **sound design**
(no music: that still gets added in Instagram). `study-001-v4-painted.mp4` is kept as the
earlier painted cut; older versions are in git history.

v6 adds the signature and the transitions: "teti." cycles through eleven typefaces and
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

## 1. Add the music inside Instagram (do not burn it in)

Instagram licenses "Parisienne Walkways" only when the track is added in the app. Burning it into
the export risks a mute or a takedown, and kills reach.

1. New Reel → upload `study-001-v6.mp4`.
2. Add audio → search **Parisienne Walkways (Gary Moore)** → studio version.
3. Slide the track's start so the **bend lands at 09.6s** — that is the exact frame where the cursor
   drags the ease curve and the dead frame comes alive. This one alignment is the whole point of the
   sound choice; everything else can be slightly off and it still works.
4. In the audio mixer, keep **original audio** up — that is the sound design (clicks,
   keyframe ticks, whooshes). Music around 70–80%, original around 40–50% is a good start.
5. Check on the phone before posting. If the bend can't reach 09.6s inside the app's trimmer, tell
   Claude and the beat can be re-timed to the track instead of the other way round.

## 2. Cover

Use `study-001-v6-cover.png` (the first frame — "STILL." with the selection handles). It reads as
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

Re-render: the exact commands are in `../../CLAUDE.md` (render at 120 fps, shutter-average
down to 30 — that is where the motion blur comes from, so do not shortcut it).

## 5. Taking it into DaVinci Resolve instead

The MP4 is post-ready as is. If you'd rather finish it yourself in Resolve:

- Import `study-001-v6.mp4` as a base layer and work on top — it's a clean 1080×1920 30p H.264.
- Or rebuild any single beat in Fusion following `BUILD.md`, and cut it against the rendered version.
- The beat most worth re-shooting yourself is **beat 4 (08.2–12.2s)**: a real screen recording of you
  dragging a real ease curve in Resolve's Spline editor is more honest than the simulated UI here,
  and it is literally footage of you doing the job. Swap it in and the video gets stronger.

## Beat map (for trimming and alignment)

| Beat | In | Out | What |
|---|---|---|---|
| 1 | 00.0 | 01.6 | STILL. — the frozen post (cover frame); grain-dissolves out |
| 2 | 01.6 | 04.2 | Study title, MOTION drops in; paint wipe out |
| 3 | 04.2 | 08.2 | The anatomy: timing, spacing, easing, weight, rhythm |
| 4 | 08.2 | 12.2 | The editor's hand — **bend lands 09.6** |
| 5 | 12.2 | 15.8 | Someone has to decide how things move. |
| 6 | 15.8 | 19.2 | teti. — type cycle → portrait mark, then MOVE. moves |
