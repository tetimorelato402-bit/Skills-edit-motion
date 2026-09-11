"""Shared helpers for the Stone Memory pipeline.

Everything here is dependency-light on purpose: numpy, Pillow, and an ffmpeg
binary on PATH. No OpenCV, no librosa, so it installs anywhere in seconds.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np

REPO_ROOT = Path(__file__).resolve().parent.parent
PRESET_DIR = Path(__file__).resolve().parent / "presets"


def die(msg: str, code: int = 1) -> None:
    print(f"error: {msg}", file=sys.stderr)
    sys.exit(code)


def require_ffmpeg() -> None:
    for tool in ("ffmpeg", "ffprobe"):
        if shutil.which(tool) is None:
            die(f"{tool} not found on PATH. Run pipeline/install.sh first.")


def seconds_to_frame(t: float, fps: float) -> int:
    """Snap a timestamp to the nearest frame index. The single source of truth
    for 'which frame is the cue', used by cue.py, render.py and verify.py so
    they can never disagree by a frame."""
    return int(round(t * fps))


def frame_to_seconds(n: int, fps: float) -> float:
    return n / fps


def deep_merge(base: dict, override: dict) -> dict:
    out = dict(base)
    for k, v in override.items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = deep_merge(out[k], v)
        else:
            out[k] = v
    return out


def load_preset(path: str | Path | None) -> dict:
    """Load the default preset, then layer the given preset on top of it.

    A piece preset may itself name a `base` preset (relative to
    pipeline/presets or an absolute path) to extend instead of the default.
    """
    default = json.loads((PRESET_DIR / "default.json").read_text())
    if path is None:
        return default
    p = Path(path)
    if not p.exists():
        alt = PRESET_DIR / (p.name if p.suffix else p.name + ".json")
        if alt.exists():
            p = alt
        else:
            die(f"preset not found: {path}")
    override = json.loads(p.read_text())
    base_name = override.pop("base", None)
    base = load_preset(base_name) if base_name else default
    return deep_merge(base, override)


def decode_audio_mono(path: str | Path, sr: int = 22050, start: float = 0.0,
                      duration: float | None = None) -> np.ndarray:
    """Decode any audio/video file to mono float32 PCM via ffmpeg."""
    require_ffmpeg()
    cmd = ["ffmpeg", "-v", "error", "-nostdin"]
    if start > 0:
        cmd += ["-ss", f"{start:.6f}"]
    cmd += ["-i", str(path)]
    if duration is not None:
        cmd += ["-t", f"{duration:.6f}"]
    cmd += ["-vn", "-ac", "1", "-ar", str(sr), "-f", "f32le", "-"]
    out = subprocess.run(cmd, check=True, capture_output=True).stdout
    return np.frombuffer(out, dtype=np.float32)


def probe_duration(path: str | Path) -> float:
    require_ffmpeg()
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
        check=True, capture_output=True, text=True).stdout.strip()
    return float(out)


def probe_video(path: str | Path) -> dict:
    """Return width, height, fps, nb_frames for the first video stream."""
    require_ffmpeg()
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0",
         "-show_entries", "stream=width,height,r_frame_rate,nb_frames",
         "-of", "json", str(path)],
        check=True, capture_output=True, text=True).stdout
    s = json.loads(out)["streams"][0]
    num, den = s["r_frame_rate"].split("/")
    return {
        "width": int(s["width"]),
        "height": int(s["height"]),
        "fps": float(num) / float(den),
        "nb_frames": int(s.get("nb_frames") or 0),
    }


def ease_in_out(t: np.ndarray | float) -> np.ndarray | float:
    """Smoothstep. Used for the slow push so it never starts or stops abruptly."""
    t = np.clip(t, 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)


def ease_out(t: np.ndarray | float, power: float = 3.0) -> np.ndarray | float:
    """Decelerating curve: fast start, soft landing. Right for an enter/reveal."""
    t = np.clip(t, 0.0, 1.0)
    return 1.0 - (1.0 - t) ** power
