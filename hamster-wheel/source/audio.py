"""Sound design for the 4 s hamster clip, modelled on the reference reel's structure:
quiet diegetic intro (no music) -> sync hit on the 'eyes open' moment -> riser -> beat drop at
the action start (148 BPM, cuts on the beat) -> hard cut at the end.
Writes stems to audio/ and a mix to audio/mix.wav (48 kHz)."""
import numpy as np, wave, os

SR = 48000
DUR = 4.0
BPM = 148
BEAT = 60 / BPM
T_DROP = 4 * BEAT              # 1.622 s: hamster launches, wheel spins, music drops
T_C = T_DROP + 3 * BEAT        # 2.838 s: cut to close-up
T_D = T_DROP + 4.5 * BEAT      # 3.446 s: cut to hero angle
T_EYES = 0.85                  # eyes snap open
rng = np.random.default_rng(7)
N = int(SR * DUR)
t_all = np.arange(N) / SR


def buf():
    return np.zeros(N)


def place(dst, sig, t0, gain=1.0):
    i = int(round(t0 * SR))
    if i >= N:
        return
    j = min(N, i + len(sig))
    if i < 0:
        sig = sig[-i:]; j = min(N, len(sig)); i = 0
    dst[i:j] += sig[: j - i] * gain


def env_ad(n, a, d):
    """attack/exp-decay envelope, a & d in seconds"""
    t = np.arange(n) / SR
    e = np.exp(-np.maximum(t - a, 0) / d)
    e[t < a] = t[t < a] / max(a, 1e-4)
    return e


def onepole_lp(x, fc):
    a = np.exp(-2 * np.pi * fc / SR); y = np.empty_like(x); s = 0.0
    for i, v in enumerate(x):
        s = (1 - a) * v + a * s; y[i] = s
    return y


def bandpass(x, lo, hi):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR)
    m = (f >= lo) & (f <= hi)
    w = np.where(m, 1.0, 0.0)
    # soft edges
    w = np.convolve(w, np.hanning(31) / np.hanning(31).sum(), mode='same')
    return np.fft.irfft(X * w, len(x))


def sweep_bandpass(x, f0, f1):
    """time-varying bandpass via short-time FFT (for whooshes / risers)"""
    hop, win = 256, 1024; y = np.zeros(len(x) + win); w = np.hanning(win)
    nfr = (len(x) - win) // hop + 1
    f = np.fft.rfftfreq(win, 1 / SR)
    for k in range(max(nfr, 1)):
        seg = x[k * hop: k * hop + win]
        if len(seg) < win:
            seg = np.pad(seg, (0, win - len(seg)))
        c = f0 * (f1 / f0) ** (k / max(nfr - 1, 1))
        g = np.exp(-0.5 * (np.log(np.maximum(f, 1) / c) / 0.45) ** 2)
        y[k * hop: k * hop + win] += np.fft.irfft(np.fft.rfft(seg * w) * g, win) * w
    return y[: len(x)] / 1.5


def tone(freq, dur, harmonics=((1, 1),), phase=0):
    t = np.arange(int(dur * SR)) / SR
    if callable(freq):
        ph = 2 * np.pi * np.cumsum(freq(t)) / SR
    else:
        ph = 2 * np.pi * freq * t
    return sum(a * np.sin(h * ph + phase) for h, a in harmonics)


def norm(x, peak=1.0):
    m = np.max(np.abs(x)) or 1
    return x / m * peak

# ---------------------------------------------------------------- ambience / room tone
amb = buf()
brown = np.cumsum(rng.standard_normal(N)); brown -= onepole_lp(brown, 3); brown = norm(brown)
amb += onepole_lp(brown, 400) * 0.9
city = bandpass(rng.standard_normal(N), 150, 1200)            # distant city through a window
amb += norm(city) * 0.25
amb = norm(amb) * 0.05
# room tone ducks a little under the drop, like the reference's bed
amb *= np.where(t_all < T_DROP, 1.0, 0.55)

