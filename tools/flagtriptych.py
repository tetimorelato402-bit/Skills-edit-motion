#!/usr/bin/env python3
"""
Three angles of one run, on a single ramp of time. Eleven bars, hard cuts.

The three clips are the same action from three distances — inside the fabric,
the runner in full from the reverse side, and the bird's eye — so the film is
built as a scale progression: TEXTURE, then FIGURE, then LANDSCAPE. One
continuous acceleration runs underneath all three, the way flagramp.py does,
and the movements themselves shorten (4 bars, 4 bars, 3 bars) so the film
speeds up twice over: once inside each movement and once across them. Eleven
bars is 30.00s exactly at 88 BPM.

THE CUTS ARE CUTS. An earlier version dissolved through a pixel grid, and the
grid is the wrong instrument here for a simple reason: no film has ever
pixelated between two shots, so it reads as an artifact rather than as an
edit. What makes a hard cut feel like cinema is not a device laid over it —
it is that the eye does not have to go looking for the subject again. So the
incoming shot is nudged so the banner arrives roughly where the outgoing
banner was, and that nudge eases away over one bar, after which the shot is
framed entirely on its own terms. Position is matched, never size: the three
shots are a scale progression and the flag shrinking across each cut is the
whole point. The only thing laid over a cut is LIGHT — the halation swells
for a few frames as the new shot lands, so the join is carried by the lamp
behind the fabric, which is the one thing all three shots actually share.

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
from still import blur, film_finish, grade, to_linear, to_srgb        # noqa: E402

BPM = 88.0                        # reported, not measured — see flagramp.py
BEAT = 60.0 / BPM
BAR = 4 * BEAT
BARS = 11                         # 30.00s exactly at 88 BPM
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
MOVES = [("A", 4, (92, 120), 2.0, (1500, 1980)),
         ("B", 4, (8, 118), 1.1, (566, 638)),
         ("C", 3, (1, 123), 0.5, (600, 638))]

# How long the incoming shot keeps its match offset before easing back to its
# own framing: one bar. Longer and the cut stops being a cut and becomes a move.
MATCH_BARS = 1.0
MATCH_CAP = 0.10          # never displace the frame more than a tenth of it


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
        out.append((xs.mean() * step, ys.mean() * step, len(xs) / L.size)
                   if len(xs) > 8 else (out[-1] if out else (w / 2, h / 2, 0.0)))
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
        tracks[tag] = (smooth(tr[:, 0], 41), smooth(tr[:, 1], 41), tr[:, 2])
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
        fx, fy, _ = tracks[tag]
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

    def flag_screen(mi, f):
        """Where the banner sits in the OUTPUT frame, 0..1, for movement mi."""
        tag, t, cx, cy, ww = move_state(mi, f)
        W, H = CLIPS[tag]["w"], CLIPS[tag]["h"]
        bw = min(int(round(ww)), W); bh = min(int(round(bw * H_OUT / W_OUT)), H)
        x0 = max(0, min(W - bw, int(round(cx - bw / 2))))
        y0 = max(0, min(H - bh, int(round(cy - bh / 2))))
        fx, fy, _ = tracks[tag]
        gx = float(np.interp(t, np.arange(len(fx)), fx))
        gy = float(np.interp(t, np.arange(len(fy)), fy))
        return (gx - x0) / bw, (gy - y0) / bh

    # A CUT IS CINEMA; A PIXEL GRID IS AN ARTIFACT. What makes a hard cut read
    # as an edit rather than a jolt is that the eye does not have to go looking
    # for the subject again: the thing it was watching is still roughly where
    # it left it. So the incoming shot is nudged so the banner lands where the
    # outgoing banner was, and that offset eases away over one bar — after
    # which the shot is framed entirely on its own terms. Matching POSITION
    # only, never size: the three shots are a scale progression and shrinking
    # the flag across each cut is the whole point.
    match = {}
    for ci, c in enumerate(cuts):
        ox, oy = flag_screen(ci, c - 1)
        ix, iy = flag_screen(ci + 1, c)
        match[ci + 1] = (float(np.clip(ox - ix, -MATCH_CAP, MATCH_CAP)),
                         float(np.clip(oy - iy, -MATCH_CAP, MATCH_CAP)))
        print(f"  cut {ci + 1} @ {c}: banner {ox:.2f},{oy:.2f} -> {ix:.2f},{iy:.2f}"
              f"   match nudge {match[ci + 1][0]:+.3f},{match[ci + 1][1]:+.3f}", flush=True)

    match_len = MATCH_BARS * BAR * FPS

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
        mx = my = 0.0
        if mi in match:
            e = np.clip((f - bounds[mi][0]) / match_len, 0, 1)
            k = (1 - e) ** 2                       # strongest on the cut frame, gone by bar 2
            mx, my = match[mi][0] * bw * k, match[mi][1] * bh * k
        x0 = int(round(cx - bw / 2 - mx + wob_x[f]))
        y0 = int(round(cy - bh / 2 - my + wob_y[f]))
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

    # GRAIN RAMPS ACROSS A CUT, it does not switch. C needs more of it than the
    # other two (it is the contoured plate, and grain is the only thing that
    # touched those contours), but changing the amount on the cut frame reads
    # as a change of film stock — the one thing that would give away that these
    # are three different sources rather than three angles of one night.
    gseq = np.full(N, 1.15)
    for i, (a_, b_) in enumerate(bounds):
        gseq[a_:b_] = 1.75 if MOVES[i][0] == "C" else 1.15
    k = np.hanning(25); k /= k.sum()
    gseq = np.convolve(np.r_[np.full(12, gseq[0]), gseq, np.full(12, gseq[-1])],
                       k, mode="same")[12:12 + N]

    # A film cuts. What it is allowed on top of a cut is LIGHT: the halation
    # swells for a few frames as the new shot arrives, so the join is carried
    # by the one thing all three shots share — the lamp behind the fabric —
    # rather than by an effect laid over them. Two frames before, eight after,
    # because a bloom that fades into the incoming shot reads as the cut
    # breathing, while one that fades into the outgoing reads as a mistake.
    cutw = np.zeros(N)
    for c in cuts:
        for f in range(max(0, c - 2), min(N, c + 9)):
            u = (f - (c - 2)) / 10.0
            cutw[f] = max(cutw[f], math.sin(math.pi * min(max(u, 0), 1)) ** 1.3)

    f0 = max(0, args.f0)
    f1 = min(N, args.f1) if args.f1 else N
    for f in range(f0, f1, step):
        mi = next(i for i, (a_, b_) in enumerate(bounds) if a_ <= f < b_)
        img = render_side(mi, f)
        tag = move_state(mi, f)[0]

        lin = to_linear(img) * vig
        if cutw[f] > 0.01:
            L = lin @ np.array([0.2126, 0.7152, 0.0722], np.float32)
            hot = np.clip((L - 0.34) / 0.66, 0, None) ** 1.5
            lin += (blur(hot, 22) * 0.6 + blur(hot, 80) * 0.5)[..., None] \
                * np.array([1.00, 0.44, 0.22], np.float32) * (0.16 * cutw[f])
        lin *= flick[f] * fade[f]

        out = film_finish(np.clip(to_srgb(lin), 0, 1).astype(np.float32),
                          seed=3000 + f, grain=float(gseq[f]))
        wr.send(np.ascontiguousarray(np.asarray(out)))
        if f % 40 == 0:
            print(f"    {f}/{N}  {tag}  src {move_state(mi, f)[1]:6.2f}", flush=True)
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
