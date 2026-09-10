#!/usr/bin/env python3
"""
Eight seconds built from the flag photographs. One shot, no cuts.

The idea is a single reversal. In a film the camera holds and the world moves;
here the WORLD holds and the camera moves — and then, three times, time runs
for a quarter of a second and the flag actually changes shape before freezing
again. A photograph that keeps remembering it was film.

That gives the piece its shape without a single transition in it. There is
nothing to dissolve, wipe or cut, because it never stops being the same image:
the camera starts inside the lit fabric, where you cannot tell what you are
looking at, and spends eight seconds pulling back until you can see it is a
kid carrying it down a beach. The reveal is the edit.

Three things make it hold together, and all three were measured, not guessed:

  THE BURSTS ARE STABILISED.  The source camera cranes about ten pixels a
  frame. Left alone, every burst would kick — the flag would come alive and
  the horizon would jump with it, which reads as a glitch, not as life. The
  vertical drift is measured by phase correlation on a strip of sky and sea
  that contains neither the flag nor the runner, fitted to a smooth curve
  (a crane does not move in steps), and subtracted by moving the camera
  window with it. What is left over IS the subject: fabric and legs.

  THE GRAIN MOVES AND THE PICTURE DOES NOT.  Grain belongs to the print, not
  to the negative, so it is applied per output frame at output resolution.
  Bake it into the plate instead and it freezes — sixteen distinct grain
  fields across 192 frames reads unmistakably as dirt on the lens.

  THE HOLDS SHORTEN AND THE BURSTS LENGTHEN.  1.75s, 1.83s, 1.58s of stillness
  against 5, 6 and 7 frames of motion. The film wakes up a little more each
  time and settles a little less, and then the last hold is the longest of all
  so it can go back to being a photograph and stay there.

    python3 tools/flagfilm.py IN.mp4 --out flag-8s.mp4
"""
import argparse
import math
import os
import subprocess
import sys
import wave
from pathlib import Path

import imageio_ffmpeg
import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from humanise import band_noise                                    # noqa: E402
from still import blur, film_finish, grade, lum, to_linear, to_srgb  # noqa: E402

FPS = 24
DUR = 8.0
N = int(round(DUR * FPS))          # 192
OUT = 1080
SR = 48000

# hold, then burst — in output frames, with the source frame each runs from.
# 42+5 + 44+6 + 38+7 + 50 = 192
PLAN = [("hold", 42, 104), ("burst", 5, 104),
        ("hold", 44, 108), ("burst", 6, 108),
        ("hold", 38, 113), ("burst", 7, 113),
        ("hold", 50, 119)]

# the camera: starts inside the lit fabric, ends on the whole picture
CAM_A = dict(cx=2060, cy=880, size=1520)
CAM_B = dict(cx=1660, cy=1180, size=2150)

# the strip used to measure the crane. It has to contain no flag and no runner,
# or the correlation locks onto the thing that is supposed to be moving.
BG = (slice(200, 2300, 2), slice(0, 700, 2))


def timeline():
    """(output frame -> source frame) and the burst envelope."""
    src = np.zeros(N, int)
    burst = np.zeros(N)
    f = 0
    for kind, n, s0 in PLAN:
        for i in range(n):
            src[f] = s0 + (i + 1 if kind == "burst" else 0)
            burst[f] = 1.0 if kind == "burst" else 0.0
            f += 1
    assert f == N, f
    return src, burst


def phase_shift(a, b):
    """Vertical/horizontal offset that puts b onto a."""
    A = np.fft.rfft2(a - a.mean()); B = np.fft.rfft2(b - b.mean())
    R = A * np.conj(B); R /= np.abs(R) + 1e-9
    c = np.fft.irfft2(R, a.shape)
    p = np.unravel_index(np.argmax(c), c.shape)
    dy = p[0] - a.shape[0] if p[0] > a.shape[0] // 2 else p[0]
    dx = p[1] - a.shape[1] if p[1] > a.shape[1] // 2 else p[1]
    return dy * 2, dx * 2


