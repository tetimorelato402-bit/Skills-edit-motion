# Anvil — the UI

Anvil is on TestFlight. This is the design pass over it: the whole spine of the
app, tightened where it existed and designed where it did not, delivered as a
slideshow so the shape of the product can be seen in one sitting.

`build.sh` rebuilds everything in about a minute.

| | |
|---|---|
| `source/screens.html` | All 23 screens. One artboard each, 393 x 852 CSS px. |
| `source/shoot.py` | Screenshots them at deviceScaleFactor 3 -> 1179 x 2556. |
| `source/slideshow.py` | Builds the deck and encodes `outputs/anvil-slideshow.mp4`. |

## The screens are 1:1 with the device

393 x 852 at 3x is 1179 x 2556, which is exactly what the TestFlight screen
recording is. So a measurement taken off one of these is a number that can be
typed into SwiftUI without scaling anything. That is the point of building them
in HTML at real metrics rather than drawing them.

## The palette is measured, not chosen

Sampled off the recording, not invented:

| | |
|---|---|
| bone | `#E3DACD` — the page |
| card | `#EEE9DE` — every raised surface |
| ink | `#231C15` — type, buttons, the tab bar |
| gold | `#9E7C52` — streaks, the active tab, the numerals |
| rust | `#9A3B21` — **new.** A Miss. |

**There is no green and no iOS red.** A kept day is INK, the strongest mark bone
can carry; a broken one is rust. The first pass used a success-green for hits and
the boards came out looking like a fitness tracker — a whole screen of it in the
streak grid. A stock red in this room reads as an error dialog rather than as a
broken promise. Four warm colours, and the record grid ends up looking like
something printed.

## What was tightened

- **The gold dash in Standings was a placeholder.** It is a streak number now,
  with the unit under it, and a seven-day strip under each name — a number says
  how long, the strip says how it is going.
- **"The deal" was one long paragraph** in the commitment sheet. It is three
  numbered clauses now. They are terms, so they are set as terms.
- **The map was raw Apple Maps** — blue ocean, a Legal link, the one rectangle in
  the app that belonged to somebody else's design. It is drawn now: bone streets,
  an ink pin, a dashed 150m ring.
- **Tab bar kept.** The floating dark bar with gold labels and an underline on the
  active tab was already the best thing in the build. Only the icons and the
  label tracking changed.

## What did not exist yet

The Miss, the week board, the streak page, the circle, the invite, a member's
profile, the routine, the commitment detail, your own record, settings, and a
plain-language page for what Anvil knows. Thirteen of the twenty-three.

## The slideshow

70 seconds, 1080x1920, seven section cards and twenty-three screens. Held 2.6s
each, a five-frame dissolve inside a section and a hard cut on the section cards.
No push-ins and no 3D device tilts: teti asked for a deck, not a showreel, and an
effect here would only be something in front of the screens.

It is **silent on purpose** — put a track under it in the Reel editor.

## Gotchas paid for

- **`.body` was both the screen container and the paragraph class.** Every
  paragraph inherited `position:absolute; inset:0` and rendered on top of the
  status bar, on ten screens at once. It looks like a layout bug and it is a
  namespace bug.
- **A week strip on a dark card has to invert.** Once a hit became ink, every hit
  inside the ink "due today" card vanished into the card it was printed on.
  `.on-ink` flips them to bone.
- **`primitive` caption + a 704px shot is 1844px in a 1828px column**, so the
  home bar was sliced off the bottom of every screen in the deck. 648px fits.
- **PIL cannot open woff2.** The slide captions have to be set in the app's own
  faces, so the slides are built in HTML and screenshot rather than composited.
- **Frames are piped to the encoder, never written out.** 2109 frames of
  1080x1920 PNG is a couple of gigabytes and this container's writable
  allowance is not that big.

## Open questions for the next pass

1. **Camera in the tab bar.** It is a verb sitting between two nouns. It may
   belong as a button on Routine's "due today" card instead, which is where the
   intent actually starts.
2. **Home vs Routine.** Home is the circle's board, Routine is your own list.
   Those are two different apps' worth of home screen; one of them may be the
   real one.
3. **What a Miss costs.** Right now it zeroes a streak and is announced. Whether
   there is anything past shame — a forfeit, a handicap — is a product decision
   and it changes the Miss screen.
