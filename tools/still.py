#!/usr/bin/env python3
"""
Pull one frame out of a video and finish it as a PHOTOGRAPH.

A frame and a photograph are not the same object. A frame is one sample of a
moving thing, graded so that the two hundred either side of it also work. A
photograph only has to work once, so it can be pushed much further — and it has
to be, because everything a still image has instead of motion (surface, grain,
the way light spills) is exactly what a codec spends its bitrate throwing away.

The order below is not arbitrary. Anything that models LIGHT — halation,
bloom, vignette — has to happen in linear, where light actually adds. Anything
that models PERCEPTION — local contrast, split tone, vibrance, grain — happens
after the tone curve, where the eye is. Doing halation in sRGB gives you a grey
smear instead of a glow; doing grain in linear buries it in the shadows.

  1  linear        undo the display transform, get back to light
  2  halation      the one that matters most on a backlit night frame
  3  bloom         a little veil, the way a real lens scatters
  4  vignette      lens falloff, off-centre so it aims at the subject
  5  tone          exposure, then a shoulder so the highlight rolls
  6  structure     large-radius local contrast: opens the subject, not the sky
  7  split tone    cool shadows, warm highlights, restrained
  8  vibrance      saturation weighted AGAINST what is already saturated
  9  grain         luminance-weighted, because film grain lives in the midtones
 10  sharpen       last, and masked out of the shadows so grain stays grain

    python3 tools/still.py IN.mp4 --frame 104 --out photo.png
"""
import argparse
from pathlib import Path

import imageio_ffmpeg
import numpy as np
from PIL import Image, ImageFilter


# ----------------------------------------------------------------- colour
def to_linear(x):
    return np.where(x <= 0.04045, x / 12.92, ((x + 0.055) / 1.055) ** 2.4)


def to_srgb(x):
    x = np.clip(x, 0.0, None)
    return np.where(x <= 0.0031308, x * 12.92, 1.055 * x ** (1 / 2.4) - 0.055)


LUMA = np.array([0.2126, 0.7152, 0.0722], np.float32)


def lum(rgb):
    return rgb @ LUMA


