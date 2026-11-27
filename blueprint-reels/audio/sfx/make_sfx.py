"""Synthesized SFX library for the Blueprint reels (BRIEF Appendix C). 48 kHz stereo WAV.
Every sound is original and generated here; run `python3 make_sfx.py` to rebuild."""
import os
import wave

import numpy as np

SR = 48000
OUT = os.path.dirname(os.path.abspath(__file__))
rng = np.random.default_rng(26112026)


# ---------------------------------------------------------------- helpers
def t_(d):
    return np.arange(int(round(d * SR))) / SR


def mtof(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def modal(f, d, tau, partials=((1, 1.0),), attack=0.0015):
    t = t_(d)
    x = sum(a * np.sin(2 * np.pi * f * r * t + rng.uniform(0, 6.28)) * np.exp(-t / (tau / (r ** 0.5))) for r, a in partials)
    x *= np.minimum(1, t / attack)
    return x


def band(x, lo, hi):
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    w = ((f >= lo) & (f <= hi)).astype(float)
    k = np.hanning(41)
    w = np.convolve(w, k / k.sum(), 'same')
    return np.fft.irfft(X * w, len(x))


def lowpass(x, fc):
    return band(x, 0, fc)


def highpass(x, fc):
    return band(x, fc, SR / 2)


def pink(n):
    X = np.fft.rfft(rng.standard_normal(n))
    f = np.fft.rfftfreq(n, 1 / SR)
    X[1:] /= np.sqrt(f[1:])
    X[0] = 0
    return norm(np.fft.irfft(X, n))


def norm(x, p=1.0):
    m = np.max(np.abs(x))
    return x * (p / m) if m > 0 else x


def pad(x, n):
    return np.pad(x, (0, max(0, n - len(x))))[:n] if len(x) < n else x


def place(dst, src, at):
    i = int(round(at * SR))
    j = min(len(dst), i + len(src))
    if j > i:
        dst[i:j] += src[: j - i]


def stereo(l, r=None):
    r = l if r is None else r
    n = max(len(l), len(r))
    return np.stack([pad(l, n), pad(r, n)], 1)


def pan(x, p):  # p in -1..1, constant power
    a = (p + 1) * np.pi / 4
    return stereo(x * np.cos(a), x * np.sin(a))


def plate(st, length=0.8, mix=0.18):
    """Short plate-ish reverb: exponentially decaying, band-limited noise IR per channel."""
    n = int(length * SR)
    out = []
    for c in range(2):
        ir = band(rng.standard_normal(n), 300, 9000) * np.exp(-np.arange(n) / SR / (length / 5))
        ir /= np.sqrt((ir ** 2).sum())
        dry = np.pad(st[:, c], (0, n))
        wet = pad(np.convolve(st[:, c], ir), len(dry))[: len(dry)]
        out.append(dry + mix * wet)
    return np.stack(out, 1)


def fade_tail(st, d=0.01):
    n = int(d * SR)
    st[-n:] *= np.linspace(1, 0, n)[:, None]
    return st


def write(name, st, peak=0.89):
    if st.ndim == 1:
        st = stereo(st)
    st = fade_tail(st.copy())
    st = norm(st, peak)
    with wave.open(os.path.join(OUT, name + '.wav'), 'wb') as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((np.clip(st, -1, 1) * 32767).astype('<i2').tobytes())
    return st


BELL = ((1, 1.0), (2.76, 0.4), (5.40, 0.18))
made = []

# ---------------------------------------------------------------- CHING (full) ~0.9 s
n = int(0.9 * SR)
L = np.zeros(n)
R = np.zeros(n)
b1 = modal(2637, 0.9, 0.35, BELL)
b2 = modal(3136, 0.9, 0.35, BELL)
L += b1 * 1.0 + b2 * 0.55
R += b1 * 0.55 + b2 * 1.0
# drawer: 120 Hz thunk with 30 ms pitch drop, + 40 ms band noise at +30 ms
tt = t_(0.25)
th = np.sin(2 * np.pi * np.cumsum(120 + 90 * np.exp(-tt / 0.03)) / SR) * np.exp(-tt / 0.06)
dn = band(rng.standard_normal(int(0.04 * SR)), 800, 3000) * np.hanning(int(0.04 * SR))
for ch in (L, R):
    place(ch, 0.55 * th, 0.0)
    place(ch, 0.35 * norm(dn), 0.03)
# coin shimmer: six tiny metallic ticks 4.5-7.5 kHz, tau 25 ms, 0-250 ms, random pan
for _ in range(6):
    tk = modal(rng.uniform(4500, 7500), 0.12, 0.025, ((1, 1), (1.47, 0.4)))
    p = rng.uniform(-1, 1)
    a = (p + 1) * np.pi / 4
    at = rng.uniform(0, 0.25)
    place(L, 0.22 * tk * np.cos(a), at)
    place(R, 0.22 * tk * np.sin(a), at)
# 40 ms bright transient at 0
tr = highpass(rng.standard_normal(int(0.04 * SR)), 3000) * np.exp(-t_(0.04) / 0.006)
place(L, 0.5 * norm(tr), 0)
place(R, 0.5 * norm(tr), 0)
write('ching_full', plate(stereo(L, R), 0.8, 0.22))
made.append('ching_full')

# ---------------------------------------------------------------- CHING (light) ~0.45 s, -6 dB
n = int(0.45 * SR)
x = modal(3136, 0.45, 0.18, BELL)
st = stereo(x, x)
for _ in range(2):
    tk = modal(rng.uniform(4500, 7500), 0.1, 0.025, ((1, 1), (1.47, 0.4)))
    p = rng.uniform(-0.8, 0.8)
    a = (p + 1) * np.pi / 4
    at = rng.uniform(0, 0.12)
    tmp = np.zeros(n)
    place(tmp, 0.25 * tk, at)
    st[:, 0] += tmp * np.cos(a)
    st[:, 1] += tmp * np.sin(a)
write('ching_light', plate(st, 0.5, 0.15), peak=0.89 * 10 ** (-6 / 20))
made.append('ching_light')


# ---------------------------------------------------------------- notification pop / dopamine ladder
def pop(midi, octave_double=False):
    f0 = mtof(midi)
    tt = t_(0.12)
    glide = f0 * 2 ** ((7 / 12) * np.minimum(1, tt / 0.04))  # up a fifth over 40 ms
    x = np.sin(2 * np.pi * np.cumsum(glide) / SR)
    if octave_double:
        x += 0.6 * np.sin(2 * np.pi * np.cumsum(glide * 2) / SR)
    x *= np.exp(-tt / 0.06) * np.minimum(1, tt / 0.002)
    click = highpass(rng.standard_normal(int(0.003 * SR)), 2000) * np.hanning(int(0.003 * SR))
    x[: len(click)] += 0.3 * click
    return x


for name, m in [('E5', 76), ('Fs5', 78), ('Gs5', 80), ('A5', 81), ('B5', 83)]:
    write(f'pop_ladder_{name}', pop(m))
    made.append(f'pop_ladder_{name}')
write('pop_live', pop(83 + 2, octave_double=True))  # brightest: C#6 doubled an octave up
made.append('pop_live')
for k in range(12):  # chat pops, each a semitone higher
    write(f'pop_chat_{k:02d}', pop(72 + k), peak=0.7)
made.append('pop_chat_00..11')

# ---------------------------------------------------------------- phone buzz (1.2 s)
tt = t_(1.2)
sq = np.sign(np.sin(2 * np.pi * 172 * tt))
gate = ((tt % 0.24) < 0.15).astype(float)
gate = np.convolve(gate, np.hanning(200) / np.hanning(200).sum(), 'same')
rattle = band(rng.standard_normal(len(tt)), 2000, 6000) * (np.sin(2 * np.pi * 172 * tt) > 0.95)
write('phone_buzz', lowpass(sq, 1800) * gate + 0.25 * rattle * gate)
made.append('phone_buzz')


# ---------------------------------------------------------------- typing ticks
def tick():
    n = int(0.012 * SR)
    x = np.zeros(n)
    nz = highpass(rng.standard_normal(int(0.004 * SR)), 3000) * np.hanning(int(0.004 * SR))
    x[: len(nz)] += nz
    x += 0.5 * modal(rng.uniform(1600, 1900), 0.012, 0.003)
    return x


write('type_tick', tick())
seq = np.zeros(int(2.0 * SR))
at = 0.02
while at < 1.95:
    place(seq, tick() * rng.uniform(0.6, 1.0), at)
    at += rng.uniform(0.07, 0.14)
write('typing_2s', seq)
made += ['type_tick', 'typing_2s']

# ---------------------------------------------------------------- pen scratch (1 s)
tt = t_(1.0)
rate = 8 + 5 * rng.random()
am = np.clip(np.sin(2 * np.pi * np.cumsum(rate + 1.5 * np.sin(2 * np.pi * 0.7 * tt)) / SR), 0, 1) ** 1.5
write('pen_scratch', band(pink(len(tt)), 1800, 7500) * am)
made.append('pen_scratch')

# ---------------------------------------------------------------- stamp thud
tt = t_(0.35)
x = np.sin(2 * np.pi * np.cumsum(130 + 120 * np.exp(-tt / 0.015)) / SR) * np.exp(-tt / 0.08)
x[: int(0.015 * SR)] += 0.5 * band(rng.standard_normal(int(0.015 * SR)), 500, 6000)
write('stamp_thud', x)
made.append('stamp_thud')

# ---------------------------------------------------------------- check ding (glockenspiel-like)
write('check_ding', modal(mtof(95), 1.0, 0.4, BELL), peak=0.75)  # B6
write('check_ding_2', modal(mtof(100), 1.0, 0.4, BELL), peak=0.75)  # E7
made += ['check_ding', 'check_ding_2']


# ---------------------------------------------------------------- call connect: two vibraphone notes a fifth apart, 120 ms
def vib(f, d=0.9):
    tt = t_(d)
    return modal(f, d, 0.45, ((1, 1), (4.0, 0.25), (10.0, 0.05))) * (1 + 0.15 * np.sin(2 * np.pi * 5.5 * tt))


x = np.zeros(int(1.1 * SR))
place(x, vib(mtof(72)), 0)
place(x, vib(mtof(79)), 0.12)
write('call_connect', plate(stereo(x), 0.6, 0.15), peak=0.7)
made.append('call_connect')

# ---------------------------------------------------------------- end signature
# switch click: press click (2.9 + 4.3 kHz, tau 6 ms) + thunk (190, 430, 980 Hz, tau 20-30 ms); release click 70 ms later
x = np.zeros(int(0.25 * SR))
press = modal(2900, 0.05, 0.006) + modal(4300, 0.05, 0.006)
thunk = modal(190, 0.15, 0.03) + 0.7 * modal(430, 0.15, 0.025) + 0.5 * modal(980, 0.15, 0.02)
place(x, press + 0 * press, 0)
place(x, 0.9 * thunk, 0)
place(x, 0.4 * press, 0.07)
write('switch_click', x, peak=0.8)
made.append('switch_click')


def warm_rise(total, root_midi=64):
    """Tonic triad sines (+2nd/3rd harmonics) gliding up 5 semitones into pitch over 0.3 s (exp),
    ~0.9 s swell, sustain, fade to zero by the end. Low-passed at 2.4 kHz."""
    tt = t_(total)
    glide = 2 ** ((-5 / 12) * np.exp(-tt / 0.3 * 3))
    x = np.zeros(len(tt))
    for m in (root_midi, root_midi + 4, root_midi + 7):
        f = mtof(m) * glide
        ph = 2 * np.pi * np.cumsum(f) / SR
        x += np.sin(ph) + 0.3 * np.sin(2 * ph) + 0.12 * np.sin(3 * ph)
    env = np.minimum(1, tt / 0.9) ** 1.5 * np.clip((total - tt) / (total * 0.45), 0, 1)
    return lowpass(x * env, 2400)


write('warm_rise_film01', warm_rise(110 / 30), peak=0.6)  # ON 790 -> 900
write('warm_rise_film02_04', warm_rise(111 / 30), peak=0.6)  # ON 489 -> 600
for i in range(1, 6):
    write(f'ray_tick_{i}', modal(2637 * 2 ** (2 * (i - 1) / 12), 0.4, 0.09, ((1, 1), (2.32, 0.35), (4.1, 0.15))), peak=0.55)
made += ['warm_rise_film01', 'warm_rise_film02_04', 'ray_tick_1..5']

# ---------------------------------------------------------------- whooshes, glint, lock, stylus, heartbeat, clock
def whoosh(d, f0, f1, peak_at=0.6):
    tt = t_(d)
    nz = rng.standard_normal(len(tt))
    hop, win = 256, 1024
    y = np.zeros(len(tt) + win)
    w = np.hanning(win)
    fr = np.fft.rfftfreq(win, 1 / SR)
    nfr = (len(tt) - win) // hop + 1
    for k in range(nfr):
        c = f0 * (f1 / f0) ** (k / max(1, nfr - 1))
        g = np.exp(-0.5 * (np.log(np.maximum(fr, 1) / c) / 0.5) ** 2)
        y[k * hop : k * hop + win] += np.fft.irfft(np.fft.rfft(nz[k * hop : k * hop + win] * w) * g, win) * w
    y = y[: len(tt)]
    env = np.where(tt < d * peak_at, (tt / (d * peak_at)) ** 2, np.exp(-(tt - d * peak_at) / (d * 0.15)))
    return y * env


write('whoosh_soft', whoosh(0.6, 400, 3000), peak=0.6)
write('whoosh_later', whoosh(0.7, 2500, 300, 0.3), peak=0.55)
write('whip', whoosh(0.25, 800, 6000, 0.7), peak=0.7)
write('air_swell_slowmo', whoosh(1.4, 200, 1500, 0.8), peak=0.55)
write('air_rise_to_endcard', whoosh(0.4, 300, 5000, 0.95), peak=0.6)
gl = sum(modal(f, 0.8, 0.25, ((1, 1),)) * 0.3 for f in (3520, 4435, 5274, 7040))
write('glint_shimmer', plate(stereo(gl * (1 + 0.5 * np.sin(2 * np.pi * 14 * t_(0.8)))), 0.6, 0.25), peak=0.5)
write('lock_click', modal(1800, 0.08, 0.006) + 0.6 * modal(950, 0.08, 0.012), peak=0.6)
tt = t_(0.6)
write('stylus_stroke', band(pink(len(tt)), 1500, 6000) * np.sin(np.pi * tt / 0.6) ** 0.8, peak=0.4)
hb = np.zeros(int(1.0 * SR))
for at, a in ((0, 1), (0.22, 0.7)):
    place(hb, a * modal(55, 0.3, 0.07) + a * 0.4 * modal(110, 0.3, 0.04), at)
write('heartbeat', hb)
write('clock_tick', modal(3200, 0.05, 0.004) + 0.5 * modal(1100, 0.05, 0.01), peak=0.6)
made += ['whoosh_soft', 'whoosh_later', 'whip', 'air_swell_slowmo', 'air_rise_to_endcard', 'glint_shimmer', 'lock_click', 'stylus_stroke', 'heartbeat', 'clock_tick']

# ---------------------------------------------------------------- film-specific stings
# horror screech (film 04): 8 detuned saws within 40 cents, fast tremolo, HP 900 Hz, 0.6 s
tt = t_(0.6)
x = sum(2 * ((mtof(88) * 2 ** (c / 1200) * tt) % 1) - 1 for c in np.linspace(-20, 20, 8))
x *= (1 + 0.6 * np.sin(2 * np.pi * 18 * tt)) * np.minimum(1, tt / 0.02) * np.exp(-tt / 0.45)
write('horror_screech', highpass(x, 900), peak=0.7)
# comic organ sting (film 02): three descending organ chords, 0.25 s each
x = np.zeros(int(0.85 * SR))
for i, root in enumerate((67, 64, 60)):
    tt = t_(0.27)
    c = np.zeros(len(tt))
    for m in (root, root + 3, root + 7):
        for h, a in ((1, 1), (2, 0.6), (3, 0.4), (4, 0.25), (6, 0.15)):  # drawbars
            c += a * np.sin(2 * np.pi * mtof(m) * h * tt)
    c *= np.minimum(1, tt / 0.01) * np.clip((0.27 - tt) / 0.03, 0, 1)
    place(x, c, i * 0.25)
write('organ_sting', x, peak=0.6)
# brass stab / sax sting (film 03): saw + noise with fast-opening filter envelope, 0.4 s
for name, notes in (('brass_stab', (62, 65, 69)), ('sax_sting', (74,))):
    tt = t_(0.4)
    x = sum(2 * ((mtof(m) * tt) % 1) - 1 for m in notes) + 0.08 * rng.standard_normal(len(tt))
    hop = 480
    y = np.zeros(len(tt))
    for k in range(0, len(tt) - hop, hop):
        fc = 600 + 4000 * np.exp(-(k / SR) / 0.12) * min(1, (k / SR) / 0.02 + 0.1)
        seg = x[k : k + 2 * hop]
        y[k : k + len(seg)] += lowpass(seg * np.hanning(len(seg)), fc)
    y *= np.minimum(1, tt / 0.01) * np.clip((0.4 - tt) / 0.08, 0, 1)
    write(name, y, peak=0.7)
made += ['horror_screech', 'organ_sting', 'brass_stab', 'sax_sting']

print('made:', ', '.join(made))
