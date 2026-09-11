#!/usr/bin/env python3
"""
Measure a track's grid, and find the silences the film is cut to.

Everything in this film's timeline that is not a design choice came out of here:
the tempo (129.000), the grid phase, and the two hard silences that decide where
the petal lets go and where the studio calms down. Re-run it if the track is ever
swapped, and re-derive the constants — do not carry the old ones across.

  python3 scripts/track.py audio/gracias-a-ti-129.mp3

Tempo is fitted rather than tapped: a spectral-flux onset envelope is combed
against every candidate (BPM, phase) over a long window and the pair with the
highest mean on-beat onset energy wins. Phase is then confirmed against the
silences, which is the part worth trusting — a break that ends exactly on a
downbeat proves the grid in a way an autocorrelation peak cannot.
"""
import subprocess
import sys
import wave

import numpy as np

SR = 22050


def load(path):
    import imageio_ffmpeg
    ff = imageio_ffmpeg.get_ffmpeg_exe()
    tmp = "/tmp/_track_%d.wav" % abs(hash(path))
    subprocess.run([ff, "-y", "-loglevel", "error", "-i", path,
                    "-ac", "1", "-ar", str(SR), "-f", "wav", tmp], check=True)
    w = wave.open(tmp)
    a = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16)
    return a.astype(float) / 32768.0


def onset_envelope(a, hop=256, win=1024):
    nf = (len(a) - win) // hop
    idx = np.arange(nf)[:, None] * hop + np.arange(win)
    S = np.abs(np.fft.rfft(a[idx] * np.hanning(win), axis=1))
    return np.concatenate([[0.0], np.maximum(0, np.diff(S, axis=0)).sum(1)])


def fit_grid(flux, lo=20.0, hi=120.0, hop=256, bpm_range=(100.0, 160.0)):
    f = (flux - flux.mean()) / flux.std()
    best = None
    for bpm in np.arange(bpm_range[0], bpm_range[1], 0.01):
        b = 60.0 / bpm
        for ph in np.arange(0, b, 0.005):
            idx = np.round((np.arange(ph, hi - lo, b) + lo) * SR / hop).astype(int)
            idx = idx[(idx > 0) & (idx < len(f))]
            if len(idx) < 8:
                continue
            sc = f[idx].mean()
            if best is None or sc > best[2]:
                best = (bpm, ph, sc)
    return best


def silences(a, block=0.02, floor=1e-6, least=0.15):
    B = int(block * SR)
    nb = len(a) // B
    rms = np.sqrt((a[:nb * B].reshape(nb, B) ** 2).mean(1))
    out, run = [], None
    for i in range(nb):
        q = rms[i] < floor
        if q and run is None:
            run = i * block
        if not q and run is not None:
            if i * block - run > least:
                out.append((run, i * block))
            run = None
    return out


def main():
    a = load(sys.argv[1])
    print("duration %.2fs" % (len(a) / SR))
    bpm, _, sc = fit_grid(onset_envelope(a))
    beat = 60.0 / bpm
    print("tempo %.3f BPM   beat %.5fs   bar %.5fs   (on-beat score %.3f)"
          % (bpm, beat, 4 * beat, sc))

    runs = silences(a)
    # Near-silences matter as much as true ones. This track's second break is a
    # musical drop-out at about -38 dBFS, not a sample-exact stop, and it is
    # still a downbeat-aligned bar of nothing you can cut on. Reporting only
    # digital zero would have hidden half the film's structure.
    near = [r for r in silences(a, floor=0.012, least=0.5) if r not in runs]
    if not runs and not near:
        print("no silences")
        return
    # Pin the phase on the silences: they end on downbeats, and that is a far
    # stronger constraint than the comb's own phase estimate.
    ends = [e for _, e in runs]
    ph = np.median([e - round(e / (4 * beat)) * 4 * beat for e in ends])
    print("grid phase %.4fs  (pinned on the silences, which end on downbeats)" % ph)
    for label, group in (("hard silences (sample-exact zero)", runs),
                         ("near-silences (below -38 dBFS)", near)):
        if not group:
            continue
        print("\n%s:" % label)
        for s, e in group:
            print("  %8.3f -> %8.3f  (%.3fs)   beats %.2f -> %.2f"
                  % (s, e, e - s, (s - ph) / beat, (e - ph) / beat))


if __name__ == "__main__":
    main()
