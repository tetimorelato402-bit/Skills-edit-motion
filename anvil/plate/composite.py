#!/usr/bin/env python3
"""
ANVIL plate composite.

Phases (plate frames are 1-based, 60 fps):
  L   1-229   lock screen: remove the recording pill, rebuild the right
              status cluster and battery. Lock content untouched.
  T 230-274   the unlock zoom: the plate's giant flying icons sweep most of
              the frame, so everything above the rising dock is erased and
              rebuilt — status bar redrawn, the Anvil icon flown in on a
              synthetic version of the same decelerating zoom.
  H 275-318   settled home: grid + Search pill erased, Anvil tile at rest.
  O 319-345   app open (27 f): home recedes and dims, the app card expands
              from the icon with an iOS-style emphasized decelerate.
  C 346-435   hold on the Circle screen (1.5 s).

Status patches are composited with per-pixel max() so white text lands on
whatever is beneath without stamping black rectangles.
"""
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

W, H = 1180, 2556
SRC = "frames/p%04d.png"
OUT = "out"; os.makedirs(OUT, exist_ok=True)
os.makedirs("alpha", exist_ok=True)

# ---------------------------------------------------------------- helpers

def load(n): return Image.open(SRC % n).convert("RGB")

def bezier(x1, y1, x2, y2):
    def f(x):
        if x <= 0: return 0.0
        if x >= 1: return 1.0
        t = x
        for _ in range(9):
            t2 = 1 - t
            cx = 3*t2*t2*t*x1 + 3*t2*t*t*x2 + t*t*t
            dx = 3*t2*t2*x1 + 6*t2*t*(x2-x1) + 3*t*t*(1-x2)
            if dx == 0: break
            if abs(cx-x) < 1e-6: break
            t -= (cx-x)/dx
        t2 = 1 - t
        return 3*t2*t2*t*y1 + 3*t2*t*t*y2 + t*t*t
    return f

easeOpen = bezier(0.05, 0.7, 0.1, 1.0)     # iOS emphasized decelerate
easeZoom = bezier(0.17, 0.6, 0.15, 1.0)

def maxpaste(dst, patch, box):
    """white-on-black status patch: lighten-composite, no black stamping"""
    x, y = box
    region = np.asarray(dst.crop((x, y, x+patch.width, y+patch.height)), dtype=np.uint8)
    p = np.asarray(patch.convert("RGB"), dtype=np.uint8)
    dst.paste(Image.fromarray(np.maximum(region, p)), (x, y))

# ------------------------------------------------------- status ingredients

att   = load(60).crop((80, 40, 285, 132))       # "AT&T"
clock = load(310).crop((80, 40, 300, 132))      # "11:49 ☾"
sig   = load(310).crop((850, 55, 1008, 120))    # bars + 5G+

def draw_battery(im):
    d = ImageDraw.Draw(im, "RGBA")
    # body 1015-1090, y 76-106; healthy: white fill
    d.rounded_rectangle((1015, 76, 1090, 106), radius=10,
                        outline=(255, 255, 255, 130), width=3)
    d.rounded_rectangle((1020, 81, 1085, 101), radius=6, fill=(255, 255, 255, 255))
    d.pieslice((1092, 84, 1104, 98), -70, 70, fill=(255, 255, 255, 130))

def minpaste(dst, patch, box):
    """dark variant: the white-on-black patch inverted becomes black text on
    white, and a per-pixel min() lays black text over the light app."""
    x, y = box
    region = np.asarray(dst.crop((x, y, x+patch.width, y+patch.height)), dtype=np.uint8)
    p = 255 - np.asarray(patch.convert("RGB"), dtype=np.uint8)
    dst.paste(Image.fromarray(np.minimum(region, p)), (x, y))

def draw_battery_dark(im):
    d = ImageDraw.Draw(im, "RGBA")
    d.rounded_rectangle((1015, 76, 1090, 106), radius=10,
                        outline=(21, 19, 14, 120), width=3)
    d.rounded_rectangle((1020, 81, 1085, 101), radius=6, fill=(21, 19, 14, 255))
    d.pieslice((1092, 84, 1104, 98), -70, 70, fill=(21, 19, 14, 120))

def status_dark(im):
    """over a light app the status content flips dark, as iOS does"""
    minpaste(im, clock, (80, 40))
    minpaste(im, sig, (850, 55))
    draw_battery_dark(im)

def status(im, left):     # left: "att" | "clock" | ("mix", a)
    if left == "att": maxpaste(im, att, (80, 40))
    elif left == "clock": maxpaste(im, clock, (80, 40))
    else:
        a = left[1]
        fade = Image.blend(att.resize(clock.size), clock, a)
        maxpaste(im, fade, (80, 40))
    maxpaste(im, sig, (850, 55))
    draw_battery(im)

