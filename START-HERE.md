# Start here

This is the complete handoff for **teti studio — Study 001**, packaged so a Claude Code
session on the desktop can pick the work up with no explaining.

## The fastest path (recommended)

Everything here is already committed to the repo, so cloning gets you the same files
plus full history:

```sh
git clone https://github.com/tetimorelato402-bit/Skills-edit-motion.git
cd Skills-edit-motion
git checkout claude/motion-editors-video-concept-fz6opf
claude
```

Claude Code reads `CLAUDE.md` automatically on startup, so it arrives already knowing how
the film is built, the rules that are load-bearing, and the bugs already paid for. A good
opening line is simply: *"Read HANDOFF.md and let's start on Study 002."*

## If you'd rather not clone

Drop this folder wherever you keep the project, `cd` into it, and run `claude`. The layout
matches the repo, so every path in the docs resolves. You lose git history, nothing else.

## What's in here

| Path | What it is |
|---|---|
| `CLAUDE.md` | Auto-loaded context: how to rebuild the film, load-bearing rules, bugs already solved |
| `HANDOFF.md` | The story, what's still open, and a ranked roadmap of what to improve and create |
| `projects/001-why-motion-editors/BRIEF.md` | The creative brief, with rejected alternatives and why |
| `projects/001-why-motion-editors/POSTING.md` | How to post it: cover, caption, hashtags — and why nothing gets added for sound |
| `projects/001-why-motion-editors/BUILD.md` | Beat-by-beat build notes in DaVinci Resolve terms |
| `projects/001-why-motion-editors/source/` | **The film itself** — `video.html` is the whole thing, `render.py` renders it, `paint.py` makes the oil-paint textures |
| `projects/001-why-motion-editors/sound.py` + `.wav` | **The whole soundtrack** — a 75 BPM beat and a sound for every motion, synthesised from the film's own timings |
| `projects/001-why-motion-editors/resolve/` | Resolve scripting setup + a timeline builder (untested against a live Resolve) |
| `projects/001-why-motion-editors/study-001-v7.mp4` | **The finished film** — this is the one to post; its soundtrack is complete, add no music |
| `brand/PALETTE.md` | The colour system, extracted from the portrait |
| `brand/pfp/` | The eight profile-picture options; `opt1_portrait.png` is the one chosen and live |

## To rebuild the film

Needs Python with `playwright` and `pillow`, plus `ffmpeg`. From
`projects/001-why-motion-editors/`:

```sh
python3 source/render.py --out frames120 --fps 120     # ~30 min
ffmpeg -framerate 120 -i frames120/f%05d.png -i sound.wav \
  -filter_complex "[0:v]tmix=frames=3:weights='1 2 1',fps=30,noise=alls=2:allf=t+u,format=yuv420p[v]" \
  -map "[v]" -map 1:a -c:v libx264 -profile:v high -crf 17 -preset slow \
  -c:a aac -b:a 192k -movflags +faststart -shortest out.mp4
```

While iterating, render a few frames instead of all 2304:
`python3 source/render.py --out pv --times 4.9,9.7,14.6`

## The one thing still open

**Shoot the real Resolve capture for beat 4.** The curve editor at 8.2–12.2s is currently
simulated. A real screen recording of the Spline editor being dragged is the highest-value
upgrade left, and the only one that needs a human. (The profile picture is decided and live —
the portrait — and the film's end card resolves into it.)
