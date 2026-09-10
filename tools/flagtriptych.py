#!/usr/bin/env python3
"""
Three angles of one run, on a single ramp of time. Twelve bars, no dissolves.

The three clips are the same action from three distances — inside the fabric,
the runner in full from the reverse side, and the bird's eye — so the film is
built as a scale progression: TEXTURE, then FIGURE, then LANDSCAPE. One
continuous acceleration runs underneath all three, the way flagramp.py does,
and the movements themselves shorten (5 bars, 4 bars, 3 bars) so the film
speeds up twice over: once inside each movement and once across them.

The order is not a taste call. Only clip A is 3326x2494; B and C are 640x480.
The opening is nearly frozen and magnified, which is the one place softness
cannot hide, so the big plate has to go first and the small ones have to land
where motion covers for them. The scale progression falls out of that for free.

MATCHING THE THREE IS THE WHOLE JOB, and "the same treatment" cannot mean the
same numbers. Graded identically, C lands at median 9 against A's 22 — it is
two and a half stops darker — and B's highlights clip at 254 where A's stop at
234. Two matching rules were tried and both are wrong:

  match the frame MEDIAN   forces C's empty sand up to A's midtone, and C's
                           median is empty sand where A's is flag and sea. It
                           is what drags the compression contours in the dark
                           into plain view.
  match the FLAG           needs +5.9 stops, because C's banner is twenty
                           pixels wide. It floods everything to median 72.

An aerial at night IS a darker shot, so it is graded darker on purpose and
matched by eye at the one thing the three share: the banner reads as the same
light in all three. C's contours are in the SOURCE — h264 posterising a dark
gradient, not 8-bit quantisation, which is why neither dither nor a threshold
deband touches them — so they are handled the way film handles them, with
grain, and by giving C the shortest movement.

    python3 tools/flagtriptych.py --out flag-tri.mp4
"""
import argparse
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
from humanise import band_noise                                       # noqa: E402
from still import film_finish, grade, to_linear, to_srgb              # noqa: E402

BPM = 88.0                        # reported, not measured — see flagramp.py
BEAT = 60.0 / BPM
BAR = 4 * BEAT
BARS = 12                         # 32.73s, inside teti's 30-35s
FPS = 24
N = int(round(BARS * BAR * FPS))  # 785
W_OUT, H_OUT = 1440, 1080
SONG_IN = 54.0

U = "/root/.claude/uploads/a12bd814-6ca7-558a-a53e-296125050f1e"
CLIPS = {
    # A keeps dither at 0 so the 121 plates already on disk stay valid; it is
    # a well-exposed plate and has nothing to deband.
    "A": dict(path=f"{U}/4abea13e-openart02178900621786400000000000000000000ffff"
                   f"c0a87ff3727d14_1789006539501_e50cccaf.mp4",
              cache="tools/cache/flagplates",
              sig="vig0.10-exp0.45-white4.5-hal0.70",
              g=dict(exposure=0.45, white=4.5, vig=0.10, dither=0.0)),
    "B": dict(path=f"{U}/9d70a468-openart9QXIe1b7vvfb6_rrIbauK_minimaxh3_"
                   f"1789010561229_6e473597.mp4",
              cache="tools/cache/plates_B", sig="B-exp0.85-white6.0",
              g=dict(exposure=0.85, white=6.0, vig=0.10, dither=1.2)),
    "C": dict(path=f"{U}/c1c0bb04-openart9XMJDEm0LHDFWXKoFWwR_minimaxh3_"
                   f"1789010678715_78f5b978.mp4",
              cache="tools/cache/plates_C", sig="C-exp1.75-white3.0",
              g=dict(exposure=1.75, white=3.0, vig=0.10, dither=1.2)),
}

# clip, bars, source range, ramp exponent, window width start/end (plate px)
MOVES = [("A", 5, (100, 113), 2.2, (1500, 1900)),
         ("B", 4, (15, 93), 1.2, (566, 638)),
         ("C", 3, (2, 122), 0.6, (600, 638))]

