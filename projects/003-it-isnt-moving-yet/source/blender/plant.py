#!/usr/bin/env python3
"""
ACT I — the jar. A dead thing in a mason jar, growing in the dark, that blooms.

Built the way the rest of this repo is built: there are NO KEYFRAMES. The scene
is constructed once and `set_time(t)` positions every element for time `t`, the
same contract as `window.renderFrame(t)` in video.html. Blender's animation
system is a second source of truth and a second thing to keep in sync with the
125 BPM grid; a pure function of t is neither.

The plant is the film's question made literal. "How do you make ideas that
aren't alive, alive?" — this is a dead thing becoming alive, in the dark, slowly,
and then all at once. Nothing on screen explains that and nothing should.

  python3 render_plant.py --times 0,4,8,11,13 --res 540
"""
import math
import os
import sys

import bpy
from mathutils import Vector

# ---------------------------------------------------------------- the grid
# Identical to video.html and to 001. Act I is seven bars: the jar sits in the
# dark for a bar, the stem climbs for five, the bud swells, and the flower opens
# on the last beat — where the paint bloom takes the frame.
BPM = 125
BEAT = 60.0 / BPM          # 0.48
BAR = 4 * BEAT             # 1.92
bt = lambda n: n * BEAT

DARK      = (bt(0),  bt(4))    # the jar alone, barely lit
CLIMB     = (bt(4),  bt(22))   # the stem grows
BUD       = (bt(20), bt(26))   # the bud forms and swells
OPEN      = (bt(26), bt(28))   # the flower opens; the paint takes over at bt(28)
ACT_I_END = bt(28)             # 13.44s — seven bars

# ---------------------------------------------------------------- palette
# The ground never leaves the warm family. The living green is the plant's own
# accent and is deliberately an olive, not a chlorophyll green — it has to sit
# next to umber without arguing with it.
UMBER      = (0.043, 0.017, 0.010, 1.0)
DEAD_STEM  = (0.058, 0.043, 0.028, 1.0)
LIVE_STEM  = (0.088, 0.121, 0.052, 1.0)
DEAD_LEAF  = (0.062, 0.046, 0.028, 1.0)
LIVE_LEAF  = (0.105, 0.155, 0.062, 1.0)
PETAL      = (0.520, 0.098, 0.038, 1.0)   # rust — the same accent as the paint
PETAL_TIP  = (0.640, 0.240, 0.060, 1.0)   # ochre


def clamp01(v):
    return max(0.0, min(1.0, v))


def seg(t, a, b):
    return clamp01((t - a) / (b - a))


def ease_out(u):
    return 1 - (1 - u) ** 3


def ease_in_out(u):
    return 4 * u ** 3 if u < 0.5 else 1 - ((-2 * u + 2) ** 3) / 2


# ---------------------------------------------------------------- scaffolding
def wipe():
    bpy.ops.wm.read_factory_settings(use_empty=True)


def principled(name, **kw):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    b = mat.node_tree.nodes["Principled BSDF"]
    for k, v in kw.items():
        if k in b.inputs:
            b.inputs[k].default_value = v
    return mat


def mesh_from(name, verts, faces, mat=None):
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], faces)
    me.validate()
    me.shade_smooth()
    ob = bpy.data.objects.new(name, me)
    if mat:
        ob.data.materials.append(mat)
    bpy.context.collection.objects.link(ob)
    return ob


