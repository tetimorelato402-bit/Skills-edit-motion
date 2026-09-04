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
from mathutils import Vector, Matrix

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
GLITCH_FR = 0                  # RETIRED: two whole-frame substitutions in a
                               # calm piano track read as a fault in the file,
                               # not a preview; the set previews the looks now
ACT_I_END = bt(44)             # 20.465s — eleven bars
LAND_Z    = 0.012              # where the petal's origin sits once it is lying on the floor

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
# --- THE STUDIO. Eleven bars, all of them Blender. ------------------------
#
# The room was a studio the whole time. For eleven bars it is one beam in the
# dark; on bt(44), when the petal touches the table and the music slams back,
# every light comes on at once, the walls turn out to be a white cyclorama, and
# the flower that has been the only thing in the world is the SUBJECT OF A
# SHOOT. That is the drop — not paint erupting over the flower, the flower being
# produced. It stays the same object throughout, which is the one thing a cut
# to 2D could never give it.
#
# Five LOOKS, each a lighting rig + a material + a place for type + a camera:
#   EDITORIAL  rust     isolated on white, one soft key, huge type behind it
#   GRID       blue     the geometry voxelises on the beat, labels on the cells
#   COLLAGE    red      the petals tear off as paper, tape holds them in the air
#   INK        mustard  a line drawing that draws itself on
#   PAINTED    plum     impasto material, type brush-lettered ON a petal
#
# The type is THE QUESTION, reassembled: asked once in bar 1, never answered,
# its words come back one per look around and on the flower, and "alive?" lands
# on all five at once. By the end the whole question has been restated in five
# voices on one flower, and the answer is what you just watched.
REVEAL    = (bt(44), bt(48))    # lights up, cyc, the camera pulls back
# CALM. The track is a piano over a beat, and the first cut of the back half
# treated it like a drop: a strobe of five looks on the eighths, the room
# whipping a quarter-turn per cut, words the size of the frame. "Look at the
# piano, the calm. It needs to match." So: five looks, TWO BARS EACH, one
# slow unbroken turn of the room under all of them, a dip of the lights
# between looks instead of a cut, no words, and the set doing the talking.
LOOKSPAN  = (bt(48), bt(88))    # five looks, two bars each, in LOOKS order
LOOK_BEATS = 8
COLLAPSE  = (bt(84), bt(88))    # the last look's last bar: lights down, beam back
BREAK     = (bt(88), bt(92))    # the track drops out; the room is one beam again
LOOKS     = ('editorial', 'grid', 'collage', 'ink', 'painted')
WORDS     = ('how', 'do you', 'make', "ideas that aren't", 'alive,')
LAST_WORD = 'alive?'
STUDIO_GAIN = 0.36

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
# the cyc, per look — every one of them is in the warm family except the grid's,
# which is the sanctioned exception the accents already have
CYC_BONE   = (0.84, 0.76, 0.60, 1.0)
CYC_CANVAS = (0.80, 0.71, 0.54, 1.0)
CYC_GRID   = (0.62, 0.66, 0.74, 1.0)
CYC_RED    = (0.66, 0.05, 0.02, 1.0)
CYC_MUSTARD= (0.48, 0.23, 0.035, 1.0)
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


def Rz(a):
    return Matrix.Rotation(a, 3, 'Z')


# ---------------------------------------------------------------- THE ORBIT
# The studio camera goes ROUND the flower, and it goes round ON THE BEAT. Each
# hit advances it one step — fast, then settling (ease_out inside the beat) —
# so the room turns under the flower the way a turntable would if somebody
# nudged it on every kick. The step is sized by section: the statement turns
# 18° a beat, the cutting 18° a beat and then 9° an eighth, and the strobe
# jumps 72° an eighth — five looks, five angles, a full turn every two and a
# half beats. The collapse is the one continuous move, decelerating home to
# az=0, which is where Act I's camera stood and where the ending's stands.
# Everything the camera sees — the rig, the words, the tape — is placed in the
# camera's azimuth frame, so a look reads identically from every angle and the
# set is what turns.
AZ_REVEAL = 30.0   # degrees the reveal pull-back arcs, on top of the dolly



def studio_az(t):
    """Camera azimuth at time t, in radians — a pure function of the grid.
    The reveal arcs 30 degrees; then ONE slow turn over the ten bars of the
    looks, easing out of the reveal and easing home to az=0 at the break, so
    the beam that returns is on the axis Act I stood on. No kicks: the room
    turns the way a turntable does when nobody is nudging it."""
    if t < REVEAL[1]:
        return math.radians(AZ_REVEAL * ease_in_out(seg(t, *REVEAL)))
    if t < LOOKSPAN[1]:
        return math.radians(AZ_REVEAL + (360.0 - AZ_REVEAL) * ease_in_out(seg(t, *LOOKSPAN)))
    return 0.0


