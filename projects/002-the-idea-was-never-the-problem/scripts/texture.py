#!/usr/bin/env python3
"""
T1 TEXTURE PASS — generates the plates in public/tex/.

Every plate is a *surface*, not an effect: it sits on the lens, full-frame,
never transformed with the content. That is the difference between a film that
looks printed and one that looks filtered.

WHY THE PAPER PLATE IS SPLIT IN TWO.  A single mid-grey plate in `multiply` is
the obvious build and it is wrong: multiply can only ever take light away, so
any plate with enough contrast to be visible also shifts the whole ground
darker, and the BONE in the film stops being the BONE in the palette. T1 says
it plainly — "multiply and darken for shadow-side texture, screen and color
dodge for light-side". So one fibre field is split at zero into a dark plate
(multiplied) and a light plate (screened). Together they add tooth with no net
shift in the ground.

It also makes the pass ground-agnostic. On BONE the multiply does most of the
work and the screen barely registers; on UMBER it inverts automatically, and
the texture lifts the blacks exactly as the brief asks — with no second set of
plates and no inverted copy.

Plates are written at half resolution and scaled up by the browser. Paper grain
wants to be slightly soft; at 1:1 it reads as sensor noise instead of fibre.

  python3 scripts/texture.py
"""
import numpy as np
from PIL import Image, ImageFilter
import pathlib

W, H = 540, 960          # half of 1080x1920
TILE = 384               # film-grain tile, repeated across the frame
GRAIN_PLATES = 8         # cycled at 20fps so the grain crawls, not strobes
OUT = pathlib.Path(__file__).resolve().parent.parent / 'public' / 'tex'
OUT.mkdir(parents=True, exist_ok=True)

rng = np.random.default_rng(1204)   # fixed: the texture must be reproducible


def save(a, name):
    img = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), 'L')
    img.save(OUT / name, optimize=True)
    print(f'  {name:22s} {img.size[0]}x{img.size[1]}  mean {np.clip(a,0,255).mean():6.1f}')


def blur(a, r):
    return np.asarray(
        Image.fromarray(np.clip(a + 128, 0, 255).astype(np.uint8), 'L')
        .filter(ImageFilter.GaussianBlur(r)),
        dtype=float,
    ) - 128


def split(field, dark_name, light_name):
    """Field centred on zero -> a multiply plate and a screen plate."""
    save(255.0 + np.minimum(field, 0.0), dark_name)   # <=255, neutral at 255
    save(np.maximum(field, 0.0), light_name)          # >=0,   neutral at 0


def paper():
    f = rng.normal(0, 26, (H, W))                       # fibre speckle

    # Short, mostly-horizontal streaks — the way laid paper reads under raking
    # light. Drawn as a sparse mask, then blurred along the grain.
    fib = np.zeros((H, W))
    ys = rng.integers(0, H, 4200)
    xs = rng.integers(0, W, 4200)
    for y, x, L in zip(ys, xs, rng.integers(6, 40, 4200)):
        fib[y, x:min(W, x + L)] -= rng.uniform(10, 42)
    f += blur(fib, 0.8)

    # A very low-frequency mottle so the sheet is not uniformly bright. Held at
    # a third of the fibre strength on purpose: a downscale to Reel size (390px
    # wide) throws away the fibre and keeps the mottle, so anything stronger
    # reads as a dirty ground on a phone while still looking fine at 1080.
    small = rng.normal(0, 30, (H // 24, W // 24))
    f += (np.asarray(Image.fromarray(np.clip(small + 128, 0, 255).astype(np.uint8), 'L')
                     .resize((W, H), Image.BICUBIC), dtype=float) - 128) * 0.35

    f = blur(f, 0.5)
    split(f, 'paper_dark.png', 'paper_light.png')


def crumple():
    """
    Long soft creases and a broad fold gradient. Static and unmoving — a fold in
    the paper does not animate. Same dark/light split, same reason.
    """
    f = np.zeros((H, W))
    yy, xx = np.mgrid[0:H, 0:W]
    for _ in range(9):
        x0, y0 = rng.uniform(0, W), rng.uniform(0, H)
        ang = rng.uniform(0, np.pi)
        dx, dy = np.cos(ang), np.sin(ang)
        d = (xx - x0) * dy - (yy - y0) * dx          # signed distance to the crease
        width = rng.uniform(30, 110)
        # a lit side and a shadow side, falling off — a fold, not a line
        f += rng.uniform(16, 38) * (d / width) * np.exp(-(d / width) ** 2)

    small = rng.normal(0, 34, (H // 40, W // 40))
    f += (np.asarray(Image.fromarray(np.clip(small + 128, 0, 255).astype(np.uint8), 'L')
                     .resize((W, H), Image.BICUBIC), dtype=float) - 128) * 0.45

    f = blur(f, 1.4)
    split(f, 'crumple_dark.png', 'crumple_light.png')


def grain():
    """
    Film grain, cycled by frame. Eight plates is enough that the eye reads it as
    grain; fewer and it pulses, more and nobody can tell.

    These stay as single overlay tiles rather than a split pair: grain is meant
    to sit on top of everything including the paper, it is symmetric about
    neutral by construction, and at this amplitude the net shift is nil.
    """
    for i in range(GRAIN_PLATES):
        a = 128.0 + rng.normal(0, 46, (TILE, TILE))
        a = np.asarray(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), 'L')
                       .filter(ImageFilter.GaussianBlur(0.4)), dtype=float)
        a = (a - 128.0) * 2.2 + 128.0   # blurring costs contrast; put it back
        save(a, f'grain{i}.png')


if __name__ == '__main__':
    print('T1 texture plates ->', OUT)
    paper()
    crumple()
    grain()
