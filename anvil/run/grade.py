#!/usr/bin/env python3
"""
ANVIL run clip: grade, re-edit, reframe.

The grade is one vectorized function; the .cube LUT is sampled from the same
function, so the delivered video and the exported LUT are the same grade by
construction. Grain and vignette are spatial and applied per output after
reframing (a LUT cannot carry them).
"""
import os
import numpy as np
from PIL import Image

SRCN = 124
PAPER = np.array([231, 224, 210], dtype=np.float32) / 255.0

# ------------------------------------------------------------------ grade

def smooth(a, b, x):
    t = np.clip((x - a) / (b - a), 0, 1)
    return t * t * (3 - 2 * t)

def grade(rgb):
    """rgb float32 [0,1], any shape (...,3)"""
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    L = 0.2126 * r + 0.7152 * g + 0.0722 * b

    # warm white balance, highlights warmest — never split-tone cool
    r = r * (1.030 + 0.050 * L)
    g = g * (1.000 + 0.012 * L)
    b = b * (0.955 - 0.055 * L)

    # ---- hue surgery in HSV
    mx = np.maximum(np.maximum(r, g), b)
    mn = np.minimum(np.minimum(r, g), b)
    d = mx - mn + 1e-9
    h = np.zeros_like(mx)
    m = (mx == r); h[m] = (60 * ((g - b) / d) % 360)[m]
    m = (mx == g); h[m] = (60 * ((b - r) / d) + 120)[m]
    m = (mx == b); h[m] = (60 * ((r - g) / d) + 240)[m]
    s = np.where(mx > 0, d / (mx + 1e-9), 0)
    v = mx

    # the slate ocean: desaturate blues hard, walk the hue to warm grey-green
    wb = smooth(175, 195, h) * (1 - smooth(255, 275, h))
    s = s * (1 - 0.60 * wb)
    h = h + (163 - h) * 0.58 * wb

    # global pull to ~76%, except the bronze/amber band keeps the ember
    wa = smooth(18, 27, h) * (1 - smooth(45, 56, h))
    s = s * (0.88 + 0.44 * wa)

    # back to rgb
    hh = (h % 360) / 60.0
    i = np.floor(hh).astype(int) % 6
    f = hh - np.floor(hh)
    p = v * (1 - s); q = v * (1 - s * f); t = v * (1 - s * (1 - f))
    r = np.select([i == 0, i == 1, i == 2, i == 3, i == 4, i == 5], [v, q, p, p, t, v])
    g = np.select([i == 0, i == 1, i == 2, i == 3, i == 4, i == 5], [t, v, v, q, p, p])
    b = np.select([i == 0, i == 1, i == 2, i == 3, i == 4, i == 5], [p, p, t, v, v, q])
    out = np.stack([r, g, b], axis=-1)

    # gentle S-curve, low contrast, filmic and open
    pivot, k = 0.46, 0.14
    out = pivot + (out - pivot) * (1 + k * (1 - np.abs(out - pivot) * 1.6))

    # lifted blacks (floor ~22) and a ceiling with soft roll (~245)
    out = 0.086 + out * (0.925 - 0.086) / 0.925
    Lg = out @ np.float32([0.2126, 0.7152, 0.0722])

    # highlights roll toward PAPER — the guardrail stays creamy, never white
    wހ = (smooth(0.70, 0.96, Lg) * 0.45)[..., None]
    toward = Lg[..., None] * (PAPER / (PAPER @ np.float32([0.2126, 0.7152, 0.0722])))
    out = out * (1 - wހ) + toward * wހ

    # warm-brown shadow tint
    ws = ((1 - Lg) ** 2)[..., None]
    out = out + ws * np.float32([0.030, 0.011, -0.021])

    return np.clip(out, 0.0, 0.961)   # 245 ceiling, hard

# ------------------------------------------------------------------- LUT

def write_cube(path, n=33):
    ax = np.linspace(0, 1, n, dtype=np.float32)
    B, G, R = np.meshgrid(ax, ax, ax, indexing="ij")
    grid = np.stack([R, G, B], axis=-1).reshape(-1, 3)
    out = grade(grid)
    with open(path, "w") as f:
        f.write("TITLE \"ANVIL forge grade\"\nLUT_3D_SIZE %d\n" % n)
        f.write("DOMAIN_MIN 0.0 0.0 0.0\nDOMAIN_MAX 1.0 1.0 1.0\n")
        for row in out:
            f.write("%.6f %.6f %.6f\n" % tuple(row))
    print("wrote", path)