def eased(n, rise=0.14, fall=0.18):
    """
    0 -> 1 with soft ends and a constant middle.

    A plain ease-in-out over eight seconds makes the midpoint travel nearly
    twice the average speed, which on a move this slow is visible as a surge.
    Ramping the VELOCITY and integrating it keeps the middle honest.
    """
    t = np.linspace(0, 1, n)
    v = np.ones(n)
    a = t / rise
    v = np.where(t < rise, a * a * (3 - 2 * a), v)
    b = (1 - t) / fall
    v = np.where(t > 1 - fall, np.minimum(v, b * b * (3 - 2 * b)), v)
    c = np.cumsum(v)
    return (c - c[0]) / (c[-1] - c[0])


def k_weight(x):
    """
    BS.1770 K-weighting, in the frequency domain: a high-pass around 38Hz and
    a +4dB shelf above 1.7kHz. It is the difference between how loud a signal
    IS and how loud it SOUNDS, and for a surf bed that difference is enormous.
    """
    f = np.fft.rfftfreq(len(x), 1 / SR)
    hp = 1 / np.sqrt(1 + (38.0 / np.maximum(f, 1e-6)) ** 4)
    shelf = 1 + (10 ** (4 / 20) - 1) * (f ** 2 / (f ** 2 + 1681.0 ** 2))
    return np.fft.irfft(np.fft.rfft(x) * hp * shelf, len(x))


def lufs(stereo):
    z = sum(np.mean(k_weight(stereo[:, c]) ** 2) for c in range(stereo.shape[1]))
    return -0.691 + 10 * math.log10(max(z, 1e-12))


