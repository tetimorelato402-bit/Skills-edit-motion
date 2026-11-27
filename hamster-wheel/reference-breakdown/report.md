# How this video was made: ref.mp4

**In one line**: Relatable meme: friend calls at 3am with a business idea and you go from asleep to full CEO mode
**How it was made**: Mixed production: AI-generated video 99% + still image + pan/zoom 1%

- 0:28 · vertical 3:4 · 16 shots, 1.8s each on average
- Confidence 72%, based on: tool measurements + AI assistant reviewed 16 shots
- ⚠️ 4 points are uncertain, see “Open questions”

![storyboard](storyboard.jpg)

# Part one · Breakdown: how this video is built

## What makes it work

- **The hook**: 0-4s phone buzzing in the dark + wide-eyed wake-up, music silent until the drop
- Silent buzzing intro then a beat drop at 7.0s when he leaps out of bed
- Cuts on the 148 BPM beat
- Escalating 'boss' gestures: shades, shush, cash snap

## Production pipeline at a glance

| Stage | What this video uses | Remake approach |
|---|---|---|
| **Base picture** | AI-generated video 15 shots (99%), still image + pan/zoom 1 shot (<1%) | AI in 4 generations; a single image held or moved |
| **Packaging** | Stickers / GIFs: animated sticker / GIF ×4; SFX hits on: cut ×2; 3 persistent layers (unchanged across cuts: lay each on once for its span, not per shot): animated sticker / GIF 0.1–2.6s, animated sticker / GIF 2.8–6.9s, animated sticker / GIF 26.1–28.1s | export `packaging/timeline.json` for timeline alignment |
| **Sound** | music (148 BPM, to confirm), 1 distinct effects (5 hits) | music: find a track with the same tempo and mood; effects: add from a library at the listed times |

## Content and structure

- The whole video's content was not analysed this time (needs AI image reading); subtitle text is under “Packaging layer”

- No narrative line this time (what each shot is doing in the story needs AI image reading); the “Picture” column of the shot list is a start

## Shot list

