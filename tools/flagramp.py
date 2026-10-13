#!/usr/bin/env python3
"""
Thirty-five seconds of the banner, on one accelerating ramp of time.

The 8s version froze time and let it off the leash three times, which is a
stutter by design. This one is the opposite and has no stutter in it at all:
time runs CONTINUOUSLY from the first frame to the last, starting at about
ninety times slow and ending near real speed. Nothing is held, nothing is cut,
nothing repeats — the whole piece is one exponential ramp.

That only works with real frame interpolation, and the choice was tested
rather than assumed. Naive cross-fading between two source frames doubles the
stars in the canton at the halfway point — you can count two sets of dots.
Farneback optical flow, warped from both sides and blended, keeps them as
single dots, because it moves the pixels instead of averaging them. Stripes
and stars are the aperture problem's favourite subject, so this was the one
thing worth proving before spending the render.

Two curves run against each other, and that is the whole design:

  TIME accelerates    r(u) = A e^(4u), from ~0.011 to ~0.57 source frames per
                      output frame. Early on the flag barely breathes.
  CAMERA decelerates  it drifts across the fabric while time is nearly stopped,
                      and settles as time speeds up.

Run them the same way and the piece is dead for fifteen seconds and frantic
for the last five. Run them against each other and the total motion on screen
stays roughly constant while its SOURCE migrates from the camera to the
subject — which is the only reason a 90x slow-motion opening is watchable.

The camera is defined relative to the FLAG, not to the plate: the banner's
centroid is tracked across all 121 frames (it wanders about 600px, and the
source camera cranes underneath it) and heavily low-passed, so the window
follows the flag's drift without inheriting its flutter. That is what keeps
"mostly the banner waving" true by construction rather than by luck.

    python3 tools/flagramp.py IN.mp4 --out flag-35s.mp4
"""
import argparse
import hashlib
import json
import math
import os
import shutil
import subprocess
import sys
import wave
from pathlib import Path

import cv2
import imageio_ffmpeg
import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from humanise import band_noise                                  # noqa: E402
from still import blur, film_finish, grade, lum, to_linear, to_srgb  # noqa: E402

# ---------------------------------------------------------------- the grid
# 88 BPM is REPORTED, not measured — it comes from the usual BPM databases for
# Lana Del Rey's "God Bless America - And All The Beautiful Women In It", not
# from the audio, which this container has never seen. Everything downstream
# reads it from here, so correcting it is one number and one re-run of the
# click track (a remux, not a render).
BPM = 88.0
BEAT = 60.0 / BPM                 # 0.6818s
BAR = 4 * BEAT                    # 2.7273s
BARS = 13                         # 35.46s — the whole number of bars nearest 35
FPS = 24
N = int(round(BARS * BAR * FPS))  # 851
W_OUT, H_OUT = 1440, 1080         # 4:3

SONG_IN = 54.0                    # the piece's frame 0 sits at this point in the song

# time: source frames consumed per output frame, r(u) = A e^(K u)
K_RAMP = 4.0
# camera: tight on the fabric, then the pull-back, which starts on a downbeat
PULL_BAR = 10
W_TIGHT, W_MID, W_WIDE = 1500, 1850, 3320
FLOW_SCALE = 4                    # flow is smooth; computing it at 1/4 costs nothing


def flag_track(path, n_src):
    """
    Where the banner is, frame by frame. It is the only warm bright thing in a
    blue night frame, which makes it separable with two thresholds and no
    model at all.
    """
    g = imageio_ffmpeg.read_frames(path)
    info = g.__next__()
    w, h = info["size"]
    out = []
    for f in g:
        a = np.frombuffer(f, np.uint8).reshape(h, w, 3)[::4, ::4].astype(np.float32)
        m = (a.mean(2) > 55) & ((a[..., 0] - a[..., 2]) > 12)
        ys, xs = np.nonzero(m)
        out.append((xs.mean() * 4, ys.mean() * 4) if len(xs) else out[-1])
    return np.array(out[:n_src]), w, h


def smooth(x, win):
    """Low-pass by reflection, so the ends do not sag toward zero."""
    k = np.hanning(win); k /= k.sum()
    pad = win // 2
    return np.convolve(np.r_[x[pad:0:-1], x, x[-2:-pad - 2:-1]], k, mode="same")[pad:pad + len(x)]


def ease(u, p):
    return 1.0 - (1.0 - u) ** p


