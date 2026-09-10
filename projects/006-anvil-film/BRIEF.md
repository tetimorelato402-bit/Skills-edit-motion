# Anvil — "Sit still. Keep up."

A brand film for **Anvil**, the app designed in `projects/005-anvil/`. Not teti's studio
work and not in teti's palette — this uses Anvil's own.

Delivered: **`anvil-v4.mp4`**, 1080×1920, 14.0 s, 30 fps, 1.9 MB, −14.3 LUFS / −1.7 dBFS.

## The idea

**The ad is a test, and the viewer either passes it or does not.**

Text types out and *accelerates* until it cannot be read, while the film pulls the eye
away — and what pulls it away is **the Anvil app itself**. Being distracted by the product
is the joke and the sell in one move, and it means the ad carries real product material
without ever stopping for a demo.

**14.0 s — 7 bars at 120 BPM.** Direct, not narrated.

| time | |
|---|---|
| 0.0–2.5 | **GET READY.** SIT STILL. wide / KEEP UP. squeezed, then 3 · 2 · 1 on the beat. The "1" is rust. |
| 2.5–3.0 | **KEEP UP.** reversed out of full-frame ink, held, so the film cuts *into* the test off a hard frame. |
| 3.0–10.5 | **THE TEST.** Five pages, 16 → 62 characters per second, a different typeface each. |
| 9.75–10.5 | **THE REDACT.** The words stop being words: the face switches to Redacted mid-sentence. |
| 10.5–11.5 | **THE PAUSE.** One second. A blinking caret, and nothing in the speakers. |
| 11.5–13.0 | **THE PAYOFF.** "Don't sit still." typed slowly, alone. |
| 13.0–14.0 | **The mark.** *Anvil*, and nothing said over it. |

## Six rules, all load-bearing

1. **The distractions are EDITS, not objects.** Jump cuts, flash frames, zoom punches,
   stutters in the type, ghost doubles, a chromatic split, a full-frame negative, a
   letterbox slam, a wipe crossing frame. A drifting shape is decoration; a cut is
   something a motion editor did on purpose, and craft is the thing being sold. This
   replaced an earlier pass of floating dots.
2. **Nothing obscures the text for longer than a blink.** The distraction layer is built
   *before* the type so it cannot paint over a word, every full-frame event is capped at
   two or three frames, and no card may enter `SAFE`.
3. **Every event lands on the 120 BPM grid**, and nothing is off a sixteenth (0.125 s).
   Off-grid motion reads as an accident rather than as pressure.
   `scripts/check-sync.py` is what proves it, and it fails loudly.
4. **The UI is SIMPLIFIED AND ENLARGED, never a screenshot of a whole phone.** A 590 px
   screen dropped into a 1080 frame is a picture of an app; one row of it at 3× is the
   app speaking. Every word on these cards is real copy off a real screen — *A MISS / Joe
   missed the Dining Hall*, *Barrios · Gym · no misses · 24 WEEKS*, *◆ VERIFIED*,
   *51.5074, 0.1278 · 13:41*, *POST THE PROOF*, *Once it is posted it cannot be deleted*,
   *Who is holding you to it?* — and the photographs are the app's own check-in proofs.
   Other people, who actually did the thing. That is what the product is.
5. **The type breathes.** Size swings page to page (a 96 px ceiling against a 210 px one)
   and word to word inside a line, so reading it is never a steady state. Emphasis is set
   *into* the sentence as per-token scale rather than applied to it, which is why the size
   can swing without the line re-flowing or the baseline moving.
6. **The film stops**, and it closes on the mark alone. A full second of nothing at
   −72.3 dB against a −11.5 dB build — a **61 dB cliff**. Everything before it is spent
   buying that second.

## The readout

A reading test with no instruments is just text moving. A HUD carries the premise: the
name top-left, the **speed in characters per second** top-right, a page count and a bar
filling along the bottom. The speed goes rust the moment it passes readable. The readout
is also the thing that **gives up first** — at the redact it drops to `-- CPS` and starts
dropping frames, so the film admits the test broke before the viewer has to.

## The sound is four stages, and the design is in the sync

- **LOCKED** — one key per character, on the frame the letter appears. The viewer learns
  that sound and picture are the same clock without being told.
- **UNLOCKED** — from the speed-up the keys run progressively late (a smooth curve to
  ~165 ms), some doubling, some dropped. Breaking a sync the viewer has *already learned*
  is far more disorienting than noise, because they can hear that it is wrong. Random
  jitter would just read as a broken render.
- **REDACTED** — the picture stops making letters, so the keyboard stops making letter
  sounds: same rhythm, dull and wide, nothing left in it, over a failing sweep.
- **DEAD** — the pause, inside one frame.

Every other cue is a **motion**, not a musical event: a card landing, a shutter for each
person arriving, a knock for the letterbox, a burst for the negative, a travelling sweep
for the wipe. Zoom punches and jump cuts are **deliberately silent** — a film where every
edit has a sound has no accents left.

## Load-bearing detail

- **RUST is the app's colour for a Miss**, so every distraction in the film is rust: the
  antagonist wears the product's own failure state. Palette sampled off the app —
  bone `#E3DACD`, ink `#231C15`, gold `#9E7C52`, rust `#9A3B21`, card `#EEE9DE`.
  There is no green and no iOS red anywhere.
- **The end card is the logo and nothing else.** It is set in the app's own serif, so the
  ad closes on the literal mark rather than on an ad's idea of one. A tagline under a
  wordmark is the sound of not trusting the work; an earlier cut had one and it went.
- **The negative is differenced against WARM WHITE, not white.** Bone comes back as a dark
  warm brown and ink as bone — the film's own two colours swapping. Against pure white the
  ground inverts to a cold navy, a colour that appears nowhere in the product.
- **The photo-in-type is a duotone plate, not the photograph.** Poured into letterforms at
  Reel size the raw check-in photo reads as "the text went pale grey". `scripts/fillplate.py`
  remaps it INK → GOLD with the contrast stretched first, so it stays a photograph and the
  frame stays in the family.
- **Every typeface is self-hosted** — Archivo, Big Shoulders, Bebas Neue, Instrument Serif,
  Redacted, Inter, IBM Plex Mono — for 003's reason, and `render.py` loads each one
  explicitly before the first screenshot because `document.fonts.ready` resolves happily
  without a face that is not used until second 9.
- **No grain.** 001's noise pass costs 5 MB and softens a film whose brief is *crisp*.
  Grain belongs to the painted world, not to this one.

## Open

1. **Anvil's logotype.** The end card sets the name in Instrument Serif, matching the app's
   own headers. A real drawn mark should replace it when there is one.
2. **The copy is mine, from the product facts in `005-anvil/BRIEF.md`.** teti should
   rewrite it in Anvil's voice — the type auto-fits, so new copy cannot break the layout.
