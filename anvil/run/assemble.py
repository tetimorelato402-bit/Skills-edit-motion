#!/usr/bin/env python3
"""Assemble the three deliverables from the graded masters."""
import os
import numpy as np
from PIL import Image, ImageFilter
from grade import finish, head_track, sky

SW, SH = 1920, 1440
PLANT = 4                       # the footfall the whip lands on
SKY_F, WHIP_F = 19, 5
rng_c = {3: np.random.default_rng(5).uniform(0, 6, 4),
         7: np.random.default_rng(9).uniform(0, 6, 4)}

def g(n): return Image.open(f"graded/g{n:03d}.png")

def vmotion(a, k):
    """true vertical motion blur: box filter along y via cumsum"""
    if k <= 1: return a
    f = a.astype(np.float32)
    pad = np.pad(f, ((k, k), (0, 0), (0, 0)), mode="edge")
    c = np.cumsum(pad, axis=0)
    out = (c[k * 2:] - c[:-k * 2]) / (k * 2)
    return out[: a.shape[0]]

track = head_track()

def side_crop(n, W, H):
    """9:16 reframe: him weighted slightly left, water filling the right"""
    cw = int(SH * W / H)
    x = int(np.clip(track(n) - 0.40 * cw, 0, SW - cw))
    return g(n).crop((x, 0, x + cw, SH)).resize((W, H), Image.LANCZOS)

def rear_crop(n, W, H):
    """tracked push into his back: head/shoulders centre, world streaming past"""
    p = (n - PLANT) / (124 - PLANT)
    ch = int(1250 - 280 * (p ** 0.8))            # the push
    cw = int(ch * W / H)
    cx = track(n) - 30
    cy = 620
    x = int(np.clip(cx - cw * 0.46, 0, SW - cw))
    y = int(np.clip(cy - ch * 0.42, 0, SH - ch))
    return g(n).crop((x, y, x + cw, y + ch)).resize((W, H), Image.LANCZOS)

def build(name, W, H, opening, framer):
    os.makedirs(name, exist_ok=True)
    rng = np.random.default_rng(31)
    seq = []
    if opening:
        for i in range(SKY_F):
            seq.append(Image.fromarray((sky(W, H, i / 24, rng_c) * 255).astype(np.uint8)))
        # The whip is one continuous move: the sky sits directly above the road
        # on a tall virtual canvas and the camera travels down across the seam,
        # motion-blurred by its own velocity. No fill, no black — smear.
        skyim = np.asarray(seq[-1].convert("RGB"))
        travel = ((PLANT - 2, 0.10, 46), (PLANT - 2, 0.38, 150), (PLANT - 1, 0.74, 150),
                  (PLANT, 0.93, 64), (PLANT, 1.00, 12))
        for m, py, k in travel:
            tall = np.vstack([skyim, np.asarray(framer(m, W, H).convert("RGB"))])
            y = int(py * H)
            seq.append(Image.fromarray(
                vmotion(tall[y:y + H], k).clip(0, 255).astype(np.uint8)))
        start = PLANT + 1
    else:
        start = PLANT
    for n in range(start, 125):
        seq.append(framer(n, W, H))
    for i, im in enumerate(seq):
        finish(im, rng).save(f"{name}/o{i:04d}.png")
    print(name, len(seq), "frames")

build("out_side_v", 1080, 1920, True, side_crop)
build("out_side_w", 1920, 1440, True,
      lambda n, W, H: g(n).resize((W, H)) if (W, H) == (SW, SH) else g(n))
build("out_rear_v", 1080, 1920, False, rear_crop)
