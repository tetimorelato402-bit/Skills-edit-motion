#!/usr/bin/env python3
"""
THE PAINTING, HUNG IN AN OLD ROOM.

A still, not a film: a reference plate to feed an image-to-video model, so the
room can be brought to life somewhere else. The point is that the picture on
the wall is not an illustration of the poppy — it IS the painted look's canvas,
built from `plant.canvas_marks()`, the same marks in the same colours in the
same composition. One painting, two places, because it is generated rather than
drawn twice: change the marks and both the film and this room change together.

Everything else is a room made of boxes and planes — floorboards, plaster, a
skirting, a window out of frame throwing an afternoon across the wall, a table,
a chair, dust in the air.

    python3 scripts/vintage_room.py --out outputs/vintage --res 1920x1080
"""
import argparse
import math
import os
import sys

import bpy
from mathutils import Vector

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "source", "blender"))
from plant import canvas_marks, principled, wipe, aim_at, mesh_from  # noqa: E402

# The room is warm and old. Everything here is LINEAR, like the film's own
# constants — an sRGB hex pasted straight in renders about 40% bright.
# Darker than they look right: one window in a small room is not a lot of
# light, and a wall painted for a bright render blows to white and takes all
# the colour with it — the first pass was a cream fog with a brown flower.
PLASTER = (0.210, 0.166, 0.112, 1.0)
PLASTER2 = (0.170, 0.132, 0.088, 1.0)
FLOOR_A = (0.072, 0.036, 0.015, 1.0)
FLOOR_B = (0.098, 0.052, 0.023, 1.0)
TRIM = (0.155, 0.128, 0.096, 1.0)
FRAME_W = (0.052, 0.028, 0.014, 1.0)
CANVAS = (0.560, 0.500, 0.395, 1.0)     # aged linen, darker than the studio's

ROOM = dict(back=3.10, left=-2.30, right=2.30, ceil=2.72)
PAINT_AT = (0.36, ROOM["back"] - 0.02, 1.46)   # centre of the picture
PAINT_SCALE = 0.86                             # canvas 0.82m -> 0.71m wide


