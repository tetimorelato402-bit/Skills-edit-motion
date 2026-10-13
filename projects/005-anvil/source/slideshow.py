#!/usr/bin/env python3
"""
The Anvil deck, cut to its own beat.

Still a slideshow — one screen at a time, held long enough to read. What
changed is that the holds are BARS and not arbitrary seconds, so every
transition lands on a downbeat with a click on it, and the screens arrive on
a spring instead of a dissolve.

Three rules out of Apple's fluid-interface work decide the motion, and they
are the reason this reads as crafted rather than as effects:

  HARMONY   the click, the strike and the first frame of the new screen are
            the same frame. Latency between the senses is what kills the
            illusion, so the cue times come from deck.py, which is also what
            the encoder counts frames against.
  BOUNCE ONLY WHERE MOMENTUM IS IMPLIED
            screens are critically damped — they arrive and stop. Section
            cards, which land on the heavy thunk, get a little overshoot,
            because something with weight behind it is allowed to overshoot.
  HINT IN THE DIRECTION
            everything rises INTO place, so the motion points at where the
            deck is going rather than merely interpolating to it.

The picture is composed from three layers rather than one flat slide, so the
caption can lead the screen by two frames — a caption and a phone arriving
on the identical frame reads as one lump sliding, which is the thing that
makes template decks look like template decks.

    python3 source/sound.py --out outputs/anvil.wav
    python3 source/slideshow.py --out outputs/anvil-slideshow.mp4
"""
import argparse
import math
import os
import subprocess
import sys
from pathlib import Path

import imageio_ffmpeg
import numpy as np
from PIL import Image
from playwright.sync_api import sync_playwright

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from deck import DECK, FPS, FRAMES_PER_BAR, H, W, sequence  # noqa: E402

CHROME = os.environ.get("CHROME", "/opt/pw-browsers/chromium-1194/chrome-linux/chrome")

CSS = """
@font-face{font-family:'Playfair';src:url('fonts/playfair.woff2') format('woff2');font-weight:400 900}
@font-face{font-family:'Inter';src:url('fonts/inter.woff2') format('woff2');font-weight:100 900}
@font-face{font-family:'Plex';src:url('fonts/plexmono.woff2') format('woff2');font-weight:400 700}
*{margin:0;padding:0;box-sizing:border-box}
body{background:#0E0B09}
.slide{width:1080px;height:1920px;position:relative;overflow:hidden;
  background:#151009;color:#E3DACD;font-family:Inter}
.slide::after{content:'';position:absolute;inset:0;
  background:radial-gradient(120% 78% at 50% 36%, rgba(158,124,82,.16), transparent 68%)}
.in{position:absolute;inset:0;z-index:2;display:flex;flex-direction:column;
    align-items:center;padding:104px 0 92px}
.cap{display:flex;flex-direction:column;align-items:center;text-align:center}
.kick{font:500 20px Plex;letter-spacing:.34em;color:#9E7C52;text-transform:uppercase}
.ttl{font-family:Playfair;font-weight:500;font-size:62px;letter-spacing:-.015em;margin-top:22px}
.sub{font:400 25px/1.45 Inter;color:rgba(227,218,205,.62);margin-top:18px;max-width:760px}
/* the shadow has to live INSIDE the element that gets screenshot, or the
   element-clip cuts it off and the phone sits on the ground with a hard edge */
.shotwrap{margin-top:46px;padding:70px}
.shot{width:648px;border-radius:90px;overflow:hidden;
      box-shadow:0 40px 90px rgba(0,0,0,.55), 0 0 0 1px rgba(227,218,205,.09)}
.shot img{width:100%;display:block}
.card .kick{font-size:24px}
.card .ttl{font-size:132px;line-height:1.02;letter-spacing:-.02em;margin-top:34px}
.card .sub{font-size:30px;margin-top:26px}
.mark{position:absolute;left:0;right:0;bottom:52px;text-align:center;z-index:3;
      font:700 26px Playfair;color:rgba(227,218,205,.34)}
.hidein .in,.hidein .mark{display:none}
"""


def build_html(path: Path):
    p = [f"<meta charset='utf-8'><style>{CSS}</style>"]
    p.append("<div class='slide hidein' id='ground'></div>")
    n = 0
    for sec, blurb, screens in DECK:
        p.append(f"<div class='slide card' id='c{n}'>"
                 f"<div class='in' style='justify-content:center'><div class='cap'>"
                 f"<div class='kick'>Anvil</div><div class='ttl'>{sec}</div>"
                 f"<div class='sub'>{blurb}</div></div></div></div>")
        n += 1
        for sid, cap, line in screens:
            p.append(f"<div class='slide' id='s{n}'><div class='in'>"
                     f"<div class='cap'><div class='kick'>{sec}</div>"
                     f"<div class='ttl'>{cap}</div><div class='sub'>{line}</div></div>"
                     f"<div class='shotwrap'><div class='shot'>"
                     f"<img src='../outputs/screens/{sid}.png'></div></div>"
                     f"</div><div class='mark'>Anvil</div></div>")
            n += 1
    path.write_text("\n".join(p))


def spring(n, damping=1.0, response=0.34):
    """Normalised 1 -> 0 settle. Critically damped by default: it arrives and
    it stops. Under-damped only where the sound already implied weight."""
    w = 4.0 / response
    t = np.arange(n) / FPS
    if damping >= 1.0:
        return (1 + w * t) * np.exp(-w * t)
    wd = w * math.sqrt(1 - damping ** 2)
    return np.exp(-damping * w * t) * (np.cos(wd * t) + (damping * w / wd) * np.sin(wd * t))


