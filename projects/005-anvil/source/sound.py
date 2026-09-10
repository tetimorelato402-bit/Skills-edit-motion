#!/usr/bin/env python3
"""
The Anvil soundtrack, synthesised.

No sample pack. Everything here is generated, for three reasons: the licence
question disappears, the file is 40 lines instead of 40 megabytes, and — the
one that actually matters — every cue time is computed from `deck.py`, the
same module the picture cuts from. A click cannot drift off its transition
because the click and the transition are the same number read twice.

The kit is the brand taken literally. An anvil is a struck lump of metal, so
the downbeat is inharmonic metal: partials at irrational ratios, a hard
transient, a long ring. Everything else stays out of its way.

  strike  the anvil, on the downbeat of every bar
  kick    beats 1 and 3, a short pitch drop
  tick    THE PAGE CLICK, on the exact frame of every screen cut
  thunk   the heavier version, on a section card
  hat     eighths, quiet, only once the thing is moving
  sub     one low note per section

    python3 source/sound.py --out outputs/anvil.wav
"""
import argparse
import math
import wave
from pathlib import Path

import numpy as np

from deck import BAR, BEAT, DURATION, SECTION_ROOT, sequence

SR = 48000


def env(n, attack, decay, curve=2.4):
    """A percussive envelope: near-instant attack, exponential tail."""
    a = max(1, int(attack * SR))
    e = np.empty(n, dtype=np.float64)
    e[:a] = np.linspace(0.0, 1.0, a) ** 0.5
    t = np.arange(n - a) / SR
    e[a:] = np.exp(-t / max(1e-4, decay) * curve)
    return e


def strike(dur=1.25, gain=1.0):
    """
    Struck metal. A bar of steel is INHARMONIC — its partials are not whole
    multiples of a fundamental, which is exactly why it reads as metal and not
    as a note. Ratios below are irrational on purpose; make them 2, 3, 4 and
    it turns into a church bell, then into a synth pad.
    """
    n = int(dur * SR)
    t = np.arange(n) / SR
    out = np.zeros(n)
    for ratio, amp, dec in ((1.00, 1.00, 0.52), (2.76, 0.62, 0.34),
                            (5.40, 0.38, 0.22), (8.93, 0.24, 0.15),
                            (13.34, 0.14, 0.10), (18.60, 0.08, 0.07)):
        f = 320.0 * ratio
        out += amp * np.sin(2 * np.pi * f * t + ratio) * np.exp(-t / dec * 2.6)
    # the hammer itself: a click of noise before the ring
    rng = np.random.default_rng(7)
    hit = rng.standard_normal(n) * np.exp(-t / 0.004 * 3.0)
    out = out * 0.30 + hit * 0.55
    return out * gain


def kick(dur=0.42, gain=1.0):
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = 46 + 96 * np.exp(-t / 0.028)          # a drop, not a boom
    ph = 2 * np.pi * np.cumsum(f) / SR
    body = np.sin(ph) * env(n, 0.0008, 0.20, 3.2)
    rng = np.random.default_rng(3)
    click = rng.standard_normal(n) * np.exp(-t / 0.003 * 3.0) * 0.25
    return (body * 0.95 + click) * gain


def tick(dur=0.05, gain=1.0, tone=3400.0):
    """
    THE PAGE CLICK. Short, dry and high — a keyboard tick, not a snare. It has
    to be small: it fires 22 times and anything with a tail would turn the
    whole track into a stutter.
    """
    n = int(dur * SR)
    t = np.arange(n) / SR
    rng = np.random.default_rng(11)
    noise = rng.standard_normal(n)
    # a cheap resonant band: ring a sine with the noise as its exciter
    band = np.sin(2 * np.pi * tone * t) * noise * np.exp(-t / 0.006 * 3.0)
    body = np.sin(2 * np.pi * (tone * 0.55) * t) * np.exp(-t / 0.010 * 3.0)
    return (band * 0.7 + body * 0.5) * env(n, 0.0004, 0.014, 3.0) * gain


def thunk(dur=0.30, gain=1.0):
    """The section-card version of the click: lower, woodier, more weight.
    A bigger change in the picture gets a bigger sound — causality."""
    n = int(dur * SR)
    t = np.arange(n) / SR
    rng = np.random.default_rng(19)
    noise = rng.standard_normal(n) * np.exp(-t / 0.012 * 3.0)
    wood = np.sin(2 * np.pi * 232 * t) * np.exp(-t / 0.055 * 2.6)
    low = np.sin(2 * np.pi * 88 * t) * np.exp(-t / 0.11 * 2.4)
    return (noise * 0.30 + wood * 0.55 + low * 0.75) * gain


