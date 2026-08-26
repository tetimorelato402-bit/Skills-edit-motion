#!/usr/bin/env python3
"""
ANVIL — the UI sound library, synthesised.

Every sound here is built to one rule: warm, organic, tactile. Felt, wood,
leather, low breath. Nothing bright, plastic or synthetic — if it could
belong to a fintech app it is wrong.

In practice that means: no content above ~4 kHz worth speaking of, attacks
measured in milliseconds rather than samples (a zero-length attack is what
makes a click sound digital), inharmonic partials rather than clean integer
ratios, a noise component in everything, and a touch of pitch drift so no
two playbacks of the same body sound mechanically identical.
"""
import os, sys, wave
import numpy as np

SR = 44100
rng = np.random.default_rng(11)          # deterministic library


# ---------------------------------------------------------------- helpers

def t(n):
    return np.arange(int(n * SR)) / SR


def env(x, attack, decay, curve=2.5):
    """Soft attack, exponential-ish decay. The attack is what keeps it warm."""
    n = len(x)
    a = max(int(attack * SR), 2)
    e = np.ones(n)
    e[:a] = np.sin(np.linspace(0, np.pi / 2, a)) ** 1.4
    d = np.exp(-curve * np.linspace(0, 1, n) * (len(x) / SR) / max(decay, 1e-4))
    return x * e * d


def lp(x, cutoff, order=2):
    """One-pole lowpass, cascaded. Blunt, which is the point."""
    a = np.exp(-2 * np.pi * cutoff / SR)
    y = x.copy()
    for _ in range(order):
        out = np.empty_like(y)
        z = 0.0
        for i in range(len(y)):
            z = (1 - a) * y[i] + a * z
            out[i] = z
        y = out
    return y


def hp(x, cutoff):
    return x - lp(x, cutoff, 1)


def noise(n):
    return rng.standard_normal(int(n * SR))


def wood(dur, f0, damp=28, detune=(1.0, 2.71, 4.19, 6.83)):
    """A struck body: inharmonic partials, heavily damped. Reads as wood."""
    x = np.zeros(int(dur * SR))
    tt = t(dur)
    for i, r in enumerate(detune):
        f = f0 * r * (1 + rng.normal(0, 0.004))
        x += (0.9 ** i) * np.sin(2 * np.pi * f * tt) * np.exp(-damp * (1 + i * 0.7) * tt)
    return x


def norm(x, peak=0.9):
    m = np.abs(x).max()
    return x * (peak / m) if m > 0 else x


def write(name, x, peak=0.9):
    x = norm(np.asarray(x, dtype=np.float64), peak)
    # a 3 ms tail ramp so nothing ends on a discontinuity
    k = int(0.003 * SR)
    x[-k:] *= np.linspace(1, 0, k)
    path = os.path.join("audio/sfx", f"{name}.wav")
    with wave.open(path, "wb") as w:
        w.setnchannels(1); w.setsampwidth(3); w.setframerate(SR)
        w.writeframes((np.clip(x, -1, 1) * (2 ** 23 - 1)).astype("<i4")
                      .view("<u1").reshape(-1, 4)[:, :3].tobytes())
    print(f"  {name:<16} {len(x)/SR:5.3f}s")


# ------------------------------------------------------------- the library

def ui_tap():
    """Felt. A fingertip on a soft surface — body, no click."""
    d = 0.13
    body = wood(d, 240, damp=40, detune=(1.0, 2.4, 3.9))
    thud = np.sin(2 * np.pi * 104 * t(d)) * np.exp(-40 * t(d))
    # the felt itself lives in the low mids; without it the tap is a thump
    # that disappears entirely on a phone speaker
    felt = lp(hp(noise(d), 300), 1500) * np.exp(-58 * t(d))
    return env(body * 0.55 + thud * 0.4 + felt * 0.55, 0.004, 0.05)


def key():
    """A light mechanical key. Wood and felt, not plastic."""
    d = 0.07
    click = lp(noise(d), 2600) * np.exp(-150 * t(d))
    body = wood(d, 420, damp=95, detune=(1.0, 2.9, 5.1))
    return env(click * 0.5 + body * 0.5, 0.0015, 0.02)


def whoosh(direction):
    """
    Low airy travel. Pitched to the direction of the move: a downward move
    sweeps its band down, a forward move sweeps up. Air, never a synth sweep.
    """
    d = 0.42
    tt = t(d)
    n = lp(noise(d), 4000)
    # band centre travels; lowpass cascade does the shaping
    lo, hi = (1500, 420) if direction == "down" else (420, 1600)
    cut = lo + (hi - lo) * (tt / d) ** 0.7
    out = np.zeros_like(n)
    a = np.exp(-2 * np.pi * cut / SR)
    z = 0.0
    for i in range(len(n)):
        z = (1 - a[i]) * n[i] + a[i] * z
        out[i] = z
    swell = np.sin(np.pi * (tt / d) ** 0.8) ** 1.6
    return hp(out * swell, 90) * 0.9


