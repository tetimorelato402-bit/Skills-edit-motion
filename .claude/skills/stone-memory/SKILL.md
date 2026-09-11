---
name: stone-memory
description: Run the Stone Memory pipeline for a faceless symbolic motion piece (OpenArt still, motion pass, VFX reveal, frame-accurate sync to a song cue, caption). Use when asked to make, continue, or ship a piece for this project, pick a song cue, render or verify a cut, or write a piece caption. Follows the standing instructions in CLAUDE.md.
---

# Stone Memory piece workflow

You are producing one short, symbolic, texture-driven motion piece. Read `CLAUDE.md` at the repo root first: it holds the standing instructions and the current piece brief. This skill turns those into the exact sequence to run. Never skip a step and never run them out of order.

Hard rules that apply at every step:

- All image and video generation goes through the OpenArt MCP connector. Confirm it is live with `openart_account_get` before any generation step. If it is unavailable, stop and say so. Do not substitute another generator.
- No text, captions, or logos inside generated images. Precision elements are composited in post.
- One timestamped audio cue per piece. If the reveal is not on that frame, the piece does not ship.
- No em dashes in any copy. Commas, colons, or parentheses instead.
- Do not import campaign mechanics (product, CTA, brand logic). Mood, symbol, craft.

## Step 0: research (fresh for every piece)

Search the web for current best-in-class work in each of these, then write `pieces/<piece>/research-YYYY-MM.md`:

1. macro / texture motion design
2. symbolic short film
3. sound-synced VFX reveals
4. whatever visual trend is dominant this month

For each source, cite the URL and write one line on what to borrow (a technique or a pacing choice) and one line on what not to copy (anything that is one artist's signature). Finish with three concrete decisions for this piece drawn from the research.

## Step 1: concept lock

Restate the story in one paragraph, in your own words: the symbolic meaning, what is hidden, when it reveals, why it is true (name the real fact behind it). If you cannot do it without hedging, ask Vanessa instead of generating. Record the paragraph in `pieces/<piece>/brief.md`. Wait for Vanessa's confirmation before step 2 unless the brief already says the concept is locked.

## Step 2: song selection

1. Get the track file from Vanessa (any ffmpeg-readable format).
2. List candidate cues: `python3 pipeline/cue.py <song> --fps 30`.
3. Choose one moment by ear: a key change, a drop, or the end of a silence. The tool ranks energy jumps; a key change may not rank, so trust listening.
4. Snap it: `python3 pipeline/cue.py <song> --snap <seconds>` and record `cue_time` and the song filename in `pieces/<piece>/brief.md`.

This timestamp is the target for every later step.

## Step 3: base image (OpenArt)

1. `openart_account_get` to confirm the connection.
2. `openart_model_list`, then `openart_model_form_get` for a text2image model suited to photoreal macro texture (avoid anime-leaning models for this project).
3. Write the prompt with the hidden detail composed in from the start: name the motif, its position in the frame (which stratum), and that it is rendered in nearly the same color as the surrounding rock. Ask for no text, no people, no logos. Use `.claude/skills/stone-memory/PROMPTS.md` as the prompt scaffold.
4. Generate a small batch, pick the still where the detail is invisible at a glance and clear when pointed at. Save it as `pieces/<piece>/base.png`. Note: the OpenArt CDN (`cdn.openart.ai`) is blocked by egress policy in the Claude Code web sandbox, so the bytes cannot be downloaded there. Show the result card with `openart_creation_show`, ask Vanessa to download the chosen still and upload it into the session, then save it.
5. Make `pieces/<piece>/mask.png` with `python3 pipeline/mask.py --image base.png --shape doorway --cx .. --cy .. --w .. --h .. --out mask.png`. It also writes `mask-overlay.png`; look at it and adjust the numbers until the orange shape sits exactly on the imprint. For a quick preview `render.py --region cx,cy,rx,ry` works without a mask.
6. Lock the still. Everything downstream references this file and nothing else.

## Step 4 and 5: motion pass and VFX layer

Both come from the preset, not from hand-tuned code:

1. Copy `pipeline/presets/default.json` values you want to change into `pieces/<piece>/preset.json` (only overrides, keep the file small). Set `duration` and `reveal_at` (where in the piece the cue lands, usually past the halfway point so the first viewing settles before the reveal).
2. For a silence cue, start from `"base": "reveal-silence"`.
3. Preview the motion silently: `python3 pipeline/render.py --image base.png --mask mask.png --cue <reveal_at> --preset pieces/<piece>/preset.json --size 540x960 --out pieces/<piece>/out/preview.mp4`.
4. Judge it against the animation skills in this repo: the push should be slow enough to read as time passing, the reveal easing must be ease-out (fast in, soft landing), the whole-frame flash must stay tiny, the light on the shape carries the reveal.

## Step 6: sync and assembly

```
python3 pipeline/render.py \
  --image pieces/<piece>/base.png --mask pieces/<piece>/mask.png \
  --audio <song> --cue <cue_time> \
  --preset pieces/<piece>/preset.json \
  --out pieces/<piece>/out/final.mp4
python3 pipeline/verify.py pieces/<piece>/out/final.mp4
```

`verify.py` must print `SYNC OK` with delta 0 frames on the video line. If it fails, fix the preset or the mask and re-render. Do not ship on a tolerance.

## Step 7: caption

Written last, after watching the final cut. One true sentence tied to what is actually on screen, built on the real fact from step 1. Save to `pieces/<piece>/caption.md`. Then add the caption as a composited text layer in post if it is meant to be on the video, never re-generate the image with text.

## Handoff to Vanessa

Report: the cue timestamp and frame, the verify output, the file paths, the caption, and the three research decisions you applied. Keep it short and free of em dashes.
