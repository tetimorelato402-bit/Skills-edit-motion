#!/usr/bin/env python3
"""
THE HANDOFF — where the 3D act becomes the 2D one.

Two numbers have to come out of Blender and into video.html, and neither should
ever be typed by hand:

  1. WHERE the paint erupts. The bloom was built with its origin at a send
     button that no longer exists. Its origin is now the flower head, and that
     is a 3D point — so it is projected through the actual camera rather than
     eyeballed off a screenshot. Nudge the camera and this number is wrong
     again, silently, and the paint starts somewhere that is not the flower.

  2. WHAT COLOUR it is. 001's palette was not chosen, it was extracted from
     teti's oil portrait by k-means. Same method here: the bloom's colours are
     clustered out of the rendered flower itself. The 2D paint is the same
     colour as the 3D poppy because it literally came from it — not because
     someone matched two swatches by eye.

  python3 scripts/handoff.py
"""
import os
import sys

import numpy as np
from PIL import Image

import bpy
from bpy_extras.object_utils import world_to_camera_view

HERE = os.path.dirname(os.path.abspath(__file__))
BLEND = os.path.join(HERE, "..", "source", "blender")
sys.path.insert(0, BLEND)
from plant import SHUTTER, Scene             # noqa: E402
from render_plant import configure           # noqa: E402

W, H = 1080, 1920
OUT = os.path.abspath(os.path.join(HERE, "..", "outputs", "handoff"))
os.makedirs(OUT, exist_ok=True)


def kmeans(px, k, iters=40, seed=7):
    """Small k-means; sklearn is not installed and this is 30 lines."""
    rng = np.random.default_rng(seed)
    c = px[rng.choice(len(px), k, replace=False)]
    for _ in range(iters):
        d = ((px[:, None, :] - c[None, :, :]) ** 2).sum(2)
        lab = d.argmin(1)
        for j in range(k):
            m = lab == j
            if m.any():
                c[j] = px[m].mean(0)
    counts = np.bincount(lab, minlength=k)
    order = np.argsort(-counts)
    return c[order], counts[order]


def main():
    scene = Scene()
    configure(W, 128)
    # The LAST LIT FRAME, not ACT_I_END — the act now ends on a sixteenth of
    # black, and sampling a palette out of a black frame returns black.
    scene.set_time(SHUTTER[0] - 1 / 120.0)

    # --- 1. where -----------------------------------------------------------
    dg = bpy.context.evaluated_depsgraph_get()
    co = world_to_camera_view(bpy.context.scene, scene.cam,
                              scene.head.matrix_world.translation)
    # world_to_camera_view returns 0..1 from the BOTTOM left; screen space is
    # top-left, so y flips.
    px, py = co.x * W, (1.0 - co.y) * H
    print(f"  flower head, projected:  x = {px:7.1f}   y = {py:7.1f}   "
          f"({co.x*100:.1f}%, {(1-co.y)*100:.1f}% of frame)")

    # --- 2. what colour -----------------------------------------------------
    still = os.path.join(OUT, "handoff.png")
    if "--reuse" in sys.argv and os.path.exists(still):
        print("  reusing the existing handoff render")
    else:
        bpy.context.scene.render.filepath = still
        bpy.ops.render.render(write_still=True)

    im = np.asarray(Image.open(still).convert("RGB"), dtype=float)
    # The camera now ends inside the flower, so the petals ARE the frame —
    # there is no head-box to find any more. Sample the whole image.
    box = im.reshape(-1, 3)

    # Filter on SATURATION, not brightness. Act I is a near-monochrome dark
    # scene, so a luminance threshold keeps every shadow brown and every
    # specular grey in the sample — the first run returned #381D0F, #5D3118 and
    # a lavender highlight, none of which is the flower. The poppy is the only
    # saturated object in the frame, so saturation is what isolates it.
    mx, mn = box.max(1), box.min(1)
    sat = np.divide(mx - mn, np.maximum(mx, 1e-6))
    lit = box[(sat > 0.34) & (mx > 34)]
    print(f"  {len(lit)} saturated pixels of {len(box)} in the head box "
          f"({len(lit)*100.0/len(box):.1f}%)")

    cols, counts = kmeans(lit, 6)
    print("\n  the flower as rendered — its hue, at the light it actually gets:")
    raw = []
    for c, n in zip(cols, counts):
        h = "#%02X%02X%02X" % tuple(int(round(v)) for v in c)
        raw.append(h)
        print(f"    {h}   {n*100.0/len(lit):5.1f}%")

    # The flower sits in a dark scene, so its literal pixels are dark — used
    # raw they would make a mud-coloured bloom. CLAUDE.md already says what to
    # do: "colour may move in VALUE; it must not leave the warm family." So the
    # hue and saturation come from the poppy and only the value is lifted. The
    # paint is the same colour as the flower, seen in full light.
    import colorsys
    lifted = []
    targets = [0.86, 0.76, 0.68, 0.60, 0.52, 0.44, 0.38, 0.33]
    # Value alone is not enough. Eight entries at one hue produced a bloom that
    # was a single flat orange field — technically "the flower's colour" and
    # visually monochrome. A real poppy in full light runs vermilion through
    # scarlet to ochre, so the ramp fans +/- 14 degrees around the extracted
    # hue. That is variety INSIDE the warm family, which is what the palette
    # rule permits; it is not a second colour.
    spread = [-0.038, 0.022, -0.014, 0.034, -0.030, 0.010, 0.038, -0.022]
    print("\n  the bloom's warm ramp — that hue, fanned and lifted into paint:")
    for i, v_t in enumerate(targets):
        c = cols[i % len(cols)] / 255.0
        h, l, sat_hls = colorsys.rgb_to_hls(*c)
        h = (h + spread[i]) % 1.0
        # saturation is pushed toward, not to, full — paint is saturated but
        # a flat 1.0 across eight entries reads as vector fill
        s_new = min(0.92, max(0.55, sat_hls * 1.35))
        r, g, b = colorsys.hls_to_rgb(h, v_t * 0.62, s_new)
        hx = "#%02X%02X%02X" % (round(r * 255), round(g * 255), round(b * 255))
        lifted.append(hx)
        print(f"    {hx}")

    with open(os.path.join(OUT, "handoff.txt"), "w") as f:
        f.write(f"ORIGIN {px:.1f} {py:.1f}\n")
        f.write("RAW " + " ".join(raw) + "\n")
        f.write("WARM " + " ".join(lifted) + "\n")
    print(f"\n  written to {OUT}/handoff.txt")


if __name__ == "__main__":
    main()