def scrub_pill(im):
    ImageDraw.Draw(im).rectangle((315, 22, 848, 148), fill=(0, 0, 0))

def scrub_cluster(im):
    ImageDraw.Draw(im).rectangle((845, 35, 1112, 138), fill=(0, 0, 0))

# ------------------------------------------------------------- home pieces

tile = Image.open("icon_tile.png").resize((300, 450), Image.LANCZOS)  # 1x
TILE_ICON = (58.5, 20.0)          # icon top-left inside the 1x tile
ICON_XY = (90.0, 245.0)           # grid position 1
ICON_W = 183.0
art = Image.open("icon_art.png")  # 1024 squircle art
circle = Image.open("circle_full.png").convert("RGB")

def paste_tile(im, s=1.0, alpha=1.0, label=1.0):
    """tile transformed by the home-layer zoom: scale s about screen centre"""
    t = tile.copy()
    if label < 1.0:                # label+badge fade separately from icon
        a = np.asarray(t).copy()
        a[420//2*2:, :, 3] = (a[450-30*2:, :, 3])  # no-op guard
        t = Image.fromarray(a)
        lab = t.crop((0, 430, 300, 450))
    if s != 1.0:
        t = t.resize((max(1, int(300*s)), max(1, int(450*s))), Image.LANCZOS)
    cx, cy = 590.0, 1278.0
    x = cx + (ICON_XY[0] - TILE_ICON[0] - cx) * s
    y = cy + (ICON_XY[1] - TILE_ICON[1] - cy) * s
    if alpha < 1.0:
        a = np.asarray(t).copy()
        a[:, :, 3] = (a[:, :, 3].astype(float) * alpha).astype(np.uint8)
        t = Image.fromarray(a)
    im.paste(t, (int(round(x)), int(round(y))), t)

# label/badge fade handled by splitting the tile rows
tile_icon_only = tile.copy()
_a = np.asarray(tile_icon_only).copy()
_a[218:, :, 3] = 0        # below icon: label rows (label starts ~y 220 in 1x tile)
_b = np.asarray(tile).copy()
_b[:218, 0:170, 3] = 0    # keep only badge (x>170 in top region) + label rows
tile_icon_only = Image.fromarray(_a)
tile_extras = Image.fromarray(_b)

def paste_tile_split(im, s, alpha_icon, alpha_extra):
    for t0, al in ((tile_icon_only, alpha_icon), (tile_extras, alpha_extra)):
        if al <= 0: continue
        t = t0
        if s != 1.0:
            t = t.resize((max(1, int(300*s)), max(1, int(450*s))), Image.LANCZOS)
        cx, cy = 590.0, 1278.0
        x = cx + (ICON_XY[0] - TILE_ICON[0] - cx) * s
        y = cy + (ICON_XY[1] - TILE_ICON[1] - cy) * s
        if al < 1.0:
            a = np.asarray(t).copy()
            a[:, :, 3] = (a[:, :, 3].astype(float) * al).astype(np.uint8)
            t = Image.fromarray(a)
        im.paste(t, (int(round(x)), int(round(y))), t)

# dock top per transition frame (measured icon-top minus panel margin)
DOCK = {239: 2340, 240: 2310, 244: 2303, 248: 2228, 252: 2214,
        256: 2225, 260: 2240, 264: 2252, 268: 2258, 272: 2260, 274: 2260}
def dock_top(n):
    ks = sorted(DOCK)
    if n <= ks[0]: return DOCK[ks[0]] - 74
    for a, b in zip(ks, ks[1:]):
        if a <= n <= b:
            t = (n - a) / (b - a)
            return DOCK[a] + (DOCK[b] - DOCK[a]) * t - 74
    return DOCK[ks[-1]] - 74

# ---------------------------------------------------------------- phases

frames_out = []

def emit(im):
    frames_out.append(im)

# L + T + H from the plate
for n in range(1, 319):
    im = load(n)
    d = ImageDraw.Draw(im)
    if n <= 229:                                    # -------- lock
        scrub_pill(im); scrub_cluster(im)
        maxpaste(im, sig, (850, 55)); draw_battery(im)
    elif n <= 274:                                  # -------- transition
        keep = int(dock_top(n)) if n >= 239 else 2300
        d.rectangle((0, 0, W, keep), fill=(0, 0, 0))
        # Anvil flies in on the home zoom: decelerating from 2.4x
        p = (n - 242) / (268 - 242)
        if p > 0:
            s = 2.4 - 1.4 * easeZoom(min(p, 1.0))
            if n >= 268: s = max(1.0, s - 0)        # settled
            a_icon = min(1.0, max(0.0, (n - 242) / 10))
            a_ext = min(1.0, max(0.0, (n - 262) / 10))
            paste_tile_split(im, s, a_icon, a_ext)
        left = "att" if n < 234 else ("clock" if n > 242 else ("mix", (n-234)/8))
        status(im, left)
    else:                                           # -------- settled home
        d.rectangle((0, 185, W, 2183), fill=(0, 0, 0))
        scrub_pill(im); scrub_cluster(im)
        maxpaste(im, sig, (850, 55)); draw_battery(im)
        paste_tile_split(im, 1.0, 1.0, 1.0)
    emit(im)

# -------- app open + hold, synthetic, from the last cleaned home frame
home_clean = frames_out[-1].copy()
home_noicon = load(318)
dh = ImageDraw.Draw(home_noicon)
dh.rectangle((0, 185, W, 2183), fill=(0, 0, 0))
scrub_pill(home_noicon); scrub_cluster(home_noicon)
maxpaste(home_noicon, sig, (850, 55)); draw_battery(home_noicon)

OPEN_F = 27
ix, iy, iw = ICON_XY[0], ICON_XY[1], ICON_W
# final rect overshoots the frame so its rounded corners fall outside
FX, FY, FW, FH = -18.0, -39.0, W + 36.0, H + 78.0

def app_card(e, for_alpha=False):
    """the expanding card at ease-progress e; returns RGBA at full frame"""
    x = ix + (FX - ix) * e
    y = iy + (FY - iy) * e
    w = iw + (FW - iw) * e
    h = iw + (FH - iw) * e
    r = 41 + (150 - 41) * e
    card = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    # content: icon art crossfading into the circle screen, aspect-fill
    content = Image.new("RGB", (max(2, int(w)), max(2, int(h))), "#E7E0D2")
    if e < 0.42:
        sart = art.resize((int(w), int(w)), Image.LANCZOS)
        content.paste(sart, (0, int((h - w) / 2)))
    if e > 0.12:
        sc = max(w / W, h / H)
        aw, ah = int(W * sc), int(H * sc)
        app = circle.resize((aw, ah), Image.LANCZOS)
        app = app.crop((int((aw - w) / 2), int((ah - h) / 2),
                        int((aw - w) / 2) + int(w), int((ah - h) / 2) + int(h)))
        if e < 0.42:
            fade = (e - 0.12) / 0.30
            content = Image.blend(content, app, fade)
        else:
            content = app
    mask = Image.new("L", content.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, content.width - 1, content.height - 1),
                                           radius=int(r), fill=255)
    card.paste(content, (int(round(x)), int(round(y))), mask)
    if not for_alpha:
        # a soft shadow under the card while it is smaller than the frame
        if e < 0.96:
            sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            ImageDraw.Draw(sh).rounded_rectangle(
                (x - 8, y + 6, x + w + 8, y + h + 22), radius=int(r) + 8,
                fill=(0, 0, 0, int(120 * (1 - e))))
            sh = sh.filter(ImageFilter.GaussianBlur(18))
            base = Image.alpha_composite(sh, card)
            return base
    return card