def blade(length, halfwidth, cup, bend, nu=13, nv=5, fullness=0.7, crimp=0.0):
    """
    One leaf or petal, generated rather than modelled.

    A flat plane reads as paper at any lighting; the two things that make a
    blade read as botanical are the width profile (widest short of the middle,
    tapering to a point) and the CUP across the width, which is what catches a
    rim light along the centre line and leaves the edges dark.
    """
    verts, faces = [], []
    for i in range(nu):
        u = i / (nu - 1)
        w = halfwidth * (math.sin(math.pi * u) ** fullness) * (1.0 - 0.25 * u)
        drop = bend * (u ** 2)
        for j in range(nv):
            v = j / (nv - 1) * 2 - 1
            x = v * w
            # A poppy petal comes out of the pod CREASED and opens by
            # uncreasing. The crimp is a standing wave across the width,
            # strongest at mid-length where the petal is widest — it is the
            # single feature that separates a poppy from a tulip, and it is
            # what makes the opening read as unfolding rather than scaling.
            crease = crimp * math.sin(v * math.pi * 2.5) * math.sin(math.pi * u) * halfwidth
            verts.append((x, u * length, -drop - cup * (x ** 2) + crease))
    for i in range(nu - 1):
        for j in range(nv - 1):
            a = i * nv + j
            faces.append((a, a + 1, a + nv + 1, a + nv))
    return verts, faces