class Plates:
    """
    The graded plates, cached on disk.

    Grading is the expensive half (about 17s a frame at 3326x2494) and it is
    identical for every re-cut, so it is paid once and kept. The cache carries
    a SIGNATURE of the grade settings: resume-by-counting cannot tell "already
    graded" from "graded under different settings", and a stale plate is a
    perfectly valid JPEG of a plausible picture that nothing will ever flag.
    """

    def __init__(self, src, n_src, cache, sig, nograde=False):
        self.nograde = nograde
        self.src, self.n = src, n_src
        self.dir = Path(cache)
        stamp = self.dir / "signature.json"
        if self.dir.exists():
            old = json.loads(stamp.read_text()) if stamp.exists() else None
            if old != sig:
                print("  cache signature changed — wiping", flush=True)
                shutil.rmtree(self.dir)
        self.dir.mkdir(parents=True, exist_ok=True)
        stamp.write_text(json.dumps(sig, indent=1))
        self._mem, self._flow = {}, {}

    def build(self):
        missing = [k for k in range(self.n) if not (self.dir / f"f{k:03d}.jpg").exists()]
        if not missing:
            print(f"  {self.n} graded plates already cached", flush=True)
            return
        print(f"  {'caching raw' if self.nograde else 'grading'} {len(missing)} plates "
              f"(~{len(missing) * (0.3 if self.nograde else 17) / 60:.0f} min)", flush=True)
        g = imageio_ffmpeg.read_frames(self.src)
        info = g.__next__(); w, h = info["size"]
        for k, f in enumerate(g):
            if k >= self.n:
                break
            if k not in missing:
                continue
            plate = np.frombuffer(f, np.uint8).reshape(h, w, 3)
            img = plate if self.nograde else (grade(plate, vig=0.10) * 255).astype(np.uint8)
            Image.fromarray(img).save(self.dir / f"f{k:03d}.jpg", quality=94, subsampling=0)
            print(f"    graded {k}/{self.n}", flush=True)

    def get(self, k):
        k = int(np.clip(k, 0, self.n - 1))
        if k not in self._mem:
            if len(self._mem) > 3:
                self._mem.pop(next(iter(self._mem)))
            self._mem[k] = np.asarray(Image.open(self.dir / f"f{k:03d}.jpg").convert("RGB"))
        return self._mem[k]

    def flow(self, k):
        """Forward and backward flow across the pair (k, k+1), computed lazily.

        The ramp only ever moves forward, so a one-pair cache is all it needs:
        early on a single pair serves ninety output frames, and late on it
        serves one.
        """
        if k not in self._flow:
            self._flow.clear()
            a, b = self.get(k), self.get(k + 1)
            s = FLOW_SCALE
            ga = cv2.cvtColor(cv2.resize(a, (a.shape[1] // s, a.shape[0] // s)), cv2.COLOR_RGB2GRAY)
            gb = cv2.cvtColor(cv2.resize(b, (b.shape[1] // s, b.shape[0] // s)), cv2.COLOR_RGB2GRAY)
            kw = dict(pyr_scale=0.5, levels=5, winsize=31, iterations=5,
                      poly_n=7, poly_sigma=1.5, flags=cv2.OPTFLOW_FARNEBACK_GAUSSIAN)
            f1 = cv2.calcOpticalFlowFarneback(ga, gb, None, **kw)
            f2 = cv2.calcOpticalFlowFarneback(gb, ga, None, **kw)
            hw = (a.shape[1], a.shape[0])
            self._flow[k] = (cv2.resize(f1, hw) * s, cv2.resize(f2, hw) * s)
        return self._flow[k]


def sample(plates, t, box, margin=240):
    """
    The picture at fractional source time t, cropped to box=(x0,y0,w,h).

    Only the box plus a margin is warped. The margin has to exceed the largest
    flow vector (measured at 176px here) or the remap reaches outside what was
    cropped and smears the edge.
    """
    i = int(np.clip(np.floor(t), 0, plates.n - 2))
    a = float(np.clip(t - i, 0.0, 1.0))
    A = plates.get(i)
    if a < 0.004:
        x0, y0, bw, bh = box
        return A[y0:y0 + bh, x0:x0 + bw].astype(np.float32)
    B = plates.get(i + 1)
    F1, F2 = plates.flow(i)
    H, W = A.shape[:2]
    x0, y0, bw, bh = box
    sx0, sy0 = max(0, x0 - margin), max(0, y0 - margin)
    sx1, sy1 = min(W, x0 + bw + margin), min(H, y0 + bh + margin)
    sub = (slice(sy0, sy1), slice(sx0, sx1))
    hh, ww = sy1 - sy0, sx1 - sx0
    xx, yy = np.meshgrid(np.arange(ww, dtype=np.float32), np.arange(hh, dtype=np.float32))

    def warp(img, fl, amt):
        return cv2.remap(img[sub].astype(np.float32),
                         (xx + fl[sub][..., 0] * amt).astype(np.float32),
                         (yy + fl[sub][..., 1] * amt).astype(np.float32),
                         cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)

    # EACH FRAME IS WARPED WITH THE OPPOSITE FLOW, and the sign matters more
    # than it looks. To build the pixel that sits at x at time a, A must be
    # sampled where that pixel WAS (x + a*F_BA) and B where it WILL BE
    # (x + (1-a)*F_AB). Pair each frame with its own forward flow instead and
    # the two halves land 2d apart: every star in the canton comes out as two
    # dots, which at thumbnail size looks like a slightly soft frame and at
    # full size is unusable.
    both = warp(A, F2, a) * (1 - a) + warp(B, F1, 1 - a) * a
    return both[y0 - sy0:y0 - sy0 + bh, x0 - sx0:x0 - sx0 + bw]


def clicks(path):
    """
    A quiet tick on every beat, whose only job is alignment — the same trick
    004 uses. Slide the song until its beat sits on the tick, then mute this.
    It is not music and is not meant to survive into the edit.
    """
    sr = 48000
    n = int(N / FPS * sr)
    buf = np.zeros(n)
    d = int(0.02 * sr)
    env = np.exp(-np.linspace(0, 9, d))
    rng = np.random.default_rng(1)
    tick = (np.sin(2 * np.pi * 2600 * np.arange(d) / sr) * 0.6
            + rng.standard_normal(d) * 0.25) * env
    down = (np.sin(2 * np.pi * 1300 * np.arange(d) / sr) * 0.8
            + rng.standard_normal(d) * 0.2) * env
    b = 0
    while b * BEAT * sr < n:
        i = int(b * BEAT * sr)
        sig = down if b % 4 == 0 else tick
        j = min(n, i + d)
        buf[i:j] += sig[:j - i] * (0.5 if b % 4 == 0 else 0.26)
        b += 1
    st = (np.stack([buf, buf], 1) * 32767 * 0.6).astype("<i2")
    with wave.open(str(path), "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(sr)
        w.writeframes(st.tobytes())
    return b


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("--out", default="tools/outputs/flag-35s.mp4")
    ap.add_argument("--cache", default="tools/cache/flagplates")
    ap.add_argument("--nograde", action="store_true",
                    help="skip the colour work — check camera and timing cheaply first")
    ap.add_argument("--preview", type=int, default=0,
                    help="render only every Nth frame, to check the design cheaply")
    args = ap.parse_args()

    track, w, h = flag_track(args.src, 10 ** 9)
    n_src = len(track)
    print(f"  source {n_src} frames {w}x{h}   out {N} frames = {N / FPS:.2f}s "
          f"= {BARS} bars at {BPM:g} BPM", flush=True)

    sig = dict(grade="raw" if args.nograde else "vig0.10-exp0.45-white4.5-hal0.70",
               n=n_src, w=w, h=h)
    plates = Plates(args.src, n_src, args.cache, sig, args.nograde)
    plates.build()

    # ------------------------------------------------------------- the ramp
    u = np.arange(N) / (N - 1)
    r = np.exp(K_RAMP * u)
    tmap = np.concatenate([[0.0], np.cumsum(r)[:-1]])
    tmap = tmap / tmap[-1] * (n_src - 1)          # spans the clip exactly, by construction
    rate = np.diff(np.r_[tmap, tmap[-1]])
    print(f"  time  {1 / max(rate[0], 1e-9):.0f}x slow -> {1 / rate[-2]:.1f}x slow", flush=True)

    # ------------------------------------------------------------ the camera
    fx = smooth(track[:, 0], 41)
    fy = smooth(track[:, 1], 41)
    cx = np.interp(tmap, np.arange(n_src), fx)
    cy = np.interp(tmap, np.arange(n_src), fy)

    pull = int(round(PULL_BAR * BAR * FPS))
    ww = np.empty(N)
    ua = np.clip(np.arange(N) / pull, 0, 1)
    ww[:pull] = W_TIGHT + (W_MID - W_TIGHT) * ease(ua[:pull], 1.6)
    ub = (np.arange(pull, N) - pull) / (N - pull)
    ww[pull:] = W_MID + (W_WIDE - W_MID) * (ub * ub * (3 - 2 * ub))

    # while time is nearly stopped the camera carries the motion, so it drifts
    # across the fabric; as time speeds up the drift is already spent
    dr = ease(ua, 1.7)
    cx = cx + (-260 + 560 * dr)
    cy = cy + (-190 + 420 * dr)
    # and as it pulls out, hand the framing back to the plate
    hand = np.zeros(N); hand[pull:] = ub * ub * (3 - 2 * ub)
    cx = cx * (1 - hand) + (w / 2) * hand
    cy = cy * (1 - hand) + (h / 2) * hand

    rng = np.random.default_rng(7)
    cx = cx + band_noise(N, FPS, 0.3, 2.0, rng) * 2.6      # gate weave
    cy = cy + band_noise(N, FPS, 0.3, 2.0, rng) * 2.6
    flick = 1.0 + band_noise(N, FPS, 0.15, 1.2, rng) * 0.010

    fade = np.ones(N)
    fi = int(0.8 * FPS)
    fade[:fi] = np.linspace(0, 1, fi) ** 1.6   # no fade-out: every last frame stays choppable

    yy, xx = np.mgrid[0:H_OUT, 0:W_OUT].astype(np.float32)
    vr = np.sqrt((xx / W_OUT - 0.5) ** 2 + ((yy / H_OUT - 0.5) * 0.75) ** 2)
    vig = (1.0 - 0.28 * np.clip(vr / 0.55, 0, 1) ** 2.2)[..., None]

    out_path = Path(args.out); out_path.parent.mkdir(parents=True, exist_ok=True)
    silent = out_path.with_suffix(".silent.mp4")
    step = max(1, args.preview)
    wr = imageio_ffmpeg.write_frames(
        str(silent), (W_OUT, H_OUT), fps=FPS / step, codec="libx264", quality=None,
        macro_block_size=1, ffmpeg_log_level="error",
        output_params=["-crf", "16", "-preset", "slow", "-pix_fmt", "yuv420p",
                       "-profile:v", "high"])
    wr.send(None)

    for f in range(0, N, step):
        bw = int(round(ww[f])); bh = int(round(bw * H_OUT / W_OUT))
        bw = min(bw, w); bh = min(bh, h)
        x0 = int(round(cx[f] - bw / 2)); y0 = int(round(cy[f] - bh / 2))
        x0 = max(0, min(w - bw, x0)); y0 = max(0, min(h - bh, y0))

        win = sample(plates, tmap[f], (x0, y0, bw, bh))
        img = np.asarray(Image.fromarray(np.clip(win, 0, 255).astype(np.uint8))
                         .resize((W_OUT, H_OUT), Image.LANCZOS), dtype=np.float32) / 255.0

        lin = to_linear(img) * vig * (flick[f] * fade[f])
        out = film_finish(np.clip(to_srgb(lin), 0, 1).astype(np.float32), seed=2000 + f)
        wr.send(np.ascontiguousarray(np.asarray(out)))
        if f % 40 == 0:
            print(f"    frame {f}/{N}  src {tmap[f]:6.2f}  win {bw}", flush=True)
    wr.close()

    ff = imageio_ffmpeg.get_ffmpeg_exe()
    wav = out_path.with_suffix(".wav")
    nb = clicks(wav)
    print(f"  {nb} beats of click track at {BPM:g} BPM", flush=True)
    subprocess.run([ff, "-y", "-v", "error", "-i", str(silent), "-i", str(wav),
                    "-map", "0:v", "-map", "1:a", "-c:v", "copy",
                    "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart",
                    "-shortest", str(out_path)], check=True)
    silent.unlink()
    info = subprocess.run([ff, "-hide_banner", "-i", str(out_path)],
                          capture_output=True, text=True).stderr
    print("  " + [l.strip() for l in info.splitlines() if "Duration" in l][0])
    print(f"  song lines up at {SONG_IN:g}s; the piece runs to {SONG_IN + N / FPS:.2f}s of it")
    print(f"  -> {out_path}")


if __name__ == "__main__":
    main()
