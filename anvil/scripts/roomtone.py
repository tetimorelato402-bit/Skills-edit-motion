#!/usr/bin/env python3
"""
Room tone for the dry mix.

The film has no music, so its silences would otherwise be digital zero —
which does not read as quiet, it reads as the file having stopped. This is
a pink-noise floor, band-limited to the range a room actually occupies and
sat far enough down that it never competes with the voice: audible as
texture in the gaps, inaudible under speech.
"""
import sys, wave
import numpy as np

SR = 44100
RMS = 0.005          # ≈ −46 dBFS
SEED = 7             # deterministic: the same tone on every render


def pink(n, rng):
    """1/f noise by spectral shaping — smoother than filtered white."""
    white = rng.standard_normal(n)
    spec = np.fft.rfft(white)
    f = np.fft.rfftfreq(n, 1 / SR)
    shape = np.ones_like(f)
    shape[1:] = 1 / np.sqrt(f[1:])
    # a room has no content below ~45 Hz and little above ~3.5 kHz
    shape *= 1 / (1 + (45 / np.maximum(f, 1e-6)) ** 4)      # highpass
    shape *= 1 / (1 + (np.maximum(f, 0) / 3500) ** 2)        # gentle lowpass
    return np.fft.irfft(spec * shape, n)


def ramp(n, dur, sr=SR):
    """Raised-cosine, so the tone arrives and leaves without an edge."""
    k = int(dur * sr)
    w = np.ones(n)
    e = 0.5 - 0.5 * np.cos(np.linspace(0, np.pi, k))
    w[:k] = e
    w[-k:] = e[::-1]
    return w


if __name__ == "__main__":
    duration = float(sys.argv[1])
    out = sys.argv[2]
    fade_out_at = float(sys.argv[3]) if len(sys.argv) > 3 else None

    n = int(duration * SR)
    x = pink(n, np.random.default_rng(SEED))
    x *= RMS / np.sqrt((x ** 2).mean())
    x *= ramp(n, 0.9)

    if fade_out_at is not None:
        # the tone goes out with the picture, not after it
        k0 = int(fade_out_at * SR)
        tail = np.linspace(0, np.pi, n - k0)
        x[k0:] *= 0.5 + 0.5 * np.cos(tail)

    pcm = np.clip(x, -1, 1)
    with wave.open(out, "wb") as w:
        w.setnchannels(1); w.setsampwidth(3); w.setframerate(SR)
        w.writeframes((pcm * (2 ** 23 - 1)).astype("<i4").view("<u1")
                      .reshape(-1, 4)[:, :3].tobytes())
    print(f"{out}: {duration:.3f}s, RMS {np.sqrt((x**2).mean()):.5f} "
          f"({20*np.log10(np.sqrt((x**2).mean())):.1f} dBFS)")