def over(bg, fg, alpha, x, y):
    """Composite an RGBA layer onto a float RGB canvas at (x, y)."""
    h, w = fg.shape[:2]
    x0, y0 = max(0, x), max(0, y)
    x1, y1 = min(W, x + w), min(H, y + h)
    if x1 <= x0 or y1 <= y0:
        return
    sub = fg[y0 - y:y1 - y, x0 - x:x1 - x]
    a = alpha[y0 - y:y1 - y, x0 - x:x1 - x][..., None]
    bg[y0:y1, x0:x1] = bg[y0:y1, x0:x1] * (1 - a) + sub * a


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="outputs/anvil-slideshow.mp4")
    ap.add_argument("--audio", default="outputs/anvil.wav")
    args = ap.parse_args()

    here = Path(__file__).resolve().parent
    html = here / "slides.html"
    build_html(html)

    layers = {}
    with sync_playwright() as p:
        launch = dict(args=["--force-color-profile=srgb", "--font-render-hinting=none"])
        if os.path.exists(CHROME):
            launch["executable_path"] = CHROME
        br = p.chromium.launch(**launch)
        pg = br.new_page(viewport={"width": W, "height": H}, device_scale_factor=1)
        pg.goto(html.as_uri())
        pg.evaluate("document.fonts.ready")
        pg.wait_for_timeout(700)
        tmp = Path("/tmp/_anvil_layers"); tmp.mkdir(exist_ok=True)

        pg.locator("#ground").screenshot(path=str(tmp / "ground.png"))
        ground = np.asarray(Image.open(tmp / "ground.png").convert("RGB")).astype(np.float32)

        for kind, sid, sec in sequence():
            item = {}
            for part in (("cap", "shotwrap") if kind == "screen" else ("cap",)):
                loc = pg.locator(f"#{sid} .{part}")
                box = loc.bounding_box()
                slide = pg.locator(f"#{sid}").bounding_box()
                f = tmp / f"{sid}_{part}.png"
                loc.screenshot(path=str(f), omit_background=True)
                im = np.asarray(Image.open(f).convert("RGBA")).astype(np.float32)
                item[part] = (im[..., :3], im[..., 3] / 255.0,
                              int(round(box["x"] - slide["x"])),
                              int(round(box["y"] - slide["y"])))
            layers[sid] = item
        br.close()
    print(f"  {len(layers)} slides, layered", flush=True)

    out = Path(args.out); out.parent.mkdir(parents=True, exist_ok=True)
    silent = out.with_suffix(".silent.mp4")
    wr = imageio_ffmpeg.write_frames(
        str(silent), (W, H), fps=FPS, codec="libx264", quality=None,
        macro_block_size=1, ffmpeg_log_level="error",
        output_params=["-crf", "18", "-preset", "slow", "-pix_fmt", "yuv420p",
                       "-profile:v", "high"])
    wr.send(None)

    RISE, LEAD = 22, 2                     # frames of settle, caption lead
    seq = sequence()
    nframes = 0
    for kind, sid, sec in seq:
        item = layers[sid]
        # the two springs: the card lands with weight, a screen just arrives
        s_cap = spring(RISE, 0.86 if kind == "card" else 1.0, 0.36)
        s_shot = spring(RISE, 1.0, 0.34)
        settled = None
        for f in range(FRAMES_PER_BAR):
            # a global breath on the kick — the room reacts to the beat while
            # the UI itself stays absolutely still, which is the only way to
            # cut to music without the interface looking like it is wobbling
            g = 1.0
            if f < 2:
                g = 1.035
            elif f == 2:
                g = 1.015
            elif 36 <= f < 38:
                g = 1.018

            if f >= RISE and settled is not None and g == 1.0:
                wr.send(settled); nframes += 1
                continue

            canvas = ground.copy()
            cap, ca, cx, cy = item["cap"]
            k = f if f < RISE else RISE - 1
            dy = s_cap[k] * 24.0
            over(canvas, cap, ca * min(1.0, (f + 1) / 3.0), cx, cy + int(round(dy)))
            if "shotwrap" in item:
                sh, sa, sx, sy = item["shotwrap"]
                ks = max(0, f - LEAD)
                ks = ks if ks < RISE else RISE - 1
                dys = s_shot[ks] * 46.0
                over(canvas, sh, sa * min(1.0, max(0, f - LEAD + 1) / 4.0),
                     sx, sy + int(round(dys)))
            if g != 1.0:
                canvas *= g
            frame = np.ascontiguousarray(np.clip(canvas, 0, 255).astype(np.uint8))
            if f == RISE - 1 and g == 1.0:
                settled = frame
            wr.send(frame); nframes += 1
    wr.close()
    print(f"  {nframes} frames, {nframes / FPS:.1f}s", flush=True)

    ff = imageio_ffmpeg.get_ffmpeg_exe()
    subprocess.run([ff, "-y", "-v", "error", "-i", str(silent), "-i", args.audio,
                    "-map", "0:v", "-map", "1:a", "-c:v", "copy",
                    "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart",
                    "-shortest", str(out)], check=True)
    silent.unlink()
    info = subprocess.run([ff, "-hide_banner", "-i", str(out)],
                          capture_output=True, text=True).stderr
    print("  " + [l.strip() for l in info.splitlines() if "Duration" in l][0])
    print(f"  -> {out}")


if __name__ == "__main__":
    main()
