#!/usr/bin/env python3
"""Find candidate sync cues in a song: drops, energy jumps, ends of silence.

Usage:
    python3 pipeline/cue.py song.mp3                 # top candidates
    python3 pipeline/cue.py song.mp3 --fps 30 --top 8
    python3 pipeline/cue.py song.mp3 --snap 47.31    # snap a chosen time to a frame

The chosen timestamp is the target for every downstream step. Always snap it
with --snap and record the printed frame-aligned value in the piece preset so
render.py and verify.py work from the exact same number.
"""

from __future__ import annotations

import argparse

import numpy as np

from common import decode_audio_mono, frame_to_seconds, seconds_to_frame


def rms_envelope(x: np.ndarray, sr: int, hop_ms: float = 10.0) -> tuple[np.ndarray, float]:
    hop = max(1, int(sr * hop_ms / 1000.0))
    n = len(x) // hop
    if n == 0:
        return np.zeros(1, dtype=np.float32), hop / sr
    frames = x[: n * hop].reshape(n, hop)
    rms = np.sqrt(np.mean(frames.astype(np.float64) ** 2, axis=1) + 1e-12)
    return rms.astype(np.float32), hop / sr


def find_candidates(x: np.ndarray, sr: int, window_s: float = 0.25,
                    min_gap_s: float = 1.0, top: int = 8) -> list[dict]:
    rms, hop_s = rms_envelope(x, sr)
    db = 20.0 * np.log10(rms + 1e-9)
    w = max(1, int(window_s / hop_s))

    # Contrast: mean level in the window after each point minus the window before.
    # A drop, a hit, or a re-entry after silence all produce a large positive step.
    csum = np.concatenate([[0.0], np.cumsum(db)])
    idx = np.arange(w, len(db) - w)
    after = (csum[idx + w] - csum[idx]) / w
    before = (csum[idx] - csum[idx - w]) / w
    contrast = after - before

    # Onset sharpness: how much the level rises across just a couple of hops.
    # Rewards a hard transient at the exact point rather than a slow swell.
    sharp = db[idx + 1] - db[idx - 1]

    score = contrast + 0.5 * np.clip(sharp, 0, None)

    order = np.argsort(score)[::-1]
    picked: list[dict] = []
    min_gap = int(min_gap_s / hop_s)
    for o in order:
        i = int(idx[o])
        if any(abs(i - p["_hop"]) < min_gap for p in picked):
            continue
        # Refine to the hop with the steepest rise inside +-window so the cue
        # sits on the transient itself, not on the centre of the contrast window.
        lo, hi = max(1, i - w), min(len(db) - 1, i + w)
        local = db[lo + 1:hi + 1] - db[lo - 1:hi - 1]
        j = lo + int(np.argmax(local))
        kind = "re-entry after silence" if before[o] < -45 else "energy jump / drop"
        picked.append({"_hop": i, "time": j * hop_s, "score": float(score[o]),
                       "before_db": float(before[o]), "after_db": float(after[o]),
                       "kind": kind})
        if len(picked) >= top:
            break
    return picked


def find_silences(x: np.ndarray, sr: int, thresh_db: float = -50.0,
                  min_len_s: float = 0.3) -> list[tuple[float, float]]:
    rms, hop_s = rms_envelope(x, sr)
    db = 20.0 * np.log10(rms + 1e-9)
    quiet = db < thresh_db
    out = []
    start = None
    for i, q in enumerate(quiet):
        if q and start is None:
            start = i
        elif not q and start is not None:
            if (i - start) * hop_s >= min_len_s:
                out.append((start * hop_s, i * hop_s))
            start = None
    if start is not None and (len(quiet) - start) * hop_s >= min_len_s:
        out.append((start * hop_s, len(quiet) * hop_s))
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("audio")
    ap.add_argument("--fps", type=float, default=30.0, help="frame rate of the piece (default 30)")
    ap.add_argument("--top", type=int, default=8)
    ap.add_argument("--snap", type=float, default=None, help="snap this timestamp (s) to the nearest frame and exit")
    ap.add_argument("--sr", type=int, default=22050)
    args = ap.parse_args()

    if args.snap is not None:
        n = seconds_to_frame(args.snap, args.fps)
        t = frame_to_seconds(n, args.fps)
        print(f"cue {args.snap:.4f}s -> frame {n} @ {args.fps:g}fps = {t:.6f}s  (delta {1000*(t-args.snap):+.1f} ms)")
        print(f"put this in the piece preset:  \"cue_time\": {t:.6f}")
        return

    x = decode_audio_mono(args.audio, sr=args.sr)
    dur = len(x) / args.sr
    print(f"{args.audio}: {dur:.2f}s, analysing at {args.sr} Hz, piece fps {args.fps:g}\n")

    cands = find_candidates(x, args.sr, top=args.top)
    print(f"{'#':>2}  {'time':>9}  {'frame':>6}  {'before':>7}  {'after':>7}  {'step':>6}  kind")
    for k, c in enumerate(cands, 1):
        n = seconds_to_frame(c["time"], args.fps)
        print(f"{k:>2}  {c['time']:>8.3f}s  {n:>6}  {c['before_db']:>6.1f}dB  {c['after_db']:>6.1f}dB  "
              f"{c['after_db']-c['before_db']:>+5.1f}  {c['kind']}")

    sil = find_silences(x, args.sr)
    if sil:
        print("\nsilences (>= 0.3s): a reveal can also land on the END of one")
        for a, b in sil[:10]:
            print(f"   {a:8.3f}s -> {b:8.3f}s  ({b-a:.2f}s)   end = frame {seconds_to_frame(b, args.fps)}")

    print("\nnext: listen, choose one, then `cue.py <audio> --snap <time>` and copy cue_time into the preset.")


if __name__ == "__main__":
    main()