def blur(a, radius):
    """
    Gaussian blur, done at a reduced size when the radius is large.

    A 140px blur on a 3300px plate is minutes through a straight convolution
    and visually identical to a 9px blur on a plate an eighth the size — the
    kernel is far wider than the detail either one can carry.
    """
    if radius < 12:
        return _pil_blur(a, radius)
    k = int(min(8, max(2, radius / 8)))
    h, w = a.shape[:2]
    sm = np.asarray(Image.fromarray(np.clip(a * 255, 0, 255).astype(np.uint8))
                    .resize((max(1, w // k), max(1, h // k)), Image.BILINEAR)) / 255.0
    sm = _pil_blur(sm.astype(np.float32), radius / k)
    return np.asarray(Image.fromarray(np.clip(sm * 255, 0, 255).astype(np.uint8))
                      .resize((w, h), Image.BILINEAR)).astype(np.float32) / 255.0


def _pil_blur(a, radius):
    mx = max(1e-6, float(a.max()))
    im = Image.fromarray(np.clip(a / mx * 255, 0, 255).astype(np.uint8))
    return np.asarray(im.filter(ImageFilter.GaussianBlur(radius))).astype(np.float32) / 255.0 * mx


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("--frame", type=int, default=0)
    ap.add_argument("--out", required=True)
    ap.add_argument("--ratio", default="3:2", help="output aspect, or 'source'")
    ap.add_argument("--halation", type=float, default=0.70)
    ap.add_argument("--grain", type=float, default=1.0)
    ap.add_argument("--exposure", type=float, default=0.45, help="stops")
    ap.add_argument("--white", type=float, default=4.5,
                    help="the input level that maps to white; lower clips sooner")
    ap.add_argument("--seed", type=int, default=11)
    args = ap.parse_args()

    g = imageio_ffmpeg.read_frames(args.src)
    info = g.__next__()
    w, h = info["size"]
    plate = None
    for i, raw in enumerate(g):
        if i == args.frame:
            plate = np.frombuffer(raw, np.uint8).reshape(h, w, 3).copy()
            break
    if plate is None:
        raise SystemExit(f"frame {args.frame} is past the end of {args.src}")
    print(f"  frame {args.frame} of {w}x{h}", flush=True)

    # ------------------------------------------------------------- 0  crop
    # Trimmed from BOTH edges, not just the top. The flag's top corner and the
    # runner's trailing foot are the two things closest to leaving the frame,
    # so taking the whole trim off one side puts one of them against the edge.
    if args.ratio != "source":
        rw, rh = (float(v) for v in args.ratio.split(":"))
        want_h = int(round(w * rh / rw))
        if want_h < h:
            cut = h - want_h
            top = int(cut * 0.54)
            plate = plate[top:top + want_h]
        else:
            want_w = int(round(h * rw / rh))
            cut = w - want_w
            plate = plate[:, cut // 2:cut // 2 + want_w]
    H, W = plate.shape[:2]
    print(f"  crop  {W}x{H}  ({W / H:.3f}:1)", flush=True)

    lin = to_linear(plate.astype(np.float32) / 255.0)

    # --------------------------------------------------------- 2  halation
    # The single biggest difference between this and a photograph. A bright
    # source behind fabric does not stop at the fabric: on film it scatters
    # back off the base and re-exposes the emulsion around it, and it does so
    # RED, because the anti-halation backing gives up in the long wavelengths
    # first. That is why every backlit night frame that reads as film has a
    # warm bleed and every digital one has a hard edge.
    L = lum(lin)
    T = 0.30
    hot = np.clip((L - T) / (1 - T), 0, None) ** 1.6
    halo = (blur(hot, 10) * 0.55 + blur(hot, 46) * 0.34 + blur(hot, 150) * 0.30)
    tint = np.array([1.00, 0.30, 0.13], np.float32)      # the red bleed
    lin += halo[..., None] * tint * (0.42 * args.halation)

    # ------------------------------------------------------------ 3  bloom
    # A separate, neutral, much weaker veil. Halation is the emulsion; this is
    # the glass. Keeping them apart is what stops the highlight turning into
    # one orange blob.
    lin += blur(lin, 90) * 0.055

    # --------------------------------------------------------- 4  vignette
    # Off-centre, aimed between the runner and the light in the flag, so the
    # falloff is doing composition rather than just darkening corners.
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    r = np.sqrt(((xx / W - 0.46) * 1.06) ** 2 + ((yy / H - 0.44) * 1.32) ** 2)
    # capped short of black: a vignette that reaches 0 is not a lens, it is a
    # hole, and it takes the wet sand in the bottom corner with it
    lin *= (1.0 - 0.40 * np.clip(r / 0.86, 0, 1) ** 2.1)[..., None]

    # ------------------------------------------------------------- 5  tone
    lin *= 2.0 ** args.exposure
    # extended Reinhard: linear through the midtones, a shoulder at the top,
    # so the glow gains shape instead of clipping to a white hole
    WP = args.white
    lin = lin * (1.0 + lin / (WP * WP)) / (1.0 + lin)

    img = np.clip(to_srgb(lin), 0, 1)

    # -------------------------------------------------------- 6  structure
    # Large-radius local contrast. This is what makes the runner's back read
    # as a body instead of a silhouette, and it leaves the sky alone for free:
    # a flat area has nothing for a large-radius unsharp to find.
    Ld = lum(img)
    base = blur(Ld, 130)
    detail = Ld - base
    gain = np.where(Ld > 1e-4, (Ld + detail * 0.62) / np.maximum(Ld, 1e-4), 1.0)
    img *= np.clip(gain, 0.55, 1.9)[..., None]
    img = np.clip(img, 0, 1)

    # ------------------------------------------------------- 7  split tone
    # Night is already blue, so the shadows only need confirming, not
    # inventing. The work is in the highlights: pushing them warm is what
    # separates the flag from the sea instead of letting one blue swamp both.
    Ld = lum(img)
    ws = (1.0 - Ld) ** 3.0
    wh = Ld ** 1.8
    img += ws[..., None] * np.array([-0.012, 0.004, 0.040], np.float32)
    img += wh[..., None] * np.array([0.030, 0.008, -0.030], np.float32)
    # a film toe: real blacks are lifted and slightly cool, never zero
    img = 0.018 + img * (1.0 - 0.018)
    img[..., 2] += 0.008 * (1.0 - Ld) ** 2
    img = np.clip(img, 0, 1)

    # --------------------------------------------------------- 8  vibrance
    # Weighted against what is already saturated, so the wet sand and the surf
    # find colour while the flag's red — which is at the top already — does not
    # tip over into fluorescent. Kept low: a night sky and a night sea are two
    # different blues, and pushing the unsaturated end hard merges them into
    # one, which is the exact opposite of depth.
    mx = img.max(2); mn = img.min(2)
    sat = (mx - mn) / np.maximum(mx, 1e-4)
    grey = lum(img)[..., None]
    img = np.clip(grey + (img - grey) * (1.0 + 0.26 * (1.0 - sat))[..., None], 0, 1)
    # and separate them again by depth: the darkest blue goes deeper and
    # slightly greener, which is what open water at night actually looks like
    d = (1.0 - lum(img)) ** 2.4
    img[..., 0] -= 0.020 * d
    img[..., 2] -= 0.014 * d
    img = np.clip(img, 0, 1)

    # ------------------------------------------------------------ 9  grain
    # Weighted to the midtones, because that is where silver halide actually
    # clumps; uniform noise reads as sensor noise, which is the opposite of
    # the thing being aimed at. Blurred slightly, because a grain has a size.
    rng = np.random.default_rng(args.seed)
    gr = rng.standard_normal((H, W)).astype(np.float32)
    gr = _pil_blur(gr - gr.min(), 0.8)
    gr = (gr - gr.mean()) / (gr.std() + 1e-9)
    Ld = lum(img)
    img += (gr * (4.0 * Ld * (1.0 - Ld)) * 0.030 * args.grain)[..., None]
    img += rng.standard_normal((H, W, 3)).astype(np.float32) * 0.006 * args.grain
    img = np.clip(img, 0, 1)

    # -------------------------------------------------------- 10  sharpen
    out = Image.fromarray((img * 255).astype(np.uint8))
    out = out.filter(ImageFilter.UnsharpMask(radius=1.6, percent=62, threshold=3))

    p = Path(args.out); p.parent.mkdir(parents=True, exist_ok=True)
    out.save(p, quality=97, subsampling=0)
    a = np.asarray(out).astype(np.float32)
    print(f"  levels  black {np.percentile(a, 0.5):.0f}  median {np.median(a):.0f}  "
          f"white {np.percentile(a, 99.8):.0f}", flush=True)
    print(f"  -> {p}  {out.size[0]}x{out.size[1]}")


if __name__ == "__main__":
    main()
