# Hamster wheel — 4 s, 9:16, 1080×1920 @ 30 fps

`hamster_wheel.mp4` copies the format of the reference reel ("When bro call me at 3am…", @ink.industries_). The breakdown below was made with rea-video.

## What the reference does (rea-video + manual review)
- **Picture:** all 16 shots are AI-generated video in a Pixar-like stylized 3D look. Lighting is a warm orange lamp key against cool blue moon/city light, mostly at night, with shallow depth of field and soft grain.
- **Structure:** a quiet intro with no music (0–7 s: phone buzzing, wake-up, groggy voice). Then the **beat drops** on the big action (jumping out of bed, 7.0 s). After that, cuts land on a **~148 BPM** trap beat, and the clip ends on a hard cut.
- **Caption:** two lines of a condensed serif in golden yellow (#F8C820 → #E8A000) with a soft dark shadow, about 42% down the frame. It stays on screen for the whole clip.

## Our version: shot list
| Time | Shot | Picture |
|---|---|---|
| 0.00–1.62 | A: dark close-medium, slow push-in | Hamster asleep in a still wheel. Eyes **snap open at 0.85 s**, then it crouches |
| 1.62–2.84 | B: wide 3/4, camera shake | **Drop**: the hamster sprints and the wheel spins up fast |
| 2.84–3.45 | C: close-up | Determined face, mid-sprint |
| 3.45–4.00 | D: low hero angle | Full sprint, then a hard cut at 4.0 s |

## Sound cue sheet (`audio/`)
| Time | Sound | Matches in the reference |
|---|---|---|
| 0.00–1.62 | Room tone + distant city through a window, **no music** | Quiet diegetic intro |
| 0.05, 0.52 | Tiny hamster snores (whistle in, purr out) | Sleeping character |
| 0.85 | Cartoon "bink" + air pop on the eyes opening | Wake-up sync hit |
| 1.02 | Startled "eek" squeak (3→4.4 kHz chirp) | Groggy vocal reaction |
| 1.15–1.30 | Fur rustle + claws gripping the wire rungs | Foley on the get-up |
| 1.12–1.62 | Noise + tone riser, cut dead on the drop | Build into the drop |
| 1.45 | Metal creak as the wheel starts | — |
| **1.62** | **Sub boom + crack, then the 148 BPM trap beat starts** (kick, clap, hats, 808, dark C-minor bells, pad, kick pump) | Beat drop on the action |
| 1.62–4.00 | Wheel: axle squeak once per turn, a tick for each rung, rolling rumble; ~18 paw taps per second | Detailed on-screen foley |
| 2.84, 3.45 | Whooshes into each cut, plus a hi-hat roll into 3.45 | Cuts on the beat |
| 4.00 | Hard cut | Hard-cut ending |

The mix is mastered to −14 LUFS, the reference's loudness. Separate stems (`ambience`, `foley`, `fx`, `wheel`, `music`) are included so you can rebalance them or lay them under an AI-generated picture.

## Rebuild
```bash
cd source && npm i three@0.170.0
node render.js frames 60          # 240 frames, three.js via headless Chromium
python3 audio.py                  # synthesizes the stems + mix
# composite: see the ffmpeg command in the commit message / chat
```
