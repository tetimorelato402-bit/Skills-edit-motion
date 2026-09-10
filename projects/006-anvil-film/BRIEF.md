# Anvil — "Sit still. Keep up."

A brand film for **Anvil**, the app designed in `projects/005-anvil/`. Not teti's studio
work and not in teti's palette — this uses Anvil's own.

## The idea

**The ad is a test, and the viewer either passes it or does not.**

Text types out and *accelerates* until it cannot be read, while the film pulls the eye
away — and what pulls it away is **the Anvil app itself**. Being distracted by the product
is the joke and the sell in one move, and it means the ad carries real product footage
without stopping for a demo.

**14.0 s — 7 bars at 120 BPM.** Direct, not narrated.

| bar | |
|---|---|
| 1–1.5 | **GET READY.** SIT STILL. / KEEP UP., then 3 · 2 · 1 on the beat. The "1" is rust. |
| 1.5–5.25 | **THE TEST.** Five pages, 16 → 62 characters per second, a different typeface each. |
| 5.25–5.75 | **THE PAUSE.** One second. Nothing on screen, nothing in the speakers. |
| 5.75–6.5 | **THE PAYOFF.** "Don't sit still." typed slowly, alone. |
| 6.5–7 | ANVIL. *Pick a task. Choose your friends.* |

## Four rules, all load-bearing

1. **The distractions are EDITS, not objects.** Jump cuts, flash frames, zoom punches,
   stutters in the type, ghost doubles, and the app cutting in on the beat. A drifting
   shape is decoration; a cut is something a motion editor did on purpose, and it reads
   as craft rather than as clutter. This replaced an earlier pass of floating dots.
2. **Nothing obscures the text for longer than a blink.** The distraction layer is built
   *before* the type so it cannot paint over a word, every full-frame event is capped at
   two frames, and the device sits in one of four slots that are all outside `SAFE`. The
   device is 1279 px tall, so any top edge between `SAFE.y-1279` and `SAFE.y+SAFE.h`
   crosses the sentence — one pass put it at y=120 and it sat straight over the words.
3. **Every event lands on the 120 BPM grid.** Off-grid motion reads as an accident rather
   than as pressure, and this film has to feel deliberate.
4. **The film stops.** A full second of nothing, at −72 dB against a −15.7 dB build — a
   56 dB cliff. Everything before it is spent buying that second.

## The sound is three stages, and the design is in the sync

- **LOCKED** — one key per character, on the frame the letter appears. The viewer learns
  that sound and picture are the same clock without being told.
- **UNLOCKED** — from the speed-up the keys run progressively late (a smooth curve to
  ~165 ms), some doubling, some dropped. Breaking a sync the viewer has *already learned*
  is far more disorienting than noise, because they can hear that it is wrong. Random
  jitter would just read as a broken render.
- **DEAD** — the pause, inside one frame.

## Load-bearing detail

- **RUST is the app's colour for a Miss**, so every distraction in the film is rust: the
  antagonist wears the product's own failure state. Palette sampled off the app —
  bone `#E3DACD`, ink `#231C15`, gold `#9E7C52`, rust `#9A3B21`, card `#EEE9DE`.
- **The type auto-fits to one size per register.** Sizing each page to its own longest
  line makes the type jump between pages, which reads as sloppy rather than as emphasis.
- **Palette constants are declared at the top of the file.** The type is built before the
  distraction layer, so a `const` declared down there is in the temporal dead zone when
  the instruction line asks for `INK` — and the file then fails to define `renderFrame`
  at all, which looks exactly like a render hang rather than like an error.
- **`render.py` decodes the app screens before the first screenshot.** An `<img>` assigned
  mid-render paints nothing on the frame it appears on, and a cut landing on a
  half-decoded screen is invisible in the log.
- **Fonts are self-hosted** — Inter, IBM Plex Mono, Playfair — for 003's reason.

## Open

1. **Anvil's logotype.** The end card sets the name in Inter; a real mark should replace it.
2. **The copy is mine, from the product facts in `005-anvil/BRIEF.md`.** teti should
   rewrite it in Anvil's voice — the type auto-fits, so new copy cannot break the layout.
