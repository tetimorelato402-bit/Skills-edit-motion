#!/usr/bin/env python3
"""Make (or check) the hidden-shape mask for a locked still.

Draws a clean silhouette at normalised coordinates, sized to the still, so the
mask always lines up with base.png. Shapes: doorway (rounded top, flat bottom),
ellipse, rect. Also writes an overlay PNG so the placement can be checked by
eye against the still before anything is rendered.

Usage:
    python3 pipeline/mask.py --image base.png --shape doorway --cx 0.58 --cy 0.72 --w 0.17 --h 0.14 --out mask.png
    python3 pipeline/mask.py --image base.png --mask mask.png --overlay-only     # just re-check an existing mask

Coordinates are fractions of the image (0..1), cx/cy the centre, w/h the size.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter


def draw_shape(size: tuple[int, int], shape: str, cx: float, cy: float, w: float, h: float,
               feather: float, rotate: float = 0.0) -> Image.Image:
    W, H = size
    bw, bh = w * W, h * H
    # draw on a padded canvas then rotate, so a tilted doorway is possible
    pad = int(max(bw, bh))
    cw, ch = int(bw) + 2 * pad, int(bh) + 2 * pad
    m = Image.new("L", (cw, ch), 0)
    d = ImageDraw.Draw(m)
    x0, y0, x1, y1 = pad, pad, pad + bw, pad + bh
    if shape == "doorway":
        r = bw / 2
        d.pieslice([x0, y0, x1, y0 + 2 * r], 180, 360, fill=255)  # arched top
        d.rectangle([x0, y0 + r, x1, y1], fill=255)                # straight body, flat bottom
    elif shape == "ellipse":
        d.ellipse([x0, y0, x1, y1], fill=255)
    elif shape == "rect":
        d.rectangle([x0, y0, x1, y1], fill=255)
    else:
        raise SystemExit(f"unknown shape {shape}")
    if rotate:
        m = m.rotate(rotate, resample=Image.BICUBIC, expand=False)
    if feather > 0:
        m = m.filter(ImageFilter.GaussianBlur(feather))
    out = Image.new("L", (W, H), 0)
    out.paste(m, (int(cx * W - cw / 2), int(cy * H - ch / 2)))
    return out


def overlay(image: Image.Image, mask: Image.Image, path: Path) -> None:
    base = image.convert("RGB")
    tint = Image.new("RGB", base.size, (255, 120, 40))
    a = mask.resize(base.size).point(lambda v: int(v * 0.55))
    out = Image.composite(tint, base, a)
    # outline for precision
    edge = np.asarray(mask.resize(base.size), np.float32)
    gx = np.abs(np.diff(edge, axis=1, prepend=0)); gy = np.abs(np.diff(edge, axis=0, prepend=0))
    ring = Image.fromarray(np.clip((gx + gy) * 4, 0, 255).astype(np.uint8))
    out = Image.composite(Image.new("RGB", base.size, (255, 255, 255)), out, ring)
    out.save(path)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--image", required=True, help="the locked still (sets the mask size)")
    ap.add_argument("--out", help="mask PNG to write")
    ap.add_argument("--mask", help="existing mask to check instead of drawing one")
    ap.add_argument("--overlay-only", action="store_true")
    ap.add_argument("--shape", default="doorway", choices=["doorway", "ellipse", "rect"])
    ap.add_argument("--cx", type=float, default=0.5)
    ap.add_argument("--cy", type=float, default=0.7)
    ap.add_argument("--w", type=float, default=0.16)
    ap.add_argument("--h", type=float, default=0.14)
    ap.add_argument("--rotate", type=float, default=0.0, help="degrees, counter-clockwise")
    ap.add_argument("--feather", type=float, default=2.0)
    args = ap.parse_args()

    img = Image.open(args.image)
    if args.mask:
        m = Image.open(args.mask)
        m = m.getchannel("A") if "A" in m.getbands() else m.convert("L")
        out_path = Path(args.mask)
    else:
        if not args.out:
            raise SystemExit("--out is required when drawing a mask")
        m = draw_shape(img.size, args.shape, args.cx, args.cy, args.w, args.h, args.feather, args.rotate)
        out_path = Path(args.out)
        if not args.overlay_only:
            m.save(out_path)
            print(f"wrote {out_path} ({img.size[0]}x{img.size[1]})")
    ov = out_path.with_name(out_path.stem + "-overlay.png")
    overlay(img, m, ov)
    print(f"wrote {ov}: check the orange shape sits on the imprint, then render")


if __name__ == "__main__":
    main()