# ------------------------------------------------------ finishing (spatial)

def finish(img, rng):
    """film grain (heavier in shadows) + very soft warm vignette, at output res"""
    a = np.asarray(img, dtype=np.float32)
    L = (a @ np.float32([0.2126, 0.7152, 0.0722])) / 255.0
    sigma = 2.0 + 4.6 * np.power(np.clip(1 - L, 0, 1), 1.5)
    gl = rng.standard_normal(L.shape).astype(np.float32)
    gc = rng.standard_normal(a.shape).astype(np.float32) * 0.35
    a = a + (gl[..., None] + gc) * sigma[..., None]
    h, w = L.shape
    yy, xx = np.mgrid[0:h, 0:w]
    dist = np.sqrt(((xx - w / 2) / (w / 2)) ** 2 + ((yy - h / 2) / (h / 2)) ** 2)
    vig = 1 - 0.052 * np.clip(dist - 0.55, 0, 1) ** 1.8
    a = a * vig[..., None]
    a[..., 2] *= (1 - 0.006 * np.clip(dist - 0.55, 0, 1)[..., None][..., 0] ** 1.8)
    # the floor survives the grain: gaussian tails would otherwise punch
    # a lifted 21 down to true black
    return Image.fromarray(np.clip(a, 18, 247).astype(np.uint8))

# --------------------------------------------------------------- the track

def head_track():
    xs, ns = [], []
    for n in range(1, SRCN + 1, 3):
        a = np.asarray(Image.open(f"src/f{n:03d}.png").convert("RGB"),
                       dtype=np.float32) / 255
        reg = a[:648]
        m = (reg[..., 0] > 0.55) & (reg[..., 0] - reg[..., 2] > 0.13)
        y, x = np.where(m)
        if len(x) > 200:
            ns.append(n); xs.append(np.median(x))
    c = np.polyfit(ns, xs, 3)
    return lambda n: float(np.polyval(c, n))

# --------------------------------------------------------------- sky plate

_cloud_field = None

def _cloud(w, h):
    """one large smooth field, sampled with a slow drift — coarse random grids
    upscaled bicubically read as soft cloud; sin-products read as argyle"""
    global _cloud_field
    if _cloud_field is None:
        rng = np.random.default_rng(23)
        f = np.zeros((h * 2, w * 2), dtype=np.float32)
        for gw, gh, amp in ((9, 4, 1.0), (19, 7, 0.45), (37, 12, 0.2)):
            coarse = rng.standard_normal((gh, gw)).astype(np.float32)
            up = np.asarray(Image.fromarray(coarse).resize((w * 2, h * 2),
                                                           Image.BICUBIC))
            f += amp * up
        _cloud_field = f / np.abs(f).max()
    return _cloud_field

def sky(w, h, t, rng_c=None):
    """warm dawn gradient, soft cloud, no sun disc; t in seconds for drift"""
    yy = np.linspace(0, 1, h, dtype=np.float32)[:, None] + t * 0.004
    top = np.float32([158, 138, 118]) / 255
    mid = np.float32([205, 176, 138]) / 255
    low = np.float32([234, 210, 172]) / 255
    g1 = np.clip(yy * 1.6, 0, 1); g2 = np.clip((yy - 0.55) * 2.2, 0, 1)
    col = top * (1 - g1[..., None]) + mid * g1[..., None]
    col = col * (1 - g2[..., None]) + low * g2[..., None]
    img = np.repeat(col, w, axis=1).reshape(h, w, 3)
    field = _cloud(w, h)
    dx = int(w * 0.25 + t * 14); dy = int(h * 0.3 + t * 3)
    n = field[dy:dy + h, dx:dx + w]
    band = (0.55 - np.abs(yy - 0.42)).clip(0.08, 0.55)
    img += (n * 0.075 * band)[..., None] * np.float32([1.0, 0.95, 0.84])
    return grade(np.clip(img, 0, 1))

if __name__ == "__main__":
    os.makedirs("graded", exist_ok=True)
    write_cube("anvil_run.cube")
    for n in range(1, SRCN + 1):
        a = np.asarray(Image.open(f"src/f{n:03d}.png").convert("RGB"),
                       dtype=np.float32) / 255
        Image.fromarray((grade(a) * 255).astype(np.uint8)).save(f"graded/g{n:03d}.png")
        if n % 30 == 0: print("graded", n)
    print("masters done")