def soundbed(cuts, target=-15.0, seed=5):
    """
    Surf, wind, and the fabric. Synthesised, because the film should carry its
    own sound rather than borrow a track — and because a cue that comes from
    the same numbers as the picture cannot drift off it.

    Balanced toward the FOAM rather than the swell. The first version was
    mostly low-passed brown noise, which is what surf looks like on a meter
    and nothing like what it sounds like: it measured -19 dBFS RMS and -39
    LUFS, because K-weighting discounts everything under 200Hz — and a phone
    speaker does worse than discount it, it cannot produce it at all. The
    hiss of breaking foam, up around 1-5kHz, is the part that actually
    carries. Normalising to LUFS instead of RMS is what forced the issue.
    """
    n = int(DUR * SR)
    rng = np.random.default_rng(seed)
    t = np.arange(n) / SR

    def lp(x, hz):
        f = np.fft.rfftfreq(len(x), 1 / SR)
        return np.fft.irfft(np.fft.rfft(x) / (1 + (f / hz) ** 2), len(x))

    def bp(x, lo, hi):
        f = np.fft.rfftfreq(len(x), 1 / SR)
        g = 1 / (1 + (np.maximum(f, 1e-6) / hi) ** 3)
        g *= 1 - 1 / (1 + (np.maximum(f, 1e-6) / lo) ** 3)
        return np.fft.irfft(np.fft.rfft(x) * g, len(x))

    out = np.zeros((n, 2))
    for ch in range(2):
        # surf: brown noise, with wave sets arriving on their own slow clock
        brown = np.cumsum(rng.standard_normal(n)); brown /= np.abs(brown).max()
        sets = (0.55 + 0.45 * np.sin(2 * np.pi * 0.17 * t + ch * 1.1)
                * np.sin(2 * np.pi * 0.071 * t + 2.0))
        out[:, ch] += lp(brown, 900) * sets * 0.55            # the swell
        out[:, ch] += bp(rng.standard_normal(n), 1100, 6000) * sets * 0.60   # the foam
        # wind, sitting between the two so it fills rather than competes
        out[:, ch] += bp(rng.standard_normal(n), 260, 1400) * (
            0.32 + 0.18 * np.sin(2 * np.pi * 0.13 * t + ch * 2.3)) * 0.30

    # THE FABRIC. One soft snap where the flag comes alive, so the ear is told
    # the same thing the eye is. Placed on the burst's first frame exactly —
    # a sound this soft that arrives even 60ms late reads as a separate event.
    for k, (at, hard) in enumerate(cuts):
        i = int(at * SR)
        d = int(0.34 * SR)
        env = np.exp(-np.linspace(0, 7.0, d)) * (1 - np.exp(-np.linspace(0, 40, d)))
        snap = bp(rng.standard_normal(d), 420 + 120 * k, 2600 + 500 * k) * env
        j = min(n, i + d)
        out[i:j, 0] += snap[:j - i] * 0.42 * hard
        out[i:j, 1] += snap[:j - i] * 0.38 * hard

    # match the picture's fades, or the sound announces the cut to black
    fi, fo = int(0.7 * SR), int(0.6 * SR)
    out[:fi] *= np.linspace(0, 1, fi)[:, None] ** 1.6
    out[-fo:] *= np.linspace(1, 0, fo)[:, None] ** 1.6

    # drive, then normalise to LOUDNESS, then check the peak — in that order
    out = np.tanh(out * 1.3) * 0.98
    out *= 10 ** ((target - lufs(out)) / 20)
    peak = np.abs(out).max()
    if peak > 0.89:
        out = np.tanh(out * (0.89 / peak) * 1.06) * 0.89
    print(f"  sound  {lufs(out):.1f} LUFS, peak {20 * math.log10(peak):.1f} dBFS",
          flush=True)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("--out", default="tools/outputs/flag-8s.mp4")
    ap.add_argument("--silent", action="store_true", help="picture only")
    ap.add_argument("--sound-only", action="store_true",
                    help="rebuild the track and remux it onto the existing picture")
    args = ap.parse_args()

    if args.sound_only:
        remux(Path(args.out)); return

    src_of, burst = timeline()
    need = sorted(set(src_of.tolist()))
    print(f"  {N} frames at {FPS}fps = {N / FPS:.2f}s, {len(need)} source frames "
          f"({need[0]}..{need[-1]})", flush=True)

    # ------------------------------------------------------- read and measure
    g = imageio_ffmpeg.read_frames(args.src)
    info = g.__next__()
    w, h = info["size"]
    raw = {}
    lo, hi = need[0], need[-1]
    for i, f in enumerate(g):
        if lo <= i <= hi:
            raw[i] = np.frombuffer(f, np.uint8).reshape(h, w, 3).copy()
        if i > hi:
            break

    ref = raw[lo][BG].mean(2).astype(np.float32)
    meas = np.array([phase_shift(ref, raw[k][BG].mean(2).astype(np.float32))[0]
                     for k in range(lo, hi + 1)], float)
    # A crane accelerates smoothly; the raw measurement is quantised to two
    # pixels and occasionally latches a frame late, which would put a visible
    # kick on the first frame of a burst. Fit the motion instead of trusting
    # each sample of it.
    ks = np.arange(lo, hi + 1)
    dy = np.polyval(np.polyfit(ks, meas, 3), ks)
    print(f"  crane fit  residual {np.abs(dy - meas).mean():.1f}px, "
          f"total {dy[-1] - dy[0]:.0f}px over {hi - lo} frames", flush=True)
    dy_of = {k: float(dy[k - lo]) for k in ks}

    # ---------------------------------------------------------------- grade
    # Once per distinct source frame: the grade is a property of the picture,
    # and the camera then moves around inside the result.
    plates = {}
    for j, k in enumerate(need):
        plates[k] = (grade(raw.pop(k), vig=0.10) * 255).astype(np.uint8)
        print(f"    graded {k}  ({j + 1}/{len(need)})", flush=True)
    raw.clear()

    # ---------------------------------------------------------------- camera
    u = eased(N)
    cx = CAM_A["cx"] + (CAM_B["cx"] - CAM_A["cx"]) * u
    cy = CAM_A["cy"] + (CAM_B["cy"] - CAM_A["cy"]) * u
    sz = CAM_A["size"] + (CAM_B["size"] - CAM_A["size"]) * u
    # gate weave: a projector never holds perfectly still, and its absence is
    # part of why a digital move over a still reads as a slideshow
    rng = np.random.default_rng(3)
    cx = cx + band_noise(N, FPS, 0.35, 2.2, rng) * 2.4
    cy = cy + band_noise(N, FPS, 0.35, 2.2, rng) * 2.4
    flick = 1.0 + band_noise(N, FPS, 0.15, 1.2, rng) * 0.012

    fade = np.ones(N)
    fi, fo = int(0.7 * FPS), int(0.6 * FPS)
    fade[:fi] = np.linspace(0, 1, fi) ** 1.6      # in linear the glow arrives first
    fade[-fo:] = np.linspace(1, 0, fo) ** 1.6

    yy, xx = np.mgrid[0:OUT, 0:OUT].astype(np.float32)
    vr = np.sqrt((xx / OUT - 0.5) ** 2 + (yy / OUT - 0.5) ** 2)
    vig = (1.0 - 0.30 * np.clip(vr / 0.72, 0, 1) ** 2.2)[..., None]
    # the burst glow, smeared a few frames either side so the light swells into
    # the motion rather than snapping on with it
    bw = np.convolve(burst, np.hanning(13) / np.hanning(13).sum(), mode="same")
    bw /= max(bw.max(), 1e-6)

    out_path = Path(args.out); out_path.parent.mkdir(parents=True, exist_ok=True)
    silent = out_path.with_suffix(".silent.mp4")
    wr = imageio_ffmpeg.write_frames(
        str(silent), (OUT, OUT), fps=FPS, codec="libx264", quality=None,
        macro_block_size=1, ffmpeg_log_level="error",
        output_params=["-crf", "16", "-preset", "slow", "-pix_fmt", "yuv420p",
                       "-profile:v", "high"])
    wr.send(None)

    for f in range(N):
        k = int(src_of[f])
        s = sz[f]
        x0 = int(round(cx[f] - s / 2))
        y0 = int(round(cy[f] - s / 2 - dy_of[k]))   # subtract the crane
        x0 = max(0, min(w - int(s), x0))
        y0 = max(0, min(h - int(s), y0))
        win = plates[k][y0:y0 + int(s), x0:x0 + int(s)]
        img = np.asarray(Image.fromarray(win).resize((OUT, OUT), Image.LANCZOS),
                         dtype=np.float32) / 255.0

        lin = to_linear(img) * vig
        if bw[f] > 0.01:
            # the light wakes with the fabric
            L = lum(lin)
            hot = np.clip((L - 0.35) / 0.65, 0, None) ** 1.5
            lin += (blur(hot, 26) * 0.6 + blur(hot, 90) * 0.5)[..., None] \
                * np.array([1.00, 0.42, 0.20], np.float32) * (0.18 * bw[f])
        lin *= flick[f] * fade[f]

        out = film_finish(np.clip(to_srgb(lin), 0, 1).astype(np.float32),
                          seed=1000 + f)
        wr.send(np.ascontiguousarray(np.asarray(out)))
        if f % 32 == 0:
            print(f"    frame {f}/{N}", flush=True)
    wr.close()

    if args.silent:
        silent.rename(out_path)
        print(f"  -> {out_path}"); return

    remux(out_path, silent)


