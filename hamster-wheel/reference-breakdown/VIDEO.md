---
videomd: 1
name: ref
description: 'Relatable meme: friend calls at 3am with a business idea and you go from asleep to full CEO mode Made with (inferred): AI-generated video 99%, still image + pan/zoom 1%'
source:
  file: ref.mp4
  sha256: c436ca6ad57776ef2df954f2e88f9c74b30f7b14bf52ecfcc2eab0f1516bc42d
  duration: 28.533
  size: 720x976
  fps: 30.0
  aspect: '3:4'
shots: 16
lang: en
made_mix:
  ai_video: 0.9906
  still_motion: 0.0094
confidence: 0.719
readers:
- tools
- agent
open_questions: 4
generator:
  name: rea-video
  version: 0.1.0
---

# ref.mp4

**Verdict** (inferred): Mixed production: AI-generated video 99% + still image + pan/zoom 1%; overlays: animated sticker / GIF, static graphics (composited in code / an editor); cuts land on the music beat; audio: music 147.7BPM (to confirm, leaning stock library music) + 5 sound effects; packaging: stickers / GIFs ×4
**What it says**: Relatable meme: friend calls at 3am with a business idea and you go from asleep to full CEO mode
**Made with** (inferred, by duration): AI-generated video 99%, still image + pan/zoom 1%
**Remake**: 15 AI video shots → 4 generation units, 4 MiniMax H3 / H3 Max calls; still-image move / static frame 1 shot → rebuilt locally

## Next steps

- Remake: Capsule Cinema does the generation, assembly and checks. `rea-video remake <this dir>` hands over to it, does what can be done automatically and keeps the original elsewhere; `remake/status.md` says per shot what is left. Add incoming clips to `remake/mine.json` and run it again
- AI shots: prompts are in the generation units of `video/remake.md`; for automatic generation use Capsule Cinema: `scripts/remake_reference.py prepare <this dir>`, then `run <jobs.json> --dry-run` (paid: ask the user first)

## Open questions

- Shot #15 (27.9–28.2s): Tools say still image + pan/zoom, the image review says AI-generated video; on the AI / live-action axis the fusion follows the tools (ev…
- Shot #15 (27.9–28.2s): photo / image: real material or generated, to confirm
- No AI listened to the soundtrack (the review covered the picture only): real voice versus TTS is inferred from the waveform; the effects were found on the separ…
- music source to confirm: most likely stock library music (63%); how to check is under “Sound”

## Map

Read this page first; for detail, open only the file you need. Each line is `path | ~tokens | what is in it · when to read it`; paths are relative to this directory.

```videomd-map
video/timeline.md | 1113 | Timeline: one line per shot · what a stretch says, which shots need review, how a shot was made
video/content.md | 87 | Content and structure · what it says, the narrative line, structure, the script
video/cast.md | 93 | Cast, scenes and props · reference images for characters, first-frame prompts
video/sound.md | 481 | Sound · voice, music, sound effects, beats and sources
video/rhythm.md | 563 | Rhythm and key frames · when cuts and transitions happen, shot lengths, the change curve, key frames of each shot
video/packaging.md | 285 | Packaging · subtitles, styled text, stickers, picture-in-picture: timing and style
video/remake.md | 3586 | Remake plan · generation units, shoots, code builds, real material to collect, acting and emotion
video/shots/*.md | 514 | Per-shot detail, tokens per file on average · checking one shot: what is seen, the inference and its basis, prompts, frames
breakdown.json | 52133 | Full raw data · for programs; a model rarely needs it
shots/ | - | contact sheet, first and last frame of each shot · checking by eye
storyboard.jpg | - | storyboard of the whole video · the whole video at a glance
stems/ | - | voice, music and effects stems · listening, remaking the sound
sfx/ | - | a clip of each sound effect · finding matching effects
packaging/ | - | subtitle files, packaging timeline, sticker frames · remaking subtitles and packaging
frames/ | - | picture scenes: full-size frames, the drawn layer cut out and sampled, measurements · remaking rendered pictures
audio.png | - | waveform and beat chart · seeing the rhythm
```

## How to read

- One shot per line: `#<n> start-end (s) | key value | …`. A key ending in `~` is the tools' inference; keys without it are visible on screen or measured directly.
- `story` job in the story and the point · `seen` what is on screen · `act` acting (emotion, strength, face) · `camera` camera move · `overlay` overlays · `made~` how it was made (inferred) · `material~` where the material came from (inferred) · `remake` remake route · `flag` needs a second look
- Full detail for a shot is in `video/shots/<n>.md` (e.g. `video/shots/07.md`).
- What is “seen” can be checked against the frames; what is “inferred” is the tools' and image readers' judgement, with the basis in each shot file. When they disagree, trust the frames.