# ---------------------------------------------------------------- the build
class Scene:
    """Everything in the shot, plus the one function that moves it."""

    def __init__(self):
        wipe()
        self.mat_stem = principled("stem", **{"Base Color": DEAD_STEM, "Roughness": 0.72})
        self.mat_leaf = principled("leaf", **{"Base Color": DEAD_LEAF, "Roughness": 0.62})
        # Poppy petals are thin and translucent — backlit they glow rather than
        # simply being lit, which is the entire reason for a rim key in a dark
        # scene. Without transmission they read as painted card.
        self.mat_petal = principled(
            "petal", **{"Base Color": PETAL, "Roughness": 0.38,
                        "Transmission Weight": 0.38, "IOR": 1.36})
        self.mat_eye = principled(
            "eye", **{"Base Color": (0.022, 0.014, 0.012, 1.0), "Roughness": 0.55})
        self.mat_glass = principled(
            "glass", **{"Base Color": (0.86, 0.88, 0.84, 1.0), "Roughness": 0.045,
                        "IOR": 1.45, "Transmission Weight": 1.0})
        self.mat_water = principled(
            "water", **{"Base Color": (0.115, 0.082, 0.048, 1.0), "Roughness": 0.06,
                        "IOR": 1.33, "Transmission Weight": 0.85})
        self.mat_table = principled(
            "table", **{"Base Color": (0.030, 0.021, 0.014, 1.0), "Roughness": 0.86})

        self._table()
        self._jar()
        self._stem()
        self._leaves()
        self._flower()
        self._lights()
        self._camera()
        self._world()

    # -- set ----------------------------------------------------------------
    def _table(self):
        bpy.ops.mesh.primitive_plane_add(size=6, location=(0, 0, 0))
        t = bpy.context.object
        t.name = "table"
        t.data.materials.append(self.mat_table)

    def _jar(self):
        """
        A mason jar: a straight body, a shoulder that pulls in, a short neck.
        Built as a lathe of a profile rather than a cylinder, because the whole
        reason to use a jar is the shoulder — it is where the rim light breaks.
        """
        prof = [(0.000, 0.000), (0.062, 0.000), (0.062, 0.150), (0.062, 0.188),
                (0.055, 0.205), (0.046, 0.222), (0.046, 0.243)]
        verts, faces = [], []
        seg_n = 48
        for ring, (r, z) in enumerate(prof):
            for k in range(seg_n):
                a = k / seg_n * math.tau
                verts.append((r * math.cos(a), r * math.sin(a), z))
        for ring in range(len(prof) - 1):
            for k in range(seg_n):
                k2 = (k + 1) % seg_n
                a = ring * seg_n + k
                b = ring * seg_n + k2
                c = (ring + 1) * seg_n + k2
                d = (ring + 1) * seg_n + k
                faces.append((a, b, c, d))
        jar = mesh_from("jar", verts, faces, self.mat_glass)
        # Thickness is what makes glass read as glass — a zero-width surface
        # refracts like a soap film and the jar looks like a hologram.
        jar.modifiers.new("solid", 'SOLIDIFY').thickness = 0.004

        # A finger of water, not half a jar. At 13cm deep it filled the body
        # and read as an opaque tin can rather than as glass with something in
        # it — the jar has to be mostly EMPTY for the light to get through it.
        bpy.ops.mesh.primitive_cylinder_add(radius=0.0585, depth=0.042,
                                            location=(0, 0, 0.021))
        w = bpy.context.object
        w.name = "water"
        w.data.materials.append(self.mat_water)

    def _stem(self):
        """
        The stem is a curve with a bevel, and growth is `bevel_factor_end` —
        the cleanest growth primitive Blender has. It extrudes the profile
        along the path, so a partially grown stem is a real, closed, lit
        object rather than a scaled one.
        """
        cu = bpy.data.curves.new("stem", 'CURVE')
        cu.dimensions = '3D'
        cu.bevel_depth = 0.0045
        cu.bevel_resolution = 3
        cu.use_fill_caps = True
        sp = cu.splines.new('BEZIER')
        pts = [(0.000, 0.000, 0.055), (0.012, 0.006, 0.150), (-0.010, -0.004, 0.250),
               (0.014, 0.008, 0.345), (0.004, 0.000, 0.430)]
        sp.bezier_points.add(len(pts) - 1)
        for bp, p in zip(sp.bezier_points, pts):
            bp.co = Vector(p)
            bp.handle_left_type = bp.handle_right_type = 'AUTO'
        self.stem = bpy.data.objects.new("stem", cu)
        self.stem.data.materials.append(self.mat_stem)
        bpy.context.collection.objects.link(self.stem)
        self.stem_pts = pts

    def _leaves(self):
        """Six leaves up the stem, alternating sides, each with its own beat."""
        self.leaves = []
        spec = [(0.20, 20, 0.052), (0.32, 200, 0.060), (0.44, 95, 0.056),
                (0.56, 275, 0.050), (0.68, 150, 0.044), (0.80, 330, 0.038)]
        for i, (h, az, ln) in enumerate(spec):
            v, f = blade(ln, ln * 0.30, 5.5, ln * 0.34)
            ob = mesh_from(f"leaf{i}", v, f, self.mat_leaf)
            z = 0.055 + h * (0.430 - 0.055)
            ob.location = (0, 0, z)
            ob.rotation_euler = (math.radians(58), 0, math.radians(az))
            ob.scale = (0, 0, 0)
            self.leaves.append((ob, h))

    def _flower(self):
        """
        A POPPY, and the choice is structural rather than decorative.

        Its bud is a nodding grey-green pod that reads as dead; the head LIFTS
        before it opens, which is anticipation happening in the plant itself;
        and the petals come out creased and open by uncreasing. A tulip bud
        already looks like a flower and a tulip opens by scaling — neither
        carries "a dead thing coming alive" the way this does.

        Everything hangs off `self.head`, an empty at the top of the stem, so
        the nod is one rotation rather than five objects kept in sync.
        """
        bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, 0.430))
        self.head = bpy.context.object
        self.head.name = "head"

        def child(ob):
            ob.parent = self.head
            ob.matrix_parent_inverse = self.head.matrix_world.inverted()

        # A real poppy has four petals. Four MODELLED petals do not work: from a
        # front-on camera you see two face-on and two edge-on, and the open
        # flower reads as a pair of blades sticking out sideways rather than as
        # a bowl. Six wide, heavily overlapping petals give the same silhouette
        # a poppy has — a continuous cup — from any angle. Botany loses to the
        # camera here.
        self.petals = []
        NP = 6
        for i in range(NP):
            v, f = blade(0.086, 0.078, 3.0, 0.008, nu=17, nv=11,
                         fullness=0.38, crimp=0.26)
            ob = mesh_from(f"petal{i}", v, f, self.mat_petal)
            ob.location = (0, 0, 0.430)
            ob.rotation_euler = (0, 0, (i / NP) * math.tau + math.radians(30))
            ob.scale = (0, 0, 0)
            child(ob)
            self.petals.append(ob)

        # the pod: two sepals that split and fall away as the flower opens
        self.calyx = []
        for i in range(2):
            v, f = blade(0.062, 0.042, 4.0, 0.008, fullness=0.38)
            ob = mesh_from(f"sepal{i}", v, f, self.mat_stem)
            ob.location = (0, 0, 0.424)
            ob.rotation_euler = (math.radians(16), 0, i * math.pi)
            ob.scale = (0, 0, 0)
            child(ob)
            self.calyx.append(ob)

        # the dark boss at the centre, and a ring of stamens around it — the
        # black eye is most of what makes a red flower read as a poppy
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.015, location=(0, 0, 0.4345))
        boss = bpy.context.object
        boss.name = "boss"
        boss.scale = (1, 1, 0.62)
        boss.data.materials.append(self.mat_eye)
        child(boss)
        self.boss = boss

        self.stamens = []
        for i in range(28):
            a = i / 28 * math.tau
            bpy.ops.mesh.primitive_cylinder_add(
                radius=0.0011, depth=0.026,
                location=(0.020 * math.cos(a), 0.020 * math.sin(a), 0.4395))
            st = bpy.context.object
            st.rotation_euler = (math.radians(13) * math.cos(a + math.pi),
                                 math.radians(13) * math.sin(a), 0)
            st.data.materials.append(self.mat_eye)
            st.scale = (0, 0, 0)
            child(st)
            self.stamens.append(st)

    def _lights(self):
        """
        Dark. One warm key behind and left, raking across the jar; a dim cool
        fill from the right so the glass has an edge on both sides; nothing
        else. The point of the act is that most of the frame is black.
        """
        bpy.ops.object.light_add(type='AREA', location=(-0.62, 0.68, 0.62))
        k = bpy.context.object
        k.data.energy = 46
        k.data.size = 0.80
        k.data.color = (1.0, 0.72, 0.44)
        k.rotation_euler = (math.radians(58), 0, math.radians(-138))
        self.key = k

        bpy.ops.object.light_add(type='AREA', location=(0.75, 0.30, 0.34))
        f = bpy.context.object
        f.data.energy = 5.5
        f.data.size = 0.7
        f.data.color = (0.62, 0.70, 0.92)
        f.rotation_euler = (math.radians(76), 0, math.radians(108))
        self.fill = f

    def _camera(self):
        """
        Framed from the geometry, not by eye. The subject runs from the table at
        z=0 to the open flower at about z=0.52, and it has to sit inside a 9:16
        frame with headroom — so the distance is solved for, not guessed.

        The first pass put the camera 0.86m away on an 85mm lens, which covers
        24cm of height: the jar filled the bottom of the frame, the stem ran off
        the top, and the flower — the entire point of the act — was never in
        shot at all.
        """
        self.lens = 65.0
        self.sensor_v = 24.0          # sensor_fit VERTICAL uses sensor_height
        subject_h = 0.62              # table to above the open flower, with air
        self.cam_far = subject_h / (2 * math.tan(
            math.atan(self.sensor_v / (2 * self.lens))))
        self.cam_near = self.cam_far * 0.88     # the push-in lands here
        self.cam_z = 0.255

        bpy.ops.object.camera_add(location=(0, -self.cam_far, self.cam_z))
        c = bpy.context.object
        c.data.lens = self.lens
        c.data.sensor_fit = 'VERTICAL'
        c.rotation_euler = (math.radians(90), 0, 0)
        bpy.context.scene.camera = c
        self.cam = c

    def _world(self):
        w = bpy.data.worlds.new("w")
        w.use_nodes = True
        w.node_tree.nodes["Background"].inputs[0].default_value = UMBER
        w.node_tree.nodes["Background"].inputs[1].default_value = 0.012
        bpy.context.scene.world = w

    # -- the one function that moves anything -------------------------------
    def set_time(self, t):
        """Position every element for time `t`. No keyframes anywhere."""
        # the stem climbs
        grow = ease_out(seg(t, *CLIMB))
        self.stem.data.bevel_factor_end = max(0.001, grow)

        # each leaf unfurls when the stem passes it, one eighth apart
        for ob, h in self.leaves:
            start = CLIMB[0] + (CLIMB[1] - CLIMB[0]) * h * 0.92
            u = ease_out(seg(t, start, start + BEAT * 1.5))
            ob.scale = (u, u, u)

        # THE NOD. The head hangs over while the pod swells, then lifts to
        # upright just before it opens. This is anticipation, performed by the
        # plant rather than applied to it — and it is the reason the opening
        # lands: the head arrives, holds for a beat, and only then breaks.
        swell = ease_out(seg(t, *BUD))
        # It lifts to -20 degrees, not to level. The camera sits below the
        # flower, so a head that comes fully upright presents the open bowl
        # edge-on and the poppy reads as a flat squashed disc. Leaning it
        # toward the lens is also what a real flower does — they face light.
        lift = ease_in_out(seg(t, BUD[0] + BEAT, OPEN[0]))
        self.head.rotation_euler = (math.radians(-74 + 54 * lift), 0, 0)

        opening = ease_in_out(seg(t, *OPEN))
        for ob in self.calyx:
            # the two sepals split back and drop away as the petals emerge
            ob.scale = (swell, swell, swell)
            ob.rotation_euler = (math.radians(16 + 96 * opening),
                                 0, ob.rotation_euler.z)

        for st in self.stamens:
            u = ease_out(seg(t, OPEN[0] + BEAT * 0.5, OPEN[1]))
            st.scale = (u, u, u)

        self.boss.scale = (swell, swell, swell * 0.62)

        for i, ob in enumerate(self.petals):
            ob.scale = (swell, swell, swell)
            # CLOSED IS HIGH PITCH. The blade is generated along +Y and pitch
            # rotates about X, so pitch 90 stands the petal upright (a bud) and
            # pitch 0 lays it flat (open). Writing this the intuitive way round
            # — small angle for "closed" — ran the bloom backwards: the flower
            # was wide open at 12.5s and a tight bud at 13.4s.
            # 96 -> 18 degrees, not 96 -> -8. Taken all the way past flat the
            # petals reflex right back and the flower reads as a parasol; a
            # flower that has just opened still has its petals lifting.
            pitch = math.radians(104 - 74 * opening)
            ob.rotation_euler = (pitch, 0, i / len(self.petals) * math.tau)

        # dead to alive, in the material rather than in a swap
        life = seg(t, CLIMB[0] + BAR, OPEN[1])
        mix = lambda a, b: tuple(a[i] + (b[i] - a[i]) * life for i in range(4))
        self.mat_stem.node_tree.nodes["Principled BSDF"].inputs["Base Color"] \
            .default_value = mix(DEAD_STEM, LIVE_STEM)
        self.mat_leaf.node_tree.nodes["Principled BSDF"].inputs["Base Color"] \
            .default_value = mix(DEAD_LEAF, LIVE_LEAF)

        # the light comes up as the thing comes alive — the act starts nearly black
        self.key.data.energy = 46 * (0.28 + 0.72 * ease_out(seg(t, bt(2), bt(20))))

        # a slow push in, the whole act. 86cm to 68cm over thirteen seconds is
        # barely perceptible per second and unmistakable across the act.
        push = ease_in_out(seg(t, 0, ACT_I_END))
        dist = self.cam_far + (self.cam_near - self.cam_far) * push
        self.cam.location = (0, -dist, self.cam_z + 0.030 * push)
