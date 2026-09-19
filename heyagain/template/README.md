# hey again. — the social template

One motion system, two outputs, eight decks. Orange field, cream Inter, the 3D dot as the
full stop of the wordmark. No stock photography.

## The decks

Everything maps back to the three product categories. The stranger deck is never called
that on camera — it ships as **general questions**.

| deck | category | theme card |
|---|---|---|
| `partner` | couple | questions for / your partner |
| `situationship` | couple | questions for / your situationship |
| `someonenew` | couple | questions for / someone new |
| `ex` | ex | questions for / your ex |
| `gotaway` | ex | questions for / your almost |
| `general` | general | a round of / general questions |
| `firstdate` | general | questions for / a first date |
| `bestfriend` | general | questions for / your best friend |

Five questions per deck, forty in total, all distinct — `decks.py` asserts it, because a
duplicate would quietly ship as the same slide in two different posts.

## The reel — `reel.py`

1080×1920, 30fps, 18–22s depending on question length.

A white sphere drops in, bounces twice, then shrinks onto the exact pixel where the
period of `hey again.` sits and the wordmark fades up around it. The theme card rises,
three questions type at 10 characters/second, then the dot climbs back out of the foot of
the last `?`, arcs across, and rebuilds the wordmark over `play now for free.`

```
DECK=partner python3 reel.py
```

Renders to `v6/heyagain_reel_<deck>.mp4`. Eight run in parallel safely — the dot asset,
frame directory and audio track are all keyed per deck.

## The carousel — `carousel.py`

2160×2700 (4:5), seven PNGs per deck:

| slide | content |
|---|---|
| 1 | `hey again.` with the topic line under it — *questions for your partner* |
| 2–6 | the five questions |
| 7 | `hey again.` with *play now with a friend for free.* |

Slides 1 and 7 are deliberately the same lockup: the post opens on the brand and closes
on it, and only the line underneath changes. Both are centred on the same optical line as
the question slides (45.5% of frame height), measured rather than assumed, so the seven
slides read as one set instead of the ends floating high.

```
python3 carousel.py
```

## The sound — `sfx.py`

Every keystroke is drawn from a bank of 14 synthesised variants (body pitch 148–236 Hz,
wood resonance 760–1480 Hz, randomised bandwidth and decay) at its own velocity. One
cached clack repeated per letter is what made the first pass sound like a machine.

The strike is low-passed, not differentiated. A differentiated noise burst adds
+6 dB/octave and is what gave the early version its plasticky edge.

Levels live in one place, `reel.py:SFX_LEVELS`. The shipped setting puts the typing at
roughly −17 dBFS — under the read rather than over it.

## Why the layout is measured, not calculated

ffmpeg's `drawtext` anchors `y` to the drawn string's own ink bounding box, not to the
font ascender. Two strings at the same `y` with different ascenders do not share a
baseline. So the dot's resting position is found by rendering the glyph white-on-black
and scanning the raw gray plane for it (`measure.py`), and advance widths come straight
out of the font's `hmtx`/`cmap` tables (`fontmetrics.py`). Pillow and numpy are not
installable in the build sandbox.

## Dependencies

A static ffmpeg under `tools/`, headless Chromium for the sphere, and
`assets/Inter-Medium.ttf`. Nothing from pip.

## Known inconsistency

The carousel closes on *play now with a friend for free.* The reels still close on
*play now for free.* — they were rendered before that line was settled. Re-rendering the
eight reels is the fix; it takes about six minutes.
