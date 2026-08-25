# ANVIL — VO trim + onset map

## Trim

| | source | trimmed |
|---|---|---|
| first speech | 2.387 s | 0.135 s |
| last kept speech ends | 22.592 s ("…compounds.") | 20.355 s |
| duration | 26.593 s | **20.550 s** |

- Head cut at **2.250 s** (0.137 s of lead before the first word), 40 ms fade-in.
- Tail cut at **22.800 s**, 120 ms fade-out landing entirely in silence.
- Cut content: spoken *"Anvil"* (23.132–23.583) and *"Sharpen iron with iron."*
  (23.973–25.159). Nearest kept speech ends 0.33 s before the cut, so nothing
  is clipped.
- No stretch, no pitch shift, no repositioning. Working master is
  `audio/vo_trimmed.wav` (44.1 kHz mono, 24-bit); `vo_trimmed.mp3` is a
  convenience copy.

## Detector

Energy envelope, 15 ms RMS window, threshold 3 % of peak window energy,
bursts merged under 0.22 s, segments under 0.12 s discarded as breaths.
(`scripts/onsets.py`)

Result: **15 segments, 0 discarded.** Every source segment survives the trim
at exactly −2.250 s.

## Segments (trimmed timebase)

```
  1   0.135 →  1.051  (0.916s)     9  12.730 → 13.435  (0.706s)
  2   1.636 →  2.627  (0.991s)    10  13.931 → 14.186  (0.255s)
  3   2.882 →  4.038  (1.156s)    11  14.816 → 15.537  (0.721s)
  4   4.623 →  5.659  (1.036s)    12  15.987 → 16.858  (0.871s)
  5   6.095 →  7.115  (1.021s)    13  17.308 → 17.954  (0.645s)
  6   7.731 →  8.541  (0.811s)    14  18.464 → 19.049  (0.585s)
  7   9.307 → 10.388  (1.081s)    15  19.485 → 20.355  (0.871s)
  8  10.943 → 11.904  (0.961s)
```

## Line assignment

| screen | segs | onset | end | line |
|---|---|---|---|---|
| `01_onboard_name.svg` | 1 | 0.135 | 1.051 | "It starts with your name." |
| `02_onboard_phone.svg` | 2,3 | 1.636 | 4.038 | "Verified once." / "So your circle knows you're real." |
| `03_onboard_birthday.svg` | — | — | — | *(no line)* |
| `04_onboard_commitments.svg` | 4 | 4.623 | 5.659 | "Choose what you're committing to." |
| `05_onboard_places.svg` | 5 | 6.095 | 7.115 | "And exactly where you'll do it." |
| `06_home.svg` | 6 | 7.731 | 8.541 | "This is your word." |
| `07_tab_camera.svg` | 7 | 9.307 | 10.388 | "The camera stays locked." |
| `08_arrival_toast.svg` | 8 | 10.943 | 11.904 | "Until you actually arrive." |
| `09_camera_unlocked.svg` | 9 | 12.730 | 13.435 | "Then it opens." |
| `11_circle_live.svg` | 10,11 | 13.931 | 15.537 | "Proof," / "not words." |
| `10_friend_arrived.svg` | 12,13 | 15.987 | 17.954 | "Your circle sees it." / "And you see them." |
| `07_tab_routine.svg` | 14,15 | 18.464 | 20.355 | "Show up enough," / "and it compounds." |
| logo close | — | — | — | SILENT |
| tagline | — | — | — | SILENT |

11 spoken lines → 15 segments. The four extra splits are the internal
sentence/comma breaks in lines 02, 11_circle_live, 10_friend_arrived and
07_tab_routine, confirmed against a word-level pass (`scripts/substructure.py`).

## Gaps available between lines

```
before 02  0.585    before 08  0.555    before 10_friend  0.450
before 04  0.585    before 09  0.826    before routine    0.510
before 05  0.436    before 11  0.496
before 06  0.616
before 07  0.766
```

The two widest gaps (0.766 s before "The camera stays locked", 0.826 s before
"Then it opens") sit exactly at the Act 2 and Act 3 doors — the hero beat has
the most room in the read.
