#!/usr/bin/env python3
"""Prove the sync of a finished cut instead of eyeballing it.

Reads the rendered mp4 back, finds the first frame where the hidden shape
lights up (video), finds the frame where the audio energy jumps (audio),
and compares both against the cue frame recorded in the .sync.json sidecar.

Usage:
    python3 pipeline/verify.py pieces/.../out/final.mp4
    python3 pipeline/verify.py final.mp4 --mask mask.png      # region to watch
    python3 pipeline/verify.py final.mp4 --expect-frame 240   # without sidecar
    python3 pipeline/verify.py final.mp4 --no-audio-check     # silent preview

Exit code 0 means the reveal frame matches (within --tolerance frames), 1 otherwise.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image

from common import decode_audio_mono, die, probe_video, require_ffmpeg, seconds_to_frame


def frame_luma_in_region(path: str, region_mask: np.ndarray, w: int, h: int) -> np.ndarray:
    require_ffmpeg()
    cmd = ["ffmpeg", "-v", "error", "-nostdin", "-i", path, "-f", "rawvideo", "-pix_fmt", "gray",
           "-s", f"{w}x{h}", "-"]
    raw = subprocess.run(cmd, check=True, capture_output=True).stdout
    n = len(raw) // (w * h)
    frames = np.frombuffer(raw[: n * w * h], np.uint8).reshape(n, h, w).astype(np.float32)
    weight = region_mask / max(region_mask.sum(), 1e-6)
    return np.tensordot(frames, weight, axes=([1, 2], [0, 1]))


def first_jump(series: np.ndarray, baseline_frames: int, min_delta: float) -> int | None:
    base = series[: max(1, baseline_frames)]
    mu, sd = float(np.median(base)), float(np.std(base))
    thresh = mu + max(min_delta, 4.0 * sd)
    for i in range(len(series)):
        if series[i] > thresh:
            return i
    return None


def audio_jump_frame(path: str, fps: float, hop_ms: float = 5.0) -> int | None:
    x = decode_audio_mono(path, sr=22050)
    if len(x) == 0:
        return None
    sr = 22050
    hop = int(sr * hop_ms / 1000)
    n = len(x) // hop
    rms = np.sqrt(np.mean(x[: n * hop].reshape(n, hop) ** 2, axis=1) + 1e-12)
    db = 20 * np.log10(rms + 1e-9)
    w = int(0.2 / (hop / sr))
    if len(db) <= 2 * w:
        return None
    csum = np.concatenate([[0.0], np.cumsum(db)])
    idx = np.arange(w, len(db) - w)
    contrast = (csum[idx + w] - csum[idx]) / w - (csum[idx] - csum[idx - w]) / w
    i = int(idx[int(np.argmax(contrast))])
    lo, hi = max(1, i - w), min(len(db) - 1, i + w)
    local = db[lo + 1:hi + 1] - db[lo - 1:hi - 1]
    j = lo + int(np.argmax(local))
    return seconds_to_frame(j * hop / sr, fps)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("video")
    ap.add_argument("--mask", help="mask PNG of the hidden shape; default: read from sidecar")
    ap.add_argument("--region", help="ellipse cx,cy,rx,ry in 0..1 if no mask")
    ap.add_argument("--expect-frame", type=int, help="cue frame; default: read from sidecar")
    ap.add_argument("--tolerance", type=int, default=0, help="allowed frame error (default 0)")
    ap.add_argument("--min-delta", type=float, default=6.0, help="luma rise (0-255) that counts as the reveal")
    ap.add_argument("--no-audio-check", action="store_true")
    args = ap.parse_args()

    info = probe_video(args.video)
    fps, W, H = info["fps"], info["width"], info["height"]
    sidecar = Path(args.video).with_suffix(".sync.json")
    meta = json.loads(sidecar.read_text()) if sidecar.exists() else {}
    expect = args.expect_frame if args.expect_frame is not None else meta.get("cue_frame")
    if expect is None:
        die("no --expect-frame and no .sync.json sidecar next to the video")

    mask_src = args.mask or (meta.get("mask") if meta.get("mask", "").endswith(".png") else None)
    if mask_src:
        m = Image.open(mask_src)
        m = m.getchannel("A") if "A" in m.getbands() else m.convert("L")
        # Analyse at a reduced size for speed; the region is large relative to the frame.
        aw, ah = max(64, W // 4), max(64, H // 4)
        region = np.asarray(m.resize((aw, ah), Image.BILINEAR), np.float32) / 255.0
    elif args.region or meta.get("mask"):
        spec = args.region or meta["mask"]
        cx, cy, rx, ry = (float(v) for v in spec.split(","))
        aw, ah = max(64, W // 4), max(64, H // 4)
        yy, xx = np.mgrid[0:ah, 0:aw]
        region = (((xx / aw - cx) / rx) ** 2 + ((yy / ah - cy) / ry) ** 2 <= 1.0).astype(np.float32)
    else:
        die("need --mask or --region to know where the hidden shape is")

    # The mask is in source (overscanned) space; the output frame is a centred
    # window on it, so map it to output space at the unzoomed centre crop.
    over = meta.get("overscan", 1.0)
    if over > 1.0:
        aw, ah = region.shape[1], region.shape[0]
        cw, ch = int(aw / over), int(ah / over)
        l, t = (aw - cw) // 2, (ah - ch) // 2
        region = np.asarray(Image.fromarray((region[t:t + ch, l:l + cw] * 255).astype(np.uint8)).resize((aw, ah)), np.float32) / 255.0

    aw, ah = region.shape[1], region.shape[0]
    luma = frame_luma_in_region(args.video, region, aw, ah)
    baseline = max(3, expect - 1)
    video_frame = first_jump(luma, baseline, args.min_delta)

    ok = True
    print(f"{args.video}: {len(luma)} frames @ {fps:g}fps, expected cue frame {expect} (t={expect / fps:.4f}s)")
    if video_frame is None:
        print("  video : no reveal detected in the hidden-shape region (light too weak or wrong mask)")
        ok = False
    else:
        d = video_frame - expect
        flag = "OK" if abs(d) <= args.tolerance else "FAIL"
        print(f"  video : hidden shape first lights on frame {video_frame} (t={video_frame / fps:.4f}s)  delta {d:+d} frames  {flag}")
        print(f"          region luma before/at/after: {luma[max(0, expect-1)]:.1f} / {luma[min(expect, len(luma)-1)]:.1f} / {luma[min(expect+2, len(luma)-1)]:.1f}")
        ok = ok and abs(d) <= args.tolerance

    if not args.no_audio_check:
        af = audio_jump_frame(args.video, fps)
        if af is None:
            print("  audio : no audio stream or no clear transient (fine if the cue is a key change; check by ear)")
        else:
            d = af - expect
            note = "OK" if abs(d) <= max(1, args.tolerance) else "check: the loudest transient is not on the cue frame (can be legitimate for a key change or a silence cue)"
            print(f"  audio : strongest energy jump on frame {af} (t={af / fps:.4f}s)  delta {d:+d} frames  {note}")

    print("RESULT:", "SYNC OK, ships" if ok else "SYNC FAIL, does not ship")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