alpha_frames = []
for i in range(OPEN_F):
    e = easeOpen((i + 1) / OPEN_F)
    # background: home recedes and dims (icon's label fades with it)
    bs = 1 - 0.12 * e
    bg = home_noicon.resize((int(W * bs), int(H * bs)), Image.LANCZOS)
    canvas = Image.new("RGB", (W, H), (0, 0, 0))
    canvas.paste(bg, (int((W - bg.width) / 2), int((H - bg.height) / 2)))
    canvas = Image.fromarray(
        (np.asarray(canvas, dtype=np.float32) * (1 - 0.5 * e)).astype(np.uint8))
    # the tile's label and badge fade with the home layer, not in one frame
    if i < 8:
        paste_tile_split(canvas, bs, 0.0, 1 - i / 8)
    card = app_card(e)
    canvas = Image.alpha_composite(canvas.convert("RGBA"), card).convert("RGB")
    # the status bar stays on top and flips to dark content over the light app
    if e < 0.42:
        status(canvas, "clock")
    elif e < 0.72:
        light = canvas.copy(); status(light, "clock")
        dark = canvas.copy(); status_dark(dark)
        canvas = Image.blend(light, dark, (e - 0.42) / 0.30)
    else:
        status_dark(canvas)
    emit(canvas)
    alpha_frames.append(app_card(e, for_alpha=True))

final = Image.alpha_composite(Image.new("RGBA", (W, H), (0, 0, 0, 255)),
                              app_card(1.0, for_alpha=True)).convert("RGB")
status_dark(final)
for _ in range(90):
    emit(final.copy())

# ---------------------------------------------------------------- write

for i, im in enumerate(frames_out):
    im.save(f"{OUT}/f{i:04d}.png")
for i, im in enumerate(alpha_frames):
    im.save(f"alpha/a{i:04d}.png")
final.save("anvil_circle_final.png")
print(f"{len(frames_out)} frames, {len(alpha_frames)} alpha frames")
