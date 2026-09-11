#!/usr/bin/env python3
"""Synthetic test assets so the whole chain can run without OpenArt credits.

Creates in --out (default pipeline/test-assets/):
    stone.png   a procedural banded-stone cross-section (sedimentary strata)
    mask.png    the hidden imprint (a doorway shape) buried in one deep band
    song.wav    a quiet drone that "drops" (hard energy jump) at --drop seconds

Usage:
    python3 pipeline/synth.py --out pipeline/test-assets --size 1080x1920 --drop 21.5
"""

from __future__ import annotations

import argparse
import struct
import wave
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter


def value_noise(h: int, w: int, rng: np.random.Generator, octaves: int = 5) -> np.ndarray:
    out = np.zeros((h, w), np.float32)
    amp = 1.0
    for o in range(octaves):
        gh, gw = max(2, h >> (octaves - o + 1)), max(2, w >> (octaves - o + 1))
        g = rng.random((gh, gw)).astype(np.float32)
        img = Image.fromarray((g * 255).astype(np.uint8)).resize((w, h), Image.BICUBIC)
        out += amp * (np.asarray(img, np.float32) / 255.0)
        amp *= 0.5
    return out / out.max()


def make_stone(w: int, h: int, seed: int) -> tuple[Image.Image, Image.Image]:
    rng = np.random.default_rng(seed)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    warp = value_noise(h, w, rng) * 0.18 * h + 0.05 * h * np.sin(xx / w * 6.0)
    band = (yy + warp) / h * 14.0  # ~14 strata
    idx = np.floor(band).astype(int)
    frac = band - idx
    palette = np.array([
        [92, 70, 52], [140, 108, 78], [176, 150, 118], [110, 84, 64], [201, 178, 142],
        [84, 66, 56], [158, 122, 90], [124, 98, 72], [190, 164, 130], [100, 78, 60],
        [146, 116, 88], [80, 60, 48], [168, 140, 104], [120, 92, 68], [96, 74, 56],
    ], np.float32)
    col = palette[np.clip(idx, 0, len(palette) - 1) % len(palette)]
    # soften the boundary between strata and add fine grain
    edge = np.clip((frac - 0.9) * 10.0, 0, 1)[:, :, None]
    nxt = palette[np.clip(idx + 1, 0, len(palette) - 1) % len(palette)]
    col = col * (1 - edge) + nxt * edge
    tex = value_noise(h, w, rng, octaves=6)[:, :, None]
    col = col * (0.85 + 0.3 * tex)

    # hidden doorway imprint in a deep band (lower third), nearly the same tone
    mask = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(mask)
    dw, dh = int(w * 0.16), int(h * 0.12)
    cx, cy = int(w * 0.56), int(h * 0.68)
    d.rounded_rectangle([cx - dw // 2, cy - dh // 2, cx + dw // 2, cy + dh // 2], radius=dw // 2, fill=255)
    d.rectangle([cx - dw // 2, cy, cx + dw // 2, cy + dh // 2], fill=255)  # flat bottom: a doorway
    mask = mask.filter(ImageFilter.GaussianBlur(2))
    m = np.asarray(mask, np.float32)[:, :, None] / 255.0
    col = col * (1 - 0.045 * m)  # 4.5% darker: invisible on first viewing, present on second
    img = Image.fromarray(np.clip(col, 0, 255).astype(np.uint8))
    return img, mask


def make_song(path: Path, length: float, drop: float, sr: int = 44100, seed: int = 3) -> None:
    rng = np.random.default_rng(seed)
    t = np.arange(int(length * sr)) / sr
    drone = 0.06 * (np.sin(2 * np.pi * 55 * t) + 0.5 * np.sin(2 * np.pi * 110.3 * t))
    drone += 0.02 * rng.normal(0, 1, len(t)) * (0.5 + 0.5 * np.sin(2 * np.pi * 0.2 * t))
    hit = np.zeros_like(t)
    on = t >= drop
    tt = t[on] - drop
    hit[on] = (0.9 * np.exp(-tt * 2.5) * np.sin(2 * np.pi * 41.2 * tt)
               + 0.4 * np.exp(-tt * 8) * rng.normal(0, 1, on.sum()))
    sustain = np.zeros_like(t)
    sustain[on] = 0.25 * (1 - np.exp(-tt * 3)) * np.sin(2 * np.pi * 82.4 * tt)
    x = np.clip(drone + hit + sustain, -1, 1)
    with wave.open(str(path), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(struct.pack(f"<{len(x)}h", *(x * 32767).astype(np.int16)))


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default="pipeline/test-assets")
    ap.add_argument("--size", default="1080x1920")
    ap.add_argument("--drop", type=float, default=21.5, help="seconds into the test song where the drop lands")
    ap.add_argument("--length", type=float, default=40.0)
    ap.add_argument("--seed", type=int, default=11)
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    w, h = (int(v) for v in args.size.split("x"))
    img, mask = make_stone(w, h, args.seed)
    img.save(out / "stone.png")
    mask.save(out / "mask.png")
    make_song(out / "song.wav", args.length, args.drop)
    print(f"wrote {out}/stone.png {out}/mask.png {out}/song.wav (drop at {args.drop}s)")


if __name__ == "__main__":
    main()
