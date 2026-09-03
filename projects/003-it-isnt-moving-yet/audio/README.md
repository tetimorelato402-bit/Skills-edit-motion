# The track, and why every number in the film comes from it

`gracias-a-ti-129.mp3` — Luifer, *Gracias a Ti* (beat). Supplied by teti. **Not
teti's work**: it is a third-party beat, so it is gitignored here and the rights
question belongs to whoever posts the film, not to this repo.

## Measured, not assumed

| | |
|---|---|
| tempo | **129.000 BPM** exactly — beat `0.46512s`, bar `1.86047s` |
| grid phase | first beat at **0.043s**; downbeats at `0.043 + n × 1.86047` |
| length | 141.91s = 76 bars |

Tempo was fitted by combing the spectral-flux onset envelope against candidate
grids over 20–120s and taking the (BPM, phase) with the highest mean onset
energy on beat. It came out at 129.000, matching the filename to three decimals,
and the phase was then pinned by the fact that both silences END exactly on a
downbeat.

## The film uses bars 25–52 — track **46.555s → 96.787s**

That is the loudest, fullest 27 bars in the track, and it contains **both** of
its breaks. The film is 27 bars, so the window is exact.

## The two breaks are the film's structure

Neither is a fade, and both END on a downbeat — which is what makes them edit
points rather than atmosphere. They are not the same KIND of break, though, and
the difference is worth keeping straight:

| break | track | beats | film | kind | what it is |
|---|---|---|---|---|---|
| 1 | 64.240 → 67.020 (2.780s) | **138 → 144**, six beats | `bt(38)` → `bt(44)` | **sample-exact digital silence** | THE PETAL FALLS |
| 2 | 87.460 → 89.280 (1.820s) | **188 → 192**, four beats | `bt(88)` → `bt(92)` | musical drop-out, about −38 dBFS | IT CALMS DOWN |

Break 1 is a true stop: the file is zero. Break 2 is the arrangement pulling out,
which still reads as silence against the bar either side of it but is not one.
That is why `track.py` reports the two separately — searching only for digital
zero finds break 1 and misses the film's whole second half.

So the petal lets go on the last beat of music there is, falls through six beats
of nothing, and the music comes back on the downbeat that detonates the studio.
The film did not have that beat imposed on it — the track already had it, and the
film was moved onto it.

## Consequences for anyone editing

- **The grid is 129, not 125.** `BPM` in `plant.py` and in `video.html` are the
  only two places it lives, and every section boundary in both is written in
  `bt()`, so changing that one number re-times the whole film correctly.
- **`DETACH` and the studio's start are not free.** They are `bt(37)`–`bt(38)`
  and `bt(44)`, because that is where the silence is. Moving them means
  re-deriving them from the audio, not choosing new ones.
- **A sixteenth is now `0.11628s`**, not 0.12. Nothing may be re-timed to a value
  that is not a multiple of it.

## Rebuild the analysis

```sh
python3 scripts/track.py audio/gracias-a-ti-129.mp3
```
