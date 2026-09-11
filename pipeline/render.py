#!/usr/bin/env python3
"""Render a Stone Memory piece: still + motion + VFX + song, reveal on an exact frame.

Usage:
    python3 pipeline/render.py \
        --image pieces/01-what-the-stone-remembers/base.png \
        --mask  pieces/01-what-the-stone-remembers/mask.png \
        --audio /path/to/song.wav --cue 47.3 \
        --preset pieces/01-what-the-stone-remembers/preset.json \
        --out pieces/01-what-the-stone-remembers/out/final.mp4

Timeline model
--------------
The preset says how long the piece is (`duration`) and where inside it the
reveal happens (`reveal_at`, seconds from the start of the piece). `--cue` is
the timestamp of the chosen moment in the SONG. The renderer starts the song at
`cue - reveal_at`, so the song's moment lands on piece time `reveal_at`, which
is frame `round(reveal_at * fps)`. Every VFX curve is expressed in seconds
relative to that frame, so moving the reveal never re-times the effects.

Frames are generated in numpy and piped raw to ffmpeg together with the audio,
so there is no re-encoding drift and no intermediate image sequence.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from common import (die, ease_in_out, ease_out, frame_to_seconds, load_preset,
                    probe_duration, require_ffmpeg, seconds_to_frame)


# --------------------------------------------------------------------------- #
# image prep
# --------------------------------------------------------------------------- #

def cover_resize(img: Image.Image, w: int, h: int, overscan: float) -> Image.Image:
    """Resize to cover (w*overscan, h*overscan) then centre-crop. The overscan
    gives the push/drift room to move without ever showing an edge."""
    tw, th = int(round(w * overscan)), int(round(h * overscan))
    s = max(tw / img.width, th / img.height)
    nw, nh = int(round(img.width * s)), int(round(img.height * s))
    img = img.resize((nw, nh), Image.LANCZOS)
    left, top = (nw - tw) // 2, (nh - th) // 2
    return img.crop((left, top, left + tw, top + th))


def load_mask(path: str | None, region: str | None, size: tuple[int, int]) -> np.ndarray:
    """Return a float32 HxW mask in [0,1] of the hidden shape, in source-image
    space after cover_resize. Either a PNG (alpha or luminance) or a
    normalised ellipse region 'cx,cy,rx,ry'."""
    w, h = size
    if path:
        m = Image.open(path)
        m = m.getchannel("A") if "A" in m.getbands() else m.convert("L")
        m = m.resize((w, h), Image.LANCZOS)
        return np.asarray(m, dtype=np.float32) / 255.0
    if region:
        cx, cy, rx, ry = (float(v) for v in region.split(","))
        yy, xx = np.mgrid[0:h, 0:w]
        d = ((xx / w - cx) / rx) ** 2 + ((yy / h - cy) / ry) ** 2
        return np.clip(1.0 - (d - 0.8) / 0.4, 0, 1).astype(np.float32)
    die("need --mask PNG or --region cx,cy,rx,ry for the hidden shape")


# --------------------------------------------------------------------------- #
# motion
# --------------------------------------------------------------------------- #

def motion_params(t_norm: float, t: float, cfg: dict) -> tuple[float, float, float]:
    """Scale and translation (px, in output space) for piece time t.

    slow push  : scale eases from zoom_start to zoom_end across the piece
    drift      : a slow linear pan plus a very low-frequency breathing wobble
    """
    z0, z1 = cfg["zoom_start"], cfg["zoom_end"]
    scale = z0 + (z1 - z0) * float(ease_in_out(t_norm))
    dx = cfg["drift_x"] * t_norm + cfg["wobble_px"] * np.sin(2 * np.pi * cfg["wobble_hz"] * t)
    dy = cfg["drift_y"] * t_norm + cfg["wobble_px"] * np.cos(2 * np.pi * cfg["wobble_hz"] * 0.7 * t)
    return scale, float(dx), float(dy)


def transform_layer(src: Image.Image, out_w: int, out_h: int, scale: float,
                    dx: float, dy: float) -> Image.Image:
    """Affine sample of the overscanned source so the output shows a window
    zoomed by `scale` and shifted by (dx, dy), centred. Uses inverse mapping
    through PIL for sub-pixel accuracy without seams."""
    sw, sh = src.size
    # output pixel -> source pixel
    a = 1.0 / scale
    cx_src, cy_src = sw / 2.0 - dx, sh / 2.0 - dy
    c = cx_src - a * out_w / 2.0
    f = cy_src - a * out_h / 2.0
    return src.transform((out_w, out_h), Image.AFFINE, (a, 0, c, 0, a, f), resample=Image.BICUBIC)


# --------------------------------------------------------------------------- #
# VFX
# --------------------------------------------------------------------------- #

def build_crack(mask: np.ndarray, cfg: dict, seed: int) -> list[tuple[float, float]]:
    """A jagged polyline from a frame edge to the centroid of the hidden shape,
    in source-image normalised coords. Deterministic per seed so re-renders
    match exactly."""
    rng = np.random.default_rng(seed)
    h, w = mask.shape
    ys, xs = np.nonzero(mask > 0.5)
    if len(xs) == 0:
        cx, cy = 0.5, 0.5
    else:
        cx, cy = xs.mean() / w, ys.mean() / h
    edge = cfg.get("from_edge", "top")
    start = {"top": (cx + rng.uniform(-0.15, 0.15), 0.0),
             "bottom": (cx + rng.uniform(-0.15, 0.15), 1.0),
             "left": (0.0, cy + rng.uniform(-0.15, 0.15)),
             "right": (1.0, cy + rng.uniform(-0.15, 0.15))}[edge]
    n = int(cfg.get("segments", 18))
    pts = [start]
    x, y = start
    for i in range(1, n + 1):
        t = i / n
        tx, ty = start[0] + (cx - start[0]) * t, start[1] + (cy - start[1]) * t
        jitter = cfg.get("jitter", 0.04) * (1.0 - t)  # calmer as it reaches the shape
        x, y = tx + rng.normal(0, jitter), ty + rng.normal(0, jitter)
        pts.append((x, y))
    pts.append((cx, cy))
    return pts


def crack_layers(pts: list[tuple[float, float]], progress: float, size: tuple[int, int],
                 cfg: dict) -> tuple[np.ndarray, np.ndarray]:
    """Rasterise the crack up to `progress` in [0,1]. Returns (dark, glow)
    float32 HxW layers in source space."""
    w, h = size
    if progress <= 0:
        z = np.zeros((h, w), np.float32)
        return z, z
    total = len(pts) - 1
    k = progress * total
    full = int(np.floor(k))
    seg = [(x * w, y * h) for x, y in pts[: full + 1]]
    if full < total:
        (x0, y0), (x1, y1) = pts[full], pts[full + 1]
        f = k - full
        seg.append(((x0 + (x1 - x0) * f) * w, (y0 + (y1 - y0) * f) * h))
    if len(seg) < 2:
        z = np.zeros((h, w), np.float32)
        return z, z
    core = Image.new("L", (w, h), 0)
    ImageDraw.Draw(core).line(seg, fill=255, width=max(1, int(cfg.get("width_px", 3))))
    dark = np.asarray(core, np.float32) / 255.0
    glow = np.asarray(core.filter(ImageFilter.GaussianBlur(cfg.get("glow_px", 14))), np.float32) / 255.0
    return dark, glow


def light_envelope(dt: float, cfg: dict) -> float:
    """Intensity of the light on the hidden shape, dt = seconds since the cue.

    Hard step at the cue: the first cue frame already carries `hit` so the
    reveal is visible (and verifiable) on that exact frame, then it eases up to
    full over `attack` and settles to `sustain` over `decay`."""
    if dt < 0:
        return 0.0
    hit, attack, decay, sustain = cfg["hit"], cfg["attack"], cfg["decay"], cfg["sustain"]
    if dt <= attack:
        return hit + (1.0 - hit) * float(ease_out(dt / attack))
    d = min(1.0, (dt - attack) / max(decay, 1e-6))
    return 1.0 + (sustain - 1.0) * float(ease_in_out(d))


def spike_envelope(dt: float, length: float) -> float:
    """1 at the cue, easing to 0 over `length` seconds. 0 before the cue."""
    if dt < 0 or length <= 0:
        return 0.0
    return float(1.0 - ease_out(dt / length)) if dt < length else 0.0


def pre_tremor(dt: float, cfg: dict, rng: np.random.Generator) -> float:
    """Anticipation before the cue: a faint flicker that grows as the cue nears."""
    lead = cfg.get("lead", 0.0)
    if lead <= 0 or dt >= 0 or dt < -lead:
        return 0.0
    a = (dt + lead) / lead  # 0 -> 1 approaching the cue
    return cfg.get("amount", 0.0) * a * a * rng.uniform(0.3, 1.0)


def apply_chromatic(frame: np.ndarray, px: float) -> np.ndarray:
    if px < 0.5:
        return frame
    s = int(round(px))
    out = frame.copy()
    out[:, :, 0] = np.roll(frame[:, :, 0], -s, axis=1)
    out[:, :, 2] = np.roll(frame[:, :, 2], s, axis=1)
    return out


def apply_grain(frame: np.ndarray, amount: float, rng: np.random.Generator) -> np.ndarray:
    if amount <= 0:
        return frame
    noise = rng.normal(0.0, amount * 255.0, size=frame.shape[:2]).astype(np.float32)
    return frame + noise[:, :, None]


# --------------------------------------------------------------------------- #
# main render loop
# --------------------------------------------------------------------------- #

def render(args: argparse.Namespace) -> dict:
    require_ffmpeg()
    P = load_preset(args.preset)
    if args.duration:
        P["duration"] = args.duration
    if args.reveal_at is not None:
        P["reveal_at"] = args.reveal_at
    fps = float(args.fps or P["fps"])
    W, H = (int(v) for v in (args.size or P["size"]).split("x"))
    duration = float(P["duration"])
    reveal_at = float(P["reveal_at"])
    if not 0 < reveal_at < duration:
        die(f"reveal_at ({reveal_at}) must fall inside the piece duration ({duration})")

    cue_frame = seconds_to_frame(reveal_at, fps)
    reveal_at = frame_to_seconds(cue_frame, fps)  # snap so audio and video agree
    n_frames = seconds_to_frame(duration, fps)
    audio_start = args.cue - reveal_at
    if audio_start < 0:
        die(f"song cue {args.cue}s is earlier than reveal_at {reveal_at}s; lower reveal_at in the preset")
    if args.audio:
        song_len = probe_duration(args.audio)
        if audio_start + duration > song_len + 1e-3:
            die(f"song ends at {song_len:.2f}s but the piece needs audio until {audio_start + duration:.2f}s")

    mcfg, vcfg = P["motion"], P["vfx"]
    overscan = mcfg["overscan"]

    base = Image.open(args.image).convert("RGB")
    src = cover_resize(base, W, H, overscan)
    sw, sh = src.size
    mask_src = load_mask(args.mask, args.region, (sw, sh))
    # Feathered mask so light never looks like a cut-out.
    feather = vcfg["light"].get("feather_px", 6)
    mask_img = Image.fromarray((mask_src * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(feather))
    crack_pts = build_crack(mask_src, vcfg["crack"], P.get("seed", 7)) if vcfg["crack"].get("enabled", True) else None
    light_rgb = np.array(vcfg["light"]["color"], np.float32).reshape(1, 1, 3)
    rng = np.random.default_rng(P.get("seed", 7))

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    cmd = ["ffmpeg", "-y", "-v", "error", "-nostdin",
           "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-framerate", f"{fps:g}",
           "-i", "-"]
    if args.audio:
        cmd += ["-ss", f"{audio_start:.6f}", "-i", args.audio]
    cmd += ["-map", "0:v:0"]
    if args.audio:
        cmd += ["-map", "1:a:0", "-c:a", "aac", "-b:a", "192k"]
    cmd += ["-t", f"{duration:.6f}", "-c:v", "libx264", "-preset", args.x264_preset,
           "-crf", str(args.crf), "-pix_fmt", "yuv420p", "-movflags", "+faststart",
           "-r", f"{fps:g}", "-vsync", "cfr", str(out_path)]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    assert proc.stdin is not None

    grain_base = vcfg["grain"]["base"]
    print(f"rendering {n_frames} frames @ {fps:g}fps {W}x{H}; cue on frame {cue_frame} "
          f"(t={reveal_at:.4f}s), song starts at {audio_start:.4f}s", file=sys.stderr)

    for n in range(n_frames):
        t = frame_to_seconds(n, fps)
        dt = frame_to_seconds(n - cue_frame, fps)  # seconds since the cue, exact multiple of 1/fps
        t_norm = t / duration

        scale, dx, dy = motion_params(t_norm, t, mcfg)
        # Parallax: the buried layer sits deeper, so it moves a touch less than the surface.
        par = mcfg.get("parallax", 0.0)
        img = transform_layer(src, W, H, scale, dx, dy)
        frame = np.asarray(img, np.float32)

        m = np.asarray(transform_layer(mask_img, W, H, scale, dx * (1 - par), dy * (1 - par)), np.float32) / 255.0

        # ---- VFX, all keyed to dt --------------------------------------
        L = light_envelope(dt, vcfg["light"])
        if L > 0:
            glow = m[:, :, None] * L * vcfg["light"]["strength"]
            frame = frame * (1 - 0.35 * glow) + light_rgb * 255.0 * glow  # screen-ish lift
            halo_px = vcfg["light"].get("halo_px", 0)
            if halo_px:
                halo = np.asarray(Image.fromarray((m * 255).astype(np.uint8)).filter(
                    ImageFilter.GaussianBlur(halo_px)), np.float32) / 255.0
                frame = frame + light_rgb * 255.0 * halo[:, :, None] * L * vcfg["light"].get("halo_strength", 0.25)

        if crack_pts is not None:
            c = vcfg["crack"]
            prog = 0.0 if dt < 0 else min(1.0, (dt + 1.0 / fps) / max(c["draw"], 1e-6))
            if prog > 0:
                dark_s, glow_s = crack_layers(crack_pts, prog, (sw, sh), c)
                dark = np.asarray(transform_layer(Image.fromarray((dark_s * 255).astype(np.uint8)), W, H, scale, dx, dy), np.float32) / 255.0
                glw = np.asarray(transform_layer(Image.fromarray((glow_s * 255).astype(np.uint8)), W, H, scale, dx, dy), np.float32) / 255.0
                frame = frame * (1 - c["darkness"] * dark[:, :, None])
                frame = frame + light_rgb * 255.0 * glw[:, :, None] * c["glow_strength"] * max(L, 0.4)

        chroma = vcfg["chromatic"]["px"] * spike_envelope(dt, vcfg["chromatic"]["length"])
        frame = apply_chromatic(frame, chroma)

        g = grain_base + vcfg["grain"]["spike"] * spike_envelope(dt, vcfg["grain"]["spike_length"])
        g += pre_tremor(dt, vcfg.get("tremor", {}), rng)
        frame = apply_grain(frame, g, rng)

        flash = vcfg.get("flash", {}).get("amount", 0.0) * spike_envelope(dt, vcfg.get("flash", {}).get("length", 0.0))
        if flash > 0:
            frame = frame + flash * 255.0

        proc.stdin.write(np.clip(frame, 0, 255).astype(np.uint8).tobytes())
        if n % int(fps) == 0:
            print(f"  frame {n}/{n_frames}  t={t:5.2f}s  scale={scale:.4f}  L={L:.2f}", file=sys.stderr)

    proc.stdin.close()
    if proc.wait() != 0:
        die("ffmpeg failed")

    report = {
        "out": str(out_path), "fps": fps, "size": f"{W}x{H}", "frames": n_frames,
        "duration": duration, "reveal_at": reveal_at, "cue_frame": cue_frame,
        "song_cue": args.cue, "audio_start": audio_start, "preset": args.preset,
        "image": args.image, "mask": args.mask or args.region, "audio": args.audio,
        "overscan": overscan,
    }
    sidecar = out_path.with_suffix(".sync.json")
    sidecar.write_text(json.dumps(report, indent=2))
    print(f"wrote {out_path} and {sidecar}", file=sys.stderr)
    return report


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--image", required=True, help="locked OpenArt still")
    ap.add_argument("--mask", help="PNG mask of the hidden shape (alpha or luminance)")
    ap.add_argument("--region", help="alternative to --mask: ellipse 'cx,cy,rx,ry' in 0..1 image coords")
    ap.add_argument("--audio", help="the song (any ffmpeg-readable format)")
    ap.add_argument("--cue", type=float, required=True, help="timestamp in the SONG of the reveal moment (s)")
    ap.add_argument("--preset", help="piece preset JSON (layered over presets/default.json)")
    ap.add_argument("--out", required=True)
    ap.add_argument("--fps", type=float)
    ap.add_argument("--size", help="WxH, overrides preset")
    ap.add_argument("--duration", type=float, help="overrides preset")
    ap.add_argument("--reveal-at", type=float, help="seconds into the piece where the cue lands, overrides preset")
    ap.add_argument("--crf", type=int, default=17)
    ap.add_argument("--x264-preset", default="medium")
    args = ap.parse_args()
    if not args.audio:
        print("warning: no --audio given, rendering silent (fine for motion previews, not for a final cut)", file=sys.stderr)
    render(args)


if __name__ == "__main__":
    main()
