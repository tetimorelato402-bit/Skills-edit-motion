#!/usr/bin/env python3
"""
A grayscale BRUSH plate for the bloom — value only, mean 128.

The bloom's first texture pass used 001's paper and ochre plates as overlays.
On the cream ground of the old opening that worked; over saturated vermilion it
does almost nothing — a low-contrast paper plate has no value range left to
push once the base colour is already strong, and at 1:1 the paint read as flat
vector fill with a faint weave over it.

This plate is built for the job instead: overlapping brush strokes at 60-220px,
carrying +/- 45 levels of value and nothing else. Because it is neutral grey it
can sit over ANY of the bloom's colours in `overlay` and carve strokes into it
without shifting the hue — which is the palette rule ("value may move, hue may
not") expressed as a texture.

Strokes are stamped ellipses along a path, never `ImageDraw.line`: PIL gives a
wide line square ends, and square-ended strokes read as scratchy hatching. That
one is already in CLAUDE.md, paid for on 001.

  python3 scripts/brushplate.py
"""
import math
import pathlib

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

W, H = 1080, 1920
OUT = pathlib.Path(__file__).resolve().parent.parent / "source" / "tex" / "brush.png"
rng = np.random.default_rng(90210)


def stroke(dr, x0, y0, ang, length, width, value):
    """One loaded brush stroke: ellipses along a path, tapering at both ends."""
    dx, dy = math.cos(ang), math.sin(ang)
    step = max(2.0, width * 0.18)
    k = 0.0
    while k < length:
        u = k / length
        taper = math.sin(math.pi * u) ** 0.40      # thin at both ends
        r = width * 0.5 * taper * rng.uniform(0.86, 1.14)
        if r > 0.7:
            # the bristle wobble is what stops a stroke looking like a shape
            wob = rng.normal(0, width * 0.06)
            cx = x0 + dx * k - dy * wob
            cy = y0 + dy * k + dx * wob
            v = int(np.clip(value + rng.normal(0, 5), 0, 255))
            dr.ellipse([cx - r, cy - r * 0.94, cx + r, cy + r * 0.94], fill=v)
        k += step


def main():
    img = Image.new("L", (W, H), 128)
    dr = ImageDraw.Draw(img)

    # Three passes, coarse to fine. A single scale reads as a pattern; the
    # coarse pass carries the sweep of the arm and the fine pass the bristles.
    for count, ln, wd, dev in ((70, (600, 1500), (120, 220), 34),
                               (150, (300, 800), (55, 120), 40),
                               (320, (120, 360), (18, 55), 45)):
        for _ in range(count):
            ang = rng.normal(math.pi / 2, 0.55)     # mostly vertical, like a hand
            if rng.random() < 0.28:
                ang += math.pi / 2                  # a cross-hatched minority
            stroke(dr,
                   rng.uniform(-0.1 * W, 1.1 * W), rng.uniform(-0.1 * H, 1.1 * H),
                   ang, rng.uniform(*ln), rng.uniform(*wd),
                   128 + rng.normal(0, dev))

    img = img.filter(ImageFilter.GaussianBlur(0.8))
    a = np.asarray(img, dtype=float)
    a = (a - a.mean()) * 1.25 + 128.0               # recentre and restore bite
    img = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), "L")
    img.save(OUT, optimize=True)
    print(f"  {OUT.name}  {W}x{H}  mean {np.asarray(img,dtype=float).mean():.1f}  "
          f"sigma {np.asarray(img,dtype=float).std():.1f}")


if __name__ == "__main__":
    main()
