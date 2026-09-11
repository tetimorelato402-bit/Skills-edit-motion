# Project: Faceless Symbolic Motion Art (working title: "Stone Memory")

## What this project is

A faceless, scalable content pipeline producing short, symbolic, texture-driven motion pieces. Each piece is a single still image (from OpenArt) that gets animated, scored to a song with a precise sync point, and layered with VFX so it rewards a second and third viewing.

The goal is not decoration: every piece must have a true, researchable meaning underneath it (geology, color theory, symbolism, psychology), not invented mysticism.

This is a different creative lane from any other Asther/marketing work in this account. Do not blend in campaign mechanics (product shots, CTAs, brand logic). This is mood, story, and craft first.

## Standing instructions (apply to every piece, not just the first)

1. **Research first.** Before generating anything, search the internet for current best-in-class reference work in: macro/texture motion design, symbolic short film, sound-synced VFX reveals, and whatever visual trend is dominant that month. Cite what you find and explain what specifically to borrow (technique, pacing, not literal copying of any artist's work). Do this fresh for every new piece, trends move fast. Save the notes as `pieces/<piece>/research-YYYY-MM.md`.
2. **OpenArt MCP only.** Connect to the OpenArt MCP connector for all image and video generation. Confirm the connection is live (`openart_account_get`) before starting generation steps. If OpenArt MCP is not available in a given session, stop and flag it rather than substituting another tool silently.
3. **Restate the story before prompting.** Before writing any prompt, restate the story back in your own words: the symbolic meaning, what's hidden, when it reveals, and why it's true (not decorative). If you can't explain the meaning in one paragraph without hedging, the concept isn't ready to generate yet, ask for clarification instead of guessing.
4. **Precision elements in post.** Composite precision elements (text, captions, logos if any) in post, never generate them directly. Same failure-mode logic as prior Asther creative work: generated text is unreliable.
5. **One timestamped audio cue per piece.** Every piece must be built around one specific, timestamped audio cue (a key change, a drop, a moment of silence). The visual reveal must be scripted to hit that timestamp exactly. If the sync isn't frame-accurate, the piece doesn't ship.

## Pipeline order (run in this sequence, every time)

1. **Concept lock.** Symbolic theme + material/texture world + what's hidden and why it's true. Confirm with Vanessa before moving on.
2. **Song selection.** Pick the track. Identify the exact timestamp of the reveal moment. This timestamp is the target for every step after this. Use `python3 pipeline/cue.py <audio>` to list candidate cues and snap the chosen one to a frame.
3. **Base image (OpenArt).** Generate the still with the hidden detail deliberately composed in from the start, not added later. Lock the winning still as the reference image for everything downstream (`pieces/<piece>/base.png` plus a mask of the hidden shape, `pieces/<piece>/mask.png`).
4. **Motion pass.** Animate the still (slow push/zoom, parallax, drift) so the reveal is motion-driven. Motion parameters live in preset JSON files (`pipeline/presets/`, overridden per piece in `pieces/<piece>/preset.json`) so they're reusable across future pieces, not hand-tuned one-off values.
5. **VFX layer.** Add the effect that sells the reveal (light catching the hidden shape, a crack opening, grain/chromatic shift), timed to the audio cue from step 2. The VFX timeline is expressed relative to the cue frame in the same preset.
6. **Sync + assembly.** Final cut: image + motion + VFX locked to the song's timestamp. Use ffmpeg/Python for frame-accurate assembly (`pipeline/render.py`), don't eyeball it. Run `pipeline/verify.py` on the output; it must report the reveal on the expected frame.
7. **Caption.** Written last, after the final cut exists, one true sentence of meaning tied to what's actually on screen (not a generic mystical caption). Save as `pieces/<piece>/caption.md`.

The `/stone-memory` skill in `.claude/skills/stone-memory/` walks through this sequence with the exact commands.

## Piece 1 brief: "What the Stone Remembers"

- **Theme:** memory and nostalgia, told through mineral time.
- **Visual world:** a cross-section of layered stone, sedimentary bands (agate, marble, banded rock). Each stratum reads as a different era.
- **The hidden detail:** buried in one deep layer is a faint, fossil-like imprint, a shape (hand, doorway, face, or another motif to decide) rendered nearly the same color as the surrounding rock so it's invisible on first viewing.
- **The reveal:** on rewatch, a crack opens and light catches the imprint. This is the frame-accurate sync point against the chosen song's key change or drop.
- **The true meaning (for the caption):** sedimentary rock is literally compressed time, each layer a physical record of a different era. Memory works the same way, it doesn't disappear, it gets buried under newer layers until something (light, a crack, a trigger) exposes it again. This is a real geological fact, not invented symbolism, use it straight.

**Status:** piece 1 cut rendered and verified against "Storms" by Fleetwood Mac (Tusk, 1979), 25 s from 1:08, reveal on piece frame 604 (song 88.133 s). Caption written. Awaiting Vanessa's review; see `pieces/01-what-the-stone-remembers/brief.md`. Piece files live in `pieces/01-what-the-stone-remembers/`. Song files go in `pieces/<piece>/audio/`, which is git-ignored (copyrighted tracks are never committed).

## Notes on account context

- This is separate from the "Cold Origin" campaign work elsewhere in this account. That work follows campaign mechanics (product, human moment, payoff beat). This project follows mood/symbol/craft mechanics. Do not mix the two frameworks.
- No em dashes in any written copy (captions, notes to Vanessa, commit messages, docs in this repo). Use commas, colons, or parentheses instead.

## Tooling in this repo

- `pipeline/install.sh` installs ffmpeg plus the Python dependencies (numpy, pillow).
- `pipeline/cue.py` finds candidate audio cues (drops, energy jumps, ends of silence) and prints them as timestamps and frame numbers.
- `pipeline/render.py` renders still + motion + VFX + audio into an mp4 with the reveal on an exact frame.
- `pipeline/verify.py` proves the sync: it reads the finished mp4 back and reports the first frame where the hidden shape lights up and the frame where the audio cue lands.
- `pipeline/synth.py` builds a synthetic banded-stone still, mask, and test track so the whole chain can be tested without spending OpenArt credits.
- `pipeline/test.sh` runs the whole chain end to end on synthetic assets.
- The design and animation skills in `.claude/skills/` (from emilkowalski/skills) apply to any UI work, not to the motion pieces themselves.
