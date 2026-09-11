# Piece 1: "What the Stone Remembers"

**Status:** song chosen (step 2 in progress). Waiting on the audio file to lock the cue timestamp.

## Concept (step 1, locked)

Theme: memory and nostalgia, told through mineral time.

Visual world: a cross-section of layered stone, sedimentary bands (agate, marble, banded rock). Each stratum reads as a different era.

Hidden detail: buried in one deep layer is a faint, fossil-like imprint, a shape (hand, doorway, face, or another motif to decide) rendered nearly the same color as the surrounding rock so it is invisible on first viewing.

Reveal: on rewatch, a crack opens and light catches the imprint. This is the frame-accurate sync point against the chosen song's key change or drop.

## The story, restated

Sedimentary rock is compressed time: every band was once a surface, then got buried under the next one, and the whole stack is a physical record of eras in order. Memory behaves the same way. It does not vanish, it is buried under newer layers, and it stays legible until something (light, a crack, a trigger) exposes it again. In this piece the stone is the mind, the strata are years, and the imprint is a specific memory that was always there. The crack is the trigger, the light is recall, and the sync point is the instant the song itself changes, so the viewer's own body feels the trigger at the same time as the stone does. None of this is invented: stratigraphy is how geologists read time, and that is the fact the caption will rest on.

## Open decisions

- Motif: doorway (a threshold you once passed through) is the current lead because it composes cleanly as a void in a band and generators render it reliably. Hand and face remain options. Decide before step 3.
- Cue timestamp: needs the audio file, see step 2 record below.

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
- `cue_time` (snapped): _pending the file_
- Cue frame at 30 fps: _pending the file_

## Files

- `research-2026-09.md`: reference research for this piece (standing instruction 1).
- `preset.json`: motion and VFX overrides for this piece.
- `base.png`, `mask.png`: the locked OpenArt still and its hidden-shape mask (step 3, not yet made).
- `out/final.mp4` and `out/final.sync.json`: the finished cut and its sync record (step 6).
- `caption.md`: written last (step 7).
