"""End-card audio (BRIEF 7.4): switch click at ON, warm rise under the logo, glassy tick per ray,
VO "Blueprint." at ON and "Get paid for thinking." ~1.15 s later. Usage: endcard_mix.py <on_frame_local> <out.wav>"""
import sys, numpy as np, soundfile as sf
FPS, SR = 30, 48000
on = int(sys.argv[1]); out = sys.argv[2]
n = int(4.0 * SR)
mix = np.zeros((n, 2))
def add(path, t, gain=1.0):
    a, sr = sf.read(path, always_2d=True); assert sr == SR, (path, sr)
    i = int(round(t * SR)); j = min(n, i + len(a)); mix[i:j] += gain * a[: j - i]
T = on / FPS
add('sfx/switch_click.wav', T, 0.9)
add('sfx/warm_rise_film01.wav' if on == 10 else 'sfx/warm_rise_film02_04.wav', T, 0.35)
for i in range(1, 6):
    add(f'sfx/ray_tick_{i}.wav', (on + 8 + 5 * (i - 1)) / FPS, 0.45)
add('vo/vo_blueprint_s86.wav', T, 1.0)
add('vo/vo_tagline_s86.wav', T + 1.15, 1.0)
mix[-int(0.5 * SR):] *= np.linspace(1, 0, int(0.5 * SR))[:, None]   # 0.5 s fade on the very end
sf.write(out, mix, SR, subtype='PCM_24')
a, _ = sf.read('vo/vo_tagline_s86.wav'); vo_end = T + 1.15 + len(a) / SR
print(f'VO ends at {vo_end:.2f}s of 4.00s (needs <= 3.00s)')