| # | Frame | Time | Picture | Camera | Made with |
|---|---|---|---|---|---|
| 1 | ![#1](shots/shot_001_first.jpg) | 0:00.0 · 1.5s | Close-up: smartphone ringing on wooden nightstand (contact '… | static | AI-generated video |
| 2 | ![#2](shots/shot_002_first.jpg) | 0:01.5 · 1.1s | Phone buzzing on the nightstand, city window at night behind | static | AI-generated video |
| 3 | ![#3](shots/shot_003_first.jpg) | 0:02.7 · 0.8s | Sleepy hand flops onto the phone | static (subject moves) | AI-generated video |
| 4 | ![#4](shots/shot_004_first.jpg) | 0:03.5 · 3.6s | Extreme close-up: man asleep under blanket, eyes snap open w… | static | AI-generated video |
| 5 | ![#5](shots/shot_005_first.jpg) | 0:07.0 · 5.0s | Wide: he springs up out of bed in one bounce, lands sitting … | smooth move | AI-generated video |
| 6 | ![#6](shots/shot_006_first.jpg) | 0:12.0 · 2.3s | Dark transitional shot, moving to desk | static (subject moves) | AI-generated video |
| 7 | ![#7](shots/shot_007_first.jpg) | 0:14.3 · 1.7s | At laptop in dark, lamp light, typing | handheld shake | AI-generated video |
| 8 | ![#8](shots/shot_008_first.jpg) | 0:16.1 · 1.5s | Close-up face with glasses reflecting spreadsheet screen glo… | static | AI-generated video |
| 9 | ![#9](shots/shot_009_first.jpg) | 0:17.6 · 0.4s | Same, slight push | static | AI-generated video |
| 10 | ![#10](shots/shot_010_first.jpg) | 0:18.0 · 1.6s | Pushes sunglasses up with finger, intense stare | static | AI-generated video |
| 11 | ![#11](shots/shot_011_first.jpg) | 0:19.6 · 2.0s | Full-body at floor-to-ceiling window, on phone, city night | smooth move | AI-generated video |
| 12 | ![#12](shots/shot_012_first.jpg) | 0:21.6 · 2.6s | Sitting in chair on phone, holding cash | static | AI-generated video |
| 13 | ![#13](shots/shot_013_first.jpg) | 0:24.2 · 1.8s | Shush/finger to lips with shades, side angle | smooth move | AI-generated video |
| 14 | ![#14](shots/shot_014_first.jpg) | 0:26.0 · 1.9s | Hands pressed in prayer, full moon behind | smooth move | AI-generated video |
| 15 | ![#15](shots/shot_015_first.jpg) | 0:27.9 · 0.3s | Hands snapping a stack of $100 bills | whole-frame zoom / pan | still image + pan/zoom |
| 16 | ![#16](shots/shot_016_first.jpg) | 0:28.2 · 0.4s | Ending frame, chest close-up | static | AI-generated video |

## Cast, scenes and props

- **Visual style**: Pixar/Disney-like stylized 3D, cinematic night lighting: warm orange practical/lamp key vs cool blue moonlight fill, shallow depth of field, soft film grain

- No cast extracted this time (needs AI image reading); shots where the face detector saw a face (person or character): #8

## Packaging layer (subtitles / styled text / stickers / sound-effect hits)

- Stickers / GIFs: animated sticker / GIF ×4
- SFX hits on: cut ×2
- 3 persistent layers (unchanged across cuts: lay each on once for its span, not per shot): animated sticker / GIF 0.1–2.6s, animated sticker / GIF 2.8–6.9s, animated sticker / GIF 26.1–28.1s

**Stickers / GIFs / picture-in-picture**

| Time | Kind | Position | Motion | Confidence | Crop |
|---|---|---|---|---|---|
| 0.10–2.60s | animated sticker / GIF | x30% y70% w20% h7% | animated | medium (unchanged across a cut) | ![sticker_01](packaging/sticker_01.jpg) |
| 2.80–6.90s | animated sticker / GIF | x25% y22% w15% h7% | animated | medium (unchanged across a cut) | ![sticker_02](packaging/sticker_02.jpg) |
| 17.70–19.50s | animated sticker / GIF | x75% y37% w15% h11% | animated | medium (unchanged across a cut) | ![sticker_03](packaging/sticker_03.jpg) |
| 26.10–28.10s | animated sticker / GIF | x85% y52% w15% h18% | animated | medium (unchanged across a cut) | ![sticker_04](packaging/sticker_04.jpg) |

- Remake: find matching stickers and GIFs in an asset library

## Sound

**Music**

- Tempo: 148 BPM; C major; cuts land on the beat; ending: cut off hard
- Source: to confirm
- Remake: The original track leans stock library music: search a library by BPM / mood / key for a similar track, or generate a royalty-free track in a similar style with AI

**Sound effects** (5 hits, 1 distinct sounds)

| Sound | Listen | Type | Times used | At | On screen |
|---|---|---|---|---|---|
| F1 | [listen](sfx/sfx_01.wav) | ding | 5 | 0.4s, 3.9s, 5.8s, 7.0s, 11.9s | cut |

- Remake: play each sound, find a similar one in your editor's library and place it at the times under “At”

**Listen to the tracks**

- music: [stems/music.wav](stems/music.wav)

<details class="ref"><summary>Sound measurements and evidence</summary>

![audio](audio.png)

- Loudness -14.7 dBFS, peak -4.7 dBFS
- sound runs across cuts, laid in post as one bed (background changes 1.8dB at cuts vs 1.9dB within shots)
- tempo may also be 73.8/295.3 BPM; music on 86% of the duration (0.0–28.0s); section changes at 6.5s; 60% of cuts land on a beat (chance: about 30%)
- Music source: to confirm (stock library music 63%, well-known song 23%, AI-generated music 13%)
  - The music is a bed under the picture: in a regular video the bed usually comes from a stock library (prior)
  - The music is hard-cut at the end (still at full level when the video stops): typical of a trimmed existing track
  - Nothing about this track beyond the format prior and weak cues like the ending (no source heard, no platform music tag): source to confirm; an AI-generated bed cannot be told from a library bed here
  - How to confirm: Check the music tag on the original Douyin / Xiaohongshu / TikTok post: a song title → existing track; "original sound - @creator" → uploaded by the creator (for music videos, usually an AI song)
  - How to confirm: Run it through Shazam / ACRCloud or another song-ID service: a hit means an existing song

</details>

## Open questions

- Shot #15 (27.9–28.2s): Tools say still image + pan/zoom, the image review says AI-generated video; on the AI / live-action axis the fusion follows the tools (eval-calibrated): check the frames to see whether the review's evidence is really visible
- Shot #15 (27.9–28.2s): photo / image: real material or generated, to confirm
- No AI listened to the soundtrack (the review covered the picture only): real voice versus TTS is inferred from the waveform; the effects were found on the separated effects track and their types are estimated from the sound. Play the stems and each effect under “Sound” to check
- music source to confirm: most likely stock library music (63%); how to check is under “Sound”

# Part two · Remake plan

Planned for **MiniMax H3 / H3 Max**: ≤15 s per call, several shots per call, takes reference video (3 clips, ≤15 s in all), ≤9 reference images, first / last frame, native sound. Name another model and the split, lengths and prompts are redone for it.

## Remake it yourself: do it in this order

Copy the method and the rhythm, not the pictures: keep what each part does and fill it with your own content and material.

This is a AI visual short / montage. Do the steps in this order; the detail for each is in the matching subsection below.

1. **Write the content**: one picture of your own for each of the 16 shots in the shot list
2. **Generate**: 4 calls (28 s), several shots each. Each shot gets one source frame for composition (subtitles erased, in `remake/refs/`), the swapped-in people, animals and products get reference images, and the prompt lists the shots in order
3. **Adapt the prompts to your model**: each unit's draft is already laid out in MiniMax H3 / H3 Max's shot, tag and audio format; refine it against the model's prompt guide before generating (or run `rea-video plan <folder> --rewrite-prompts`)
4. **Stills with moves**: swap in your images; the agent moves them the way the original does
5. **Edit**: follow the order and lengths in the shot list; the original has 16 shots at 1.8s each; 2 transitions under “Edit”
6. **Subtitles and styled text**: timing and style under “Packaging layer”
7. **Music**: find a track at the same tempo and mood (source: to confirm, about 148 BPM, C major, cuts land on the beat)
8. **Sound effects**: 5; place similar ones from a library at the times under “Sound”
9. **Put it together and compare**: hand the shots you made to the agent; it places them on the original timeline, keeps the original where yours are missing, and renders a side-by-side comparison with the original

### AI generation

**4 generations, 28 s in total**

> ⚠️ G1, G2, G3, G4: the prompts are the tool's drafts, already in MiniMax H3 / H3 Max's layout. Check them against the model's conventions and good prompts for similar shots, then put the finals into `remake/prompts.json`; `rea-video plan` then checks the format.

- **How it is generated**: multi-shot from key frames

| Part | Shots | Time | Length | Prepare |
|---|---|---|---|---|
| G1 | #1–#4 | 0.0–7.0s | generate 8s, trim to 7.0s | reference images + reference audio |
| G2 | #5–#7 | 7.0–16.1s | generate 10s, trim to 9.0s | reference images + reference audio |
| G3 | #8–#11 | 16.1–21.6s | 5.6s | reference images + reference audio |
| G4 | #12–#14, #16 | 21.6–27.9s, 28.2–28.5s | 6.6s | reference images + reference audio |

<details class="ref"><summary>Why it is split this way</summary>

- Grouping: consecutive shots share a call where they fit, ≤10s per call, ≤4 shots; a long stretch is cut at a scene change first
- Inputs: the model also takes reference video, but key frames are used here: one key frame per shot fixes composition and look, swapped-in things get their own images
- Audio: the model can generate action sound effects and ambience along with the picture
- Packaging: the sticker on the generated shots is post-production packaging: keep it out of the prompts (erased from source references) and lay it back on from the packaging timeline after generation

</details>

<details><summary>Frames to make first (15)</summary>

When swapping people or products, or switching to shot-by-shot image-to-video, prepare each shot's first frame as below:

| Shot | Role | How | Reference images | Save as |
|---|---|---|---|---|
| #1 | first frame | text-to-image (or low-denoise I2I from source frame) | `shots/shot_001_first.jpg` (source first frame: composition and style reference) | `remake/redrawn/shot001.png` |
| #2 | first frame | text-to-image (or low-denoise I2I from source frame) | `shots/shot_002_first.jpg` (source first frame: composition and style reference) | `remake/redrawn/shot002.png` |
| #3 | first frame | text-to-image (or low-denoise I2I from source frame) | `shots/shot_003_first.jpg` (source first frame: composition and style reference) | `remake/redrawn/shot003.png` |
| #4 | first frame | text-to-image (or low-denoise I2I from source frame) | `shots/shot_004_first.jpg` (source first frame: composition and style reference) | `remake/redrawn/shot004.png` |
| #5 | first frame | text-to-image (or low-denoise I2I from source frame) | `shots/shot_005_first.jpg` (source first frame: composition and style reference) | `remake/redrawn/shot005.png` |
| #6 | first frame | text-to-image (or low-denoise I2I from source frame) | `shots/shot_006_first.jpg` (source first frame: composition and style reference) | `remake/redrawn/shot006.png` |
| #7 | first frame | text-to-image (or low-denoise I2I from source frame) | `shots/shot_007_first.jpg` (source first frame: composition and style reference) | `remake/redrawn/shot007.png` |
| #8 | first frame | text-to-image (or low-denoise I2I from source frame) | `shots/shot_008_first.jpg` (source first frame: composition and style reference) | `remake/redrawn/shot008.png` |
| #9 | first frame | text-to-image (or low-denoise I2I from source frame) | `shots/shot_009_first.jpg` (source first frame: composition and style reference) | `remake/redrawn/shot009.png` |
| #10 | first frame | text-to-image (or low-denoise I2I from source frame) | `shots/shot_010_first.jpg` (source first frame: composition and style reference) | `remake/redrawn/shot010.png` |
| #11 | first frame | text-to-image (or low-denoise I2I from source frame) | `shots/shot_011_first.jpg` (source first frame: composition and style reference) | `remake/redrawn/shot011.png` |
| #12 | first frame | text-to-image (or low-denoise I2I from source frame) | `shots/shot_012_first.jpg` (source first frame: composition and style reference) | `remake/redrawn/shot012.png` |
| #13 | first frame | text-to-image (or low-denoise I2I from source frame) | `shots/shot_013_first.jpg` (source first frame: composition and style reference) | `remake/redrawn/shot013.png` |
| #14 | first frame | text-to-image (or low-denoise I2I from source frame) | `shots/shot_014_first.jpg` (source first frame: composition and style reference) | `remake/redrawn/shot014.png` |
| #16 | first frame | text-to-image (or low-denoise I2I from source frame) | `shots/shot_016_first.jpg` (source first frame: composition and style reference) | `remake/redrawn/shot016.png` |

- **#1 first frame (text-to-image (or low-denoise I2I from source frame))**
  - Image prompt: Vertical 3:4. close-up, subject in the lower middle of the frame. Close-up: smartphone ringing on wooden nightstand (contact 'Bro'), sunglasses beside it, dark room
- **#2 first frame (text-to-image (or low-denoise I2I from source frame))**
  - Image prompt: Vertical 3:4. close-up, subject in the lower middle of the frame. Phone buzzing on the nightstand, city window at night behind
- **#3 first frame (text-to-image (or low-denoise I2I from source frame))**
  - Image prompt: Vertical 3:4. close-up, subject in the lower middle of the frame. Sleepy hand flops onto the phone
- **#4 first frame (text-to-image (or low-denoise I2I from source frame))**
  - Image prompt: Vertical 3:4. close-up, subject in the lower middle of the frame, camera push-in. Extreme close-up: man asleep under blanket, eyes snap open wide
- **#5 first frame (text-to-image (or low-denoise I2I from source frame))**
  - Image prompt: Vertical 3:4. close-up, subject in the lower middle of the frame, camera push-in. Wide: he springs up out of bed in one bounce, lands sitting on edge
- **#6 first frame (text-to-image (or low-denoise I2I from source frame))**
  - Image prompt: Vertical 3:4. close-up, subject in the lower middle of the frame. Dark transitional shot, moving to desk
- **#7 first frame (text-to-image (or low-denoise I2I from source frame))**
  - Image prompt: Vertical 3:4. medium close-up, subject in the lower middle of the frame, camera pull-out. At laptop in dark, lamp light, typing
- **#8 first frame (text-to-image (or low-denoise I2I from source frame))**
  - Image prompt: Vertical 3:4. extreme close-up, subject in the upper middle of the frame, camera push-in. Close-up face with glasses reflecting spreadsheet screen glow
- **#9 first frame (text-to-image (or low-denoise I2I from source frame))**
  - Image prompt: Vertical 3:4. close-up, subject in the lower middle of the frame. Same, slight push
- **#10 first frame (text-to-image (or low-denoise I2I from source frame))**
  - Image prompt: Vertical 3:4. close-up, subject in the lower middle of the frame. Pushes sunglasses up with finger, intense stare
- **#11 first frame (text-to-image (or low-denoise I2I from source frame))**
  - Image prompt: Vertical 3:4. close-up, subject in the lower middle of the frame, camera push-in. Full-body at floor-to-ceiling window, on phone, city night
- **#12 first frame (text-to-image (or low-denoise I2I from source frame))**
  - Image prompt: Vertical 3:4. close-up, subject in the lower middle of the frame. Sitting in chair on phone, holding cash
- **#13 first frame (text-to-image (or low-denoise I2I from source frame))**
  - Image prompt: Vertical 3:4. close-up, subject in the lower middle of the frame, camera push-in. Shush/finger to lips with shades, side angle
- **#14 first frame (text-to-image (or low-denoise I2I from source frame))**
  - Image prompt: Vertical 3:4. close-up, subject in the lower middle of the frame, camera push-in. Hands pressed in prayer, full moon behind
- **#16 first frame (text-to-image (or low-denoise I2I from source frame))**
  - Image prompt: Vertical 3:4. close-up, subject in the lower middle of the frame. Ending frame, chest close-up

</details>

<details><summary>G1 · shots #1–#4 · 7.0s</summary>

- reference images: source frames of shots #1, #2, #3, #4 (subtitles erased)
- reference audio: music stem `stems/music.wav` (or your replacement track at the same BPM)

Draft prompt (in MiniMax H3 / H3 Max's layout; check it and put the final into remake/prompts.json before generating):

```text
integrated_multimodal_description: Generate the shots below in order in one go, hard cuts between them; each shot takes composition, size and camera from its source frame image. Vertical 3:4; night / low-light ambient, no dedicated fill, soft light, cool tones, background clearly blurred.
[Shot 1] Close-up: smartphone ringing on wooden nightstand (contact 'Bro'), sunglasses beside it, dark room (composition: <Picture 1>)
[Shot 2] At 00:01.533, the camera cuts to: Phone buzzing on the nightstand, city window at night behind (composition: <Picture 2>)
[Shot 3] At 00:02.666, the camera cuts to: Sleepy hand flops onto the phone (composition: <Picture 3>)
[Shot 4] At 00:03.466, the camera cuts to: Extreme close-up: man asleep under blanket, eyes snap open wide (composition: <Picture 4>)
overall_soundscape: Only the natural sounds of the actions on screen.
non_diegetic_music: N/A
```

</details>

<details><summary>G2 · shots #5–#7 · 9.0s</summary>

- reference images: source frames of shots #5, #6, #7 (subtitles erased)
- reference audio: music stem `stems/music.wav` (or your replacement track at the same BPM)

Draft prompt (in MiniMax H3 / H3 Max's layout; check it and put the final into remake/prompts.json before generating):

```text
integrated_multimodal_description: Generate the shots below in order in one go, hard cuts between them; each shot takes composition, size and camera from its source frame image. Vertical 3:4; night / low-light ambient, no dedicated fill, soft light, cool tones, background clearly blurred.
[Shot 1] Wide: he springs up out of bed in one bounce, lands sitting on edge (composition: <Picture 1>)
[Shot 2] At 00:05.000, the camera cuts to: Dark transitional shot, moving to desk (composition: <Picture 2>)
[Shot 3] At 00:07.300, the camera cuts to: At laptop in dark, lamp light, typing (composition: <Picture 3>)
overall_soundscape: Only the natural sounds of the actions on screen.
non_diegetic_music: N/A
```

</details>

<details><summary>G3 · shots #8–#11 · 5.6s</summary>

- reference images: source frames of shots #8, #9, #10, #11 (subtitles erased)
- reference audio: music stem `stems/music.wav` (or your replacement track at the same BPM)

Draft prompt (in MiniMax H3 / H3 Max's layout; check it and put the final into remake/prompts.json before generating):

```text
integrated_multimodal_description: Generate the shots below in order in one go, hard cuts between them; each shot takes composition, size and camera from its source frame image. Vertical 3:4; night / low-light ambient, no dedicated fill, soft light, cool tones, background clearly blurred.
[Shot 1] Close-up face with glasses reflecting spreadsheet screen glow (composition: <Picture 1>)
[Shot 2] At 00:01.533, the camera cuts to: Same, slight push (composition: <Picture 2>)
[Shot 3] At 00:01.966, the camera cuts to: Pushes sunglasses up with finger, intense stare (composition: <Picture 3>)
[Shot 4] At 00:03.533, the camera cuts to: Full-body at floor-to-ceiling window, on phone, city night (composition: <Picture 4>)
overall_soundscape: Only the natural sounds of the actions on screen.
non_diegetic_music: N/A
```

</details>

<details><summary>G4 · shots #12–#14, #16 · 6.6s</summary>

- reference images: source frames of shots #12, #13, #14, #16 (subtitles erased)
- reference audio: music stem `stems/music.wav` (or your replacement track at the same BPM)

- these shots are separated by inserts in the cut: generate them together and put the inserts back in the edit

Draft prompt (in MiniMax H3 / H3 Max's layout; check it and put the final into remake/prompts.json before generating):

```text
integrated_multimodal_description: Generate the shots below in order in one go, hard cuts between them; each shot takes composition, size and camera from its source frame image. Vertical 3:4; night / low-light ambient, no dedicated fill, soft light, cool tones, background clearly blurred.
[Shot 1] Sitting in chair on phone, holding cash (composition: <Picture 1>)
[Shot 2] At 00:02.600, the camera cuts to: Shush/finger to lips with shades, side angle (composition: <Picture 2>)
[Shot 3] At 00:04.367, the camera cuts to: Hands pressed in prayer, full moon behind (composition: <Picture 3>)
[Shot 4] At 00:06.267, the camera cuts to: Ending frame, chest close-up (composition: <Picture 4>)
overall_soundscape: Only the natural sounds of the actions on screen.
non_diegetic_music: N/A
```

</details>

<details><summary>Prompt guides for MiniMax H3 / H3 Max</summary>

- https://huggingface.co/MiniMaxAI/MiniMax-H3/raw/main/docs/VIDEO_PROMPT_WRITING_GUIDE_base_en.md
- https://huggingface.co/MiniMaxAI/MiniMax-H3/raw/main/docs/VIDEO_PROMPT_WRITING_GUIDE_ref_en.md
- https://platform.minimax.io/docs/api-reference/video-generation-v2-create
- https://docs.comfy.org/tutorials/video/minimax/minimax-h3-prompt-guide.md

</details>

### Local rebuild

- #15 still image + pan/zoom 0.3s: one image + the measured zoom / pan parameters, rendered straight from ffmpeg

### Edit

- Cut in the order and lengths of the shot list
- Rhythm: 1.8s per shot; transitions cut×13, jump cut×1, wipe×1

**Transitions**

| Time | Into shot | Transition |
|---|---|---|
| 2.6–2.7s | #3 | wipe, downwards, 0.2s |

## Appendix

### Shot by shot

Each shot has two parts: what is visible on screen, and how the tools infer it was made (with the basis); remake prompts last. Folded by default.

<details class="ref"><summary>#1 00:00.000–00:01.533 · AI-generated video + code / editor overlays (static graphics, animated sticker / GIF)</summary>

![shot_001](shots/shot_001.jpg)

**Visible on screen** (check against the frames)
- Picture: Close-up: smartphone ringing on wooden nightstand (contact 'Bro'), sunglasses beside it, dark room
- Framing / light: close-up; centred; key light frontal (from the camera side; both sides of the subject about equally bright); soft light (almost no lit / shadow edge); neutral tone
- [AI assistant review] Consistent Pixar-style stylized 3D character across 16 shots with varied staging and soft cinematic lighting typical of image-to-video models; hair and fabric show slight texture shimmer; no rig-precise motion

**How it was made, as inferred by the tools** (inferred, not seen)
- Inference: AI-generated video 70%, 3D render 19%, 2D animation 3% (fused_agent)
- Material: AI-generated
- Basis (tool measurements, not necessarily visible to the eye):
  - Photographic texture: noise σ=0.14, 111 colours, 23% flat blocks

- Remake: Source is AI-generated: remake it with a video model; which shots share a call and what it is fed (the source clip, keyframes or first / last frames) depend on the chosen model, see the generation units in the remake plan

</details>

<details class="ref"><summary>#2 00:01.533–00:02.667 · AI-generated video + code / editor overlays (static graphics, animated sticker / GIF)</summary>

![shot_002](shots/shot_002.jpg)

**Visible on screen** (check against the frames)
- Picture: Phone buzzing on the nightstand, city window at night behind
- Framing / light: close-up; centred; key light frame left, three-quarter front; soft light (wide lit-to-shadow ramp); cool tone
- [AI assistant review] Consistent Pixar-style stylized 3D character across 16 shots with varied staging and soft cinematic lighting typical of image-to-video models; hair and fabric show slight texture shimmer; no rig-precise motion

**How it was made, as inferred by the tools** (inferred, not seen)
- Inference: AI-generated video 69%, 3D render 20%, code / template render 4% (fused_agent)
- Material: AI-generated
- Basis (tool measurements, not necessarily visible to the eye):
  - Photographic texture: noise σ=0.22, 197 colours, 13% flat blocks
  - Duplicate frames follow a 24→30 pattern (17%, period 5): a 24/25fps source transcoded up, typical of AI-generated video, 3D / animation renders or cinema footage

- Remake: Source is AI-generated: remake it with a video model; which shots share a call and what it is fed (the source clip, keyframes or first / last frames) depend on the chosen model, see the generation units in the remake plan

</details>

<details class="ref"><summary>#3 00:02.667–00:03.467 · AI-generated video + code / editor overlays (static graphics, animated sticker / GIF)</summary>

![shot_003](shots/shot_003.jpg)

**Visible on screen** (check against the frames)
- Picture: Sleepy hand flops onto the phone
- Framing / light: close-up; centred; key light frontal (from the camera side; both sides of the subject about equally bright); soft light (wide lit-to-shadow ramp); cool tone
- [AI assistant review] Consistent Pixar-style stylized 3D character across 16 shots with varied staging and soft cinematic lighting typical of image-to-video models; hair and fabric show slight texture shimmer; no rig-precise motion

**How it was made, as inferred by the tools** (inferred, not seen)
- Inference: AI-generated video 69%, 3D render 20%, code / template render 4% (fused_agent)
- Material: AI-generated
- Basis (tool measurements, not necessarily visible to the eye):
  - Photographic texture: noise σ=0.22, 165 colours, 14% flat blocks
  - Duplicate frames follow a 24→30 pattern (21%, period 5): a 24/25fps source transcoded up, typical of AI-generated video, 3D / animation renders or cinema footage

- Remake: Source is AI-generated: remake it with a video model; which shots share a call and what it is fed (the source clip, keyframes or first / last frames) depend on the chosen model, see the generation units in the remake plan

</details>

<details class="ref"><summary>#4 00:03.467–00:07.033 · AI-generated video + code / editor overlays (static graphics, animated sticker / GIF)</summary>

![shot_004](shots/shot_004.jpg)

**Visible on screen** (check against the frames)
- Picture: Extreme close-up: man asleep under blanket, eyes snap open wide
- Framing / light: close-up; centred; camera push-in; key light frontal (from the camera side; both sides of the subject about equally bright); soft light (almost no lit / shadow edge); cool tone
- Motion beats within the shot: 6.03s
- [AI assistant review] Consistent Pixar-style stylized 3D character across 16 shots with varied staging and soft cinematic lighting typical of image-to-video models; hair and fabric show slight texture shimmer; no rig-precise motion

**How it was made, as inferred by the tools** (inferred, not seen)
- Inference: AI-generated video 68%, 3D render 21%, code / template render 4% (fused_agent)
- Material: AI-generated
- Basis (tool measurements, not necessarily visible to the eye):
  - Photographic texture: noise σ=0.35, 63 colours, 3% flat blocks
  - Duplicate frames follow a 24→30 pattern (18%, period 5): a 24/25fps source transcoded up, typical of AI-generated video, 3D / animation renders or cinema footage

- Remake: Source is AI-generated: remake it with a video model; which shots share a call and what it is fed (the source clip, keyframes or first / last frames) depend on the chosen model, see the generation units in the remake plan

</details>

<details class="ref"><summary>#5 00:07.033–00:12.033 · AI-generated video + code / editor overlays (static graphics)</summary>

![shot_005](shots/shot_005.jpg)

**Visible on screen** (check against the frames)
- Picture: Wide: he springs up out of bed in one bounce, lands sitting on edge
- Framing / light: close-up; centred; camera push-in; key light frontal (from the camera side; both sides of the subject about equally bright); medium-soft; cool tone
- [AI assistant review] Consistent Pixar-style stylized 3D character across 16 shots with varied staging and soft cinematic lighting typical of image-to-video models; hair and fabric show slight texture shimmer; no rig-precise motion

**How it was made, as inferred by the tools** (inferred, not seen)
- Inference: AI-generated video 71%, 3D render 19%, code / template render 4% (fused_agent)
- Material: AI-generated
- Basis (tool measurements, not necessarily visible to the eye):
  - Photographic texture: noise σ=0.22, 98 colours, 17% flat blocks
  - Duplicate frames follow a 24→30 pattern (20%, period 5): a 24/25fps source transcoded up, typical of AI-generated video, 3D / animation renders or cinema footage

- Remake: Source is AI-generated: remake it with a video model; which shots share a call and what it is fed (the source clip, keyframes or first / last frames) depend on the chosen model, see the generation units in the remake plan

</details>

<details class="ref"><summary>#6 00:12.033–00:14.333 · AI-generated video + code / editor overlays (static graphics)</summary>

![shot_006](shots/shot_006.jpg)

**Visible on screen** (check against the frames)
- Picture: Dark transitional shot, moving to desk
- Framing / light: close-up; centred; key light frame right, three-quarter front; hard light (sharp shadow edge); cool tone
- [AI assistant review] Consistent Pixar-style stylized 3D character across 16 shots with varied staging and soft cinematic lighting typical of image-to-video models; hair and fabric show slight texture shimmer; no rig-precise motion

**How it was made, as inferred by the tools** (inferred, not seen)
- Inference: AI-generated video 67%, 3D render 21%, code / template render 3% (fused_agent)
- Material: AI-generated
- Basis (tool measurements, not necessarily visible to the eye):
  - On a dark ground the lit part is almost all fine dots / thin lines (with the smooth background taken out, only 27% of lit pixels shade gently, 10 bright peaks per 100 lit pixels): particle / point-cloud / wireframe graphics, not a shaded photo, 3D surface or AI picture
  - Rendered texture: 29% flat colour blocks, 95% of pixels use only 67 colours, 25% axis-aligned edges
  - Duplicate frames follow a 24→30 pattern (20%, period 5): a 24/25fps source transcoded up, typical of AI-generated video, 3D / animation renders or cinema footage

- Remake: Source is AI-generated: remake it with a video model; which shots share a call and what it is fed (the source clip, keyframes or first / last frames) depend on the chosen model, see the generation units in the remake plan

</details>

<details class="ref"><summary>#7 00:14.333–00:16.067 · AI-generated video</summary>

![shot_007](shots/shot_007.jpg)

**Visible on screen** (check against the frames)
- Picture: At laptop in dark, lamp light, typing
- Framing / light: medium close-up; centred; camera pull-out; key light frontal (from the camera side; both sides of the subject about equally bright); soft light (wide lit-to-shadow ramp); cool tone
- [AI assistant review] Consistent Pixar-style stylized 3D character across 16 shots with varied staging and soft cinematic lighting typical of image-to-video models; hair and fabric show slight texture shimmer; no rig-precise motion

**How it was made, as inferred by the tools** (inferred, not seen)
- Inference: AI-generated video 70%, live action 15%, 3D render 7% (fused_agent)
- Material: AI-generated
- Basis (tool measurements, not necessarily visible to the eye):
  - Photographic texture: noise σ=0.28, 254 colours, 10% flat blocks
  - Duplicate frames follow a 24→30 pattern (21%, period 5): a 24/25fps source transcoded up, typical of AI-generated video, 3D / animation renders or cinema footage

- Remake: Source is AI-generated: remake it with a video model; which shots share a call and what it is fed (the source clip, keyframes or first / last frames) depend on the chosen model, see the generation units in the remake plan

</details>

<details class="ref"><summary>#8 00:16.067–00:17.600 · AI-generated video + code / editor overlays (static graphics)</summary>

![shot_008](shots/shot_008.jpg)

**Visible on screen** (check against the frames)
- Picture: Close-up face with glasses reflecting spreadsheet screen glow
- Framing / light: extreme close-up; centred; camera push-in; key light frontal (from the camera side; both sides of the subject about equally bright); hard light (sharp shadow edge); cool tone
- Motion beats within the shot: 16.57s
- [AI assistant review] Consistent Pixar-style stylized 3D character across 16 shots with varied staging and soft cinematic lighting typical of image-to-video models; hair and fabric show slight texture shimmer; no rig-precise motion

**How it was made, as inferred by the tools** (inferred, not seen)
- Inference: AI-generated video 78%, AI avatar (talking head) 10%, 3D render 6% (fused_agent)
- Material: AI-generated
- Basis (tool measurements, not necessarily visible to the eye):
  - Photographic texture: noise σ=0.34, 215 colours, 5% flat blocks
  - Duplicate frames follow a 24→30 pattern (12%, period 5): a 24/25fps source transcoded up, typical of AI-generated video, 3D / animation renders or cinema footage
  - 67% of sampled frames show a frontal face on a fixed camera

- Remake: Source is AI-generated: remake it with a video model; which shots share a call and what it is fed (the source clip, keyframes or first / last frames) depend on the chosen model, see the generation units in the remake plan

</details>

<details class="ref"><summary>#9 00:17.600–00:18.033 · AI-generated video + code / editor overlays (static graphics, animated sticker / GIF)</summary>

![shot_009](shots/shot_009.jpg)

**Visible on screen** (check against the frames)
- Picture: Same, slight push
- Framing / light: close-up; centred; key light frontal (from the camera side; both sides of the subject about equally bright); soft light (almost no lit / shadow edge); cool tone
- [AI assistant review] Consistent Pixar-style stylized 3D character across 16 shots with varied staging and soft cinematic lighting typical of image-to-video models; hair and fabric show slight texture shimmer; no rig-precise motion

**How it was made, as inferred by the tools** (inferred, not seen)
- Inference: AI-generated video 68%, live action 13%, 3D render 9% (fused_agent)
- Material: AI-generated
- Basis (tool measurements, not necessarily visible to the eye):
  - Photographic texture: noise σ=0.32, 206 colours, 3% flat blocks

- Remake: Source is AI-generated: remake it with a video model; which shots share a call and what it is fed (the source clip, keyframes or first / last frames) depend on the chosen model, see the generation units in the remake plan

</details>

<details class="ref"><summary>#10 00:18.033–00:19.600 · AI-generated video + code / editor overlays (static graphics, animated sticker / GIF)</summary>

![shot_010](shots/shot_010.jpg)

**Visible on screen** (check against the frames)
- Picture: Pushes sunglasses up with finger, intense stare
- Framing / light: close-up; centred; key light frontal (from the camera side; both sides of the subject about equally bright); soft light (wide lit-to-shadow ramp); cool tone
- [AI assistant review] Consistent Pixar-style stylized 3D character across 16 shots with varied staging and soft cinematic lighting typical of image-to-video models; hair and fabric show slight texture shimmer; no rig-precise motion

**How it was made, as inferred by the tools** (inferred, not seen)
- Inference: AI-generated video 70%, 3D render 19%, code / template render 4% (fused_agent)
- Material: AI-generated
- Basis (tool measurements, not necessarily visible to the eye):
  - Photographic texture: noise σ=0.22, 89 colours, 14% flat blocks
  - Duplicate frames follow a 24→30 pattern (21%, period 5): a 24/25fps source transcoded up, typical of AI-generated video, 3D / animation renders or cinema footage

- Remake: Source is AI-generated: remake it with a video model; which shots share a call and what it is fed (the source clip, keyframes or first / last frames) depend on the chosen model, see the generation units in the remake plan

</details>

<details class="ref"><summary>#11 00:19.600–00:21.633 · AI-generated video + code / editor overlays (static graphics)</summary>

![shot_011](shots/shot_011.jpg)

**Visible on screen** (check against the frames)
- Picture: Full-body at floor-to-ceiling window, on phone, city night
- Framing / light: close-up; centred; camera push-in; key light frontal (from the camera side; both sides of the subject about equally bright); soft light (almost no lit / shadow edge); cool tone
- [AI assistant review] Consistent Pixar-style stylized 3D character across 16 shots with varied staging and soft cinematic lighting typical of image-to-video models; hair and fabric show slight texture shimmer; no rig-precise motion

**How it was made, as inferred by the tools** (inferred, not seen)
- Inference: AI-generated video 67%, 3D render 24%, 2D animation 3% (fused_agent)
- Material: AI-generated
- Basis (tool measurements, not necessarily visible to the eye):
  - Duplicate frames follow a 24→30 pattern (20%, period 5): a 24/25fps source transcoded up, typical of AI-generated video, 3D / animation renders or cinema footage

- Remake: Source is AI-generated: remake it with a video model; which shots share a call and what it is fed (the source clip, keyframes or first / last frames) depend on the chosen model, see the generation units in the remake plan

</details>

<details class="ref"><summary>#12 00:21.633–00:24.233 · AI-generated video + code / editor overlays (static graphics)</summary>

![shot_012](shots/shot_012.jpg)

**Visible on screen** (check against the frames)
- Picture: Sitting in chair on phone, holding cash
- Framing / light: close-up; centred; key light frontal (from the camera side; both sides of the subject about equally bright); hard light (sharp shadow edge); cool tone
- [AI assistant review] Consistent Pixar-style stylized 3D character across 16 shots with varied staging and soft cinematic lighting typical of image-to-video models; hair and fabric show slight texture shimmer; no rig-precise motion

**How it was made, as inferred by the tools** (inferred, not seen)
- Inference: AI-generated video 70%, 3D render 20%, 2D animation 2% (fused_agent)
- Material: AI-generated
- Basis (tool measurements, not necessarily visible to the eye):
  - Duplicate frames follow a 24→30 pattern (27%, period 5): a 24/25fps source transcoded up, typical of AI-generated video, 3D / animation renders or cinema footage

- Remake: Source is AI-generated: remake it with a video model; which shots share a call and what it is fed (the source clip, keyframes or first / last frames) depend on the chosen model, see the generation units in the remake plan

</details>

<details class="ref"><summary>#13 00:24.233–00:26.000 · AI-generated video + code / editor overlays (static graphics)</summary>

![shot_013](shots/shot_013.jpg)

**Visible on screen** (check against the frames)
- Picture: Shush/finger to lips with shades, side angle
- Framing / light: close-up; centred; camera push-in; key light frontal (from the camera side; both sides of the subject about equally bright); soft light (almost no lit / shadow edge); cool tone
- [AI assistant review] Consistent Pixar-style stylized 3D character across 16 shots with varied staging and soft cinematic lighting typical of image-to-video models; hair and fabric show slight texture shimmer; no rig-precise motion

**How it was made, as inferred by the tools** (inferred, not seen)
- Inference: AI-generated video 76%, 3D render 14%, code / template render 3% (fused_agent)
- Material: AI-generated
- Basis (tool measurements, not necessarily visible to the eye):
  - Photographic texture: noise σ=0.28, 89 colours, 12% flat blocks
  - Duplicate frames follow a 24→30 pattern (15%, period 5): a 24/25fps source transcoded up, typical of AI-generated video, 3D / animation renders or cinema footage

- Remake: Source is AI-generated: remake it with a video model; which shots share a call and what it is fed (the source clip, keyframes or first / last frames) depend on the chosen model, see the generation units in the remake plan

</details>

<details class="ref"><summary>#14 00:26.000–00:27.900 · AI-generated video + code / editor overlays (static graphics, animated sticker / GIF)</summary>

![shot_014](shots/shot_014.jpg)

**Visible on screen** (check against the frames)
- Picture: Hands pressed in prayer, full moon behind
- Framing / light: close-up; centred; camera push-in; key light frame right (side light); soft light (wide lit-to-shadow ramp); cool tone
- [AI assistant review] Consistent Pixar-style stylized 3D character across 16 shots with varied staging and soft cinematic lighting typical of image-to-video models; hair and fabric show slight texture shimmer; no rig-precise motion

**How it was made, as inferred by the tools** (inferred, not seen)
- Inference: AI-generated video 87%, 3D render 5%, code / template render 2% (fused_agent)
- Material: AI-generated
- Basis (tool measurements, not necessarily visible to the eye):
  - Photographic texture: noise σ=0.30, 215 colours, 8% flat blocks
  - Duplicate frames follow a 24→30 pattern (17%, period 5): a 24/25fps source transcoded up, typical of AI-generated video, 3D / animation renders or cinema footage

- Remake: Source is AI-generated: remake it with a video model; which shots share a call and what it is fed (the source clip, keyframes or first / last frames) depend on the chosen model, see the generation units in the remake plan

</details>

<details class="ref"><summary>#15 00:27.900–00:28.167 · still image + pan/zoom + code / editor overlays (animated sticker / GIF)</summary>

![shot_015](shots/shot_015.jpg)

**Visible on screen** (check against the frames)
- Picture: Hands snapping a stack of $100 bills
- [AI assistant review] Consistent Pixar-style stylized 3D character across 16 shots with varied staging and soft cinematic lighting typical of image-to-video models; hair and fabric show slight texture shimmer; no rig-precise motion

**How it was made, as inferred by the tools** (inferred, not seen)
- Inference: still image + pan/zoom 73%, AI-generated video 15%, screen recording / screenshot 6% (fused_agent)
- ⚠️ Disputed: Tools say still image + pan/zoom, the image review says AI-generated video; on the AI / live-action axis the fusion follows the tools (eval-calibrated): check the frames to see whether the review's evidence is really visible
- Still source: unknown
- Material: to confirm; real or not, to confirm: photo / image
- Basis (tool measurements, not necessarily visible to the eye):
  - Whole frame moves as one rigid transform (100% inliers, 0.12px residual, no local motion) → pan/zoom on a still image: zoom +0.0%/s, pan 8px/s
  - Photographic texture: noise σ=0.23, 187 colours, 12% flat blocks

- Remake: Still-image move: one image + the measured zoom / pan parameters, reproduced exactly with local ffmpeg

</details>

<details class="ref"><summary>#16 00:28.167–00:28.533 · AI-generated video + code / editor overlays (static graphics)</summary>

![shot_016](shots/shot_016.jpg)

**Visible on screen** (check against the frames)
- Picture: Ending frame, chest close-up
- Framing / light: close-up; centred; key light frontal (from the camera side; both sides of the subject about equally bright); soft light (almost no lit / shadow edge); warm tone
- [AI assistant review] Consistent Pixar-style stylized 3D character across 16 shots with varied staging and soft cinematic lighting typical of image-to-video models; hair and fabric show slight texture shimmer; no rig-precise motion

**How it was made, as inferred by the tools** (inferred, not seen)
- Inference: AI-generated video 71%, 3D render 18%, 2D animation 3% (fused_agent)
- Material: AI-generated
- Basis (tool measurements, not necessarily visible to the eye):
  - Photographic texture: noise σ=0.22, 112 colours, 13% flat blocks

- Remake: Source is AI-generated: remake it with a video model; which shots share a call and what it is fed (the source clip, keyframes or first / last frames) depend on the chosen model, see the generation units in the remake plan

</details>

### Metadata clues

- Encoder: `Lavf60.16.100`

### Notes

- Deterministic forensics is reliable on motion, whole-frame pan/zoom, rendered texture and 24→30 fps conversion; telling live action from AI from 3D needs image reading (a VLM or an AI assistant's review), and a look at the frames yourself.
- Platform transcoding usually strips metadata; missing metadata proves nothing.
- The full data is in `breakdown.json`; the package for models starts at `VIDEO.md`.

---

Made with [REA-VIDEO](https://github.com/JuneYaooo/rea-video) · https://github.com/JuneYaooo/rea-video
