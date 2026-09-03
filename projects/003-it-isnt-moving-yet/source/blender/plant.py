#!/usr/bin/env python3
"""
ACT I — the jar. A dead thing in a mason jar, growing in the dark, that blooms.

Built the way the rest of this repo is built: there are NO KEYFRAMES. The scene
is constructed once and `set_time(t)` positions every element for time `t`, the
same contract as `window.renderFrame(t)` in video.html. Blender's animation
system is a second source of truth and a second thing to keep in sync with the
129 BPM grid; a pure function of t is neither.

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
# 129, not 125, and it is not a preference — it is the tempo of the track the
# film is cut to (Luifer, "Gracias a Ti", measured at 129.000 BPM exactly).
# Every constant below is written in bt(), so the whole act re-times off this
# one number; nothing else in this file needed touching when it changed.
BPM = 129
BEAT = 60.0 / BPM          # 0.46512
BAR = 4 * BEAT             # 1.92
bt = lambda n: n * BEAT

DARK      = (bt(0),  bt(4))    # the beam finds the floor; the jar is barely there
CLIMB     = (bt(4),  bt(22))   # the stem grows
BUD       = (bt(19), bt(25))   # the bud forms and swells
OPEN      = (bt(25), bt(27))   # the flower opens, IN the beam
HOLD      = (bt(27), bt(37))   # open, and the room going out around it
DETACH    = (bt(37), bt(38))   # one petal peels, on the last beat of music
FALL      = (bt(38), bt(44))   # and falls through six beats of pure silence

# THE TWO GLITCHES, and they are frames rather than a range.
#
# "Its original colour coming down and then glitching into 2 styles." The petal
# falls in its own vermilion, and twice on the way down the WHOLE FRAME becomes
# one of the languages that is coming — two frames, then back. Not a tint on the
# petal: a glitch is a whole-frame event, and half-glitching one object in a
# frame reads as a lighting effect on the object.
#
# They land on the two beats inside the silence that are NOT the downbeats, so
# they fall where the music would have put a snare if there were any music. In a
# bar and a half of nothing, the ear is still counting.
GLITCH_AT = (bt(40), bt(42))
GLITCH_FR = 2                  # frames each, at 24fps — a sixth of a beat
ACT_I_END = bt(44)             # 20.465s — eleven bars

# --- and the other end of the film ----------------------------------------
# The last four bars are Blender again. The studio drains to black on the
# track's second break, and out of that black ONE MORE PETAL falls — the same
# object, the same light — and lands in the jar it grew out of. The camera
# pulls back through the fall to exactly the framing of frame 0, and the beam
# dies the way it arrived, so the film's last frame and its first are the same
# black room and the loop has no seam in it at all.
#
# This is the thing the birds-eye arc could never have done. A camera move
# cannot come back; a petal can.
ENDFALL   = (bt(92),  bt(105))  # it falls, and the room comes back around it
ENDDIE    = (bt(105), bt(108))  # the beam goes out. Frame 0 is black too.
FILM_END  = bt(108)             # 50.233s — twenty-seven bars

# WHERE THE BIRDS-EYE ARC USED TO BE.
#
# Bars 8-11 were a camera arc up over the open flower to a plan view and then a
# push into the petals, and BRIEF.md called it the best structural idea in the
# film: a poppy from above is petals radiating from a dark centre, which is the
# paint detonation's own picture, so the cut became a substitution.
#
# It is gone, and what replaces it is better for a reason the arc could not
# reach. The arc was the CAMERA doing something. A petal letting go is the
# FLOWER doing something — and the film is about things that are not alive
# becoming alive, so every beat it can hand to the subject instead of the rig
# is a beat that argues its own case. The substitution survives intact: the
# studio still erupts out of the last lit frame, it is just a petal now rather
# than a rosette, and handoff.py projects whatever is there.
#
# It also buys the one thing the arc never had: an object that can come back.
# The film ends on a second petal falling, and it falls into the jar it grew
# from. You cannot loop a camera move. You can loop a petal.

# THE FALL IS THE WHOLE TRANSITION.
#
# One petal lets go and drops through three bars of near-silence, lit by a beam
# that has closed down to just it. Everything else in the room is gone. It is
# the quietest the film ever gets and it sits immediately before the loudest,
# which is the only reason the studio reads as an explosion rather than as a
# busy section.
#
# The petal falls in its OWN colour — the vermilion it has been since it opened
# — and twice on the way down the whole frame glitches into one of the styles
# that is coming, for two frames, and snaps back. That is the film showing its
# hand: the fault the stem had in bar 2 has reached the flower, and this time it
# is not a colour, it is a whole language.
#
# There is no black before the studio. The petal is still on screen when the
# paint erupts out of it, because the substitution is the point: one object,
# two media, no seam. handoff.py projects whatever the last lit frame holds.
#
# AND THE TRACK WROTE THESE NUMBERS, NOT ME.
#
# The film is cut to Luifer's "Gracias a Ti" from 46.555s (its bar 25). That
# track has a HARD DIGITAL SILENCE — not a fade, a stop — running its beats
# 138 to 144, which lands at exactly bt(38) to bt(44) of the film. So:
#
#   bt(37)  the petal starts to peel, on the last beat of music there is
#   bt(38)  it lets go AND the music stops, in the same frame
#   bt(44)  the music slams back in on the downbeat, and the paint detonates
#
# Six beats of a petal falling through total silence, and the boom catches it.
# DETACH is one beat long and sits where it sits because of the track; do not
# move it without re-deriving it from the audio.

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

# THE FIVE ACCENTS, as the stem will flicker through them. These are the exact
# colours the five techniques use in video.html — rust, signal blue, hot red,
# mustard, plum — so the glitch in the stem is a genuine preview of the film's
# own back half rather than a decorative colour cycle.
#
# Converted sRGB -> linear, because Blender's colour inputs are linear and a hex
# value dropped straight in renders noticeably darker and duller than the swatch.
def _srgb(h):
    v = [int(h[i:i+2], 16) / 255.0 for i in (1, 3, 5)]
    lin = [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in v]
    return (lin[0], lin[1], lin[2], 1.0)

ACCENTS = [_srgb(h) for h in ('#A8341A', '#2C5FA8', '#D8452A', '#B8843A', '#7A2E52')]
PETAL_TIP  = (0.640, 0.240, 0.060, 1.0)   # ochre


def clamp01(v):
    return max(0.0, min(1.0, v))


def seg(t, a, b):
    return clamp01((t - a) / (b - a))


def ease_out(u):
    return 1 - (1 - u) ** 3


def ease_in_out(u):
    return 4 * u ** 3 if u < 0.5 else 1 - ((-2 * u + 2) ** 3) / 2


def ease_in(u):
    # For things that come apart. A petal starts letting go slowly and is
    # gone quickly, which is the opposite shape to anything that grows.
    return u ** 3


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


def petal_material():
    """
    A poppy petal is CREASED TISSUE, and at the size this one reaches — six
    petals filling a 1080-wide frame — a smooth Principled surface reads as
    moulded plastic. Three things fix that, and none of them is a texture file:

    * a crumple, an isotropic noise bump, which is the crease itself;
    * a ROUGHNESS variation off the same noise — matte in the folds, silkier
      on the ridges. This is the half that actually reads as tissue. A second
      bump stretched 26:1 for veining was built first and thrown away: it made
      parallel streaks running the length of the petal, and with any sheen on
      them the birds-eye read as brushed satin ribbing. Petal veins are a
      shading detail at this size, and barely even that;
    * a per-petal VALUE jitter off `Object Info > Random`. Six petals cut from
      one mesh with one colour are an identical flat fill wherever they
      overlap, and their shared edge simply vanishes. The jitter multiplies
      RGB by one scalar, so it moves value and cannot move hue — the palette
      rule, in a node graph.

    Coordinates are Generated, not Object: Generated is normalised over the
    mesh bounding box in local space, so it is unaffected by the petal's scale
    animating 0 -> 1 during the bloom. Object coordinates would swim.
    """
    mat = bpy.data.materials.new("petal")
    mat.use_nodes = True
    nt = mat.node_tree
    b = nt.nodes["Principled BSDF"]
    # No sheen. Sheen over a bump is what turned the creases into glints.
    for k, v in (("Transmission Weight", 0.38), ("IOR", 1.36),
                 ("Specular IOR Level", 0.34)):
        if k in b.inputs:
            b.inputs[k].default_value = v

    tc = nt.nodes.new("ShaderNodeTexCoord")

    def noise(scale, detail, rough, mscale):
        m = nt.nodes.new("ShaderNodeMapping")
        m.inputs["Scale"].default_value = mscale
        nt.links.new(tc.outputs["Generated"], m.inputs["Vector"])
        n = nt.nodes.new("ShaderNodeTexNoise")
        n.inputs["Scale"].default_value = scale
        n.inputs["Detail"].default_value = detail
        n.inputs["Roughness"].default_value = rough
        nt.links.new(m.outputs["Vector"], n.inputs["Vector"])
        return n

    crumple = noise(15.0, 5.0, 0.58, (1.0, 1.0, 1.0))

    bump = nt.nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.16
    bump.inputs["Distance"].default_value = 0.005
    nt.links.new(crumple.outputs["Fac"], bump.inputs["Height"])
    nt.links.new(bump.outputs["Normal"], b.inputs["Normal"])

    rgh = nt.nodes.new("ShaderNodeMapRange")
    rgh.inputs["To Min"].default_value = 0.56
    rgh.inputs["To Max"].default_value = 0.30
    nt.links.new(crumple.outputs["Fac"], rgh.inputs["Value"])
    nt.links.new(rgh.outputs["Result"], b.inputs["Roughness"])

    info = nt.nodes.new("ShaderNodeObjectInfo")
    rng = nt.nodes.new("ShaderNodeMapRange")
    rng.inputs["To Min"].default_value = 0.84
    rng.inputs["To Max"].default_value = 1.14
    nt.links.new(info.outputs["Random"], rng.inputs["Value"])
    # The crumple also darkens where it folds away from the light, which is
    # what stops the jitter reading as six flat cards of six flat tints.
    fold = nt.nodes.new("ShaderNodeMapRange")
    fold.inputs["To Min"].default_value = 0.86
    fold.inputs["To Max"].default_value = 1.05
    nt.links.new(crumple.outputs["Fac"], fold.inputs["Value"])
    both = nt.nodes.new("ShaderNodeMath")
    both.operation = 'MULTIPLY'
    nt.links.new(rng.outputs["Result"], both.inputs[0])
    nt.links.new(fold.outputs["Result"], both.inputs[1])

    tint = nt.nodes.new("ShaderNodeVectorMath")
    tint.operation = 'SCALE'
    tint.inputs[0].default_value = PETAL[:3]
    nt.links.new(both.outputs["Value"], tint.inputs["Scale"])
    nt.links.new(tint.outputs["Vector"], b.inputs["Base Color"])
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
            # One 2.5-period wave alone is what made the open flower read as a
            # ring of INFLATED TUBES: at nv=15 six samples per period is a
            # perfectly smooth lobe, and six smooth lobes are a balloon. A
            # 7-period harmonic at a third the amplitude (and enough nv to
            # resolve it) turns the same silhouette into creased tissue.
            crease = crimp * halfwidth * math.sin(math.pi * u) * (
                math.sin(v * math.pi * 2.5) * 0.70
                + math.sin(v * math.pi * 7.0 + 0.9) * 0.30)
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
        self.mat_petal = petal_material()
        # The boss is the one surface that ever fills the whole frame, and a
        # near-black diffuse with a broad specular lobe reads GREY at that size
        # — the highlight covers the sphere. A poppy's eye is velvet: almost no
        # specular, almost no gloss.
        self.mat_eye = principled(
            "eye", **{"Base Color": (0.022, 0.014, 0.012, 1.0), "Roughness": 0.88,
                      "Specular IOR Level": 0.22})
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
            v, f = blade(0.088, 0.080, 1.5, 0.008, nu=25, nv=27,
                         fullness=0.36, crimp=0.40)
            ob = mesh_from(f"petal{i}", v, f, self.mat_petal)
            ob.location = (0, 0, 0.430)
            ob.rotation_euler = (0, 0, (i / NP) * math.tau + math.radians(30))
            ob.scale = (0, 0, 0)
            child(ob)
            self.petals.append(ob)

        # THE FALLER.
        #
        # A seventh petal, identical to the six but NOT parented to the head, so
        # it can be driven in world space once it lets go. At DETACH petal 0 is
        # scaled to nothing and this one appears at exactly where petal 0 was —
        # a swap, invisible because the two are the same mesh in the same place.
        #
        # Doing it by unparenting the real petal instead means fighting
        # matrix_parent_inverse for a transform that has to stay a pure function
        # of t; a swap has no state in it at all.
        v, f = blade(0.088, 0.080, 1.5, 0.008, nu=25, nv=27,
                     fullness=0.36, crimp=0.40)
        self.faller = mesh_from("faller", v, f, self.mat_petal)
        self.faller.scale = (0, 0, 0)

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

        # Fifty-two identical cylinders standing at 13 degrees off vertical,
        # all on one radius, read from the birds-eye as a BEAD NECKLACE — from
        # directly above an upright cylinder is a disc, so the ring the whole
        # act ends on was a circle of 52 dots. The fix is the flower's real
        # anatomy: poppy stamens SPLAY, and at 30-52 degrees they present their
        # length to an overhead camera instead of their end, so the same ring
        # reads as a radiating black fringe — which is also the paint bloom's
        # figure, one shot early.
        #
        # Everything is jittered off a hashed index, never `random()`: the
        # scene has to rebuild identically on every resumed chunk of a render.
        def jit(i, salt):
            return (((i * 2654435761 + salt * 40503) % 65536) / 65536.0)

        self.stamens = []
        NST = 86
        for i in range(NST):
            a = i / NST * math.tau + jit(i, 3) * 0.09
            r = 0.016 + 0.011 * jit(i, 7)
            lean = math.radians(26.0 + 18.0 * jit(i, 11))
            length = 0.019 + 0.011 * jit(i, 13)
            bpy.ops.mesh.primitive_cylinder_add(
                radius=0.00042, depth=length, vertices=8,
                location=(r * math.cos(a), r * math.sin(a), 0.4385 + length * 0.34))
            st = bpy.context.object
            st.rotation_euler = (lean * math.cos(a + math.pi), lean * math.sin(a), 0)
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
        # Where the beam points when nothing is falling. Kept as state because
        # set_time has to be able to aim it BACK here — see the note in
        # _set_time_act_one.
        self.key_home = Vector((0.0, 0.015, 0.0))
        aim_at(k, self.key_home)          # onto the table, through the flower
        self.key = k

        # A BOUNCE, LINKED TO THE PLANT ALONE. The shaft models the flower from
        # above and leaves the stem and the leaves as silhouettes; a dim warm
        # bounce from low and front puts detail back into them without touching
        # the table, which is what the light linking is for. It is the light a
        # pool of that brightness would actually throw back up.
        bpy.ops.object.light_add(type='AREA', location=(0.30, -0.60, 0.16))
        bo = bpy.context.object
        bo.data.energy = 7.5
        bo.data.size = 0.55
        bo.data.color = (1.0, 0.83, 0.62)
        aim_at(bo, (0.0, 0.0, 0.26))
        self.bounce = bo

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

        # the bounce sees the plant and nothing else
        plants = bpy.data.collections.new("plant_receivers")
        bpy.context.scene.collection.children.link(plants)
        for ob in (self.stem, *[l for l, _ in self.leaves], *self.petals,
                   *self.calyx, self.boss, *self.stamens):
            plants.objects.link(ob)
        bo.light_linking.receiver_collection = plants

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

    def faller_at(self, t):
        """
        Where the falling petal is at time `t`, in world space.

        A petal is not a stone. It is 0.1g of tissue with a lot of area, so it
        does not accelerate — it reaches terminal velocity almost at once and
        then FLUTTERS, swinging side to side as it stalls and slips off each
        edge in turn. Modelled as a constant descent with a pendulum across it,
        the swing slow (about one cycle per bar) and widening as it goes, plus a
        tumble that is deliberately not in phase with the swing. Gravity here
        would be wrong twice over: it would look like a falling stone, and it
        would put the whole descent in the first half-second of three bars.
        """
        u = seg(t, *FALL)
        z = 0.436 + (0.052 - 0.436) * u          # head height down to the table
        # THE SWING HAS TO CLEAR THE FLOWER, and that is a lighting requirement
        # before it is a botanical one. The beam comes straight down through the
        # head, so a petal that drops more or less vertically spends the whole
        # fall inside the flower's OWN SHADOW — lit correctly, in frame, and
        # completely black. At 6cm of flutter under a 17cm flower it never got
        # out. It reaches ~16cm now, which is far enough that the key (which
        # follows it) comes down beside the flower rather than through it — so
        # the petal is lit and the plant it left drops out of the beam and goes
        # dark by itself, which is the shot teti asked for anyway.
        # A petal falls AWAY from the plant, not straight down it — so the
        # sideways travel is a monotonic drift with the flutter riding on top,
        # not a pendulum through the middle. A pendulum spends half the fall
        # back at the stem, which is both wrong and unlightable.
        swing = 0.19 * u + 0.030 * math.sin(u * math.tau * 1.9)
        drift = 0.055 * u + 0.014 * math.sin(u * math.tau * 1.3 + 1.1)
        return Vector((swing, drift, z)), u

    def returner_at(self, t):
        """
        Where the LAST petal is, in the final four bars.

        It is the first fall run backwards in spirit but not in fact: it enters
        from above the frame and comes down into the jar's mouth, so its
        endpoint is fixed (the jar is at the origin) where the first fall's was
        free. That means the drift has to CONVERGE rather than spread — a petal
        that flutters outward on the way down would miss the jar and land on the
        table, and landing beside the thing you are falling back into is the one
        reading this shot cannot survive.
        """
        u = seg(t, *ENDFALL)
        e = ease_in_out(u)
        z = 0.62 + (0.148 - 0.62) * e            # above frame down to the neck
        # the flutter narrows to nothing as it arrives
        wob = (1.0 - e) ** 1.4
        x = 0.115 * (1.0 - e) + 0.034 * math.sin(u * math.tau * 2.2) * wob
        y = -0.052 * (1.0 - e) + 0.020 * math.sin(u * math.tau * 1.7 + 0.7) * wob
        return Vector((x, y, z)), u

    # -- the one function that moves anything -------------------------------
    def set_time(self, t):
        """Position every element for time `t`. No keyframes anywhere."""
        if t >= ENDFALL[0]:
            return self._set_time_ending(t)
        return self._set_time_act_one(t)

    def _set_time_ending(self, t):
        """
        THE LAST FOUR BARS. Everything the plant was is gone — the stem never
        grew, the flower never opened — because this is the room the film
        started in, and the film is about to start again. All that is here is
        the jar, the table, and one petal coming down into it.
        """
        pos, u = self.returner_at(t)

        # the plant is not in this shot at all
        self.stem.data.bevel_factor_end = 0.001
        for ob, _ in self.leaves:
            ob.scale = (0, 0, 0)
        for ob in (*self.petals, *self.calyx, self.boss, *self.stamens):
            ob.scale = (0, 0, 0)
        self.head.rotation_euler = (math.radians(-74), 0, 0)
        self.mat_stem.node_tree.nodes["Principled BSDF"] \
            .inputs["Base Color"].default_value = DEAD_STEM
        self.mat_leaf.node_tree.nodes["Principled BSDF"] \
            .inputs["Base Color"].default_value = DEAD_LEAF

        # the one petal, still tumbling, slowing as it arrives
        self.faller.location = pos
        self.faller.scale = (1, 1, 1)
        spin = ease_out(u)
        self.faller.rotation_euler = (
            math.radians(28) + 3.0 * spin,
            0.30 * math.sin(u * math.tau * 1.4) * (1.0 - spin),
            math.radians(50) + 1.7 * spin)
        for ob in (*self.petals, *self.calyx, self.boss, *self.stamens,
                   *[l for l, _ in self.leaves]):
            ob.visible_shadow = False

        # THE BEAM COMES BACK, AND THEN GOES OUT.
        #
        # It has to arrive at exactly what frame 0 is, and frame 0 is BLACK:
        # `find` ramps from bt(1) to bt(4), so at t=0 every lamp in this scene
        # is at zero and the room is dark. So the film does not fade to black as
        # a gesture — it lands on the same state it opens from, and the loop is
        # a match rather than a dissolve. The light dies at the end the way it
        # finds the floor at the start, which is the same event played the other
        # way round.
        back = ease_in_out(seg(t, ENDFALL[0], ENDFALL[0] + BAR * 0.5))
        die = ease_in_out(seg(t, *ENDDIE))
        lit = back * (1.0 - die)
        self.key.data.energy = 620 * lit
        self.key.data.spot_size = math.radians(4.0 + 3.0 * back)
        self.bounce.data.energy = 0.0
        self.fill.data.energy = 42 * lit
        self.haze.inputs["Density"].default_value = 11.0 * lit
        aim_at(self.key, Vector((0.0, 0.015, 0.0)) * ease_out(u)
               + pos * (1.0 - ease_out(u)))
        aim_at(self.beam, Vector((0.0, 0.015, 0.0)) * ease_out(u)
               + pos * (1.0 - ease_out(u)))

        # THE CAMERA PULLS BACK TO FRAME 0 AND STOPS THERE.
        #
        # It starts close on the petal, high, and retreats along the same axis
        # the opening travel came in on until it is standing exactly where the
        # first frame of the film stands. The last frame of the film IS the
        # first frame of the film, so the two can be butted with nothing between
        # them and no one can find the join.
        # HOLD CLOSE, THEN RETREAT. Easing the pull across the whole four bars
        # put the camera at 5.1m of its 5.4m travel with a third of the shot
        # still to run — so the reveal was over before the petal arrived and the
        # last two bars were a static wide of a jar the size of a thumbnail.
        # The move waits: two bars close on the falling petal, then the room
        # opens out around it in the two bars it actually lands in.
        pull = ease_in_out(seg(t, ENDFALL[0] + BAR * 2.0, ENDFALL[1]))
        # 0.62m, not 0.42. At 0.42 the petal is past being a petal — it is an
        # orange shape with the frame cutting it on three sides, and the reveal
        # then has to establish what it was as well as where it is. Starting a
        # little wider keeps it legible as the same object that fell in bar 10.
        r = 0.62 + (self.cam_start - 0.62) * pull
        zc = (self.cam_z + 0.034) + (self.cam_z - self.cam_z - 0.034) * pull
        self.cam.location = Vector((0.0, -r, zc + 0.16 * (1.0 - pull)))
        if pull > 0.985:
            self.cam.rotation_euler = (math.radians(90), 0, 0)
        else:
            aim_at(self.cam, pos * (1.0 - pull)
                   + Vector((0.0, 0.0, self.cam_z)) * pull)

    def _set_time_act_one(self, t):
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
        # It used to straighten further as the camera arced overhead. There is
        # no arc now, and the camera stays below the flower for the whole act,
        # so the head holds the lean it opened with — which is the angle that
        # shows the bowl rather than its edge.
        self.head.rotation_euler = (math.radians(-74 + 54 * lift), 0, 0)

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

        # THE SWAP. Petal 0 goes to nothing at DETACH and the faller takes its
        # place in the same frame, in the same pose, in the same spot.
        gone = 1.0 if t >= DETACH[1] else 0.0
        for i, ob in enumerate(self.petals):
            sc = swell * (0.0 if (i == 0 and gone) else 1.0)
            ob.scale = (sc, sc, sc)
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

        # --- the faller ---------------------------------------------------
        # Before DETACH it does not exist. Through DETACH it peels: still on the
        # flower, pitching down and out, the one beat of the act where something
        # comes apart. After that it is in free fall and owns the frame.
        peel = ease_in(seg(t, *DETACH))
        if t < DETACH[0]:
            self.faller.scale = (0, 0, 0)
        else:
            pos, u = self.faller_at(t)
            if t < DETACH[1]:
                # still attached, hinging away from the head
                base = self.head.matrix_world @ Vector((0.0, 0.0, 0.0))
                pos = base + Vector((0.0, 0.0, -0.006 * peel))
            self.faller.location = pos
            self.faller.scale = (swell, swell, swell)
            # The tumble is deliberately out of phase with the swing: a petal
            # that rolls in time with its own sway reads as a keyframed prop.
            uu = max(0.0, seg(t, *FALL))
            self.faller.rotation_euler = (
                math.radians(30 + 74 * peel) + 1.9 * uu + 0.55 * math.sin(uu * 5.3),
                0.42 * math.sin(uu * math.tau * 2.3),
                math.radians(30) + 1.2 * uu)

        # dead to alive, in the material rather than in a swap
        life = seg(t, CLIMB[0] + BAR, OPEN[1])
        mix = lambda a, b: tuple(a[i] + (b[i] - a[i]) * life for i in range(4))
        stem_col = mix(DEAD_STEM, LIVE_STEM)

        # THE GLITCH.
        #
        # As the stem climbs it flickers through the five accent colours the
        # film's back half is built from — a preview, buried in the first act,
        # of every style that is coming. It is not decoration: those are the
        # exact five hues the techniques use, so by the time T5 arrives in rust
        # the viewer has already seen rust run up this stem.
        #
        # It has to READ as a fault rather than as a colour cycle, so: the hold
        # is a thirty-second (0.06s) and the pick is pseudo-random rather than
        # sequential, which is what stops the eye finding a rhythm in it. And it
        # DECAYS — dense and violent at the base, thinning as the stem rises,
        # gone by the time the bud forms. The plant glitches while it is still
        # deciding what it is, and stops once it knows.
        gl = seg(t, CLIMB[0], CLIMB[0] + BAR * 3.2)
        if 0 < gl < 1:
            step = int(t / (BEAT / 8))               # a thirty-second
            r = (step * 1103515245 + 12345) % 2147483648
            density = (1.0 - gl) ** 1.6              # dies away as it climbs
            if (r / 2147483648.0) < density * 0.62:
                acc = ACCENTS[(r >> 11) % len(ACCENTS)]
                # blended, not replaced: a stem that turns fully blue is a
                # different object, one that flashes toward blue is a fault
                k = 0.55 + 0.45 * density
                stem_col = tuple(stem_col[i] + (acc[i] - stem_col[i]) * k
                                 for i in range(4))

        self.mat_stem.node_tree.nodes["Principled BSDF"].inputs["Base Color"] \
            .default_value = stem_col
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
        # THE ROOM GOES OUT, THE PETAL STAYS LIT.
        #
        # "The light only shining above the petal." Through HOLD and the fall
        # the fill and the bounce go to nothing and the key's cone closes from
        # 7 degrees to 2.2, so the plant, the jar and the table all drop out of
        # the picture and the only thing left in the frame is the petal and the
        # shaft it is falling through. Nothing is faded to black by an exposure
        # trick — the lights that were lighting the room are simply switched
        # off one at a time, so what remains is genuinely lit and everything
        # else is genuinely dark.
        alone = ease_in_out(seg(t, HOLD[0], FALL[0] + BAR * 0.5))

        # EXPOSURE COMPENSATION ON THE CLOSE.
        #
        # The camera follows the petal in to about a third of its framing
        # distance, and the beam it is falling through gets brighter the whole
        # way — so the petal would render dim at bt(31) and blazing at bt(43).
        # It is one continuous shot of one petal, and a viewer reads a colour
        # that swings that far as two different objects, which is the thing
        # this act cannot afford: the studio erupts out of THIS petal, so it
        # has to be the same vermilion at the boom as it was on the flower.
        close = ease_in_out(seg(t, DETACH[0], FALL[1]))
        self.key.data.energy = 620 * find * (1.0 - 0.42 * close)
        # 4 degrees, not 2.2. At 1.8m the cone is the diameter of the pool it
        # casts: 2.2 degrees is 7cm across and the petal is 14cm long, so the
        # tightest version lit a quarter of its own subject.
        self.key.data.spot_size = math.radians(7.0 - 3.0 * alone)
        self.bounce.data.energy = 7.5 * find * (1.0 - 0.86 * alone)
        self.fill.data.energy = 42 * find * (1.0 - alone)
        # Density 0.9 is a faint mist. A shaft you can SEE in a dark room needs
        # an order of magnitude more than that — at 0.9 the pool on the floor
        # rendered but the beam making it did not, which is most of the shot.
        # It thickens through the fall: a narrower cone at the same density is
        # a thinner shaft, and the shaft is the only thing besides the petal
        # still in the frame.
        # THINNER THROUGH THE FALL, NOT THICKER — and this cost a render to
        # learn. Narrowing the cone and thickening the haze together sounded
        # right (a tight shaft should look dense) and it put the petal inside
        # an optical depth of about 2.0: 87% of it absorbed on the sight line,
        # so the fall rendered as an empty black frame with the petal PERFECTLY
        # lit and perfectly invisible inside the fog. The geometry, the camera
        # and the key were all correct, which is what made it look like a
        # missing object rather than a lighting value.
        self.haze.inputs["Density"].default_value = (
            (7.0 + 5.0 * near) * find * (1.0 - 0.62 * alone))

        # THE FLOWER STOPS CASTING once the room has gone out. The beam comes
        # from straight above, so for the first half of the fall the petal is
        # directly under the flower it just left and falls through its OWN
        # PLANT'S SHADOW — correctly lit, in frame, and pure black. It is the
        # most convincing bug in the act, because every value you would check
        # is right. Nothing that is still casting here is visible any more, so
        # dropping them out of the shadow pass costs nothing and is what makes
        # "the light only shining on the petal" literally true.
        for ob in (*self.petals, *self.calyx, self.boss, *self.stamens,
                   *[l for l, _ in self.leaves]):
            ob.visible_shadow = (t < DETACH[0])

        # THE KEY RE-AIMS AT THE PETAL. It does not move.
        #
        # The first version slid the lamp in x and y to sit above the petal, and
        # that is why the second half of the fall rendered black. This key is
        # not a vertical downlight: it hangs off to one side and is tilted in,
        # so its forward vector is 12.3 degrees off vertical. Translating it
        # carries that tilt along, which puts the cone about 40cm wide of a
        # petal sitting inside a 2 degree half-angle — six cone-widths out.
        # Every value you would print is correct and the frame is black.
        #
        # A follow spot does not slide across the grid, it swivels. Re-aiming
        # keeps the shaft coming from where it has come from for eight bars —
        # which is the whole point of having ONE light in this room — and the
        # beam cone has to be re-aimed with it or the visible shaft and the
        # light it stands for part company.
        # AIM IT EVERY FRAME, INCLUDING BACK.
        #
        # `set_time` is a pure function of t and this was the one place it was
        # not: the key was re-aimed at the petal from DETACH onward and never
        # aimed home again, so the lamp's rotation depended on which times had
        # been evaluated BEFORE this one. A sequential render never noticed —
        # t only increases — but handoff.py evaluates the end of the act and
        # then goes back to the open flower to shoot the poppy plate, and got a
        # 96%-black frame: the beam was still pointing at the spot on the table
        # where the petal had landed thirteen beats later.
        #
        # Anything that renders out of order hits this: a re-rendered range, a
        # preview at scattered times, an extraction script. The contract is the
        # whole reason there are no keyframes in this file, so it holds here too.
        if t >= DETACH[0]:
            fp, _ = self.faller_at(t)
            aim_at(self.key, fp)
            aim_at(self.beam, fp)
        else:
            aim_at(self.key, self.key_home)
            aim_at(self.beam, self.key_home)

        # --- the camera -------------------------------------------------
        # Two moves, back to back, and the whole act is one unbroken shot.
        # First the long travel across the dark room into the pool, arriving at
        # the solved framing as the flower opens. Then it goes with the petal.
        #
        # The follow is NOT a crane tracking a target. It holds the petal a
        # little above centre and lets it fall toward the middle of the frame,
        # which is what a camera operator does and what makes the descent
        # legible: pinning the subject dead centre removes every cue that it is
        # moving at all, and three bars of a motionless petal on black is the
        # opposite of tense.
        travel = ease_in_out(seg(t, 0, HOLD[0]))
        dist = self.cam_start + (self.cam_near - self.cam_start) * travel
        ground = Vector((0.0, -dist, self.cam_z + 0.034 * travel))

        if t < DETACH[0]:
            self.cam.location = ground
            self.cam.rotation_euler = (math.radians(90), 0, 0)
        else:
            fp, u = self.faller_at(t)
            # in from the framing distance to a third of it, so the petal grows
            # through the fall and is nearly frame-filling when the paint takes
            # it — the studio needs something big to erupt out of
            cl = ease_in_out(seg(t, DETACH[0], FALL[1]))
            r = dist + (0.34 * self.cam_near - dist) * cl
            # a few degrees of drift around it, so three bars of falling has
            # some parallax in it and the background dark is not a flat card
            az = math.radians(-90.0 + 9.0 * cl)
            self.cam.location = fp + Vector((
                r * math.cos(az), r * math.sin(az), 0.035 * (1.0 - cl)))
            # lead the petal: aim a little BELOW it, so it sits high in frame
            # and falls down through the middle rather than hanging in it
            self.cam.rotation_euler = (math.radians(90), 0, 0)
            aim_at(self.cam, fp - Vector((0.0, 0.0, 0.026 * (1.0 - 0.4 * u))))
