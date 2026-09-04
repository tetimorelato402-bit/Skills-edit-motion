#!/usr/bin/env python3
"""
Verify a finished build of "It isn't moving yet" — the checks that a render
which "succeeded" still gets wrong, in one run:

  frames   every frame 0..N-1 present, none black where the room is lit,
           none lit where the room is dark (per the film's own beat sheet)
  loop     the last frame is the first frame (the film is a pure loop)
  mp4      decodes end to end; duration is the film's 27 bars
  silence  the track is silent under the fall, bt(38)-bt(44), and not
           silent either side of it — the petal lets go on the frame the
           music stops, and this is the only place that can be checked
  sheet    a contact sheet, one frame per bar, to outputs/contact.png

Usage: python3 scripts/verify-film.py [outputs/it-isnt-moving-yet.mp4]
Exit status is non-zero if anything fails; the report says what.
"""
import sys, os, glob, re, subprocess, json
from pathlib import Path
import numpy as np
from PIL import Image

P = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(P / "source/blender"))
import plant  # noqa: E402  (bt, FILM_END, the section constants)

FPS = 24
N = round(plant.FILM_END * FPS)
FRAMES = P / "outputs/film"
MP4 = Path(sys.argv[1]) if len(sys.argv) > 1 else P / "outputs/it-isnt-moving-yet.mp4"
FF = subprocess.check_output([sys.executable, "-c",
     "import imageio_ffmpeg;print(imageio_ffmpeg.get_ffmpeg_exe())"]).decode().strip()

fails = []
def check(ok, msg):
    print(("  ok   " if ok else "  FAIL ") + msg)
    if not ok: fails.append(msg)

def lum(i):
    return np.asarray(Image.open(FRAMES / f"f{i:05d}.png").convert("L"), dtype=float)

# ---- frames -----------------------------------------------------------------
have = set(int(re.findall(r"\d+", os.path.basename(x))[-1]) for x in glob.glob(str(FRAMES / "f*.png")))
missing = [i for i in range(N) if i not in have]
check(not missing, f"all {N} frames present" if not missing else f"{len(missing)} frames missing, first {missing[:5]}")

# where the room is lit and where it is dark, from the beat sheet, sampled
# every 12 frames (a beat is ~11 frames, so nothing hides between samples)
lit = (plant.REVEAL[0] + plant.BEAT / 2, plant.COLLAPSE[0])       # studio, past the switch-on
dark = ((plant.bt(0), plant.bt(1)), (plant.BREAK[1], plant.ENDFALL[0] + plant.BEAT / 2))
bad = []
for i in range(0, N, 12):
    if i not in have: continue
    t = i / FPS; m = lum(i).mean()
    if lit[0] <= t < lit[1] and m < 40: bad.append((i, "studio frame is dark", round(m)))
    for a, b in dark:
        if a <= t < b and m > 40: bad.append((i, "dark frame is lit", round(m)))
check(not bad, "lit where lit, dark where dark" if not bad else f"exposure wrong at {bad[:4]}")

# ---- loop -------------------------------------------------------------------
if 0 in have and N - 1 in have:
    d = np.abs(lum(0) - lum(N - 1)).mean()
    check(d < 2.0, f"loop: frame 0 vs frame {N-1} mean|diff| {d:.2f}")

# ---- mp4 --------------------------------------------------------------------
if MP4.exists():
    r = subprocess.run([FF, "-v", "error", "-i", str(MP4), "-f", "null", "-"], capture_output=True, text=True)
    check(r.returncode == 0 and not r.stderr.strip(), f"{MP4.name} decodes clean" + (f": {r.stderr.strip()[:200]}" if r.stderr.strip() else ""))
    probe = subprocess.run([FF.replace("ffmpeg", "ffprobe") if os.path.exists(FF.replace("ffmpeg", "ffprobe")) else FF,
                            "-i", str(MP4)], capture_output=True, text=True).stderr
    m = re.search(r"Duration: (\d+):(\d+):([\d.]+)", probe)
    if m:
        dur = int(m.group(1)) * 3600 + int(m.group(2)) * 60 + float(m.group(3))
        check(abs(dur - plant.FILM_END) < 0.15, f"duration {dur:.2f}s (film is {plant.FILM_END:.2f}s)")
    # ---- silence: decode the audio to raw float and measure RMS per beat --------
    raw = subprocess.run([FF, "-v", "error", "-i", str(MP4), "-vn", "-ac", "1", "-ar", "24000", "-f", "f32le", "-"],
                         capture_output=True).stdout
    a = np.frombuffer(raw, dtype=np.float32)
    def rms(t0, t1):
        s = a[int(t0 * 24000):int(t1 * 24000)]
        return 20 * np.log10(np.sqrt((s ** 2).mean()) + 1e-9)
    fall = rms(plant.FALL[0] + 0.05, plant.FALL[1] - 0.05)
    before = rms(plant.FALL[0] - plant.BAR, plant.FALL[0] - 0.05)
    after = rms(plant.FALL[1] + 0.05, plant.FALL[1] + plant.BAR)
    check(fall < before - 30 and fall < after - 30,
          f"silence under the fall: {fall:.0f} dB, bar before {before:.0f} dB, bar after {after:.0f} dB")
else:
    print(f"  --   {MP4} not built yet; skipping mp4 checks")

# ---- sheet ------------------------------------------------------------------
bars = [round(plant.bt(4 * b) * FPS) + 6 for b in range(27)]
ims = [Image.open(FRAMES / f"f{i:05d}.png").convert("RGB") for i in bars if i in have]
if ims:
    w, h = ims[0].size; w, h = w // 2, h // 2
    sheet = Image.new("RGB", (w * 9, h * 3), "black")
    for k, im in enumerate(ims):
        sheet.paste(im.resize((w, h)), ((k % 9) * w, (k // 9) * h))
    sheet.save(P / "outputs/contact.png")
    print(f"  --   contact sheet: outputs/contact.png ({len(ims)} bars)")

print("\nVERIFY:", "PASS" if not fails else f"{len(fails)} FAILED")
sys.exit(1 if fails else 0)