# ---------------------------------------------------------------- intro foley (no music)
fol = buf()
# sleepy little snores (in-breath = noisy whistle, out-breath = soft purr)
for t0 in (0.05, 0.52):
    n = int(0.3 * SR); tt = np.arange(n) / SR
    inbreath = bandpass(rng.standard_normal(n), 1800, 5000) * np.sin(np.pi * tt / 0.3) ** 2
    purr = tone(lambda x: 210 + 30 * np.sin(2 * np.pi * 3 * x), 0.3, ((1, 1), (2, 0.5), (3, 0.25)))
    purr *= (0.5 + 0.5 * np.sign(np.sin(2 * np.pi * 34 * tt))) * np.sin(np.pi * tt / 0.3) ** 2
    place(fol, norm(inbreath) * 0.25 + norm(purr) * 0.18, t0)
# eyes snap open: cartoon "bink" + tiny air pop
bink = tone(lambda x: 1500 + 900 * np.exp(-x * 40), 0.25, ((1, 1), (2.01, 0.35), (3.02, 0.15))) * env_ad(int(0.25 * SR), 0.002, 0.06)
pop = bandpass(rng.standard_normal(int(0.05 * SR)), 300, 2500) * env_ad(int(0.05 * SR), 0.001, 0.012)
place(fol, norm(bink) * 0.55, T_EYES - 0.004); place(fol, norm(pop) * 0.3, T_EYES - 0.004)
# startled squeak "eek!" (hamster voice): FM chirp 3.0 -> 4.4 kHz with vibrato
n = int(0.16 * SR); tt = np.arange(n) / SR
eek = tone(lambda x: 3000 + 1400 * (x / 0.16) ** 0.6 + 120 * np.sin(2 * np.pi * 38 * x), 0.16, ((1, 1), (2, 0.2)))
eek *= np.sin(np.pi * tt / 0.16) ** 0.7
place(fol, norm(eek) * 0.32, 1.02)
# crouch: fur rustle + claws gripping the wire rungs
rustle = bandpass(rng.standard_normal(int(0.3 * SR)), 2000, 9000) * np.sin(np.linspace(0, np.pi, int(0.3 * SR))) ** 2
place(fol, norm(rustle) * 0.12, 1.15)
for k in range(4):
    clk = bandpass(rng.standard_normal(int(0.012 * SR)), 2500, 9000) * env_ad(int(0.012 * SR), 0.0005, 0.003)
    place(fol, norm(clk) * 0.25, 1.2 + k * 0.045 + rng.uniform(0, 0.01))

# ---------------------------------------------------------------- riser into the drop
rise_len = T_DROP - 1.12
n = int(rise_len * SR); tt = np.arange(n) / SR
riser = sweep_bandpass(rng.standard_normal(n), 400, 9000) * (tt / rise_len) ** 2.2
riser_tone = tone(lambda x: 220 * 2 ** (2 * x / rise_len), rise_len, ((1, 1), (2, 0.3))) * (tt / rise_len) ** 3
m = min(len(riser), len(riser_tone)); riser_all = norm(riser[:m]) * 0.35 + norm(riser_tone[:m]) * 0.12
riser_all[-int(0.012 * SR):] *= np.linspace(1, 0, int(0.012 * SR))   # cut dead on the drop
fx = buf(); place(fx, riser_all, 1.12)

# ---------------------------------------------------------------- drop impact
n = int(1.2 * SR); tt = np.arange(n) / SR
boom = np.sin(2 * np.pi * np.cumsum(38 + 60 * np.exp(-tt * 18)) / SR) * np.exp(-tt * 3.2)
crack = bandpass(rng.standard_normal(n), 800, 12000) * np.exp(-tt * 28)
place(fx, norm(boom) * 0.9 + norm(crack) * 0.35, T_DROP)

# ---------------------------------------------------------------- whooshes on the cuts
for tc in (T_C, T_D):
    n = int(0.32 * SR); tt = np.arange(n) / SR
    wsh = sweep_bandpass(rng.standard_normal(n), 600, 5000) * np.sin(np.pi * tt / 0.32) ** 1.5
    place(fx, norm(wsh) * 0.32, tc - 0.2)

# ---------------------------------------------------------------- the wheel
wheel = buf()
def wheel_speed(t):          # rad/s, same curve as the picture
    return np.where(t < T_DROP - 0.15, 0, 26 * (1 - np.exp(-(t - T_DROP + 0.15) / 0.25)))