def cue_times():
    """The sound's cues are read off the same PLAN the picture is cut from,
    so a click cannot drift off the frame it belongs to."""
    cuts, f = [], 0
    for kind, n, _ in PLAN:
        if kind == "burst":
            cuts.append((f / FPS, 0.7 + 0.15 * len(cuts)))
        f += n
    return cuts


def remux(out_path, picture=None):
    """Lay a freshly built track onto the picture without re-rendering it."""
    ff = imageio_ffmpeg.get_ffmpeg_exe()
    cuts = cue_times()
    print(f"  cues at {[round(c[0], 2) for c in cuts]}", flush=True)
    wav = out_path.with_suffix(".wav")
    st = (soundbed(cuts) * 32767).astype("<i2")
    with wave.open(str(wav), "wb") as ww:
        ww.setnchannels(2); ww.setsampwidth(2); ww.setframerate(SR)
        ww.writeframes(st.tobytes())

    src_v = picture or out_path
    tmp = out_path.with_suffix(".remux.mp4")
    subprocess.run([ff, "-y", "-v", "error", "-i", str(src_v), "-i", str(wav),
                    "-map", "0:v", "-map", "1:a", "-c:v", "copy",
                    "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart",
                    "-shortest", str(tmp)], check=True)
    tmp.replace(out_path)
    if picture is not None:
        picture.unlink()
    info = subprocess.run([ff, "-hide_banner", "-i", str(out_path)],
                          capture_output=True, text=True).stderr
    print("  " + [l.strip() for l in info.splitlines() if "Duration" in l][0])
    print(f"  -> {out_path}")


if __name__ == "__main__":
    main()
