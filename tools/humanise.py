#!/usr/bin/env python3
"""
Put a person behind the camera, and a nervous system inside the subject.

Generated video gives itself away in two places, and neither of them is the
pixels. The CAMERA is perfectly still or perfectly smooth, because nothing was
holding it. And the SUBJECT'S motion is periodic, because a model interpolated
it — a real anxious leg does not tick like a metronome, it stutters, stalls,
and restarts faster.

So this fixes both, and they are separate problems:

  SPATIAL   a handheld rig, built from four bands of noise that correspond to
            four real things a body does — breathing, swaying, muscle tremor,
            and re-framing. Layer them and you get handheld; use one band of
            white noise and you get a phone in a paint shaker.

  TEMPORAL  a RATE warp — the clip runs slightly fast here and slightly slow
            there — so the bounce loses its period rather than merely shifting
            phase. This is the half nobody does, and it is the half that makes
            the SUBJECT read as human rather than just the operator.
            It SNAPS to whole frames: blending between two source frames
            crossfades a fast-moving limb into a double image, which reads as
            a dissolve, not as blur. The source already carries its own
            shutter smear; holding and skipping whole frames keeps that smear
            intact and turns the warp into a stutter, which is what an anxious
            leg actually does.

Stress is not a separate mode, it is a set of dials: the tremor comes up, the
breath goes shallow and fast, and the re-frames get more frequent and less
tidy — which is exactly what a tense operator does.

    python3 tools/humanise.py IN.mp4 --out OUT.mp4 --stress 0.7
"""
import argparse
import math
import subprocess
from pathlib import Path

import imageio_ffmpeg
import numpy as np
from PIL import Image, ImageFilter


def band_noise(n, fps, lo, hi, rng, order=2.0):
    """
    Noise confined to a frequency band, via the spectrum.

    Handheld is not white noise. Every component of it lives in a band you can
    name — a breath is a fifth of a hertz, a tremor is ten — so the honest way
    to build it is to take white noise and keep only the band you want.
    """
    x = rng.standard_normal(n * 2)
    f = np.fft.rfftfreq(len(x), 1.0 / fps)
    X = np.fft.rfft(x)
    # a soft-shouldered pass, because a brick wall rings
    g = 1.0 / (1.0 + (np.maximum(f, 1e-6) / hi) ** (2 * order))
    g *= 1.0 - 1.0 / (1.0 + (np.maximum(f, 1e-6) / lo) ** (2 * order))
    y = np.fft.irfft(X * g, len(x))[:n]
    m = np.max(np.abs(y))
    return y / m if m > 1e-9 else y


