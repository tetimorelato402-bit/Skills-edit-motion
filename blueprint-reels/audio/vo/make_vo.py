"""Narrator VO (BRIEF 12.1): Kokoro af_bella, slow, then +1 semitone with formants following (ffmpeg rubberband)."""
import os, subprocess, soundfile as sf
from kokoro_onnx import Kokoro
M = os.path.expanduser('~/.cache/kokoro')
k = Kokoro(f'{M}/kokoro-v1.0.onnx', f'{M}/voices-v1.0.bin')
lines = {'vo_blueprint': 'Blueprint.', 'vo_tagline': 'Get paid for thinking.'}
for name, text in lines.items():
    for sp in (0.86, 0.9, 0.94):
        a, sr = k.create(text, voice='af_bella', speed=sp, lang='en-us')
        raw = f'{name}_s{int(sp*100)}_raw.wav'
        sf.write(raw, a, sr)
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', raw, '-af',
                        'rubberband=pitch=1.06:formant=shifted:pitchq=quality,aresample=48000', '-ac', '2', f'{name}_s{int(sp*100)}.wav'], check=True)
        os.remove(raw)
        d = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', f'{name}_s{int(sp*100)}.wav'], capture_output=True, text=True).stdout)
        print(name, sp, f'{d:.2f}s')