def hat(dur=0.06, gain=1.0):
    n = int(dur * SR)
    t = np.arange(n) / SR
    rng = np.random.default_rng(23)
    x = rng.standard_normal(n)
    x = x - np.convolve(x, np.ones(9) / 9, mode="same")     # crude high-pass
    return x * np.exp(-t / 0.011 * 3.0) * gain


def sub(freq, dur, gain=1.0):
    n = int(dur * SR)
    t = np.arange(n) / SR
    a = np.minimum(1.0, t / 0.35) * np.minimum(1.0, (dur - t) / 0.5)
    return (np.sin(2 * np.pi * freq * t) * 0.82
            + np.sin(2 * np.pi * freq * 2 * t) * 0.14) * a * gain


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="outputs/anvil.wav")
    args = ap.parse_args()

    total = int((DURATION + 1.6) * SR)
    buf = np.zeros(total)

    def put(sig, at, gain=1.0):
        i = int(at * SR)
        j = min(total, i + len(sig))
        if i < total:
            buf[i:j] += sig[:j - i] * gain

    seq = sequence()
    strike_s, kick_s, hat_s, tick_s, thunk_s = strike(), kick(), hat(), tick(), thunk()

    # one long sub per section, so seven sections move harmonically without
    # anything ever sounding like a chord change
    run_start, run_sec = 0.0, seq[0][2]
    for i, (kind, sid, sec) in enumerate(seq + [(None, None, -1)]):
        if sec != run_sec:
            put(sub(SECTION_ROOT[run_sec % len(SECTION_ROOT)],
                    i * BAR - run_start + 0.5, 0.20), run_start)
            run_start, run_sec = i * BAR, sec

    for i, (kind, sid, sec) in enumerate(seq):
        t0 = i * BAR
        # THE CUT. This is the frame the picture changes on, so this is the
        # frame the click is on. Cards get the heavy one.
        if kind == "card":
            put(thunk_s, t0, 0.80)
            put(strike_s, t0, 0.62)
        else:
            put(tick_s, t0, 0.62)
            put(strike_s, t0, 0.40)

        put(kick_s, t0, 0.85)
        put(kick_s, t0 + 2 * BEAT, 0.62)
        # the backbeat only arrives once the deck is moving, so bar 1 is bare
        if i >= 1:
            put(tick_s, t0 + 1 * BEAT, 0.16)
            put(tick_s, t0 + 3 * BEAT, 0.20)
        if i >= 2:
            for k in range(8):
                if k % 2:                                  # offbeat eighths only
                    put(hat_s, t0 + k * BEAT / 2, 0.10 if k != 7 else 0.16)
        # a small fill into every section card
        if i + 1 < len(seq) and seq[i + 1][0] == "card":
            for k, g in ((3.0, 0.18), (3.5, 0.24), (3.75, 0.30)):
                put(tick_s, t0 + k * BEAT, g)

    # DRIVE, THEN NORMALISE, THEN CHECK THE PEAK — in that order. Setting the
    # RMS first and peak-limiting afterwards just undoes the level: a struck
    # anvil has a huge crest factor, so the peak trim pulled the whole track
    # down 5dB and it landed at -20 dBFS, which is inaudible under a Reel.
    # Driving the limiter harder first squashes the transients instead.
    buf = np.tanh(buf * 1.45) * 0.98
    rms = np.sqrt(np.mean(buf ** 2))
    buf *= (10 ** (-16.0 / 20)) / max(rms, 1e-9)
    peak = np.max(np.abs(buf))
    if peak > 0.94:
        buf = np.tanh(buf * (0.94 / peak) * 1.06) * 0.94
    print(f"  rms {20 * math.log10(np.sqrt(np.mean(buf ** 2))):.1f} dBFS, "
          f"peak {20 * math.log10(np.max(np.abs(buf))):.1f} dBFS")

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    st = (np.stack([buf, buf], 1) * 32767).astype("<i2")
    with wave.open(str(out), "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes(st.tobytes())
    print(f"  {len(buf) / SR:.2f}s -> {out}")


if __name__ == "__main__":
    main()