def reframes(n, fps, rng, per_sec, amp):
    """
    The operator noticing the frame has drifted and correcting it.

    This is the thing that separates "handheld" from "vibrating": a person does
    not oscillate around the right framing, they let it slide and then take it
    back in one quick move. Fast in, slow settle.
    """
    out = np.zeros(n)
    t = 0.0
    while t < n / fps:
        t += rng.exponential(1.0 / max(per_sec, 1e-6))
        i = int(t * fps)
        if i >= n:
            break
        rise = max(2, int(rng.uniform(0.05, 0.12) * fps))
        fall = max(4, int(rng.uniform(0.25, 0.55) * fps))
        a = amp * rng.uniform(0.5, 1.0) * rng.choice([-1.0, 1.0])
        seg = np.concatenate([
            a * (np.linspace(0, 1, rise) ** 0.6),
            a * np.exp(-np.linspace(0, 4.2, fall)),
        ])
        j = min(n, i + len(seg))
        out[i:j] += seg[:j - i]
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("--out", required=True)
    ap.add_argument("--size", type=int, default=1080)
    ap.add_argument("--stress", type=float, default=0.7,
                    help="0 = calm operator, 1 = the shot is hard to hold")
    ap.add_argument("--zoom", type=float, default=1.075,
                    help="headroom for the shake; the crop must never see an edge")
    ap.add_argument("--warp", type=float, default=1.0,
                    help="how hard the subject's RATE varies; 0 keeps the original timing")
    ap.add_argument("--shake", type=float, default=1.6,
                    help="global multiplier on the whole rig")
    ap.add_argument("--sharp", type=float, default=0.35,
                    help="counters the upscale; 0 leaves the plate as soft as it came")
    ap.add_argument("--seed", type=int, default=4)
    args = ap.parse_args()

    ff = imageio_ffmpeg.get_ffmpeg_exe()
    meta = imageio_ffmpeg.read_frames(args.src)
    info = meta.__next__()
    sw, sh = info["size"]
    fps = info["fps"]
    src = [np.frombuffer(f, np.uint8).reshape(sh, sw, 3) for f in meta]
    n = len(src)
    print(f"  in  {sw}x{sh} {fps:g}fps {n} frames ({n / fps:.2f}s)", flush=True)

    S = float(np.clip(args.stress, 0, 1))
    rng = np.random.default_rng(args.seed)
    OUT = args.size

    # ---------------------------------------------------------------- the rig
    # Four bands, four real things. The amplitudes are in OUTPUT pixels.
    breath_hz = 0.28 + 0.22 * S          # tense breathing is faster and shallower
    breath = band_noise(n, fps, breath_hz * 0.6, breath_hz * 1.7, rng)
    sway_x = band_noise(n, fps, 0.7, 1.8, rng)
    sway_y = band_noise(n, fps, 0.6, 1.6, rng)
    trem_x = band_noise(n, fps, 7.0, 12.0, rng)
    trem_y = band_noise(n, fps, 7.0, 12.0, rng)
    trem_r = band_noise(n, fps, 6.0, 11.0, rng)
    drift_r = band_noise(n, fps, 0.2, 0.9, rng)
    push = band_noise(n, fps, 0.15, 0.5, rng)          # fore/aft, the operator's weight

    # THE SUBJECT DRIVES THE OPERATOR. Where the leg moves hardest the camera
    # reacts — a beat LATE, because a person cannot anticipate. Without this
    # the shake is wallpaper; with it the camera looks like it is watching.
    small = np.stack([np.asarray(Image.fromarray(f).convert("L").resize((96, 96)))
                      for f in src]).astype(np.float32)
    energy = np.zeros(n)
    energy[1:] = np.abs(np.diff(small, axis=0)).mean(axis=(1, 2))
    if energy.max() > 1e-6:
        energy /= energy.max()
    k = max(1, int(0.10 * fps))
    energy = np.convolve(energy, np.ones(k) / k, mode="same")
    react = np.concatenate([np.zeros(max(1, int(0.09 * fps))), energy])[:n]   # the late beat

    K = args.shake
    px = K * (sway_x * (2.6 + 3.4 * S)
              + trem_x * (1.0 + 4.6 * S) * (0.55 + 0.85 * react)
              + reframes(n, fps, rng, 0.35 + 1.15 * S, 5.0 + 9.0 * S))
    py = K * (breath * (2.2 + 1.4 * S)
              + sway_y * (2.0 + 3.0 * S)
              + trem_y * (1.0 + 5.0 * S) * (0.55 + 0.85 * react)
              + reframes(n, fps, rng, 0.30 + 0.95 * S, 4.0 + 8.0 * S))
    rot = K * (drift_r * (0.10 + 0.20 * S)
               + trem_r * (0.06 + 0.30 * S) * (0.55 + 0.85 * react))      # degrees
    zoom = args.zoom * (1.0 + push * (0.0035 + 0.0045 * S))

    # ROLLING SHUTTER. Every handheld camera has it, and its absence is one of
    # the quiet reasons synthetic footage reads as synthetic: a real sensor is
    # still scanning while the operator is still moving, so a fast vertical
    # move leans the frame over.
    vy = np.gradient(py)
    shear = np.clip(vy * (0.0016 + 0.0026 * S), -0.02, 0.02)

    # ------------------------------------------------------------- the retime
    # Offsetting time by a fraction of a frame only shifts the bounce's PHASE;
    # measured on this clip it moved the autocorrelation peak from 0.43 to 0.40
    # and the leg still ticked. What is actually wrong with an interpolated
    # bounce is that its PERIOD is constant, so the warp has to be a RATE:
    # integrate a slowly varying speed, and the same eleven-frame cycle comes
    # out as eight frames here and fourteen there. Renormalising the map to the
    # original length keeps the clip exactly as long as its own audio.
    rate = 1.0 + band_noise(n, fps, 0.20, 0.95, rng) * 0.34 * args.warp
    rate = np.clip(rate, 0.45, 1.7)
    tmap = np.cumsum(rate)
    tmap = (tmap - tmap[0]) / (tmap[-1] - tmap[0]) * (n - 1)
    src_idx = np.clip(np.round(tmap), 0, n - 1).astype(int)
    tw = tmap - np.arange(n)

    # HEADROOM. The crop must never see past the edge of the plate, and the
    # amount of plate the shake eats is not just the translation: rotation and
    # shear reach into the corners too. So map the four output corners back
    # through the real transform for every frame and, if any of them lands off
    # the plate, push the zoom until none of them does. Eyeballing this is how
    # a one-frame black wedge gets shipped.
    def worst_margin(zm):
        lo_x = lo_y = 1e9
        hi_x = hi_y = -1e9
        for i in range(n):
            sc = (OUT / sw) * zm[i]
            th = math.radians(rot[i])
            a = sc * math.cos(th); b = -sc * math.sin(th) + shear[i] * sc
            c = sc * math.sin(th); d = sc * math.cos(th)
            det = a * d - b * c
            ia, ib, ic, idd = d / det, -b / det, -c / det, a / det
            cx, cy = OUT / 2 + px[i], OUT / 2 + py[i]
            ox = sw / 2 - (ia * cx + ib * cy)
            oy = sh / 2 - (ic * cx + idd * cy)
            for X, Y in ((0, 0), (OUT, 0), (0, OUT), (OUT, OUT)):
                sx = ia * X + ib * Y + ox
                sy = ic * X + idd * Y + oy
                lo_x = min(lo_x, sx); hi_x = max(hi_x, sx)
                lo_y = min(lo_y, sy); hi_y = max(hi_y, sy)
        return min(lo_x, lo_y, sw - hi_x, sh - hi_y)

    for _ in range(8):
        if worst_margin(zoom) >= 1.0:
            break
        zoom = zoom * 1.02
    print(f"  zoom {zoom.mean():.4f}  plate margin {worst_margin(zoom):.1f}px", flush=True)

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    silent = out_path.with_suffix(".silent.mp4")
    wr = imageio_ffmpeg.write_frames(
        str(silent), (OUT, OUT), fps=fps, codec="libx264", quality=None,
        macro_block_size=1, ffmpeg_log_level="error",
        output_params=["-crf", "17", "-preset", "slow", "-pix_fmt", "yuv420p",
                       "-profile:v", "high"])
    wr.send(None)

    grain_rng = np.random.default_rng(args.seed + 100)
    for i in range(n):
        # temporal: a whole source frame, held or skipped. Never a blend.
        im = Image.fromarray(src[src_idx[i]])

        # spatial: one resample does scale, rotation, shear and translation, so
        # the frame is never softened twice
        s = (OUT / sw) * zoom[i]
        th = math.radians(rot[i])
        a = s * math.cos(th); b = -s * math.sin(th) + shear[i] * s
        c = s * math.sin(th); d = s * math.cos(th)
        cx, cy = OUT / 2 + px[i], OUT / 2 + py[i]
        det = a * d - b * c
        ia, ib = d / det, -b / det
        ic, idd = -c / det, a / det
        ox = sw / 2 - (ia * cx + ib * cy)
        oy = sh / 2 - (ic * cx + idd * cy)
        im = im.transform((OUT, OUT), Image.AFFINE, (ia, ib, ox, ic, idd, oy),
                          resample=Image.BICUBIC)

        # A 480px plate blown up to 1080 is softer than any lens would be, and
        # softness is itself a tell. Put a little of the edge back BEFORE the
        # grain, so the grain stays grain instead of being sharpened into
        # speckle.
        if args.sharp > 0:
            im = im.filter(ImageFilter.UnsharpMask(radius=2.0,
                                                   percent=int(args.sharp * 100),
                                                   threshold=2))

        arr = np.asarray(im).astype(np.float32)
        # a live camera is never exposure-locked to the pixel, and the plate is
        # monochrome, so the grain is monochrome too
        arr *= 1.0 + 0.006 * math.sin(i / fps * 2 * math.pi * 0.37) + 0.004 * breath[i]
        g = grain_rng.standard_normal((OUT, OUT, 1)).astype(np.float32) * (1.6 + 1.8 * S)
        arr = np.clip(arr + g, 0, 255)
        wr.send(np.ascontiguousarray(arr.astype(np.uint8)))
    wr.close()

    print(f"  shake px  x {np.abs(px).max():.1f}  y {np.abs(py).max():.1f}  "
          f"rot {np.abs(rot).max():.2f}deg  retime +/-{np.abs(tw).max():.2f}f", flush=True)

    # keep whatever audio came in; the retime is zero-mean so it stays in sync
    has_audio = subprocess.run(
        [ff, "-hide_banner", "-i", args.src], capture_output=True, text=True
    ).stderr.count("Audio:") > 0
    if has_audio:
        subprocess.run([ff, "-y", "-v", "error", "-i", str(silent), "-i", args.src,
                        "-map", "0:v", "-map", "1:a", "-c:v", "copy",
                        "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart",
                        "-shortest", str(out_path)], check=True)
        silent.unlink()
    else:
        silent.rename(out_path)
    print(f"  -> {out_path}")


if __name__ == "__main__":
    main()