# (centre frame, frames before, frames after). The second is deliberately
# lopsided: C comes OUT of the grid slowly, which is what hides its contours
# through the moment the cut most exposes them.
GRID_MAX = 58


def bars_to_frames(b):
    return int(round(b * BAR * FPS))


class Plates:
    """Graded plates on disk, keyed by a signature of the grade settings.

    Resume-by-counting cannot tell "already graded" from "graded under other
    settings", and a stale plate is a valid JPEG of a plausible picture that
    nothing would ever flag.
    """

    def __init__(self, tag, spec, n_src):
        self.tag, self.path, self.n = tag, spec["path"], n_src
        self.g = spec["g"]
        self.dir = Path(spec["cache"])
        want = dict(grade=spec["sig"], n=n_src, w=spec["w"], h=spec["h"])
        stamp = self.dir / "signature.json"
        if self.dir.exists():
            have = json.loads(stamp.read_text()) if stamp.exists() else None
            if have != want:
                print(f"  {tag}: cache signature changed — wiping", flush=True)
                shutil.rmtree(self.dir)
        self.dir.mkdir(parents=True, exist_ok=True)
        stamp.write_text(json.dumps(want, indent=1))
        self._mem, self._flow = {}, {}
        self.scale = max(1, int(round(spec["w"] / 800)))   # flow at ~800px wide

    def build(self):
        miss = [k for k in range(self.n) if not (self.dir / f"f{k:03d}.jpg").exists()]
        if not miss:
            print(f"  {self.tag}: {self.n} plates cached", flush=True)
            return
        print(f"  {self.tag}: grading {len(miss)} plates", flush=True)
        g = imageio_ffmpeg.read_frames(self.path)
        info = g.__next__(); w, h = info["size"]
        for k, f in enumerate(g):
            if k >= self.n:
                break
            if k in miss:
                p = np.frombuffer(f, np.uint8).reshape(h, w, 3)
                img = (grade(p, seed=k, **self.g) * 255).astype(np.uint8)
                Image.fromarray(img).save(self.dir / f"f{k:03d}.jpg",
                                          quality=94, subsampling=0)
                if k % 20 == 0:
                    print(f"    {self.tag} {k}/{self.n}", flush=True)

    def get(self, k):
        k = int(np.clip(k, 0, self.n - 1))
        if k not in self._mem:
            if len(self._mem) > 3:
                self._mem.pop(next(iter(self._mem)))
            self._mem[k] = np.asarray(Image.open(self.dir / f"f{k:03d}.jpg").convert("RGB"))
        return self._mem[k]

    def flow(self, k):
        if k not in self._flow:
            self._flow.clear()
            a, b = self.get(k), self.get(k + 1)
            s = self.scale
            sz = (a.shape[1] // s, a.shape[0] // s)
            ga = cv2.cvtColor(cv2.resize(a, sz), cv2.COLOR_RGB2GRAY)
            gb = cv2.cvtColor(cv2.resize(b, sz), cv2.COLOR_RGB2GRAY)
            kw = dict(pyr_scale=0.5, levels=5, winsize=31, iterations=5,
                      poly_n=7, poly_sigma=1.5, flags=cv2.OPTFLOW_FARNEBACK_GAUSSIAN)
            hw = (a.shape[1], a.shape[0])
            self._flow[k] = (cv2.resize(cv2.calcOpticalFlowFarneback(ga, gb, None, **kw), hw) * s,
                             cv2.resize(cv2.calcOpticalFlowFarneback(gb, ga, None, **kw), hw) * s)
        return self._flow[k]


def sample(pl, t, box, margin=None):
    """The picture at fractional source time t, cropped to box=(x0,y0,w,h).

    Each frame is warped with the OPPOSITE flow: to build the pixel sitting at
    x at time a, A is sampled where it was and B where it is going. Pair each
    frame with its own forward flow instead and the halves land 2d apart, and
    every star in the canton comes out as two dots.
    """
    i = int(np.clip(math.floor(t), 0, pl.n - 2))
    a = float(np.clip(t - i, 0.0, 1.0))
    A = pl.get(i)
    x0, y0, bw, bh = box
    if a < 0.004:
        return A[y0:y0 + bh, x0:x0 + bw].astype(np.float32)
    B = pl.get(i + 1)
    F1, F2 = pl.flow(i)
    H, W = A.shape[:2]
    m = margin if margin is not None else max(48, int(0.075 * W))
    sx0, sy0 = max(0, x0 - m), max(0, y0 - m)
    sx1, sy1 = min(W, x0 + bw + m), min(H, y0 + bh + m)
    sub = (slice(sy0, sy1), slice(sx0, sx1))
    hh, ww = sy1 - sy0, sx1 - sx0
    xx, yy = np.meshgrid(np.arange(ww, dtype=np.float32), np.arange(hh, dtype=np.float32))

    def warp(img, fl, amt):
        return cv2.remap(img[sub].astype(np.float32),
                         (xx + fl[sub][..., 0] * amt).astype(np.float32),
                         (yy + fl[sub][..., 1] * amt).astype(np.float32),
                         cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)

    both = warp(A, F2, a) * (1 - a) + warp(B, F1, 1 - a) * a
    return both[y0 - sy0:y0 - sy0 + bh, x0 - sx0:x0 - sx0 + bw]


def gridify(img, cell):
    """Average into square cells and hold them — 003's grammar, and here it
    also does a job: it is the one treatment that absorbs C's contouring
    instead of fighting it."""
    if cell < 1.6:
        return img
    h, w = img.shape[:2]
    nx, ny = max(1, int(round(w / cell))), max(1, int(round(h / cell)))
    small = cv2.resize(img, (nx, ny), interpolation=cv2.INTER_AREA)
    return cv2.resize(small, (w, h), interpolation=cv2.INTER_NEAREST)


def flag_track(path, n):
    """Where the banner is. Thresholds are PERCENTILE-based, not absolute:
    the three plates differ by two and a half stops, so a fixed cut that finds
    the flag in A finds nothing at all in C."""
    g = imageio_ffmpeg.read_frames(path)
    info = g.__next__(); w, h = info["size"]
    step = max(1, w // 400)
    out = []
    for k, f in enumerate(g):
        if k >= n:
            break
        a = np.frombuffer(f, np.uint8).reshape(h, w, 3)[::step, ::step].astype(np.float32)
        L = a.mean(2)
        m = (L > np.percentile(L, 99.0)) & ((a[..., 0] - a[..., 2]) > 6)
        ys, xs = np.nonzero(m)
        out.append((xs.mean() * step, ys.mean() * step) if len(xs) > 8
                   else (out[-1] if out else (w / 2, h / 2)))
    return np.array(out), w, h


def smooth(x, win):
    k = np.hanning(win); k /= k.sum()
    pad = win // 2
    return np.convolve(np.r_[x[pad:0:-1], x, x[-2:-pad - 2:-1]], k, mode="same")[pad:pad + len(x)]


def clicks(path, n_frames):
    """A quiet tick per beat for alignment only — 004's trick. Slide the song
    onto the ticks, then mute this."""
    sr = 48000
    n = int(n_frames / FPS * sr)
    buf = np.zeros(n)
    d = int(0.02 * sr)
    env = np.exp(-np.linspace(0, 9, d))
    rng = np.random.default_rng(1)
    hi = (np.sin(2 * np.pi * 2600 * np.arange(d) / sr) * .6 + rng.standard_normal(d) * .25) * env
    lo = (np.sin(2 * np.pi * 1300 * np.arange(d) / sr) * .8 + rng.standard_normal(d) * .2) * env
    b = 0
    while b * BEAT * sr < n:
        i = int(b * BEAT * sr); j = min(n, i + d)
        buf[i:j] += (lo if b % 4 == 0 else hi)[:j - i] * (0.5 if b % 4 == 0 else 0.26)
        b += 1
    st = (np.stack([buf, buf], 1) * 32767 * 0.6).astype("<i2")
    with wave.open(str(path), "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(sr)
        w.writeframes(st.tobytes())
    return b


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="tools/outputs/flag-tri.mp4")
    ap.add_argument("--preview", type=int, default=0)
    ap.add_argument("--from", dest="f0", type=int, default=0)
    ap.add_argument("--to", dest="f1", type=int, default=0)
    args = ap.parse_args()

    # ------------------------------------------------------------- prepare
    plates, tracks = {}, {}
    for tag, spec in CLIPS.items():
        tr, w, h = flag_track(spec["path"], 10 ** 9)
        spec["w"], spec["h"] = w, h
        tracks[tag] = (smooth(tr[:, 0], 41), smooth(tr[:, 1], 41))
        plates[tag] = Plates(tag, spec, len(tr))
        plates[tag].build()
        print(f"  {tag}: {len(tr)} frames {w}x{h}", flush=True)

    # -------------------------------------------------------- the timeline
    bounds, acc = [], 0
    for tag, bars, srng, k, wr in MOVES:
        bounds.append((acc, acc + bars_to_frames(bars)))
        acc += bars_to_frames(bars)
    bounds[-1] = (bounds[-1][0], N)

    def move_state(mi, f):
        """tmap / camera for movement mi at GLOBAL frame f, valid a little
        outside its own span — the incoming shot has to exist before its bar
        or the transition uncovers nothing."""
        tag, bars, (s0, s1), k, (w0, w1) = MOVES[mi]
        a, b = bounds[mi]
        u = (f - a) / max(1, b - a)                       # may go <0 or >1
        sh = (math.exp(k * min(max(u, -0.2), 1.2)) - 1) / (math.exp(k) - 1)
        t = s0 + (s1 - s0) * sh
        t = float(np.clip(t, 0, plates[tag].n - 1.001))
        uu = float(np.clip(u, 0, 1))
        ww = w0 + (w1 - w0) * (uu * uu * (3 - 2 * uu))
        fx, fy = tracks[tag]
        W, H = CLIPS[tag]["w"], CLIPS[tag]["h"]
        if tag == "A":
            cx = float(np.interp(t, np.arange(len(fx)), fx)) + (-240 + 520 * uu)
            cy = float(np.interp(t, np.arange(len(fy)), fy)) + (-170 + 380 * uu)
        else:
            # B and C are 640x480: there is no room to reframe without
            # magnifying an already-soft plate, so the window stays near the
            # full frame and only breathes.
            cx, cy = W / 2, H / 2
        return tag, t, cx, cy, ww

    cuts = [bounds[1][0], bounds[2][0]]
    trans = [(cuts[0], 8, 8), (cuts[1], 12, 30)]

    rng = np.random.default_rng(11)
    wob_x = band_noise(N, FPS, 0.3, 2.0, rng) * 2.4
    wob_y = band_noise(N, FPS, 0.3, 2.0, rng) * 2.4
    flick = 1.0 + band_noise(N, FPS, 0.15, 1.2, rng) * 0.010
    fade = np.ones(N)
    fi = int(0.8 * FPS)
    fade[:fi] = np.linspace(0, 1, fi) ** 1.6

    yy, xx = np.mgrid[0:H_OUT, 0:W_OUT].astype(np.float32)
    vr = np.sqrt((xx / W_OUT - 0.5) ** 2 + ((yy / H_OUT - 0.5) * 0.75) ** 2)
    vig = (1.0 - 0.28 * np.clip(vr / 0.55, 0, 1) ** 2.2)[..., None]

    def render_side(mi, f):
        tag, t, cx, cy, ww = move_state(mi, f)
        W, H = CLIPS[tag]["w"], CLIPS[tag]["h"]
        bw = int(min(round(ww), W)); bh = int(min(round(bw * H_OUT / W_OUT), H))
        x0 = int(round(cx - bw / 2 + wob_x[f])); y0 = int(round(cy - bh / 2 + wob_y[f]))
        x0 = max(0, min(W - bw, x0)); y0 = max(0, min(H - bh, y0))
        win = sample(plates[tag], t, (x0, y0, bw, bh))
        return np.asarray(Image.fromarray(np.clip(win, 0, 255).astype(np.uint8))
                          .resize((W_OUT, H_OUT), Image.LANCZOS), dtype=np.float32) / 255.0

    out_path = Path(args.out); out_path.parent.mkdir(parents=True, exist_ok=True)
    silent = out_path.with_suffix(".silent.mp4")
    step = max(1, args.preview)
    wr = imageio_ffmpeg.write_frames(
        str(silent), (W_OUT, H_OUT), fps=FPS / step, codec="libx264", quality=None,
        macro_block_size=1, ffmpeg_log_level="error",
        output_params=["-crf", "16", "-preset", "slow", "-pix_fmt", "yuv420p",
                       "-profile:v", "high"])
    wr.send(None)

    def grain_for(tag):
        # C is the contoured plate; grain is what film has always used on a
        # banded gradient, and it is the only thing that touched these.
        return 1.9 if tag == "C" else 1.25

    f0 = max(0, args.f0)
    f1 = min(N, args.f1) if args.f1 else N
    for f in range(f0, f1, step):
        act = next(((ti, c, pre, post) for ti, (c, pre, post) in enumerate(trans)
                    if c - pre <= f <= c + post), None)
        if act is None:
            mi = next(i for i, (a, b) in enumerate(bounds) if a <= f < b)
            img = render_side(mi, f)
            cell = 1.0
            tag = move_state(mi, f)[0]
        else:
            # transition ti sits BETWEEN movement ti and movement ti+1, and
            # both sides are rendered for every frame of it: the outgoing shot
            # has to stay alive past its own bar or the grid uncovers nothing.
            ti, c, pre, post = act
            p = (f - (c - pre)) / float(pre + post)
            cell = 1 + (GRID_MAX - 1) * math.sin(math.pi * min(max(p, 0.0), 1.0)) ** 1.15
            # the crossfade happens where the cells are largest, so the change
            # of shot is hidden inside the blockiness — you see the picture
            # break up and rebuild as something else, never a dissolve
            mix = float(np.clip((f - c) / 2.0 + 0.5, 0, 1))
            img = (gridify(render_side(ti, f), cell) * (1 - mix)
                   + gridify(render_side(ti + 1, f), cell) * mix)
            tag = move_state(ti + (1 if mix >= 0.5 else 0), f)[0]

        lin = to_linear(img) * vig * (flick[f] * fade[f])
        out = film_finish(np.clip(to_srgb(lin), 0, 1).astype(np.float32),
                          seed=3000 + f, grain=grain_for(tag))
        wr.send(np.ascontiguousarray(np.asarray(out)))
        if f % 40 == 0:
            print(f"    {f}/{N}  {tag}  cell {cell:.0f}", flush=True)
    wr.close()

    ff = imageio_ffmpeg.get_ffmpeg_exe()
    wav = out_path.with_suffix(".wav")
    nb = clicks(wav, N)
    print(f"  {nb} beats at {BPM:g} BPM", flush=True)
    subprocess.run([ff, "-y", "-v", "error", "-i", str(silent), "-i", str(wav),
                    "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac",
                    "-b:a", "160k", "-movflags", "+faststart", "-shortest",
                    str(out_path)], check=True)
    silent.unlink()
    info = subprocess.run([ff, "-hide_banner", "-i", str(out_path)],
                          capture_output=True, text=True).stderr
    print("  " + [l.strip() for l in info.splitlines() if "Duration" in l][0])
    print(f"  song lines up at {SONG_IN:g}s -> runs to {SONG_IN + N / FPS:.2f}s")
    print(f"  -> {out_path}")


if __name__ == "__main__":
    main()