ang = np.cumsum(wheel_speed(t_all)) / SR
# start-up creak: low metal groan as the wheel first moves
n = int(0.35 * SR); tt = np.arange(n) / SR
creak = tone(lambda x: 520 + 380 * (x / 0.35), 0.35, ((1, 1), (2, 0.6), (3, 0.4), (5, 0.2)))
creak *= (0.6 + 0.4 * np.sign(np.sin(2 * np.pi * 45 * tt))) * np.sin(np.pi * tt / 0.35)
place(wheel, norm(creak) * 0.22, T_DROP - 0.17)
# rhythmic axle squeak once per revolution
rev = np.floor(ang / (2 * np.pi))
for r in range(1, int(rev[-1]) + 1):
    idx = np.argmax(rev >= r); t0 = idx / SR
    n = int(0.07 * SR); tt = np.arange(n) / SR
    sq = tone(lambda x: 2150 + 350 * x / 0.07, 0.07, ((1, 1), (1.5, 0.3), (2, 0.25))) * np.sin(np.pi * tt / 0.07) ** 2
    place(wheel, norm(sq) * 0.09 * (0.8 + 0.4 * rng.random()), t0)
# rung rattle: each wire rung passing under the feet (56 rungs per revolution)
rung = np.floor(ang / (2 * np.pi / 56)); edges = np.nonzero(np.diff(rung) > 0)[0]
for idx in edges:
    n = int(0.008 * SR)
    tk = bandpass(rng.standard_normal(n), 3000, 10000) * env_ad(n, 0.0003, 0.002)
    place(wheel, norm(tk) * 0.05, idx / SR)
# steady rolling rumble
rumble = onepole_lp(rng.standard_normal(N), 180) * np.clip(wheel_speed(t_all) / 26, 0, 1)
wheel += norm(rumble) * 0.12
# paw patter: 4 legs at 28 rad/s -> ~18 taps per second
pat = buf(); step = 2 * np.pi / 28 / 4
t0 = T_DROP
while t0 < DUR:
    n = int(0.01 * SR)
    tp = bandpass(rng.standard_normal(n), 1200, 6000) * env_ad(n, 0.0005, 0.0025)
    place(pat, norm(tp) * 0.11 * (0.7 + 0.5 * rng.random()), t0 + rng.normal(0, 0.003))
    t0 += step

# ---------------------------------------------------------------- music: 148 BPM trap drop (C minor)
mus = buf()
def kick():
    n = int(0.45 * SR); tt = np.arange(n) / SR
    k = np.sin(2 * np.pi * np.cumsum(48 + 130 * np.exp(-tt * 35)) / SR) * np.exp(-tt * 7)
    k += bandpass(rng.standard_normal(n), 2000, 8000) * np.exp(-tt * 200) * 0.3
    return norm(k)
def clap():
    n = int(0.25 * SR); tt = np.arange(n) / SR
    e = sum(np.exp(-np.maximum(tt - d, 0) * 60) * (tt >= d) for d in (0, 0.011, 0.022)) + np.exp(-np.maximum(tt - 0.03, 0) * 18) * (tt >= 0.03)
    return norm(bandpass(rng.standard_normal(n), 900, 7000) * e)
def hat(open_=False):
    n = int((0.12 if open_ else 0.04) * SR); tt = np.arange(n) / SR
    return norm(bandpass(rng.standard_normal(n), 7000, 16000) * np.exp(-tt * (25 if open_ else 110)))
def bass808(f, dur, glide_to=None):
    n = int(dur * SR); tt = np.arange(n) / SR
    fr = f if glide_to is None else f + (glide_to - f) * np.clip((tt - dur * 0.6) / (dur * 0.3), 0, 1)
    x = np.sin(2 * np.pi * np.cumsum(np.broadcast_to(fr, tt.shape)) / SR)
    x = np.tanh(2.2 * x) * np.exp(-tt * 1.2)
    x[-int(0.01 * SR):] *= np.linspace(1, 0, int(0.01 * SR))
    return norm(x)
