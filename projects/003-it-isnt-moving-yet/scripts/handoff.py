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
import math
import os
import sys

import numpy as np
from PIL import Image

import bpy
from bpy_extras.object_utils import world_to_camera_view

HERE = os.path.dirname(os.path.abspath(__file__))
BLEND = os.path.join(HERE, "..", "source", "blender")
sys.path.insert(0, BLEND)
from plant import ACT_I_END, OPEN, Scene, aim_at   # noqa: E402
from mathutils import Vector                 # noqa: E402

# The flower fully open, before the room starts going out for the fall.
OPEN_LOOK = OPEN[1]
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
    # THE LAST FRAME OF THE FALL. There is no black before the studio any
    # more: the petal is still lit and still on screen when the paint erupts
    # out of it, so the frame to project and to sample is the final one of
    # Act I, not the one before a shutter that no longer exists.
    scene.set_time(ACT_I_END - 1 / 120.0)

    # --- 1. where -----------------------------------------------------------
    dg = bpy.context.evaluated_depsgraph_get()
    bpy.context.view_layer.update()
    # THE FALLING PETAL, NOT THE FLOWER HEAD.
    #
    # Act I no longer ends looking down the flower's throat — it ends on one
    # petal alone in a beam, twenty centimetres from the plant it left. Left
    # projecting the head, this printed an origin of (-1203, -2878): a point
    # a frame and a half off the top-left corner, because the head is not in
    # shot at all any more. The paint would have detonated from outside the
    # picture, which reads as the frame simply filling with colour and throws
    # away the whole reason the join is a substitution.
    # ...and its CENTROID, not its object origin. `blade()` generates the mesh
    # from y=0 outward, so a petal's origin sits at the base of the blade, off
    # at one end of the shape. Projecting that put the bloom's centre near the
    # petal's stalk and left the silhouette spanning only four of the six
    # sectors below, because every vertex was on one side of the measuring
    # point. The centroid is where the petal actually LOOKS like it is.
    ob = scene.faller
    me = ob.evaluated_get(dg).to_mesh()
    proj = []
    for v in me.vertices:
        t = world_to_camera_view(bpy.context.scene, scene.cam,
                                 ob.matrix_world @ v.co)
        # world_to_camera_view returns 0..1 from the BOTTOM left; screen space
        # is top-left, so y flips.
        proj.append((t.x * W, (1.0 - t.y) * H))
    ob.evaluated_get(dg).to_mesh_clear()
    px = sum(q[0] for q in proj) / len(proj)
    py = sum(q[1] for q in proj) / len(proj)
    print(f"  falling petal, projected:  x = {px:7.1f}   y = {py:7.1f}   "
          f"({co.x*100:.1f}%, {(1-co.y)*100:.1f}% of frame)")

    # --- 1b. which way do its petals point? -------------------------------
    # THE STRONGEST CONTINUITY CUE IN THE FILM, and it costs nothing.
    #
    # The paint's first six petals launch along the screen-space axes of the
    # flower's six real ones, so for the first frames after the cut the paint
    # is not merely erupting from where the flower was — it is continuing the
    # flower's own geometry outward. Then it diverges into sixty-six and
    # becomes paint. Nobody consciously notices; it is what makes a viewer read
    # one object across two media instead of a flower and then some colour.
    # The six axes now come from the ONE petal that is actually on screen: six
    # points around the silhouette it presents to the lens, measured from its
    # centre. The principle is unchanged and so is the payoff — the paint's
    # first strokes leave along directions the picture already contains, so for
    # the opening frames it is continuing a shape that is there rather than
    # arriving over it. Taking them from the flower's six petals would now be
    # taking them from an object outside the frame.
    pts = [(qx - px, qy - py) for qx, qy in proj]
    # the farthest vertex in each of six sectors — the silhouette's extremes
    axes = []
    for k in range(6):
        lo, hi = k * 60.0, (k + 1) * 60.0
        best, bd = None, -1.0
        for dx, dy in pts:
            a = math.degrees(math.atan2(dy, dx)) % 360.0
            if lo <= a < hi:
                d = dx * dx + dy * dy
                if d > bd:
                    best, bd = a, d
        if best is not None:
            axes.append(best)
    axes.sort()
    print("  petal axes on screen (deg): " + ", ".join(f"{a:.1f}" for a in axes))

    # --- 1c. THE POPPY PLATE ------------------------------------------------
    #
    # Two different images, for two different jobs, and conflating them was a
    # real bug rather than a tidy shortcut.
    #
    # `act1_last.png` is the JOIN: the true final frame of Act I, which the
    # paint erupts out of. Since the act now ends on one petal alone in a beam,
    # that frame is 95% black — correct for the join, and useless as a subject.
    #
    # `poppy.png` is the SUBJECT: the open flower, filling the frame, under
    # Act I's own lighting. It is what all five techniques in the back half
    # composite, and it is the whole "SAME POPPY" claim. When the techniques
    # were pointed at act1_last they were cropping into darkness — the film's
    # five languages rendered as five arrangements of grey.
    #
    # It is still extracted rather than art-directed: the same scene, the same
    # lamps, the same materials, at the moment the flower is fully open and the
    # room has not yet gone out. Only the camera is moved, and only so that the
    # flower fills a frame it is otherwise a small part of.
    scene.set_time(OPEN_LOOK)
    cam = scene.cam
    keep = (cam.location.copy(), cam.rotation_euler.copy())
    head = scene.head_at
    cam.location = head + Vector((0.0, -0.30, 0.055))
    aim_at(cam, head)
    bpy.context.view_layer.update()
    plate = os.path.join(OUT, "poppy.png")
    bpy.context.scene.render.filepath = plate
    bpy.ops.render.render(write_still=True)
    print("  poppy plate (the techniques' subject) ->", plate)
    cam.location, cam.rotation_euler = keep
    scene.set_time(ACT_I_END - 1 / 120.0)
    bpy.context.view_layer.update()

    # --- 2. what colour -----------------------------------------------------
    still = os.path.join(OUT, "handoff.png")
    if "--reuse" in sys.argv and os.path.exists(still):
        print("  reusing the existing handoff render")
    else:
        bpy.context.scene.render.filepath = still
        bpy.ops.render.render(write_still=True)

    # SAMPLE THE POPPY PLATE, NOT THE JOIN FRAME. The join frame is one petal
    # in a beam on a black stage: a few thousand lit pixels against two million
    # black ones, which pulls the k-means toward the dark and produced a ramp
    # with two muddy browns in it. The plate is the same flower under the same
    # lamps, filling the frame — same light, same material, vastly more of it.
    im = np.asarray(Image.open(plate).convert("RGB"), dtype=float)
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
        f.write("AXES " + " ".join(f"{a:.1f}" for a in axes) + "\n")
    print(f"\n  written to {OUT}/handoff.txt")


if __name__ == "__main__":
    main()
