#!/usr/bin/env python3
"""Speech-onset detection for the ANVIL VO.

Spec (BRIEF.md): energy envelope, 15 ms window, threshold ~3% of peak,
merge bursts closer than 0.22 s, discard segments under 0.12 s as breaths.
"""
import subprocess, sys, json
import numpy as np

SR = 44100
WIN = 0.015          # 15 ms analysis window
THRESH_FRAC = 0.03   # 3% of peak window energy
MERGE_GAP = 0.22     # merge bursts closer than this
MIN_SEG = 0.12       # discard shorter than this (breaths)


def decode(path):
    raw = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", path, "-f", "f32le",
         "-acodec", "pcm_f32le", "-ac", "1", "-ar", str(SR), "-"],
        capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype="<f4").astype(np.float64)


def envelope(x):
    hop = int(round(WIN * SR))
    n = len(x) // hop
    frames = x[:n * hop].reshape(n, hop)
    return np.sqrt((frames ** 2).mean(axis=1)), hop


def segments(x):
    env, hop = envelope(x)
    peak = env.max()
    thr = THRESH_FRAC * peak
    active = env >= thr

    segs = []
    start = None
    for i, a in enumerate(active):
        if a and start is None:
            start = i
        elif not a and start is not None:
            segs.append([start * hop / SR, i * hop / SR])
            start = None
    if start is not None:
        segs.append([start * hop / SR, len(active) * hop / SR])

    merged = []
    for s in segs:
        if merged and s[0] - merged[-1][1] < MERGE_GAP:
            merged[-1][1] = s[1]
        else:
            merged.append(s)

    kept = [s for s in merged if s[1] - s[0] >= MIN_SEG]
    dropped = [s for s in merged if s[1] - s[0] < MIN_SEG]
    return kept, dropped, peak, thr


if __name__ == "__main__":
    path = sys.argv[1]
    x = decode(path)
    kept, dropped, peak, thr = segments(x)
    print(f"# {path}  dur={len(x)/SR:.3f}s  peakRMS={peak:.4f}  thr={thr:.5f}")
    print(f"# kept={len(kept)} dropped(<{MIN_SEG}s)={len(dropped)}")
    for i, (a, b) in enumerate(kept, 1):
        print(f"{i:>3}  {a:8.3f} → {b:8.3f}   ({b-a:5.3f}s)")
    if dropped:
        print("# dropped:", ", ".join(f"{a:.3f}-{b:.3f}" for a, b in dropped))
    json.dump([{"i": i, "start": round(a, 3), "end": round(b, 3)}
               for i, (a, b) in enumerate(kept, 1)],
              open(sys.argv[2], "w") if len(sys.argv) > 2 else sys.stdout, indent=2)
