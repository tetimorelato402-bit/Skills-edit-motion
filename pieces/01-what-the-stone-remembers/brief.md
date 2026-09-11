# Piece 1: "What the Stone Remembers"

**Status:** cue locked (step 2 done), motif locked: doorway. Step 3 (base still) in progress.

## Concept (step 1, locked)

Theme: memory and nostalgia, told through mineral time.

Visual world: a cross-section of layered stone, sedimentary bands (agate, marble, banded rock). Each stratum reads as a different era.

Hidden detail: buried in one deep layer is a faint, fossil-like imprint, a shape (hand, doorway, face, or another motif to decide) rendered nearly the same color as the surrounding rock so it is invisible on first viewing.

Reveal: on rewatch, a crack opens and light catches the imprint. This is the frame-accurate sync point against the chosen song's key change or drop.

## The story, restated

Sedimentary rock is compressed time: every band was once a surface, then got buried under the next one, and the whole stack is a physical record of eras in order. Memory behaves the same way. It does not vanish, it is buried under newer layers, and it stays legible until something (light, a crack, a trigger) exposes it again. In this piece the stone is the mind, the strata are years, and the imprint is a specific memory that was always there. The crack is the trigger, the light is recall, and the sync point is the instant the song itself changes, so the viewer's own body feels the trigger at the same time as the stone does. None of this is invented: stratigraphy is how geologists read time, and that is the fact the caption will rest on.

## Open decisions

- Motif: doorway, confirmed by Vanessa.
- Cue: locked, see step 2 record below.

## Step 2 record

- **Song:** "Storms", Fleetwood Mac, from Tusk (1979), written and sung by Stevie Nicks, album version 5:31 ([Wikipedia](https://en.wikipedia.org/wiki/Storms_(Fleetwood_Mac_song))). Confirmed by Vanessa.
- **Why it is true for this piece:** the song's line "I have always been a storm" meets the stone on real ground. Geologists call a storm-laid sediment bed a tempestite: a violent event that ends as one quiet, permanent layer in the rock record ([Wikipedia: Tempestite](https://en.wikipedia.org/wiki/Tempestite), [Geological Digressions](https://www.geological-digressions.com/storm-surges-and-tempestites/)). The strata in the still are literally the remains of past storms, and the imprint is what one of them buried. That is the fact the caption can rest on alongside stratigraphy as compressed time.
- **Cue kind:** this song has no hard drop, it is a slow, quiet ballad, so the cue will be a lift, not a transient. Listen for these moments and pick one by ear:
  1. The first chorus arriving on "every night that goes between", the first time the full band lifts under the vocal.
  2. The line "never have I been a blue calm sea, I have always been a storm", the sentence that names the piece's fact. The cue frame is the downbeat of "storm".
  3. The end of the last held vocal before the outro, if the reveal should feel like something surfacing after the voice goes.
  The lead candidate is 2. It is the most specific moment in the song and the one the caption can quote without a stretch.
- **Preset base:** because the cue is a lift rather than a hit, start from `"base": "reveal-silence"` (no crack draw on a transient, light rises out of the strata) and re-enable a slow crack if it reads better in preview. Keep the chromatic split at 0; a channel split on a soft ballad reads as a glitch.
- **Audio file:** put it at `pieces/01-what-the-stone-remembers/audio/storms.wav` (or .mp3 / .m4a / .flac). That folder is git-ignored: the track is copyrighted and must not be committed.
- **Then run:**
  ```
  python3 pipeline/cue.py pieces/01-what-the-stone-remembers/audio/storms.wav --fps 30
  python3 pipeline/cue.py pieces/01-what-the-stone-remembers/audio/storms.wav --snap <chosen seconds>
  ```
  The ranked list will surface the lifts (the "step" column shows the level change); the exact frame for a lyric cue still comes from listening, then `--snap`.
- **Window chosen by Vanessa:** 25 seconds of the song starting at 1:08 (68.0 s to 93.0 s). The piece is 25 s long.
- **Cue analysis** (`cue.py --start 68 --end 93`): the window has no drop, the candidates fall on bar lines. The strongest full-band lift, where bass, mids and highs all step up together (about +9.7 dB over the previous quarter second), is at 88.12 s. It is late enough in the window that the first viewing settles before the reveal, and leaves about 4.9 s of lit imprint before the end.
- `cue_time` (snapped): **88.133333 s** (song frame 2644 at 30 fps, 9.3 ms from the raw detection)
- `reveal_at` in the piece: **20.133333 s** = piece frame **604**. Song start offset = 68.0 s exactly.
- Audio file in use: `audio/storms.mp3` (Storms, 2015 Remaster, 5:30.8, git-ignored).

## Step 3 record

- OpenArt connection confirmed live before generating (Pro plan).
- Generation: GPT Image 2.5 Sunburst, text2image, 9:16, 2k tier, quality high, 2 images, historyId `g4c4bmpOfmRQdViogb8u`, output 1296x2304 png.
- Prompt used: the PROMPTS.md scaffold with material "banded sedimentary stone", motif "simple arched doorway" in a wide dark-umber stratum, lower third, slightly right of centre, about one sixth of the frame width, same colour and value as the band, no cracks and no highlights on the imprint yet.
- The sandbox cannot download from `cdn.openart.ai` (egress policy), so the chosen still is downloaded from the OpenArt result card by Vanessa and uploaded, then saved as `base.png`.
- Dry run of the full 25 s cut with the real song on the synthetic stone: `verify.py` reports the reveal on frame 604, delta 0. The timing is proven before the real still is in.

## Files

- `research-2026-09.md`: reference research for this piece (standing instruction 1).
- `preset.json`: motion and VFX overrides for this piece.
- `base.png`, `mask.png`: the locked OpenArt still and its hidden-shape mask (step 3, not yet made).
- `out/final.mp4` and `out/final.sync.json`: the finished cut and its sync record (step 6).
- `caption.md`: written last (step 7).