def pol(az_deg, r, z=0.0):
    """A point on the set: azimuth in degrees (0 = where the camera stands at
    az=0, i.e. -y), radius from the flower's axis, height."""
    return Rz(math.radians(az_deg)) @ Vector((0.0, -r, z))


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
        self._studio()     # everything it adds is OFF until bt(44)

    # -- set ----------------------------------------------------------------
    def _table(self):
        bpy.ops.mesh.primitive_plane_add(size=6, location=(0, 0, 0))
        t = bpy.context.object
        t.name = "table"
        t.data.materials.append(self.mat_table)
        self.table = t

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
        # THE STUDIO IS SHOT WIDE. Act I's 65mm is a telephoto — at 1.3-1.8m
        # its frame is 27-37cm across, and a 17cm flower plus a jar plus a
        # word plus a light stand does not fit in 30cm of picture: every look
        # rendered as things cropping each other ("everything is so compressed
        # in together"). 30mm on this sensor is a phone's 0.5x: from 0.9-1.2m
        # the frame is 40-55cm wide, the flower is a third of it, the words
        # have air, and the kit and the cyc read as a ROOM going round rather
        # than as bars sweeping the edge. The fall zooms out to it — one lens
        # change, in the dark, over seven beats, so the switch lands on a
        # frame that is already wide — and the collapse zooms back in.
        # 24mm now, cameras a further 15% out: 30mm was "still too zoomed in".
        # From 1.4m the frame is 0.76m wide and the flower is a fifth of it,
        # which is what leaves room for a set behind it.
        self.lens_wide = 24.0
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


    # -- THE STUDIO --------------------------------------------------------
    def _studio(self):
        """
        Everything the drop turns on. A cyclorama, a four-light rig, a
        material per look, a font object per word, tape, and the modifiers that
        voxelise the petals. All of it is built once and left dark, hidden or
        disabled, so Act I renders exactly as it did before any of this existed
        — the studio is not a second scene, it is the same room with the lights
        on.
        """
        # THE CYC. One mesh: floor, a quarter-round cove, a wall. Built from a
        # profile swept across x, so the cove is real geometry and the key
        # falls off across it the way it does on a stage. It replaces the
        # table while it is up — both at z=0 would z-fight, so set_time swaps
        # them.
        # ...and it goes ALL THE WAY ROUND. The camera orbits the flower, so
        # the cove is a lathe — a floor disc, a quarter-round at r=3.2, a wall
        # at r=4.2 — not a wall on one side. A cove stage, not a flat.
        prof = []
        for i in range(14):                                  # floor
            prof.append((0.03 + 3.17 * i / 13, 0.0))
        for i in range(1, 13):                               # cove
            a = math.radians(-90 + 90 * i / 12)
            prof.append((3.2 + 1.0 * math.cos(a), 1.0 + 1.0 * math.sin(a)))
        for i in range(1, 6):                                # wall
            prof.append((4.2, 1.0 + 3.6 * i / 5))
        verts, faces = [], []
        NS = 72
        for j, (r, z) in enumerate(prof):
            for i in range(NS):
                a = i / NS * math.tau
                verts.append((r * math.cos(a), r * math.sin(a), z))
        for j in range(len(prof) - 1):
            for i in range(NS):
                a = j * NS + i
                b = j * NS + (i + 1) % NS
                faces.append((a, b, b + NS, a + NS))
        self.mat_cyc = principled("cyc", **{"Base Color": CYC_BONE, "Roughness": 0.92,
                                            "Specular IOR Level": 0.15})
        self.cyc = mesh_from("cyc", verts, faces, self.mat_cyc)
        self.cyc.hide_render = True

        # THE RIG. A soft key, a big fill, a rim, and a wash for the wall.
        def area(name, loc, size, energy, colour, aim):
            bpy.ops.object.light_add(type='AREA', location=loc)
            L = bpy.context.object
            L.name = name
            L.data.size = size
            L.data.energy = 0.0
            L.data.color = colour
            L["studio_energy"] = energy
            aim_at(L, aim)
            return L
        H = Vector((0.0, 0.0, 0.43))
        self.skey  = area("skey",  ( 1.5, -1.7, 2.3), 1.8, 900.0, (1.0, 0.93, 0.84), H)
        self.sfill = area("sfill", (-2.1, -1.5, 1.4), 3.0, 260.0, (0.92, 0.95, 1.0), H)
        self.srim  = area("srim",  (-0.7,  1.5, 2.0), 0.9, 420.0, (1.0, 0.88, 0.72), H)
        self.swash = area("swash", ( 0.0, -0.4, 3.6), 4.5, 700.0, (1.0, 1.0, 1.0),
                          Vector((0.0, 2.2, 1.8)))
        # the rig RIDES THE CAMERA: these are its positions at az=0, and
        # _look rotates them with the orbit so each look is lit the same way
        # from every angle. The fixtures standing on the set are dressing.
        for L in (self.skey, self.sfill, self.srim, self.swash):
            L["home"] = tuple(L.location)
        # The rig must not touch the JAR: glass under four soft sources throws
        # highlights everywhere and the jar stops reading as glass. It keeps the
        # Act I rim only.
        for L in (self.skey, self.sfill, self.srim, self.swash):
            pass

        # THE LOOK MATERIALS. Flat, deliberately: the looks are about the
        # LANGUAGE, and a language reads at its clearest on a surface that is
        # not arguing with it.
        self.mat_grid  = principled("look_grid",  **{"Base Color": ACCENTS[1],
                                                     "Roughness": 1.0, "Specular IOR Level": 0.0})
        self.mat_paper = principled("look_paper", **{"Base Color": ACCENTS[2],
                                                     "Roughness": 0.96, "Specular IOR Level": 0.08})
        # Paper-white fill under the line, on purpose. A transparent petal
        # showed every overlapping outline through every other one and read as
        # a tangle; an opaque white cut-out under a black line is a drawing.
        self.mat_ink   = principled("look_ink",   **{"Base Color": (0.96, 0.95, 0.92, 1.0),
                                                     "Roughness": 1.0, "Specular IOR Level": 0.0})
        self.mat_paint = self._paint_material()
        self.mat_tape  = principled("tape", **{"Base Color": (0.93, 0.90, 0.82, 1.0),
                                                "Roughness": 0.85, "Specular IOR Level": 0.05,
                                                "Alpha": 0.86})
        self.type_mats = {}
        for name, col in (("rust", ACCENTS[0]), ("blue", ACCENTS[1]), ("red", ACCENTS[2]),
                          ("mustard", ACCENTS[3]), ("plum", ACCENTS[4]),
                          ("ink", (0.05, 0.03, 0.02, 1.0)), ("paper", (0.97, 0.95, 0.90, 1.0))):
            self.type_mats[name] = principled("type_" + name, **{
                "Base Color": col, "Roughness": 0.62, "Specular IOR Level": 0.25})

        # THE WORDS. One font object each. Sized and placed per look in
        # set_time; here they only exist.
        here = os.path.dirname(os.path.abspath(__file__))
        fdir = os.path.join(here, "..", "fonts")
        self.font_black = bpy.data.fonts.load(os.path.join(fdir, "Inter-Black.ttf"))
        self.font_bold  = bpy.data.fonts.load(os.path.join(fdir, "Inter-ExtraBold.ttf"))
        self.font_reg   = bpy.data.fonts.load(os.path.join(fdir, "Inter-Regular.ttf"))
        self.words = {}
        for w in (*WORDS, LAST_WORD):
            cu = bpy.data.curves.new("w_" + w, type='FONT')
            cu.body = w
            cu.font = self.font_black
            cu.align_x = 'CENTER'
            cu.align_y = 'CENTER'     # or it grows up from its origin and sits a cap height too high
            cu.extrude = 0.0
            cu.resolution_u = 6
            ob = bpy.data.objects.new("w_" + w, cu)
            bpy.context.scene.collection.objects.link(ob)
            ob.scale = (0, 0, 0)
            ob.data.materials.append(self.type_mats["rust"])
            self.words[w] = ob
        self.words_big = {}
        for w in ('alive,',):
            cu = bpy.data.curves.new("wb_" + w, type='FONT')
            cu.body = w; cu.font = self.font_black
            cu.align_x = 'CENTER'; cu.align_y = 'CENTER'; cu.resolution_u = 6
            ob = bpy.data.objects.new("wb_" + w, cu)
            bpy.context.scene.collection.objects.link(ob)
            ob.scale = (0, 0, 0)
            ob.data.materials.append(self.type_mats["plum"])
            self.words_big[w] = ob

        # TAPE. Eight strips for the collage, hidden until then.
        self.tape = []
        for i in range(8):
            bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 0, -5))
            tp = bpy.context.object
            tp.name = f"tape{i}"
            tp.scale = (0.024, 0.007, 1)
            tp.data.materials.append(self.mat_tape)
            tp.hide_render = True
            self.tape.append(tp)

        # VOXELS. Solidify (a sheet has no volume to remesh) then Remesh in
        # BLOCKS mode, on every petal including the fallen one. Off by default.
        self.voxel_mods = []
        for ob in (*self.petals, self.faller):
            so = ob.modifiers.new("solid", 'SOLIDIFY')
            so.thickness = 0.006
            so.show_render = so.show_viewport = False
            rm = ob.modifiers.new("voxel", 'REMESH')
            rm.mode = 'BLOCKS'
            rm.octree_depth = 5
            rm.use_remove_disconnected = False
            rm.show_render = rm.show_viewport = False
            self.voxel_mods.append((so, rm))

        # INK. Freestyle draws the line; the petals go almost transparent
        # under it. Set up once, switched per frame.
        sc = bpy.context.scene
        sc.render.use_freestyle = False
        sc.render.line_thickness = 2.6
        fs = bpy.context.view_layer.freestyle_settings
        fs.use_culling = True
        for ls in list(fs.linesets):
            fs.linesets.remove(ls)
        ls = fs.linesets.new("ink")
        ls.select_silhouette = True
        ls.select_border = True
        ls.select_crease = True
        ls.select_by_visibility = True
        ls.linestyle.color = (0.05, 0.03, 0.02)
        ls.linestyle.thickness = 2.6
        fs.crease_angle = math.radians(118)
        # the line set only ever draws the plant, never the cyc or the jar
        inkc = bpy.data.collections.new("ink_only")
        sc.collection.children.link(inkc)
        for ob in (self.stem, *[l for l, _ in self.leaves], *self.petals,
                   self.faller, self.boss, *self.stamens):
            inkc.objects.link(ob)
        ls.select_by_collection = True
        ls.collection = inkc

        # where the fallen petal lies at the end of the fall — it stays there
        self.petal_home = self.petals[1].location.copy()
        self.landed, _ = self.faller_at(FALL[1])
        self.landed = Vector((self.landed.x, self.landed.y, LAND_Z))

        self._dressing()
        self._setpieces()

    # -- THE SET -------------------------------------------------------------
    def _dressing(self):
        """
        What a camera going all the way round a studio sees: the kit. Stands,
        a softbox, a fresnel on a boom over the flower (the Act I beam had to
        come from SOMETHING), a C-stand with a flag, a reflector, a roll of
        paper, apple boxes with a slate on them, another camera on a tripod
        looking back, sandbags, cables, tape on the floor. All matte black and
        aluminium, all procedural, all hidden until the lights come on. The
        ring sits at r=1.9-3.0 so every studio camera (r<=1.75) is inside it
        and the reveal's wide (az 60, r 3.0) has nothing in front of the lens.
        """
        self.props = []
        kit  = principled("kit",  **{"Base Color": (0.020, 0.020, 0.022, 1), "Roughness": 0.55,
                                     "Specular IOR Level": 0.3})
        alu  = principled("alu",  **{"Base Color": (0.62, 0.62, 0.60, 1), "Roughness": 0.38,
                                     "Metallic": 0.9})
        wood = principled("wood", **{"Base Color": (0.42, 0.28, 0.15, 1), "Roughness": 0.78})
        white = principled("diff", **{"Base Color": (0.92, 0.92, 0.90, 1), "Roughness": 0.7,
                                      "Specular IOR Level": 0.1})
        paper = principled("roll", **{"Base Color": CYC_MUSTARD, "Roughness": 0.9,
                                      "Specular IOR Level": 0.05})
        bag  = principled("bag",  **{"Base Color": (0.05, 0.045, 0.04, 1), "Roughness": 0.95})
        tape = principled("floortape", **{"Base Color": (0.95, 0.92, 0.80, 1), "Roughness": 0.8})
        H = Vector((0.0, 0.0, 0.43))

        def keep(ob, mat):
            ob.data.materials.append(mat)
            ob.hide_render = True
            self.props.append(ob)
            return ob

        def cyl(r, p0, p1, mat, verts=16):
            d = Vector(p1) - Vector(p0)
            bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=r, depth=d.length,
                                                location=(Vector(p0) + Vector(p1)) / 2)
            ob = bpy.context.object
            ob.rotation_euler = d.to_track_quat('Z', 'Y').to_euler()
            return keep(ob, mat)

        def box(dims, loc, mat, rz=0.0, aim=None):
            bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
            ob = bpy.context.object
            ob.scale = dims
            ob.rotation_euler = (0, 0, rz)
            if aim is not None:
                aim_at(ob, aim)
            return keep(ob, mat)

        def plane(w, hgt, loc, mat, aim=None, rz=0.0, flat=False):
            bpy.ops.mesh.primitive_plane_add(size=1, location=loc)
            ob = bpy.context.object
            ob.scale = (w, hgt, 1)
            if aim is not None:
                aim_at(ob, aim)
            elif flat:
                ob.rotation_euler = (0, 0, rz)
            else:
                ob.rotation_euler = (math.radians(90), 0, rz)
            return keep(ob, mat)

        def stand(az, r, h, legs=0.55, column=alu):
            """A light stand: three splayed legs, a column, returns the top."""
            base = pol(az, r, 0.0)
            top = pol(az, r, h)
            cyl(0.011, base + Vector((0, 0, 0.30)), top, column)
            for k in range(3):
                a = math.radians(az) + k / 3 * math.tau
                foot = base + Rz(a) @ Vector((0.0, -legs * 0.6, 0.0))
                cyl(0.007, base + Vector((0, 0, legs * 0.75)), foot, kit, 8)
                if k == 0:
                    box((0.22, 0.14, 0.08), foot * 0.6 + base * 0.4 + Vector((0, 0, 0.04)),
                        bag, rz=a)
            return top

        # 1. SOFTBOX on a stand, aimed at the flower
        top = stand(110, 2.3, 1.9)
        sb = box((0.62, 0.92, 0.36), top + Vector((0, 0, 0.25)), kit, aim=H)
        # its diffusion front, a hair in front of the box on the face toward H
        bpy.context.view_layer.update()
        front = sb.matrix_world @ Vector((0, 0, -0.51))
        plane(0.58, 0.88, front, white, aim=H)

        # 2. C-STAND with a flag
        top = stand(150, 2.0, 1.5, column=kit)
        arm_end = top + (pol(150, 1.2, 1.5) - top).normalized() * 0.8
        cyl(0.009, top, arm_end, kit)
        plane(0.45, 0.60, arm_end + Vector((0, 0, -0.30)), kit, aim=H)

        # 3. FRESNEL on a stand, barn doors open
        top = stand(200, 2.5, 2.1)
        head = top + Vector((0, 0, 0.18))
        d = (H - head).normalized()
        cyl(0.11, head - d * 0.16, head + d * 0.16, kit, 24)
        for k in range(4):
            a = math.radians(200) + k / 4 * math.tau
            plane(0.2, 0.16, head + d * 0.24 + Rz(a) @ Vector((0, 0.13, 0)), kit, aim=H)
        box((0.06, 0.16, 0.03), top + Vector((0, 0, 0.02)), kit)

        # 4. THE BOOM over the flower, carrying the Act I lamp. The beam that
        #    lit the whole act came from this. Its head sits just above the
        #    spot's origin so it never blocks the light it is supposed to make.
        top = stand(130, 2.7, 2.6)
        lamp = Vector((0.36, -0.24, 2.02))
        cyl(0.012, top, lamp + Vector((0, 0, 0.30)), alu)
        cyl(0.075, lamp + Vector((0, 0, 0.28)), lamp + Vector((0, 0, 0.05)), kit, 24)
        box((0.26, 0.18, 0.12), top - Vector((0, 0, 0.1)), bag)     # counterweight

        # 5. TRIPOD with a camera on it, looking back at the flower
        top = stand(235, 2.7, 1.15, legs=0.7)
        body = top + Vector((0, 0, 0.08))
        box((0.15, 0.10, 0.11), body, kit, aim=H)
        d = (H - body).normalized()
        cyl(0.034, body + d * 0.07, body + d * 0.20, kit, 20)
        box((0.16, 0.05, 0.03), body + Vector((0, 0, 0.09)), kit, aim=H)   # top handle

        # 6. APPLE BOXES, a slate leaning on them, a grey card
        b0 = pol(262, 1.9, 0.10)
        box((0.50, 0.30, 0.20), b0, wood, rz=math.radians(262 + 20))
        box((0.50, 0.30, 0.20), b0 + Vector((0, 0, 0.20)), wood, rz=math.radians(262 + 8))
        sl = pol(262, 1.62, 0.13)
        slate = box((0.28, 0.22, 0.012), sl, kit, aim=H + Vector((0, 0, 1.6)))
        bpy.context.view_layer.update()
        stripe = plane(0.26, 0.035, slate.matrix_world @ Vector((0, 0.085, -0.007)), white,
                       aim=H + Vector((0, 0, 1.6)))
        cu = bpy.data.curves.new("slate_text", type='FONT')
        cu.body = "SC 1  TK 5\nROLL A"
        cu.font = self.font_bold
        cu.align_x = 'CENTER'; cu.align_y = 'CENTER'
        tx = bpy.data.objects.new("slate_text", cu)
        bpy.context.scene.collection.objects.link(tx)
        tx.scale = (0.030, 0.030, 0.030)
        tx.location = slate.matrix_world @ Vector((0, -0.02, -0.008))
        tx.rotation_euler = slate.rotation_euler
        keep(tx, self.type_mats['paper'])
        plane(0.15, 0.10, pol(268, 1.70, 0.05), principled("grey", **{"Base Color": (0.18, 0.18, 0.18, 1),
              "Roughness": 0.9}), aim=H + Vector((0, 0, 1.2)))

        # 7. REFLECTOR disc on a stand
        top = stand(300, 2.2, 1.3)
        c = top + Vector((0, 0, 0.45))
        d = (H - c).normalized()
        cyl(0.46, c - d * 0.006, c + d * 0.006, white, 48)
        cyl(0.47, c - d * 0.012, c + d * 0.0, kit, 48)

        # 8. A ROLL OF PAPER on a crossbar between two stands
        for side in (-1, 1):
            stand(340 + side * 17, 2.95, 2.3)
        bar0 = pol(340 - 17, 2.95, 2.3); bar1 = pol(340 + 17, 2.95, 2.3)
        cyl(0.012, bar0, bar1, alu)
        cyl(0.075, bar0 * 0.9 + bar1 * 0.1, bar0 * 0.1 + bar1 * 0.9, paper, 24)
        # a metre of it hangs, curling out at the floor
        hang = plane(1.30, 2.05, pol(340, 2.93, 1.15), paper, rz=math.radians(340))

        # 9. STOOL and a sandbag
        s0 = pol(20, 2.4, 0.0)
        cyl(0.17, s0 + Vector((0, 0, 0.58)), s0 + Vector((0, 0, 0.61)), wood, 24)
        for k in range(3):
            a = k / 3 * math.tau
            cyl(0.008, s0 + Vector((0, 0, 0.58)), s0 + Rz(a) @ Vector((0, 0.14, 0)), kit, 8)
        box((0.32, 0.20, 0.10), pol(28, 2.55, 0.05), bag, rz=math.radians(28))

        # 10. CABLES across the floor, from the stands out to the cove
        for k, (az, r) in enumerate(((110, 2.3), (200, 2.5), (130, 2.7), (300, 2.2), (340, 2.95))):
            cu = bpy.data.curves.new(f"cable{k}", type='CURVE')
            cu.dimensions = '3D'
            cu.bevel_depth = 0.007
            cu.bevel_resolution = 3
            sp = cu.splines.new('BEZIER')
            pts = [pol(az, r, 0.007), pol(az + 9 + 6 * (k % 2), r + 0.35, 0.007),
                   pol(az - 5, r + 0.6, 0.007), pol(az + 12, min(3.15, r + 0.85), 0.007)]
            sp.bezier_points.add(len(pts) - 1)
            for bp, q in zip(sp.bezier_points, pts):
                bp.co = q
                # VECTOR, not AUTO. AUTO handles solve a smooth tangent from
                # neighbouring points and can overshoot badly on a sparse,
                # non-collinear run like this one — measured: a "cable" was
                # projecting over a metre wide from 3-4m away, an order of
                # magnitude past its 7mm bevel radius. Straight segments
                # between points read as a cable lying in a practical run,
                # not a smooth prop, and never balloon.
                bp.handle_left_type = bp.handle_right_type = 'VECTOR'
            ob = bpy.data.objects.new(f"cable{k}", cu)
            bpy.context.scene.collection.objects.link(ob)
            keep(ob, kit)

        # 11. TAPE on the floor, at the feet of three stands. (Not by the jar
        # itself — REVEAL's opening pull-back starts almost on top of the
        # landed petal, close enough that even a 14cm strip read as a huge
        # soft-edged bar sweeping the frame.)
        for az, r, rot in ((110, 2.55, 20), (235, 2.95, 55), (300, 2.45, 300)):
            plane(0.14, 0.022, pol(az, r, 0.0015) + (Vector((0.045, 0, 0)) if rot == 90 else Vector()),
                  tape, flat=True, rz=math.radians(rot))

        # 12. THE LABEL CARD the ink look pins its caption to
        self.card = plane(0.17, 0.095, (0, 0, -5), white)


    def _setpieces(self):
        """
        THE SET, PER LOOK. A studio background is DESIGNED — flats on stands,
        blocks, a floor, the things the shoot is about lying around — and a
        bare cyc with a light stand in it is a location, not a set. Each look
        dresses the same room with the same kinds of piece in its own
        language: editorial gets a rust flat and an empty plinth; grid gets
        graph-paper boards, a gridded floor and its own cubes scattered
        about; collage gets torn sheets taped to the wall and scraps on the
        floor; ink gets three brush strokes the size of a person and a stack
        of paper; painted gets a canvas on an easel, impasto slabs and a
        palette. Five languages, one room — the same argument the flower
        makes, made by the furniture.

        Every piece lives in the CAMERA'S AZIMUTH FRAME, like the rig and the
        words (see _place): the set turns with the orbit so a look reads the
        same from every angle. The world-fixed kit ring behind them supplies
        the parallax that says the room is real. All of it is hidden until
        its look asks for it, and _studio_off hides all of it.
        """
        self.sets = {k: [] for k in LOOKS}
        def M(name, col, rough=0.9, spec=0.1):
            return principled("set_" + name, **{"Base Color": col, "Roughness": rough,
                                                "Specular IOR Level": spec})
        bone   = M("bone",   (0.90, 0.84, 0.70, 1))
        white  = M("white",  (0.96, 0.95, 0.91, 1))
        black  = M("black",  (0.035, 0.028, 0.024, 1), 1.0, 0.0)
        wood   = M("wood",   (0.36, 0.24, 0.13, 1), 0.7)
        rust   = M("rust",   ACCENTS[0], 0.85, 0.15)
        # the editorial flat is UMBER, not rust: the rust 'how' is 140% of the
        # frame wide and crosses in front of whatever stands there, and rust
        # on rust erased half the word (and 'alive?' in the strobe with it)
        umber  = M("umber",  (0.14, 0.09, 0.05, 1), 0.88, 0.1)
        mustard= M("mustard",ACCENTS[3], 0.9)
        card   = M("card",   (0.62, 0.55, 0.42, 1))
        ochre  = M("ochre",  (0.55, 0.32, 0.08, 1), 0.85)
        canvas = self._paint_material_in((0.86, 0.80, 0.66, 1.0), "set_canvas")

        def hashed(n, salt=0):
            return ((n * 2654435761 + salt * 40503) % 65536) / 65536.0

        def keep(look, ob, loc, rot=(0.0, 0.0, 0.0), motion=None):
            """`motion(u)` -> (dloc, drz): a slow move over the look, so the
            set is not furniture. Slow: nothing here moves faster than the
            room turns."""
            ob.hide_render = True
            self.sets[look].append((ob, Vector(loc), tuple(rot), motion))
            return ob

        def flat(look, name, w, h, loc, mat, rz=0.0, rx=0.0, motion=None):
            """A standing flat, w wide and h tall, built at true size so a
            texture in object space is in metres. Faces -y (the camera)."""
            v = [(-w/2, 0, 0), (w/2, 0, 0), (w/2, 0, h), (-w/2, 0, h)]
            ob = mesh_from("set_" + name, v, [(0, 1, 2, 3)], mat)
            ob.data.shade_flat()
            return keep(look, ob, loc, (rx, 0.0, rz), motion)

        def slab(look, name, dims, loc, mat, rot=(0, 0, 0), motion=None):
            bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, -9))
            ob = bpy.context.object
            ob.name = "set_" + name
            ob.scale = dims
            ob.data.materials.append(mat)
            return keep(look, ob, loc, tuple(math.radians(a) for a in rot), motion)

        def disc(look, name, r, loc, mat, rot=(0, 0, 0), standing=True, motion=None, n=40):
            pts = [(r * math.cos(a), r * math.sin(a)) for a in [i / n * math.tau for i in range(n)]]
            if standing:
                verts = [(x, 0.0, y) for x, y in pts] + [(0, 0, 0)]
            else:
                verts = [(x, y, 0.0) for x, y in pts] + [(0, 0, 0)]
            ob = mesh_from("set_" + name, verts, [(i, (i + 1) % n, n) for i in range(n)], mat)
            ob.data.shade_flat()
            return keep(look, ob, loc, tuple(math.radians(a) for a in rot), motion)

        def ring(look, name, r, width, gap_deg, loc, mat, seed=0, n=64):
            """An enso: a brushed ring, its width breathing, open at one
            point, the ends thinning the way a loaded brush lifts off."""
            outer, inner = [], []
            span = math.radians(360 - gap_deg)
            for i in range(n):
                u = i / (n - 1)
                a = math.radians(-90 + gap_deg / 2) + span * u
                wv = width * (0.55 + 0.45 * math.sin(u * math.tau * 1.3 + seed))
                wv *= min(1.0, u / 0.08) ** 0.5 * min(1.0, (1 - u) / 0.12) ** 0.7 + 0.08
                outer.append((math.cos(a) * (r + wv / 2), 0.0, math.sin(a) * (r + wv / 2)))
                inner.append((math.cos(a) * (r - wv / 2), 0.0, math.sin(a) * (r - wv / 2)))
            verts = outer + inner
            faces = [(i, i + 1, n + i + 1, n + i) for i in range(n - 1)]
            ob = mesh_from("set_" + name, verts, faces, mat)
            ob.data.shade_flat()
            return keep(look, ob, loc)

        def torn(look, name, w, h, loc, mat, seed, rot=(0, 0, 0), flat_on_floor=False):
            """A sheet with a torn edge: a rectangle whose boundary wanders."""
            n = 36; pts = []
            for i in range(n):
                u = i / n
                # walk the rectangle's perimeter
                if u < 0.25:   x, y = -w/2 + w * (u / 0.25), -h/2
                elif u < 0.5:  x, y = w/2, -h/2 + h * ((u - 0.25) / 0.25)
                elif u < 0.75: x, y = w/2 - w * ((u - 0.5) / 0.25), h/2
                else:          x, y = -w/2, h/2 - h * ((u - 0.75) / 0.25)
                # a slow wander plus a little grain: 0.09 of grain per vertex
                # rendered as a saw blade, not a tear
                j = (0.028 * math.sin(u * math.tau * 2.3 + seed) + 0.018 * math.sin(u * math.tau * 5.1 + seed * 1.7)
                     + (hashed(i, seed) - 0.5) * 0.014)
                x += j * (1 if abs(x) > w/2 - 1e-6 else 0.3)
                y += j * (1 if abs(y) > h/2 - 1e-6 else 0.3)
                pts.append((x, y))
            if flat_on_floor:
                verts = [(x, y, 0.0) for x, y in pts] + [(0, 0, 0)]
            else:
                verts = [(x, 0.0, y + h/2) for x, y in pts] + [(0, 0, h/2)]
            c = len(pts)
            faces = [(i, (i + 1) % c, c) for i in range(c)]
            ob = mesh_from("set_" + name, verts, faces, mat)
            ob.data.shade_flat()
            return keep(look, ob, loc, tuple(math.radians(a) for a in rot))

        def stroke(look, name, length, width, loc, mat, rot=(0, 0, 0), seed=0):
            """A brush stroke: a lozenge that swells and thins along its
            length, with a ragged start and a dry, split end."""
            n = 22; top = []; bot = []
            for i in range(n):
                u = i / (n - 1)
                wv = width * (0.35 + 0.65 * math.sin(math.pi * min(1.0, u * 1.15)) ** 0.6)
                wv *= 1.0 + 0.14 * math.sin(u * math.tau * 1.7 + seed) + (hashed(i, seed) - 0.5) * 0.06
                if u > 0.82:
                    wv *= 1.0 - (u - 0.82) / 0.18 * 0.7
                x = -length/2 + length * u
                top.append((x, 0.0, wv/2)); bot.append((x, 0.0, -wv/2))
            verts = top + bot[::-1] + [(0, 0, 0)]
            c = len(top) * 2
            faces = [(i, (i + 1) % c, c) for i in range(c)]
            ob = mesh_from("set_" + name, verts, faces, mat)
            ob.data.shade_flat()
            return keep(look, ob, loc, tuple(math.radians(a) for a in rot))

        def cylv(look, name, r, p0, p1, mat, verts=12, motion=None):
            d = Vector(p1) - Vector(p0)
            bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=r, depth=d.length,
                                                location=(0, 0, -9))
            ob = bpy.context.object
            ob.name = "set_" + name
            ob.data.materials.append(mat)
            q = d.to_track_quat('Z', 'Y').to_euler()
            return keep(look, ob, (Vector(p0) + Vector(p1)) / 2, (q.x, q.y, q.z), motion)

        def drift(dx=0.0, dy=0.0, dz=0.0, drz=0.0):
            """Eased travel over the look, both ways symmetric about the middle."""
            return lambda u: (Vector((dx, dy, dz)) * (ease_in_out(u) - 0.5), drz * (u - 0.5))

        def rise(dz, drz=0.0):
            return lambda u: (Vector((0, 0, dz * u)), drz * u)

        # --- EDITORIAL: a rust flat, an off-white flat, an empty plinth ------
        # the umber flat crosses slowly behind the flower — the move the word
        # used to make, made by a shape — and a bone disc hangs like a moon
        flat('editorial', 'ed_umber', 1.5, 2.1, (0.85, 1.75, 0.0), umber, rz=math.radians(14),
             motion=drift(dx=-0.9))
        flat('editorial', 'ed_white', 0.95, 1.7, (-1.15, 1.55, 0.0), white, rz=math.radians(-9))
        disc('editorial', 'ed_moon', 0.42, (-0.35, 1.95, 1.25), bone, motion=rise(0.06))
        slab('editorial', 'ed_plinth', (0.55, 0.55, 0.32), (-0.68, 0.78, 0.16), bone, (0, 0, 8))
        slab('editorial', 'ed_plinth2', (0.30, 0.30, 0.62), (1.25, 0.95, 0.31), bone, (0, 0, -6))
        bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=16, radius=0.13, location=(0, 0, -9))
        sp = bpy.context.object; sp.name = "set_ed_sphere"; sp.data.materials.append(bone)
        keep('editorial', sp, (-0.68, 0.78, 0.45))
        cylv('editorial', 'ed_rod', 0.006, (1.45, 1.30, 0.0), (1.45, 1.30, 2.3), black)

        # --- GRID: graph-paper boards, a gridded floor, its cubes ------------
        gridmat = self._grid_material()
        flat('grid', 'gr_board', 1.4, 2.0, (0.95, 1.65, 0.0), gridmat)
        flat('grid', 'gr_board2', 1.1, 1.75, (-1.05, 1.8, 0.0), gridmat, rz=math.radians(-6))
        mat_v = [(-1.2, -0.9, 0.001), (1.2, -0.9, 0.001), (1.2, 1.5, 0.001), (-1.2, 1.5, 0.001)]
        floor = mesh_from("set_gr_floor", mat_v, [(0, 1, 2, 3)], gridmat)
        floor.data.shade_flat()
        keep('grid', floor, (0, 0, 0))
        cubes = ((0.45, 0.55, 0.12), (-0.62, 0.38, 0.09), (0.82, 0.18, 0.07), (-0.34, 0.92, 0.14),
                 (0.24, 1.12, 0.10), (-0.95, 0.72, 0.06), (0.62, 0.86, 0.08), (-0.18, 0.42, 0.05),
                 (0.9, 1.35, 0.55), (-0.7, 1.25, 0.85), (0.35, 1.45, 1.05))
        for i, (x, y, sz) in enumerate(cubes):
            z = sz / 2 if i < 8 else sz + 0.4 + 0.35 * hashed(i, 3)
            # snapped to the 5cm grid, because the grid is the language; the
            # floating ones rise a hand's width and turn a little over the look
            snap = lambda v: round(v / 0.05) * 0.05
            slab('grid', f'gr_cube{i}', (sz, sz, sz), (snap(x), snap(y), z), self.mat_grid,
                 motion=None if i < 8 else rise(0.10, math.radians(35)))
        for k, sz in enumerate((0.20, 0.15, 0.11, 0.08)):
            zc = sum((0.20, 0.15, 0.11, 0.08)[:k]) + sz / 2
            slab('grid', f'gr_col{k}', (sz, sz, sz), (0.95 - 0.02 * k, 0.95, zc), self.mat_grid,
                 (0, 0, 12 * k))
        for k, (x, y, sz) in enumerate(((-0.45, 1.30, 0.28), (0.15, 1.55, 0.18), (1.30, 0.55, 0.36))):
            slab('grid', f'gr_float{k}', (sz, sz, sz), (x, y, 0.9 + 0.35 * hashed(k, 9)), self.mat_grid,
                 (0, 0, 20 + 33 * k), motion=rise(0.08 + 0.04 * k, math.radians(-25)))

        # --- COLLAGE: torn sheets taped to the wall, scraps on the floor -----
        sheets = (('bone', 1.05, 0.80, (0.55, 1.62, 0.55), bone, 3, (0, 0, 7)),
                  ('white', 0.70, 0.95, (-0.85, 1.70, 0.35), white, 5, (0, 0, -11)),
                  ('mustard', 0.60, 0.45, (1.15, 1.55, 1.45), mustard, 7, (0, 0, -4)),
                  ('black', 0.45, 0.62, (-0.25, 1.75, 1.35), black, 9, (0, 0, 14)),
                  ('card', 0.55, 0.40, (0.05, 1.58, 0.95), card, 11, (0, 0, 3)))
        self.set_tape = []
        for name, w, h, loc, mat, seed, rot in sheets:
            torn('collage', 'co_' + name, w, h, loc, mat, seed, rot)
            for k in range(2):
                tp = slab('collage', f'co_tape_{name}{k}', (0.09, 0.022, 0.002),
                          (loc[0] + (-w/2 if k == 0 else w/2) * 0.8 + 0.02,
                           loc[1] - 0.006, loc[2] + h * (0.92 if k == 0 else 0.15)),
                          self.mat_tape, (90, 0, 35 + 40 * k + rot[2]))
        for i, (x, y, sz) in enumerate(((0.62, 0.42, 0.22), (-0.55, 0.30, 0.17), (0.20, 0.95, 0.26),
                                        (-0.9, 0.85, 0.19), (1.05, 0.30, 0.15), (-0.25, 1.25, 0.21))):
            torn('collage', f'co_scrap{i}', sz, sz * 0.7, (x, y, 0.002),
                 (bone, white, mustard, card, black, bone)[i], 20 + i, (0, 0, 30 + 55 * i), flat_on_floor=True)
        # cut circles and strips over the sheets — paper on paper on paper
        disc('collage', 'co_sun', 0.30, (0.95, 1.50, 1.75), mustard, motion=drift(dz=0.05))
        disc('collage', 'co_dot', 0.13, (-0.50, 1.60, 1.05), black)
        disc('collage', 'co_dot2', 0.19, (0.25, 1.52, 0.55), white)
        torn('collage', 'co_strip', 1.35, 0.11, (0.10, 1.66, 1.20), black, 31, (0, 0, -18),
             )
        torn('collage', 'co_strip2', 0.95, 0.09, (-0.70, 1.62, 1.55), card, 33, (0, 0, 9))

        # --- INK: three strokes the size of a person, paper, a pot ----------
        stroke('ink', 'in_s1', 1.9, 0.22, (0.15, 1.72, 1.35), black, (0, 0, 4), 1)
        stroke('ink', 'in_s2', 1.35, 0.22, (-0.95, 1.66, 0.85), black, (0, 0, 78), 2)
        stroke('ink', 'in_s3', 1.5, 0.26, (0.85, 1.60, 0.62), black, (0, 0, -26), 3)
        stroke('ink', 'in_s4', 0.7, 0.10, (-0.35, 1.70, 1.85), black, (0, 0, 9), 4)
        # THE ENSO: one brushed circle behind the flower, the whole look's
        # composition in a single mark; the flower sits inside it
        ring('ink', 'in_enso', 0.58, 0.11, 28.0, (0.08, 1.50, 0.72), black, seed=2)
        stroke('ink', 'in_s5', 0.9, 0.07, (0.95, 0.85, 0.001), black, (90, 0, 40), 5)   # on the floor
        for k in range(14):
            rr = 0.008 + 0.028 * hashed(k, 41) ** 2
            if k < 8:
                disc('ink', f'in_spl{k}', rr, (-1.2 + 2.4 * hashed(k, 42), 1.45 + 0.3 * hashed(k, 43),
                                              0.15 + 1.6 * hashed(k, 44)), black)
            else:
                disc('ink', f'in_spl{k}', rr, (-0.9 + 1.8 * hashed(k, 45), 0.2 + 1.1 * hashed(k, 46), 0.0015),
                     black, standing=False)
        for k in range(4):
            slab('ink', f'in_paper{k}', (0.30, 0.42, 0.002),
                 (-0.58 + 0.012 * k, 0.36 - 0.01 * k, 0.002 + 0.0025 * k), white, (0, 0, -12 + 9 * k))
        cylv('ink', 'in_pot', 0.034, (0.55, 0.52, 0.0), (0.55, 0.52, 0.055), black, 16)
        cylv('ink', 'in_brush', 0.005, (0.56, 0.53, 0.05), (0.46, 0.66, 0.28), wood, 8)

        # --- PAINTED: a canvas on an easel, impasto slabs, a palette --------
        # the easel stands left of the flower and BEHIND it, inside the 24mm
        # frame (at y=1.4 the frame spans x -0.43..0.91): at x=-1.0 only its
        # right edge was in shot
        for k, (x0, y0) in enumerate(((-0.72, 1.60), (-0.32, 1.48))):
            cylv('painted', f'pa_leg{k}', 0.014, (x0, y0, 0.0), (x0 * 0.94 + 0.03, y0 + 0.02, 1.85), wood)
        cylv('painted', 'pa_leg2', 0.014, (-0.52, 1.92, 0.0), (-0.49, 1.58, 1.85), wood)
        cylv('painted', 'pa_bar', 0.012, (-0.86, 1.50, 0.62), (-0.18, 1.36, 0.62), wood)
        flat('painted', 'pa_canvas', 0.82, 1.08, (-0.52, 1.40, 0.64), canvas, rz=math.radians(11))
        slab('painted', 'pa_stroke0', (0.42, 0.012, 0.11), (-0.60, 1.385, 1.15), self.mat_paint, (0, 0, 11 + 8))
        slab('painted', 'pa_stroke1', (0.34, 0.012, 0.09), (-0.42, 1.380, 0.98), ochre, (0, 0, 11 - 14))
        slab('painted', 'pa_stroke2', (0.26, 0.012, 0.13), (-0.65, 1.380, 0.88), self.mat_paint, (0, 0, 11 + 38))
        slab('painted', 'pa_wall0', (0.95, 0.03, 0.22), (0.95, 1.72, 1.32), self.mat_paint, (0, 0, -7))
        slab('painted', 'pa_wall1', (0.70, 0.03, 0.17), (1.15, 1.70, 0.95), ochre, (0, 0, 12))
        slab('painted', 'pa_wall2', (0.55, 0.03, 0.28), (0.55, 1.74, 1.68), rust, (0, 0, -22))
        flat('painted', 'pa_canvas2', 0.95, 0.70, (0.95, 1.55, 0.0), canvas, rz=math.radians(-16), rx=math.radians(-8))
        slab('painted', 'pa_c2s0', (0.45, 0.012, 0.16), (0.88, 1.52, 0.38), self.mat_paint, (0, -8, -16 + 6))
        slab('painted', 'pa_c2s1', (0.30, 0.012, 0.10), (1.05, 1.51, 0.22), rust, (0, -8, -16 - 20))
        for k in range(4):
            cylv('painted', f'pa_tube{k}', 0.014, (0.30 + 0.09 * k, 0.62 + 0.05 * (k % 2), 0.014),
                 (0.30 + 0.09 * k + 0.10 * math.cos(0.6 * k), 0.62 + 0.05 * (k % 2) + 0.10 * math.sin(0.6 * k), 0.014),
                 (self.mat_paint, ochre, rust, bone)[k], 10)
        cylv('painted', 'pa_jar', 0.045, (-0.62, 0.55, 0.0), (-0.62, 0.55, 0.11), white, 16)
        for k in range(3):
            a = 0.5 + 1.1 * k
            cylv('painted', f'pa_brush{k}', 0.005, (-0.62 + 0.02 * math.cos(a), 0.55 + 0.02 * math.sin(a), 0.06),
                 (-0.62 + 0.09 * math.cos(a), 0.55 + 0.09 * math.sin(a), 0.36), wood, 8)
        pal = mesh_from("set_pa_palette",
                        [(0.20 * math.cos(a) * (1.0 + 0.18 * math.cos(2 * a + 0.8)),
                          0.14 * math.sin(a) * (1.0 + 0.18 * math.sin(3 * a)), 0.004) for a in
                         [i / 28 * math.tau for i in range(28)]] + [(0, 0, 0.004)],
                        [(i, (i + 1) % 28, 28) for i in range(28)], wood)
        pal.data.shade_flat()
        keep('painted', pal, (0.62, 0.40, 0.0), (0, 0, math.radians(25)))
        for i, m in enumerate((self.mat_paint, ochre, rust, mustard, bone)):
            bpy.ops.mesh.primitive_uv_sphere_add(segments=12, ring_count=8, radius=0.018,
                                                 location=(0, 0, -9))
            d = bpy.context.object; d.name = f"set_pa_dab{i}"
            d.data.materials.append(m); d.scale = (1, 1, 0.45)
            keep('painted', d, (0.62 + 0.11 * math.cos(i * 1.25), 0.40 + 0.075 * math.sin(i * 1.25), 0.012))

    def _paint_material_in(self, col, name):
        """The impasto material in another colour (a canvas, a wall slab)."""
        mat = self._paint_material()
        mat.name = name
        mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = col
        return mat

    def _grid_material(self):
        """Graph paper: the board's colour with lighter lines every 5cm, in
        object space (metres, because the flats are built at true size)."""
        mat = bpy.data.materials.new("set_grid")
        mat.use_nodes = True
        nt = mat.node_tree
        b = nt.nodes["Principled BSDF"]
        b.inputs["Roughness"].default_value = 0.95
        b.inputs["Specular IOR Level"].default_value = 0.05
        br = nt.nodes.new("ShaderNodeTexBrick")
        br.offset = 0.0
        br.inputs["Scale"].default_value = 1.0
        br.inputs["Mortar Size"].default_value = 0.004
        br.inputs["Mortar Smooth"].default_value = 0.0
        br.inputs["Brick Width"].default_value = 0.05
        br.inputs["Row Height"].default_value = 0.05
        panel = (0.55, 0.60, 0.68, 1.0)
        br.inputs["Color1"].default_value = panel
        br.inputs["Color2"].default_value = panel
        br.inputs["Mortar"].default_value = (0.82, 0.85, 0.90, 1.0)
        tc = nt.nodes.new("ShaderNodeTexCoord")
        # x and z of the standing flat, x and y of the floor: swizzle so the
        # grid is square on both — (x, z) for a flat is (x, y) after this map
        sep = nt.nodes.new("ShaderNodeSeparateXYZ")
        add = nt.nodes.new("ShaderNodeVectorMath"); add.operation = 'ADD'
        comb = nt.nodes.new("ShaderNodeCombineXYZ")
        nt.links.new(tc.outputs["Object"], sep.inputs["Vector"])
        m2 = nt.nodes.new("ShaderNodeMath"); m2.operation = 'ADD'
        nt.links.new(sep.outputs["Y"], m2.inputs[0]); nt.links.new(sep.outputs["Z"], m2.inputs[1])
        nt.links.new(sep.outputs["X"], comb.inputs["X"]); nt.links.new(m2.outputs[0], comb.inputs["Y"])
        nt.links.new(comb.outputs["Vector"], br.inputs["Vector"])
        nt.links.new(br.outputs["Color"], b.inputs["Base Color"])
        return mat

    def _paint_material(self):
        """
        Impasto. Plum, with the brush plate driving both bump and roughness so
        the strokes catch a raking key. The plate carries only value (see
        scripts/brushplate.py) which is exactly why it can be pushed this hard
        without shifting the hue.
        """
        mat = bpy.data.materials.new("look_paint")
        mat.use_nodes = True
        nt = mat.node_tree
        b = nt.nodes["Principled BSDF"]
        b.inputs["Base Color"].default_value = ACCENTS[4]
        b.inputs["Specular IOR Level"].default_value = 0.28
        here = os.path.dirname(os.path.abspath(__file__))
        img = bpy.data.images.load(os.path.join(here, "..", "tex", "brush.png"))
        tex = nt.nodes.new("ShaderNodeTexImage"); tex.image = img
        tc = nt.nodes.new("ShaderNodeTexCoord")
        mp = nt.nodes.new("ShaderNodeMapping")
        mp.inputs["Scale"].default_value = (2.2, 2.2, 2.2)
        nt.links.new(tc.outputs["Generated"], mp.inputs["Vector"])
        nt.links.new(mp.outputs["Vector"], tex.inputs["Vector"])
        bump = nt.nodes.new("ShaderNodeBump")
        bump.inputs["Strength"].default_value = 0.85
        bump.inputs["Distance"].default_value = 0.02
        nt.links.new(tex.outputs["Color"], bump.inputs["Height"])
        nt.links.new(bump.outputs["Normal"], b.inputs["Normal"])
        rg = nt.nodes.new("ShaderNodeMapRange")
        rg.inputs["To Min"].default_value = 0.22
        rg.inputs["To Max"].default_value = 0.70
        nt.links.new(tex.outputs["Color"], rg.inputs["Value"])
        nt.links.new(rg.outputs["Result"], b.inputs["Roughness"])
        return mat

    def _studio_off(self):
        """Put the studio away. Called by the act-one and ending branches so
        their frames cannot inherit any of it — set_time stays pure."""
        self.cyc.hide_render = True
        self.table.hide_render = False
        for L in (self.skey, self.sfill, self.srim, self.swash):
            L.data.energy = 0.0
        for w in self.words.values():
            w.scale = (0, 0, 0)
        for tp in self.tape:
            tp.hide_render = True
        for so, rm in self.voxel_mods:
            so.show_render = rm.show_render = False
        bpy.context.scene.render.use_freestyle = False
        self.mat_cyc.node_tree.nodes["Principled BSDF"].inputs["Base Color"] \
            .default_value = CYC_BONE
        for ob in (*self.petals, self.faller):
            ob.data.materials[0] = self.mat_petal
        for ob in self.props:
            ob.hide_render = True
        for pieces in self.sets.values():
            for ob, _, _, _ in pieces:
                ob.hide_render = True
        self.cam.data.lens = self.lens

    def _place(self, w, local, az, rot=(90.0, 0.0, 0.0)):
        """Put a word at `local` in the camera's azimuth frame (az=0 is the
        frame every look was designed in: camera at -y), standing and facing
        the camera unless `rot` says otherwise."""
        w.location = Rz(az) @ Vector(local)
        w.rotation_euler = (math.radians(rot[0]), math.radians(rot[1]),
                            math.radians(rot[2]) + az)

    def _pose_open(self):
        """The flower fully open, one petal on the table: the studio's subject."""
        self.stem.data.bevel_factor_end = 1.0
        for ob, _ in self.leaves:
            ob.scale = (1, 1, 1)
        self.head.rotation_euler = (math.radians(-20), 0, 0)
        for ob in self.calyx:
            ob.scale = (0, 0, 0)
        for st in self.stamens:
            st.scale = (1, 1, 1)
        self.boss.scale = (1, 1, 0.62)
        # LOCATION TOO. The collage look pushes every petal off the head, and
        # a pose that resets rotation but not location leaves them hanging in
        # the air through ink, painted, the strobe and the break — every look
        # after collage rendered with the flower torn apart. Same class of bug
        # as the key aim: state that one branch writes and no branch clears.
        for i, ob in enumerate(self.petals):
            ob.scale = (0, 0, 0) if i == 0 else (1, 1, 1)
            ob.location = self.petal_home
            ob.rotation_euler = (math.radians(24), 0, i / len(self.petals) * math.tau)
        self.faller.scale = (1, 1, 1)
        self.faller.location = self.landed
        # exactly the pose the fall lands in, so the switch does not move it
        self.faller.rotation_euler = self.faller_rot(FALL[1])
        self.mat_stem.node_tree.nodes["Principled BSDF"].inputs["Base Color"] \
            .default_value = LIVE_STEM
        self.mat_leaf.node_tree.nodes["Principled BSDF"].inputs["Base Color"] \
            .default_value = LIVE_LEAF
        for ob in (*self.petals, self.faller, *self.calyx, self.boss, *self.stamens,
                   *[l for l, _ in self.leaves]):
            ob.visible_shadow = True

    def _look(self, name, u, t, strength=1.0, camera=True, az=0.0):
        """
        Dress the room for one look at progress u (0..1 through its
        appearance). `strength` scales the rig, for the collapse.
        Every look sets EVERYTHING it cares about, so cutting between them is
        a pure function of t and nothing leaks from the previous frame.
        """
        H = Vector((0.0, 0.0, 0.43))
        cyc = self.mat_cyc.node_tree.nodes["Principled BSDF"].inputs["Base Color"]
        rig = {L: 0.0 for L in (self.skey, self.sfill, self.srim, self.swash)}
        # NO WORDS in the back half any more — the question is asked once,
        # in bar 1, and the set carries the languages
        for w in (*self.words.values(), *self.words_big.values()):
            w.scale = (0, 0, 0)
        for tp in self.tape:
            tp.hide_render = True
        for so, rm in self.voxel_mods:
            so.show_render = rm.show_render = False
        bpy.context.scene.render.use_freestyle = False
        self.card.hide_render = True
        petal_mat = self.mat_petal
        R = Rz(az)
        # THE SET for this look, in the camera's frame; every other look's away
        for lk, pieces in self.sets.items():
            for ob, loc, rot, motion in pieces:
                ob.hide_render = (lk != name)
                if lk == name:
                    dloc, drz = motion(u) if motion else (Vector(), 0.0)
                    ob.location = R @ (loc + dloc)
                    ob.rotation_euler = (rot[0], rot[1], rot[2] + drz + az)
        # a hashed jitter, never random(): the handheld and the tape must
        # rebuild identically on a resumed chunk
        def h(n, salt=0):
            return ((int(t * 240) * 2654435761 + n * 40503 + salt * 7919) % 65536) / 65536.0

        if name == 'editorial':
            cyc.default_value = CYC_BONE
            rig[self.skey], rig[self.sfill], rig[self.swash] = 900, 260, 700
            rig[self.srim] = 160
            if camera:
                self.cam.location = R @ Vector((0.32 - 0.55 * u, -1.38, 0.53))
                aim_at(self.cam, H + Vector((0, 0, 0.05)))

        elif name == 'grid':
            cyc.default_value = CYC_GRID
            rig[self.skey], rig[self.sfill], rig[self.swash] = 520, 520, 900
            petal_mat = self.mat_grid
            # THE GEOMETRY QUANTISES, ON THE BEAT. Depth 3 is a fist of cubes,
            # depth 6 is nearly the petal again; it steps through them on the
            # sixteenths so the flower is never smoothly "becoming" blocks —
            # it snaps between resolutions, which is the whole language.
            # ONE step, on the downbeat of its second bar, not eight on the
            # sixteenths: a block sculpture that resolves once is calm, one
            # that flickers between resolutions is a strobe.
            depth = 4 if u < 0.5 else 5
            for so, rm in self.voxel_mods:
                so.show_render = rm.show_render = True
                rm.octree_depth = depth
            if camera:
                # a little higher and aimed a little lower than the other
                # looks, so the floor in front of the jar — where the label
                # lies — is inside the frame instead of under it
                self.cam.location = R @ Vector((0.0, -1.04, 0.85))
                aim_at(self.cam, H - Vector((0, 0, 0.23)))

        elif name == 'collage':
            cyc.default_value = CYC_RED
            rig[self.skey], rig[self.srim] = 1400, 500     # one hard source
            self.skey.data.size = 0.35
            petal_mat = self.mat_paper
            # THE PETALS TEAR OFF. Each one leaves the head and hangs in the
            # air at its own crooked angle, a strip of tape across it — the
            # flower as five pieces of red paper that used to be a flower.
            for i, ob in enumerate(self.petals):
                if i == 0:
                    continue
                k = ease_out(seg(u, 0.0 + i * 0.06, 0.45 + i * 0.06))
                a = i / len(self.petals) * math.tau
                ob.rotation_euler = (math.radians(24 + 56 * k),
                                     math.radians((h(i) - 0.5) * 40 * k), a)
                ob.location = (0.0 + math.cos(a) * 0.19 * k,
                               0.0 + math.sin(a) * 0.19 * k,
                               0.43 + (0.05 + 0.16 * h(i, 1)) * k)
            for j, tp in enumerate(self.tape):
                i = 1 + (j % 5)
                pet = self.petals[i]
                tp.hide_render = False
                tp.location = pet.matrix_world @ Vector((0.0, 0.05 + 0.03 * (j // 5), 0.004))
                tp.rotation_euler = (pet.rotation_euler.x, pet.rotation_euler.y,
                                     pet.rotation_euler.z + math.radians(72 + 30 * h(j, 2)))
            # a slow lateral drift, not a handheld jitter: the per-frame
            # hash read as nerves against a piano
            if camera:
                self.cam.location = R @ Vector((0.17 - 0.10 * math.sin(u * math.pi), -0.92, 0.45))
                aim_at(self.cam, H + Vector((0, 0, 0.02)))

        elif name == 'ink':
            cyc.default_value = CYC_MUSTARD
            rig[self.sfill], rig[self.swash] = 700, 900   # flat, shadowless
            petal_mat = self.mat_ink
            bpy.context.scene.render.use_freestyle = True
            if camera:
                self.cam.location = R @ Vector((0.0, -1.24, 0.41))
                aim_at(self.cam, H)

        elif name == 'painted':
            cyc.default_value = CYC_CANVAS
            rig[self.skey], rig[self.sfill] = 650, 140      # raking, to catch impasto
            self.skey.data.size = 0.7
            self.skey.location = R @ Vector((1.9, -0.4, 0.9))
            aim_at(self.skey, H)
            petal_mat = self.mat_paint
            pu = ease_in_out(u)
            if camera:
                # It pushes in AND rises: from level with the flower to
                # looking down into the bowl. Level, the lens sees the petals'
                # undersides at a grazing angle and anything written on them
                # foreshortens to a sliver — the word was on the petal in
                # every earlier render and legible in none of them.
                # ABOVE H, always: the big word is placed on the ray from the
                # camera through H down to z=0.22, and a camera level with H
                # sends that ray sideways and the word to infinity. Same
                # look-down angles as the 65mm version (7.5 -> 26 degrees).
                self.cam.location = R @ Vector((0.24 - 0.09 * pu, -1.04 + 0.39 * pu, 0.57 + 0.17 * pu))
            if camera:
                aim_at(self.cam, H)

        for ob in (*self.petals, self.faller):
            ob.data.materials[0] = petal_mat
        # STUDIO_GAIN. The film's exposure is set for one 620W spot in a black
        # room. Four soft sources at 500-900W plus a cyc bouncing all of it
        # back put every look about a stop and a half over: plum rendered as
        # dusty pink, signal blue as powder, the mustard field as peach. The
        # rig values above are the RATIOS between the lamps, which are right;
        # this is the one number that sets how bright the room is.
        for L, e in rig.items():
            L.data.energy = e * strength * STUDIO_GAIN
        if name != 'collage':
            self.skey.data.size = 1.8
        if name != 'painted':
            self.skey.location = R @ Vector(self.skey["home"])
            aim_at(self.skey, H)
        # the rest of the rig rides the camera too
        for L in (self.sfill, self.srim):
            L.location = R @ Vector(L["home"])
            aim_at(L, H)
        self.swash.location = R @ Vector(self.swash["home"])
        aim_at(self.swash, R @ Vector((0.0, 2.2, 1.8)))

    def _set_time_studio(self, t):
        # THE ROOM WITH THE LIGHTS ON, AND IT TURNS. The camera orbits the
        # flower on the beat (see studio_az) — the set is what turns, not the
        # subject, so the flower stays framed and lit the same way at every
        # angle. az is one number, computed once, that every look, every
        # word and every rig position for this frame is built from.
        self.beam.hide_render = True
        self.haze.inputs["Density"].default_value = 0.0
        self.key.data.energy = 0.0
        self.bounce.data.energy = 0.0
        self.fill.data.energy = 0.0
        self.table.hide_render = True
        self.cyc.hide_render = False
        self._pose_open()
        self.cam.data.lens = self.lens_wide
        H = Vector((0.0, 0.0, 0.43))
        az = studio_az(t)
        R = Rz(az)

        if t < REVEAL[1]:
            # THE DROP. The lights are a SWITCH — on inside a sixteenth — and
            # the camera takes its time, pulling back from the fallen petal
            # to a wide of the whole flower on the cyc, arcing a little as it
            # goes so the turn is already felt before the first cut. The
            # viewer learns in one frame that the room was a stage, and then
            # gets a bar to see it. THE KIT STAYS HIDDEN through this pull —
            # it starts almost on top of the landed petal, close enough that
            # a stand at the edge of the room reads as a huge soft-edged bar
            # sweeping the frame, not a light stand in the background. It
            # appears once the wide is actually established.
            # THE KIT IS THERE FROM THE FIRST LIT FRAME now that the lens is
            # wide: at 30mm from 0.6m a stand at r=1.9 is a stand, not a bar.
            for ob in self.props:
                ob.hide_render = False
            on = ease_out(seg(t, REVEAL[0], REVEAL[0] + BEAT / 4))
            self._look('editorial', 0.0, t, strength=on, az=az)
            pull = ease_in_out(seg(t, REVEAL[0], REVEAL[1]))
            # FROM EXACTLY WHERE THE FALL LEFT IT. The first lit frame is the
            # last dark frame with the lights on — same camera, same lens,
            # same petal in the same place — and only then does it lift and
            # pull back to find the flower standing in a studio.
            start, aim0, _ = self._fall_camera(FALL[1])
            end = R @ Vector((0.32, -1.38, 0.53))
            self.cam.location = start + (end - start) * pull
            aim_at(self.cam, aim0 + (H + Vector((0, 0, 0.05)) - aim0) * pull)
            self.words['how'].scale = (0, 0, 0)
            return

        for ob in self.props:
            ob.hide_render = False

        if t < LOOKSPAN[1]:
            # FIVE LOOKS, TWO BARS EACH, and the change between them is a DIP
            # of the lights — down over the last eighth of one look, up over
            # the first eighth of the next — rather than a cut. The set swaps
            # in the dip. The orbit never stops, so a look change reads as the
            # stage being re-lit while the room keeps turning, which is a
            # calmer event than a cut and belongs to the piano.
            span = LOOK_BEATS * BEAT
            i = min(4, int((t - LOOKSPAN[0]) / span))
            a = LOOKSPAN[0] + i * span
            u = seg(t, a, a + span)
            tt = t - a
            DIP = 0.30                                       # not to black
            up = 1.0 if i == 0 else DIP + (1.0 - DIP) * ease_out(seg(tt, 0.0, BEAT / 2))
            down = 1.0 if i == 4 else 1.0 - (1.0 - DIP) * ease_in(seg(tt, span - BEAT / 2, span))
            strength = up * down
            if t >= COLLAPSE[0]:
                # THE COLLAPSE, inside the last look: the rig goes, the Act I
                # beam comes back narrowing onto the flower, and the lens
                # tightens from the 24mm to Act I's 65mm while the camera
                # retreats to where the break stands — the room arriving at
                # the dark in the glass it left it in.
                strength = 1.0 - 0.92 * ease_in_out(seg(t, *COLLAPSE))
            self._look(LOOKS[i], u, t, strength=strength, az=az)
            if t >= COLLAPSE[0]:
                back = ease_in_out(seg(t, COLLAPSE[0] + BEAT, COLLAPSE[1]))
                self.beam.hide_render = back < 0.02
                self.key.data.energy = 620 * back
                self.key.data.spot_size = math.radians(7.0)
                aim_at(self.key, self.key_home); aim_at(self.beam, self.key_home)
                self.haze.inputs["Density"].default_value = 9.0 * back
                zz = ease_in_out(seg(t, *COLLAPSE))
                self.cam.data.lens = self.lens_wide + (self.lens - self.lens_wide) * zz
                cur = Vector(self.cam.location)
                target = R @ Vector((0.15, -1.60, 0.50))
                self.cam.location = cur + (target - cur) * zz
                aim_at(self.cam, H)
            return

        # THE BREAK. One beam, and then not even that. az is 0 here — home —
        # so the beam lands on the same line the fall left it on.
        self._look('editorial', 1.0, t, strength=0.0, az=az)
        for ob in self.props:
            ob.hide_render = True
        self.cyc.hide_render = True
        self.table.hide_render = False
        die = ease_in_out(seg(t, BREAK[0] + BEAT, BREAK[1]))
        self.beam.hide_render = False
        self.key.data.energy = 620 * (1.0 - die)
        self.key.data.spot_size = math.radians(7.0)
        aim_at(self.key, self.key_home); aim_at(self.beam, self.key_home)
        self.haze.inputs["Density"].default_value = 9.0 * (1.0 - die)
        self.cam.location = (0.15, -1.60, 0.50)
        self.cam.data.lens = self.lens
        aim_at(self.cam, H)

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
        # ...to the FLOOR, at the height the landed petal lies, on the last
        # frame of the fall. It used to stop 5cm up and the studio then put it
        # at 0.6cm: a 4.6cm hop, hidden by a cut that no longer exists — the
        # camera now runs straight through the switch, and a petal that hops
        # as the lights come on is the one thing the viewer would see.
        z = 0.436 + (LAND_Z - 0.436) * u         # head height down to the floor
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

    def faller_rot(self, t):
        """
        The falling petal's rotation — the peel, then the tumble, then the
        LANDING. The tumble is deliberately out of phase with the swing: a
        petal that rolls in time with its own sway reads as a keyframed prop.
        Over the last half beat it settles flat: pitch to pi (the blade's cup
        upward, so nothing goes through the floor) and the roll to nothing.
        The tumble already ends within 7 degrees of flat, so the settle is a
        petal finding the floor, not a snap. _pose_open uses the same pose,
        which is what keeps the petal still through the switch.
        """
        peel = ease_in(seg(t, *DETACH))
        uu = max(0.0, seg(t, *FALL))
        rx = math.radians(30 + 74 * peel) + 1.9 * uu + 0.55 * math.sin(uu * 5.3)
        ry = 0.42 * math.sin(uu * math.tau * 2.3)
        rz = math.radians(30) + 1.2 * uu
        land = ease_in_out(seg(t, FALL[1] - BEAT / 2, FALL[1]))
        return (rx + (math.pi - rx) * land, ry * (1.0 - land), rz)

    def _fall_camera(self, t):
        """
        The camera that goes down with the petal: (location, aim, lens), a
        pure function of t. Used by the fall AND by the reveal's first frame,
        so the switch is a change of light and nothing else.

        It holds the petal a little above centre and comes in from the framing
        distance to 0.62m — no further. It used to push to a third of that,
        so that the petal filled the frame for the paint to erupt out of; the
        paint is gone and a frame-filling orange shape followed by a cut to a
        frame-filling peach shape was the whole reason the transition read as
        two shots. On the way it ZOOMS OUT, 65mm to 30mm, and rises to 24cm
        over the petal — so it arrives on the landing looking down at a small
        petal on a dark floor, framed wide, and when the lights come on the
        room is simply there around it.
        """
        fp, u = self.faller_at(t)
        cl = ease_in_out(seg(t, DETACH[0], FALL[1]))
        lens = self.lens + (self.lens_wide - self.lens) * cl
        r = self.cam_near + (0.62 - self.cam_near) * cl
        az = math.radians(-90.0 + 16.0 * cl)
        dz = 0.035 * (1.0 - cl) + 0.24 * cl
        loc = fp + Vector((r * math.cos(az), r * math.sin(az), dz))
        # lead the petal: aim below it so it sits high and falls through the
        # middle; more lead at the end, so the floor it lands on is in shot
        aim = fp - Vector((0.0, 0.0, 0.026 * (1.0 - 0.4 * u) + 0.03 * cl))
        return loc, aim, lens

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
            self._studio_off()
            return self._set_time_ending(t)
        if t >= REVEAL[0]:
            return self._set_time_studio(t)
        self._studio_off()
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
            ob.location = self.petal_home
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
            self.faller.rotation_euler = self.faller_rot(t)

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
            # half as dense and half as deep as the first cut: the stem
            # still carries the five accents up with it, but as a shimmer
            # the piano can live with rather than a fault
            if (r / 2147483648.0) < density * 0.30:
                acc = ACCENTS[(r >> 11) % len(ACCENTS)]
                # blended, not replaced: a stem that turns fully blue is a
                # different object, one that flashes toward blue is a fault
                k = 0.30 + 0.30 * density
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

        # THE TWO GLITCHES, IN THE SAME MEDIUM AS THE STUDIO THEY PREVIEW.
        # For two frames the whole room is thrown into a look — the grid, then
        # the collage — over the fall exactly as it stands: the flower at the
        # side, the petal in the air, the beam still on. It used to be a 2D
        # frame substituted in; now it is the same Blender scene with the
        # lights on, which is what the drop is about to do for real.
        for k, g in enumerate(GLITCH_AT):
            if g <= t < g + GLITCH_FR / 24.0:
                self.table.hide_render = True
                self.cyc.hide_render = False
                self._look(('grid', 'collage')[k], 0.5, t, camera=False)

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
            self.cam.data.lens = self.lens
        else:
            # THE FOLLOW STARTS FROM WHERE THE CAMERA IS. The follow's own
            # start is 18cm higher than the travel's end and aimed at the head
            # instead of level, and switching to it on bt(37) hopped the whole
            # frame on the peel. It blends in over the peel beat instead.
            loc, aim, lens = self._fall_camera(t)
            w = ease_in_out(seg(t, DETACH[0], DETACH[1]))
            self.cam.location = ground + (loc - ground) * w
            self.cam.data.lens = lens
            self.cam.rotation_euler = (math.radians(90), 0, 0)
            aim_at(self.cam, Vector((0.0, 0.0, ground.z)) + (aim - Vector((0.0, 0.0, ground.z))) * w)