def bell(f, dur=0.5):
    n = int(dur * SR); tt = np.arange(n) / SR
    x = np.sin(2 * np.pi * f * tt) + 0.4 * np.sin(2 * np.pi * f * 2.76 * tt) * np.exp(-tt * 9) + 0.2 * np.sin(2 * np.pi * f * 5.4 * tt) * np.exp(-tt * 18)
    return norm(x * env_ad(n, 0.003, 0.22))

S16 = BEAT / 4
beats = lambda b: T_DROP + b * BEAT
for b in (0, 2.5, 4, 5.75):
    place(mus, kick(), beats(b), 0.95)
for b in (2, 6):
    place(mus, clap(), beats(b), 0.55)
place(mus, clap(), beats(3.0), 0.0)      # (rest - keeps the half-time trap feel)
# hats: 8ths, then a 16th/32nd roll leading into the cut to the hero angle
hb = 0.0
while beats(hb) < DUR:
    place(mus, hat(), beats(hb), 0.22 if hb % 1 == 0 else 0.15); hb += 0.5
for k in range(8):                         # 32nd roll before T_D
    place(mus, hat(), T_D - 8 * S16 / 2 + k * S16 / 2, 0.08 + 0.02 * k)
place(mus, hat(True), beats(3.5), 0.18)
# 808 line: C1 -> glide up to Eb, back to C
C1, Eb1, G1 = 32.70 * 2, 38.89 * 2, 49.0 * 2
place(mus, bass808(C1, 2.5 * BEAT, None), beats(0), 0.8)
place(mus, bass808(Eb1, 1.5 * BEAT, G1), beats(2.5), 0.8)
place(mus, bass808(C1, 2.0 * BEAT), beats(4), 0.8)
# dark bell motif in 8ths (C minor)
motif = [523.25, 622.25, 783.99, 622.25, 932.33, 783.99, 622.25, 523.25, 783.99, 622.25, 1046.5, 932.33]
for i, f in enumerate(motif):
    place(mus, bell(f), beats(i * 0.5), 0.16)
# pad swell under the drop (detuned saws, low-passed)
n = int((DUR - T_DROP) * SR); tt = np.arange(n) / SR
pad = sum(np.sign(np.sin(2 * np.pi * f * tt * d)) for f in (130.81, 155.56, 196.0) for d in (0.997, 1.003))
pad = onepole_lp(pad, 900) * np.minimum(1, tt / 0.3)
place(mus, norm(pad) * 0.12, T_DROP)
# sidechain-style pump from the kicks
pump = np.ones(N)
for b in (0, 2.5, 4, 5.75):
    i = int(beats(b) * SR); n = int(0.25 * SR)
    pump[i:i + n] *= 1 - 0.55 * np.exp(-np.arange(min(n, N - i)) / SR * 14)
mus = mus * pump
mus[: int(T_DROP * SR)] = 0

# ---------------------------------------------------------------- mix & write
stems = {'ambience': amb, 'foley': fol, 'fx': fx, 'wheel': wheel + pat, 'music': mus}
mix = amb * 1.0 + fol * 1.0 + fx * 0.9 + (wheel + pat) * 1.0 + mus * 0.85
mix[-int(0.004 * SR):] *= np.linspace(1, 0, int(0.004 * SR))   # hard cut at 4.0 s (no click)
os.makedirs('audio', exist_ok=True)
def write(path, x):
    x = np.clip(x, -1, 1)
    st = np.stack([x, x], 1)
    with wave.open(path, 'wb') as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((st * 32767).astype('<i2').tobytes())
for k, v in stems.items():
    write(f'audio/{k}.wav', norm(v, 0.9))
write('audio/mix_raw.wav', norm(mix, 0.95))
print('cue sheet:')
for name, tc in [('snore', 0.05), ('snore', 0.52), ('eyes-open bink', T_EYES), ('eek squeak', 1.02), ('claws/rustle', 1.15),
                 ('riser', 1.12), ('wheel creak', T_DROP - 0.17), ('DROP impact + music', T_DROP), ('whoosh/cut', T_C), ('whoosh/cut', T_D), ('hard cut', 4.0)]:
    print(f'  {tc:5.2f}s  {name}')
