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

DARK      = (bt(0),  bt(4))    # the beam finds the floor; the jar is barely there
CLIMB     = (bt(4),  bt(22))   # the stem grows
BUD       = (bt(19), bt(25))   # the bud forms and swells
OPEN      = (bt(25), bt(27))   # the flower opens, IN the beam
ARC       = (bt(27), bt(29))   # up and over: the flower becomes a rosette
PUSH      = (bt(29), bt(31))   # then down into it until the petals own the frame
SHUTTER   = (bt(32) - BEAT / 4, bt(32))    # one sixteenth of black. A blink.
ACT_I_END = bt(32)             # 15.36s — eight bars

# THE ARC IS THE WHOLE TRANSITION.
#
# A poppy seen from directly above is petals radiating from a dark centre —
# which is the same image as the paint detonation that follows it. Side-on they
# are two different pictures that have to be joined; from above they are one
# picture in two media, and the cut stops being a transition and becomes a
# SUBSTITUTION. Coming down into the petals until they fill the frame also
# strips out the jar, the table and every cue to scale, so the last 3D frame is
# already nearly abstract before the paint touches it.
#
# The black between them is a SIXTEENTH, not a beat. Long enough to read as an
# event; far too short to throw away the match the arc just built.

# ---------------------------------------------------------------- palette
# The ground never leaves the warm family. The living green is the plant's own
# accent and is deliberately an olive, not a chlorophyll green — it has to sit
# next to umber without arguing with it.
UMBER      = (0.043, 0.017, 0.010, 1.0)
DEAD_STEM  = (0.058, 0.043, 0.028, 1.0)
LIVE_STEM  = (0.088, 0.121, 0.052, 1.0)
DEAD_LEAF  = (0.062, 0.046, 0.028, 1.0)
LIVE_LEAF  = (0.105, 0.155, 0.062, 1.0)
PETAL      = (0.640, 0.170, 0.048, 1.0)   # vermilion — see BRIEF, the red-field rule
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
def aim_at(ob, target):
    """
    Point a light (or anything) at a world-space target.

    Lights get aimed by hand-typed Euler angles all over tutorials and it is
    guesswork: the rim spot in this scene was set to (118, 0, -141) degrees and
    lit nothing at all, which is indistinguishable from an energy that is too
    low. A direction vector cannot be wrong in that way.
    """
    d = ob.location - Vector(target)
    ob.rotation_euler = d.to_track_quat('Z', 'Y').to_euler()


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
        self._beam()   # after _lights: the cone is placed and aimed with the lamp
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
            # Cup 3.0 inflated each petal into a smooth bulb — from above the
            # flower read as a peach rather than as overlapping tissue. A poppy
            # petal is THIN and creased: less cup, more crimp.
            v, f = blade(0.088, 0.080, 1.5, 0.008, nu=21, nv=15,
                         fullness=0.36, crimp=0.40)
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
        # The boss fills the centre of the frame in the birds-eye, so its
        # default 32x16 faceting is visible as a hexagon. It is the one object
        # in the scene that has to survive a full-screen close-up.
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.015, segments=64, ring_count=32,
                                             location=(0, 0, 0.4345))
        boss = bpy.context.object
        boss.name = "boss"
        boss.scale = (1, 1, 0.62)
        boss.data.materials.append(self.mat_eye)
        child(boss)
        self.boss = boss

        self.stamens = []
        for i in range(52):
            a = i / 52 * math.tau
            bpy.ops.mesh.primitive_cylinder_add(
                radius=0.00075, depth=0.030,
                location=(0.019 * math.cos(a), 0.019 * math.sin(a), 0.4405))
            st = bpy.context.object
            st.rotation_euler = (math.radians(13) * math.cos(a + math.pi),
                                 math.radians(13) * math.sin(a), 0)
            st.data.materials.append(self.mat_eye)
            st.scale = (0, 0, 0)
            child(st)
            self.stamens.append(st)

    def _lights(self):
        """
        ONE SHAFT, STRAIGHT DOWN. A hard spot from high above drops a pool of
        light on the table and the jar stands in it — everything outside the
        pool is black. This replaced a back-left rake, which lit the jar
        prettily but described nothing: there was no reason for the light, no
        place for the camera to travel to, and nothing for the blackout to take
        away.

        A narrow spot with a small radius is what makes the edge of the pool
        hard. A soft-edged pool reads as a vignette; a hard one reads as a
        beam coming through something.
        """
        # DIRECTLY OVER THE JAR. Offset by 5cm and 10cm the shaft came down
        # beside the flower and lit the table next to it — which renders as a
        # bright column standing next to the subject and reads as a lit card,
        # not as a beam. The whole image is the flower standing IN the light.
        # OFF VERTICAL BY ABOUT 12 DEGREES. Straight down works for the wide
        # side-on act and fails the moment the camera arcs overhead: the camera
        # ends up inside its own light, the petals get no raking and the flower
        # reads as a flat red disc rather than as petals. A tilted shaft keeps
        # light travelling ACROSS the flower from above, which is what models it.
        # Tilted toward the camera side (-Y), not away. At (0.42, +0.36) the
        # shaft came from behind the subject and the poppy went dark exactly
        # when it needed to be at its brightest — correctly lit, and backlit.
        bpy.ops.object.light_add(type='SPOT', location=(0.36, -0.24, 2.02))
        k = bpy.context.object
        k.data.energy = 620
        # A SHAFT IS ONLY A SHAFT IF YOU CAN SEE ITS EDGES. At 19 degrees the
        # cone was 58cm across where the frame is 46cm wide, so the haze filled
        # the entire frame and read as a general lift rather than as a beam —
        # the camera was inside the light. Ten degrees puts both edges in shot
        # with black either side, which is the whole image.
        k.data.spot_size = math.radians(7)
        # A soft blend is what gives the shaft soft edges. The haze is lit BY
        # this spot, so the light's falloff is the beam's falloff.
        k.data.spot_blend = 0.52
        k.data.shadow_soft_size = 0.035
        k.data.color = (1.0, 0.79, 0.55)
        aim_at(k, (0.0, 0.015, 0.0))      # onto the table, through the flower
        self.key = k

        # THERE IS NO FILL. A cool area light used to sit off to the right to
        # give the glass an edge outside the pool, and it laid two hard pale
        # trapezoids across the table either side of the jar — which read as
        # flat cards standing behind the subject and survived several passes
        # because they look like set dressing. Turning off its camera
        # visibility does not help: what is in shot is the light it CASTS, not
        # the light itself.
        #
        # It is gone rather than repositioned, because a direct sun beam is one
        # source by definition. The glass gets its edge from the shaft's own
        # bounce off the table and from a hair of world ambient instead, which
        # is what would actually happen in a dark room with one window.
        # The rim is a narrow SPOT from behind, not an area light. An area
        # light large enough to edge the glass also lays a wide pale footprint
        # across the table, and that footprint — not the lamp itself — is what
        # rendered as two flat cards flanking the jar. A tight spot aimed at
        # the jar from behind puts its small ellipse behind the subject, where
        # the jar itself hides it, and still catches both edges of the glass.
        bpy.ops.object.light_add(type='SPOT', location=(-0.42, 0.52, 0.46))
        r = bpy.context.object
        r.data.energy = 42
        r.data.spot_size = math.radians(26)
        r.data.spot_blend = 0.6
        r.data.shadow_soft_size = 0.05
        r.data.color = (1.0, 0.80, 0.60)
        aim_at(r, (0.0, 0.0, 0.16))       # the jar's body, not the flower
        self.fill = r

        # LIGHT LINKING. Any light placed to edge the glass also throws its own
        # footprint across the table, and that footprint is what read as pale
        # cards behind the jar through several passes. Rather than hunting for
        # a position where the footprint hides — there isn't one, the table is
        # six metres wide — the rim is linked to the glass alone. It edges the
        # jar and cannot touch the table at all. The shaft stays the only thing
        # lighting the room, which is what "a direct sun beam" means.
        link = bpy.data.collections.new("rim_receivers")
        bpy.context.scene.collection.children.link(link)
        for name in ("jar", "water"):
            link.objects.link(bpy.data.objects[name])
        r.light_linking.receiver_collection = link

    def _beam(self):
        """
        The shaft made visible: a cone of thin haze from the spot down to the
        table, as a BOUNDED volume rather than a world volume. A world volume
        makes every ray in the scene a volume ray and the frame cost roughly
        triples; a cone that contains only the beam costs a fraction of that
        and is the only place the haze would be visible anyway.
        """
        # Built along -Z from an apex at the origin, then placed at the lamp and
        # aimed with it. Built in world-vertical coordinates the cone no longer
        # lines up with a tilted shaft, and the haze sits beside the light.
        h = 2.10
        r_top = 0.035
        # The haze cone is deliberately WIDER than the light cone (5.5 deg
        # against the spot's 3.5). Matched exactly, the volume's own boundary
        # is the visible edge and the beam renders as a bar with hard vertical
        # sides; wider, the edge you see is the light falling off, which is
        # what a real shaft has.
        r_bot = math.tan(math.radians(5.5)) * h
        verts, faces = [], []
        n = 36
        for ring, (r, z) in enumerate(((r_top, 0.0), (r_bot, -h))):
            for k in range(n):
                a = k / n * math.tau
                verts.append((r * math.cos(a), r * math.sin(a), z))
        for k in range(n):
            k2 = (k + 1) % n
            faces.append((k, k2, n + k2, n + k))
        # CAP BOTH ENDS. A volume needs a closed manifold — an open tube has no
        # inside for Cycles to fill, so it renders as nothing at all, at any
        # density. The beam was invisible for exactly this reason and it looks
        # identical to "the density is too low".
        faces.append(tuple(range(n)))                       # top
        faces.append(tuple(reversed(range(n, 2 * n))))      # bottom
        cone = mesh_from("beam", verts, faces)

        mat = bpy.data.materials.new("haze")
        mat.use_nodes = True
        nt = mat.node_tree
        for node in list(nt.nodes):
            if node.type != 'OUTPUT_MATERIAL':
                nt.nodes.remove(node)
        vol = nt.nodes.new("ShaderNodeVolumePrincipled")
        vol.inputs["Color"].default_value = (1.0, 0.84, 0.63, 1.0)
        vol.inputs["Density"].default_value = 0.0
        vol.inputs["Anisotropy"].default_value = 0.42
        nt.links.new(vol.outputs["Volume"], nt.nodes["Material Output"].inputs["Volume"])
        cone.data.materials.append(mat)
        cone.visible_shadow = False
        cone.location = self.key.location
        aim_at(cone, (0.0, 0.015, 0.0))
        self.beam = cone
        self.haze = vol

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
        # "and then the camera goes there" — it starts well back in the dark and
        # travels into the pool, rather than easing forward a few centimetres.
        # It arrives AT the solved framing, it does not push past it. Ending at
        # 0.86x cropped the bottom of the jar and lost the pool of light
        # entirely — the camera travelled to the beam and then straight through
        # it, which throws away the thing it travelled for.
        # The opening frame has to be WIDE. A shaft only reads while there is
        # darkness either side of it and you can see it descending from above;
        # start close and the camera is already inside the light, which is why
        # the beam kept reading as a general lift. At 3.2x the frame is ~1.1m
        # across and the beam is 21cm of it — unmistakable — and the travel
        # then means something, because it ends inside what it started outside.
        self.cam_start = self.cam_far * 3.2
        # Where the arc ends. At 0.40m the open flower (~17cm across) more than
        # covers a frame that is 8cm wide there, so the petals own the screen
        # and nothing else is in shot.
        # TWO DISTANCES, NOT ONE. The arc stops at 0.86m, where the whole
        # 17cm flower just fills a 17.9cm frame — that is the rosette, petals
        # radiating from a dark centre, and it is the entire reason for going
        # overhead. Only then does it push in to 0.42m, where the frame is 8.7cm
        # and the petals cover the screen. Going straight to 0.42 skips the
        # rosette and lands the camera INSIDE the flower, looking at one sepal.
        self.arc_r = 0.86
        self.arc_end_r = 0.36
        self.head_at = Vector((0.0, 0.0, 0.436))
        self.cam_near = self.cam_far
        self.cam_z = 0.255

        bpy.ops.object.camera_add(location=(0, -self.cam_start, self.cam_z))
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
        w.node_tree.nodes["Background"].inputs[1].default_value = 0.030
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
        # ...and then it straightens the rest of the way as the camera comes
        # over the top. A flower turning to face the light is motivated, and it
        # is what turns the overhead shot into a true plan view: arcing to 86
        # degrees above a head still tilted 20 degrees only ever gives a
        # three-quarter, which is the one thing the birds-eye must not be.
        face = ease_in_out(seg(t, ARC[0], ARC[1]))
        self.head.rotation_euler = (
            math.radians(-74 + 54 * lift + 16 * face), 0, 0)

        opening = ease_in_out(seg(t, *OPEN))
        # The petals keep relaxing for three beats after they have "opened".
        # Without it the flower is finished and static for the whole arc — a
        # dead subject during the biggest camera move in the film — and the
        # settle is follow-through, which is one of the five principles the
        # series is about.
        settle = ease_out(seg(t, OPEN[1], OPEN[1] + BEAT * 3))
        for ob in self.calyx:
            # THE SEPALS ARE SHED. A poppy's two sepals split and fall off as
            # the flower opens; they exist to be the bud and then they are gone.
            # Kept at full size they lie across the flower's face — which is
            # invisible from the side and ruins the entire birds-eye, because
            # the camera arcs overhead to look at petals and finds a 6cm green
            # blade covering the centre instead.
            g = swell * (1.0 - opening)
            ob.scale = (g, g, g)
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
            pitch = math.radians(104 - 74 * opening - 6 * settle)
            ob.rotation_euler = (pitch, 0, i / len(self.petals) * math.tau)

        # dead to alive, in the material rather than in a swap
        life = seg(t, CLIMB[0] + BAR, OPEN[1])
        mix = lambda a, b: tuple(a[i] + (b[i] - a[i]) * life for i in range(4))
        self.mat_stem.node_tree.nodes["Principled BSDF"].inputs["Base Color"] \
            .default_value = mix(DEAD_STEM, LIVE_STEM)
        self.mat_leaf.node_tree.nodes["Principled BSDF"].inputs["Base Color"] \
            .default_value = mix(DEAD_LEAF, LIVE_LEAF)

        # THE BEAM, then THE CUT.
        #
        # The shaft finds the floor over the first bar and holds; the haze
        # thickens a little as the camera comes into it, because a beam reads
        # denser the closer you are to it. Then on bt(27) everything goes, in
        # two frames — a fade would be a dimmer being turned down, and this has
        # to be a switch.
        find = ease_out(seg(t, bt(1), bt(4)))
        near = ease_in_out(seg(t, 0, ACT_I_END))
        # A CUT, NOT A DIP. Ramping across the sixteenth means the frame only
        # reaches black on the very last one and then snaps back to full — a
        # lopsided dip rather than a blink. The lights are simply off for the
        # whole sixteenth, which is what "the lights cut out" means and what
        # makes the paint arrive out of nothing.
        live = 0.0 if t >= SHUTTER[0] else 1.0

        # EXPOSURE COMPENSATION ON THE PUSH.
        #
        # The camera closes from 3.2x the framing distance down to 0.36m, and
        # the pool it is travelling into gets brighter the whole way — so the
        # poppy renders dim at 13s and blazing at 15s. It is one continuous
        # shot of one flower, but a viewer reads a colour that swings that far
        # as two different objects, which is the one thing this act cannot
        # afford. The key pulls back through the arc and the push so the petals
        # hold the same vermilion from the moment they open to the moment the
        # paint takes them.
        close = ease_in_out(seg(t, ARC[0], PUSH[1]))
        self.key.data.energy = 620 * find * live * (1.0 - 0.42 * close)
        self.fill.data.energy = 42 * find * live
        # Density 0.9 is a faint mist. A shaft you can SEE in a dark room needs
        # an order of magnitude more than that — at 0.9 the pool on the floor
        # rendered but the beam making it did not, which is most of the shot.
        self.haze.inputs["Density"].default_value = (7.0 + 5.0 * near) * find * live

        # --- the camera -------------------------------------------------
        # Two moves, back to back. First the long travel across the dark room
        # into the pool. Then the arc: up and over the flower until the lens is
        # looking straight down its throat, coming in to 40cm so the petals
        # cover the frame.
        #
        # It is an ARC, not a cut to plan view, and that is deliberate. The
        # whole act has been one unbroken move; a cut here would read as a
        # different shot and hand the viewer a seam exactly where the film is
        # trying to hide one.
        travel = ease_in_out(seg(t, 0, ARC[0]))
        a = ease_in_out(seg(t, *ARC))
        pu = ease_in_out(seg(t, *PUSH))

        dist = self.cam_start + (self.cam_near - self.cam_start) * travel
        ground = Vector((0.0, -dist, self.cam_z + 0.034 * travel))

        if a <= 0.0:
            self.cam.location = ground
            self.cam.rotation_euler = (math.radians(90), 0, 0)
        else:
            # spherical around the flower head: elevation 0 (level, where the
            # travel left off) to 86 degrees (very nearly overhead), radius
            # easing down to arc_end_r
            r0 = (ground - self.head_at).length
            r = r0 + (self.arc_r - r0) * a
            r += (self.arc_end_r - self.arc_r) * pu
            elev = math.radians(2.0 + 84.0 * a + 2.0 * pu)
            # a few degrees of azimuth as it rises, so the move has some drift
            # in it and does not read as a mechanical crane
            az = math.radians(-90.0 + 14.0 * a + 6.0 * pu)
            self.cam.location = self.head_at + Vector((
                r * math.cos(elev) * math.cos(az),
                r * math.cos(elev) * math.sin(az),
                r * math.sin(elev)))
            aim_at(self.cam, self.head_at)
