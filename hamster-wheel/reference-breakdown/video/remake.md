---
videomd: 1
part: remake
tokens: 3574
---

## Remake plan

### Step by step

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

**15 AI video shots → 4 generation units, 4 MiniMax H3 / H3 Max calls; still-image move / static frame 1 shot → rebuilt locally**

### Generation units

- **How it is generated**: multi-shot from key frames

| Part | Shots | Time | Length | Prepare |
|---|---|---|---|---|
| G1 | #1–#4 | 0.0–7.0s | generate 8s, trim to 7.0s | reference images + reference audio |
| G2 | #5–#7 | 7.0–16.1s | generate 10s, trim to 9.0s | reference images + reference audio |
| G3 | #8–#11 | 16.1–21.6s | 5.6s | reference images + reference audio |
| G4 | #12–#14, #16 | 21.6–27.9s, 28.2–28.5s | 6.6s | reference images + reference audio |

**Why it is split this way**

- Grouping: consecutive shots share a call where they fit, ≤10s per call, ≤4 shots; a long stretch is cut at a scene change first
- Inputs: the model also takes reference video, but key frames are used here: one key frame per shot fixes composition and look, swapped-in things get their own images
- Audio: the model can generate action sound effects and ambience along with the picture
- Packaging: the sticker on the generated shots is post-production packaging: keep it out of the prompts (erased from source references) and lay it back on from the packaging timeline after generation

**Frames to make first (15)**

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

**G1 · shots #1–#4 · 7.0s**

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

**G2 · shots #5–#7 · 9.0s**

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

**G3 · shots #8–#11 · 5.6s**

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

**G4 · shots #12–#14, #16 · 6.6s**

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

**Prompt guides for MiniMax H3 / H3 Max**

- https://huggingface.co/MiniMaxAI/MiniMax-H3/raw/main/docs/VIDEO_PROMPT_WRITING_GUIDE_base_en.md
- https://huggingface.co/MiniMaxAI/MiniMax-H3/raw/main/docs/VIDEO_PROMPT_WRITING_GUIDE_ref_en.md
- https://platform.minimax.io/docs/api-reference/video-generation-v2-create
- https://docs.comfy.org/tutorials/video/minimax/minimax-h3-prompt-guide.md

### Local rebuild

- #15 still image + pan/zoom 0.3s: one image + the measured zoom / pan parameters, rendered straight from ffmpeg