def box(name, dims, loc, mat, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    ob = bpy.context.object
    ob.name = name
    ob.scale = dims
    ob.rotation_euler = tuple(math.radians(a) for a in rot)
    ob.data.materials.append(mat)
    return ob


def plane(name, w, h, loc, mat, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_plane_add(size=1, location=loc)
    ob = bpy.context.object
    ob.name = name
    ob.scale = (w, h, 1)
    ob.rotation_euler = tuple(math.radians(a) for a in rot)
    ob.data.materials.append(mat)
    return ob


def lozenge(name, length, width, loc, mat, deg, yaw, seed=0.0):
    """A tapered brush mark standing in the wall plane — the same shape the
    film's canvas uses, so the two paintings are made of the same strokes."""
    n = 20
    top, bot = [], []
    for i in range(n):
        u = i / (n - 1)
        wv = width * (0.35 + 0.65 * math.sin(math.pi * min(1.0, u * 1.15)) ** 0.6)
        wv *= 1.0 + 0.14 * math.sin(u * math.tau * 1.7 + seed)
        if u > 0.82:
            wv *= 1.0 - (u - 0.82) / 0.18 * 0.7
        x = -length / 2 + length * u
        top.append((x, 0.0, wv / 2)); bot.append((x, 0.0, -wv / 2))
    verts = top + bot[::-1] + [(0, 0, 0)]
    c = len(top) * 2
    ob = mesh_from(name, verts, [(i, (i + 1) % c, c) for i in range(c)], mat)
    ob.data.shade_flat()
    ob.location = loc
    ob.rotation_euler = (0.0, math.radians(deg), math.radians(yaw))
    return ob


def build():
    wipe()
    # WALLPAPER, not paint: a narrow two-tone stripe is the single cheapest
    # thing that says the room is old rather than empty.
    plaster = bpy.data.materials.new("v_paper")
    plaster.use_nodes = True
    _nt = plaster.node_tree
    _b = _nt.nodes["Principled BSDF"]
    _b.inputs["Roughness"].default_value = 0.95
    _b.inputs["Specular IOR Level"].default_value = 0.06
    _wv = _nt.nodes.new("ShaderNodeTexWave")
    _wv.wave_type = 'BANDS'
    _wv.bands_direction = 'X'
    _wv.wave_profile = 'SAW'
    _wv.inputs["Scale"].default_value = 9.0
    _wv.inputs["Distortion"].default_value = 0.0
    _ramp = _nt.nodes.new("ShaderNodeValToRGB")
    _ramp.color_ramp.interpolation = 'CONSTANT'
    _ramp.color_ramp.elements[0].color = PLASTER
    _ramp.color_ramp.elements[1].position = 0.42
    _ramp.color_ramp.elements[1].color = (PLASTER[0] * 1.20, PLASTER[1] * 1.16,
                                          PLASTER[2] * 1.06, 1.0)
    _tc = _nt.nodes.new("ShaderNodeTexCoord")
    _nt.links.new(_tc.outputs["Object"], _wv.inputs["Vector"])
    _nt.links.new(_wv.outputs["Fac"], _ramp.inputs["Fac"])
    _nt.links.new(_ramp.outputs["Color"], _b.inputs["Base Color"])
    plaster2 = principled("v_plaster2", **{"Base Color": PLASTER2, "Roughness": 0.95,
                                           "Specular IOR Level": 0.06})
    wood_a = principled("v_floora", **{"Base Color": FLOOR_A, "Roughness": 0.52,
                                       "Specular IOR Level": 0.35})
    wood_b = principled("v_floorb", **{"Base Color": FLOOR_B, "Roughness": 0.48,
                                       "Specular IOR Level": 0.35})
    trim = principled("v_trim", **{"Base Color": TRIM, "Roughness": 0.62})
    framew = principled("v_frame", **{"Base Color": FRAME_W, "Roughness": 0.44,
                                      "Specular IOR Level": 0.4})
    gilt = principled("v_gilt", **{"Base Color": (0.28, 0.19, 0.075, 1), "Roughness": 0.34,
                                   "Metallic": 0.75})
    linen = principled("v_linen", **{"Base Color": CANVAS, "Roughness": 0.88,
                                     "Specular IOR Level": 0.05})

    # --- the shell -------------------------------------------------------
    # FLOORBOARDS, not a floor. A plane with one wood colour reads as
    # laminate; boards give the light something to run along, which is most
    # of what says "old room".
    for i in range(34):
        y0 = -2.6 + i * 0.165
        plane(f"board{i}", 5.4, 0.158, (0, y0, 0.0), wood_a if i % 2 else wood_b)
        box(f"gap{i}", (5.4, 0.006, 0.004), (0, y0 + 0.082, 0.002), trim)
    plane("wall_back", 5.4, 3.4, (0, ROOM["back"], 1.7), plaster, rot=(90, 0, 0))
    plane("wall_left", 6.4, 3.4, (ROOM["left"], 0.4, 1.7), plaster2, rot=(90, 0, 90))
    plane("wall_right", 6.4, 3.4, (ROOM["right"], 0.4, 1.7), plaster2, rot=(90, 0, 90))
    plane("ceiling", 5.4, 6.4, (0, 0.4, ROOM["ceil"]), plaster)
    box("skirt_back", (5.4, 0.035, 0.155), (0, ROOM["back"] - 0.018, 0.077), trim)
    box("rail", (5.4, 0.030, 0.055), (0, ROOM["back"] - 0.016, 1.98), trim)

    # --- the painting ----------------------------------------------------
    S = PAINT_SCALE
    px, py, pz = PAINT_AT
    plane("canvas", 0.82 * S, 1.08 * S, (px, py, pz), linen, rot=(90, 0, 0))
    cols = {
        # BRIGHTER THAN THE FILM'S. A saturated vermilion under one warm,
        # dim window multiplies down to something that reads brown: the
        # painting has to be lifted to stay a red flower in this room.
        'petal':  (0.940, 0.190, 0.048, 1.0),
        'tip':    (0.960, 0.430, 0.090, 1.0),
        'stem':   (0.150, 0.215, 0.080, 1.0),
        'leaf':   (0.185, 0.270, 0.100, 1.0),
        'jar':    (0.090, 0.045, 0.024, 1.0),
        'dark':   (0.022, 0.016, 0.012, 1.0),
        'ground': (0.620, 0.380, 0.105, 1.0),
    }
    # aged: the film's colours knocked back, because a painting in a warm room
    # under one window is not a studio swatch
    mats = {k: principled("v_mark_" + k, **{"Base Color": c, "Roughness": 0.80,
                                            "Specular IOR Level": 0.10})
            for k, c in cols.items()}
    # EACH MARK IN FRONT OF THE LAST. Every stroke at one depth is coplanar
    # geometry: the seven overlapping marks of the flower head z-fought into
    # a mottled black mass with an ochre rim, which looked exactly like a
    # colour mistake. A third of a millimetre each also IS how paint sits.
    for n, (key, mx, my, ml, mw, deg) in enumerate(canvas_marks()):
        lozenge(f"mark{n}", ml * S, mw * S,
                (px + mx * S, py - 0.006 - n * 0.00035, pz + my * S),
                mats[key], deg, 0.0, seed=n)
    # the frame: four lengths of dark wood with a gilt slip inside them
    # primitive_cube_add(size=1) scaled by `dims` has FULL extent `dims`, so
    # every length here is a whole length, not a half. Built from halves the
    # frame came out as four short bars floating clear of the picture.
    hw, hh, T, G = 0.82 * S / 2, 1.08 * S / 2, 0.046, 0.012
    for nm, dims, off in (("t", (2 * hw + 2 * T, 0.052, T), (0, hh + T / 2)),
                          ("b", (2 * hw + 2 * T, 0.052, T), (0, -hh - T / 2)),
                          ("l", (T, 0.052, 2 * hh + 2 * T), (-hw - T / 2, 0)),
                          ("r", (T, 0.052, 2 * hh + 2 * T), (hw + T / 2, 0))):
        box("frame_" + nm, dims, (px + off[0], py + 0.016, pz + off[1]), framew)
    for nm, dims, off in (("t", (2 * hw + 2 * G, 0.024, G), (0, hh + G / 2)),
                          ("b", (2 * hw + 2 * G, 0.024, G), (0, -hh - G / 2)),
                          ("l", (G, 0.024, 2 * hh + 2 * G), (-hw - G / 2, 0)),
                          ("r", (G, 0.024, 2 * hh + 2 * G), (hw + G / 2, 0))):
        box("slip_" + nm, dims, (px + off[0], py - 0.002, pz + off[1]), gilt)

    # --- what makes it somebody's room ------------------------------------
    # a small table under the picture
    tx, ty = 0.30, ROOM["back"] - 0.36
    box("table_top", (0.92, 0.44, 0.032), (tx, ty, 0.735), framew)
    for sx in (-0.41, 0.41):
        for sy in (-0.17, 0.17):
            box(f"leg{sx}{sy}", (0.038, 0.038, 0.72), (tx + sx, ty + sy, 0.36), framew)
    # a stoneware jug on it, empty — the room is waiting for the flower
    bpy.ops.mesh.primitive_cylinder_add(vertices=36, radius=0.075, depth=0.20,
                                        location=(tx - 0.24, ty - 0.02, 0.851))
    jug = bpy.context.object; jug.name = "jug"
    jug.data.materials.append(principled("v_jug", **{"Base Color": (0.30, 0.26, 0.21, 1),
                                                     "Roughness": 0.66}))
    # a couple of books, lying flat
    for k in range(3):
        box(f"book{k}", (0.20, 0.145, 0.028),
            (tx + 0.30 + 0.006 * k, ty + 0.01 * k, 0.765 + 0.030 * k),
            principled(f"v_book{k}", **{"Base Color": ((0.16, 0.055, 0.035, 1),
                                                       (0.085, 0.075, 0.055, 1),
                                                       (0.115, 0.090, 0.045, 1))[k],
                                        "Roughness": 0.85}),
            rot=(0, 0, -7 + 6 * k))
    # a bentwood chair, half in shot on the left
    cx, cy = -1.28, 2.30
    box("seat", (0.42, 0.42, 0.030), (cx, cy, 0.455), framew, rot=(0, 0, 24))
    for sx in (-0.17, 0.17):
        for sy in (-0.17, 0.17):
            box(f"cleg{sx}{sy}", (0.030, 0.030, 0.45),
                (cx + sx * 0.97 - sy * 0.41, cy + sx * 0.41 + sy * 0.97, 0.225), framew)
    box("cback", (0.40, 0.028, 0.46), (cx - 0.17 * 0.41 - 0.17 * 0.97 * 0,
                                       cy + 0.19, 0.70), framew, rot=(0, 0, 24))

    # --- the afternoon ----------------------------------------------------
    # A WINDOW OUT OF FRAME, low and to the left, so the room is lit by one
    # source with a shape. The aperture is a hole in the left wall; the lamp
    # sits outside it, so what reaches the room is a slab of light with edges
    # rather than an even fill.
    wall_l = bpy.data.objects["wall_left"]
    wall_l.hide_render = True                        # replaced by four pieces
    for nm, w, h, loc in (("a", 6.4, 1.10, (ROOM["left"], 0.4, 0.55)),
                          ("b", 6.4, 0.70, (ROOM["left"], 0.4, 2.37)),
                          ("c", 2.6, 1.02, (ROOM["left"], -1.5, 1.61)),
                          ("d", 2.6, 1.02, (ROOM["left"], 2.4, 1.61))):
        plane("wl_" + nm, w, h, loc, plaster2, rot=(90, 0, 90))
    # glazing bars, so the light lands as panes
    for k, yy in enumerate((0.05, 0.83)):
        box(f"bar{k}", (0.035, 0.030, 1.02), (ROOM["left"] + 0.02, yy, 1.61), trim)
    box("bar_h", (0.035, 1.60, 0.030), (ROOM["left"] + 0.02, 0.44, 1.61), trim)

    bpy.ops.object.light_add(type='AREA', location=(ROOM["left"] - 0.55, 0.44, 1.72))
    sun = bpy.context.object
    sun.name = "afternoon"
    sun.data.shape = 'RECTANGLE'
    sun.data.size, sun.data.size_y = 1.15, 0.85
    sun.data.energy = 780.0
    sun.data.color = (1.0, 0.790, 0.545)
    # aimed PAST the picture, so the afternoon lands as a patch on the wall to
    # its right and the picture itself sits in the softer half of the room
    aim_at(sun, Vector((1.55, 2.95, 0.85)))
    # a cool bounce off the far wall so the shadows are not dead
    bpy.ops.object.light_add(type='AREA', location=(1.9, -1.2, 1.5))
    fill = bpy.context.object
    fill.name = "bounce"
    fill.data.size = 2.6
    fill.data.energy = 14.0
    fill.data.color = (0.72, 0.80, 1.0)
    aim_at(fill, Vector((0.2, 2.6, 1.4)))

    w = bpy.data.worlds.new("vw")
    w.use_nodes = True
    w.node_tree.nodes["Background"].inputs[0].default_value = (0.010, 0.011, 0.014, 1)
    w.node_tree.nodes["Background"].inputs[1].default_value = 1.0
    bpy.context.scene.world = w

    # DUST. The whole reason for a window you cannot see: the shaft has to be
    # visible in the air or the room is just lit.
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0.5, 1.35))
    air = bpy.context.object
    air.name = "air"
    air.scale = (4.5, 5.8, 2.7)
    m = bpy.data.materials.new("v_air")
    m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        if n.type != 'OUTPUT_MATERIAL':
            nt.nodes.remove(n)
    sc = nt.nodes.new("ShaderNodeVolumeScatter")
    sc.inputs["Density"].default_value = 0.013
    sc.inputs["Anisotropy"].default_value = 0.55
    nt.links.new(sc.outputs["Volume"], nt.nodes["Material Output"].inputs["Volume"])
    air.data.materials.append(m)

    return px, py, pz


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="../outputs/vintage")
    ap.add_argument("--res", default="1920x1080")
    ap.add_argument("--samples", type=int, default=96)
    args = ap.parse_args()

    px, py, pz = build()
    W, H = (int(v) for v in args.res.lower().split("x"))

    # eye level, a little to the left of the picture and turned onto it, so
    # the room runs away to the right and the window light comes across
    # BACK, far enough that the ROOM is the subject and the picture is
    # something in it. Framed on the painting the plate is a photograph of a
    # painting, which is not what it is for.
    bpy.ops.object.camera_add(location=(-0.86, -1.55, 1.46))
    cam = bpy.context.object
    cam.data.lens = 33.0 if W >= H else 26.0
    cam.data.sensor_fit = 'AUTO'
    aim_at(cam, Vector((px - 0.10, py - 1.05, pz - 0.40)))

    sc = bpy.context.scene
    sc.camera = cam
    sc.render.engine = 'CYCLES'
    sc.cycles.device = 'CPU'
    sc.cycles.samples = args.samples
    sc.cycles.use_adaptive_sampling = True
    sc.cycles.adaptive_threshold = 0.02
    sc.cycles.volume_bounces = 2
    sc.cycles.transmission_bounces = 8
    sc.cycles.use_denoising = True
    sc.render.resolution_x, sc.render.resolution_y = W, H
    sc.render.resolution_percentage = 100
    sc.render.film_transparent = False
    # STANDARD, not Filmic. Filmic drags a saturated vermilion toward brown —
    # the poppy in the picture rendered as a dark smudge with an ochre rim
    # while the wallpaper beside it looked correct. This plate exists to be
    # fed to an image model, so the colour has to be the colour.
    sc.view_settings.view_transform = 'Standard'
    sc.view_settings.look = 'None'
    sc.view_settings.exposure = -0.15

    out = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), args.out))
    os.makedirs(os.path.dirname(out), exist_ok=True)
    sc.render.filepath = f"{out}-{W}x{H}"
    bpy.ops.render.render(write_still=True)
    print("wrote", sc.render.filepath + ".png", flush=True)


if __name__ == "__main__":
    main()