def lock_catch():
    """
    A soft mechanical catch. The sound of something being HELD closed —
    a damped wooden knock with a dry, short leather creak under it.
    Deliberately not metallic: metal would make the lock feel like a machine,
    and the lock in this film is a promise.
    """
    d = 0.22
    knock = wood(d, 186, damp=32, detune=(1.0, 2.62, 4.4))
    creak = lp(hp(noise(d), 240), 1250) * np.exp(-24 * t(d)) * (0.5 + 0.5 * np.sin(2 * np.pi * 31 * t(d)))
    seat = np.sin(2 * np.pi * 88 * t(d)) * np.exp(-32 * t(d))
    return env(knock * 0.6 + creak * 0.5 + seat * 0.34, 0.005, 0.07)


def unlock():
    """
    The biggest sound in the film, and the only one that gets room to breathe.
    Three overlapping movements: the catch giving way, a low warm swell, then
    air. It should land like an exhale — the release of something that has
    been held, not the arrival of something new.
    """
    d = 1.45
    tt = t(d)
    out = np.zeros_like(tt)

    # 1. the catch gives way — a low body with a downward bend
    give = int(0.34 * SR)
    g = tt[:give]
    bend = 186 * np.exp(-5.4 * g) + 76
    ph = 2 * np.pi * np.cumsum(bend) / SR
    body = np.sin(ph) * np.exp(-9.5 * g)
    grain = lp(noise(0.34), 620) * np.exp(-17 * g)
    out[:give] += body * 0.85 + grain * 0.3

    # 2. a warm low swell rising underneath it. Pitched up from where it
    # started: at a 58 Hz fundamental 85% of the energy sat below 90 Hz, which
    # is a rumble on studio monitors and silence on a phone.
    sw = np.zeros_like(tt)
    for f, a in ((96, 1.0), (144, 0.6), (192.6, 0.34), (251, 0.18)):
        sw += a * np.sin(2 * np.pi * f * (1 + 0.0035 * np.sin(2 * np.pi * 0.7 * tt)) * tt)
    swell_env = np.sin(np.pi * np.clip(tt / 0.95, 0, 1) ** 0.75) ** 1.5
    out += sw * swell_env * 0.42

    # 3. air — the exhale itself, arriving late and leaving slowly. This is
    # the half that carries the sound on small speakers, so it is not shy.
    air = lp(hp(noise(d), 300), 1900)
    breath = np.clip((tt - 0.22) / 0.32, 0, 1) ** 1.3 * np.exp(-1.9 * np.clip(tt - 0.22, 0, None))
    out += air * breath * 0.95

    # a throat under the breath — the body of an exhale, not just its hiss
    throat = lp(hp(noise(d), 180), 700) * np.clip((tt - 0.18) / 0.3, 0, 1) \
             * np.exp(-2.4 * np.clip(tt - 0.18, 0, None))
    out += throat * 0.55

    out = hp(lp(out, 3200), 62)
    return out * np.minimum(1, np.exp(-0.6 * np.clip(tt - 0.9, 0, None)))


def arrival():
    """One soft chime. Warm, wooden, no glassy top — a struck bowl, damped."""
    d = 0.85
    tt = t(d)
    x = np.zeros_like(tt)
    for f, a, dm in ((392, 1.0, 4.2), (588, 0.42, 5.4), (784, 0.17, 7.0), (1173, 0.06, 10.0)):
        x += a * np.sin(2 * np.pi * f * (1 + 0.002 * np.sin(2 * np.pi * 4.1 * tt)) * tt) * np.exp(-dm * tt)
    mallet = lp(noise(d), 1500) * np.exp(-90 * tt)
    return lp(env(x * 0.8 + mallet * 0.25, 0.006, 0.42, curve=1.2), 3000)


def shutter():
    """Proof posting. Tactile, mechanical, quick — a shutter's cousin."""
    d = 0.17
    a = wood(0.06, 620, damp=140, detune=(1.0, 3.3))
    b = wood(0.09, 380, damp=90, detune=(1.0, 2.8, 4.6))
    x = np.zeros(int(d * SR))
    x[:len(a)] += a * 0.7
    off = int(0.055 * SR)
    x[off:off + len(b)] += b
    x += lp(noise(d), 1900) * np.exp(-95 * t(d)) * 0.3
    return env(x, 0.0015, 0.05)


def tick(step=0):
    """A small ascending tick, one per filled day. Wood, rising by a tone."""
    d = 0.09
    f = 300 * (2 ** (step * 2 / 12))
    x = wood(d, f, damp=110, detune=(1.0, 2.76, 4.9))
    x += lp(noise(d), 2200) * np.exp(-190 * t(d)) * 0.25
    return env(x, 0.0015, 0.025)


if __name__ == "__main__":
    os.makedirs("audio/sfx", exist_ok=True)
    print("sfx library:")
    write("ui_tap", ui_tap(), 0.55)
    write("key", key(), 0.42)
    write("whoosh_down", whoosh("down"), 0.5)
    write("whoosh_up", whoosh("up"), 0.5)
    write("lock_catch", lock_catch(), 0.6)
    write("unlock", unlock(), 0.95)
    write("arrival", arrival(), 0.62)
    write("shutter", shutter(), 0.6)
    for i in range(5):
        write(f"tick{i}", tick(i), 0.4)
