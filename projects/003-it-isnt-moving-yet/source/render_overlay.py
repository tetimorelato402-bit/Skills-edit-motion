#!/usr/bin/env python3
"""
Render a transparent HTML pass and composite it onto an existing frame sequence.

Used for the question, which belongs to Act I — and Act I is Blender, so the
type cannot live in video.html. Rendering it here with alpha and compositing it
onto the rendered frames keeps the typography exact: the same Inter, the same
negative tracking, the same rust on the second "alive". Blender text objects and
ffmpeg's drawtext both get you something that is nearly that and reads as
nearly-that on a 132px line.

  python3 source/render_overlay.py --html source/question.html \
      --frames outputs/plant_hi --fps 24

Frames are matched by INDEX, and both sides count from the film's own clock, so
there is nothing to line up by hand: overlay frame i lands on plant frame i.
Frames outside the overlay's own window are left untouched rather than
rewritten, so this is safe to re-run.
"""
import argparse
import os
import tempfile
from pathlib import Path

from PIL import Image
from playwright.sync_api import sync_playwright

# The container's Chromium, when it is there. Anywhere else (a desktop after
# `playwright install chromium`) Playwright's own copy is used — passing a
# path that does not exist is a hard error, not a fallback.
CHROME = os.environ.get("CHROME", "/opt/pw-browsers/chromium-1194/chrome-linux/chrome")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--html", required=True)
    ap.add_argument("--frames", required=True)
    ap.add_argument("--fps", type=int, default=24)
    ap.add_argument("--tmp", default=os.path.join(tempfile.gettempdir(), "_overlay"))
    args = ap.parse_args()
    os.makedirs(args.tmp, exist_ok=True)

    with sync_playwright() as p:
        launch = dict(args=["--force-color-profile=srgb",
                            "--font-render-hinting=none"])
        if os.path.exists(CHROME):
            launch["executable_path"] = CHROME
        br = p.chromium.launch(**launch)
        pg = br.new_page(viewport={"width": 1080, "height": 1920},
                         device_scale_factor=1)
        errors = []
        pg.on("pageerror", lambda e: errors.append(str(e)))
        pg.goto(Path(args.html).resolve().as_uri())   # a real file: URL on Windows too
        pg.wait_for_function("window.renderFrame !== undefined")
        pg.evaluate("document.fonts.ready")
        dur = pg.evaluate("window.DUR")
        n = int(round(dur * args.fps))
        done = 0
        for i in range(n):
            pg.evaluate(f"window.renderFrame({i}/{args.fps})")
            base = os.path.join(args.frames, f"f{i:05d}.png")
            if not os.path.exists(base):
                continue
            # omit_background is what makes the pass an overlay rather than a
            # card: without it every frame comes back on opaque white and the
            # composite is a white rectangle over Act I.
            shot = os.path.join(args.tmp, f"o{i:05d}.png")
            pg.screenshot(path=shot, omit_background=True)
            over = Image.open(shot).convert("RGBA")
            if over.getextrema()[3][1] == 0:
                continue                      # nothing on this frame
            im = Image.open(base).convert("RGBA")
            # THE OVERLAY IS AUTHORED AT 1080x1920 AND THE FRAMES ARE NOT.
            #
            # Act I renders at 540x960 (see BUILD.md on Cycles cost), and
            # alpha_composite pastes at 1:1 from the top-left and silently
            # crops — so the first version composited the top-left QUARTER of
            # the type at double size, running off the right of every frame. It
            # reads exactly like a font that is too big, which is what sent me
            # to fc-list instead of to the image dimensions.
            #
            # The design stays at 1080 because that is the frame the type was
            # laid out for; it is resampled down to whatever the plate actually
            # is. Act I is lanczos-upscaled back to 1080 at conform time, so the
            # type ends up as soft as the act it sits on, which is right.
            if over.size != im.size:
                over = over.resize(im.size, Image.LANCZOS)
            im.alpha_composite(over)
            im.convert("RGB").save(base)
            done += 1
        br.close()
    if errors:
        raise SystemExit("page errors: " + "; ".join(errors[:3]))
    print(f"  composited onto {done} frames")


if __name__ == "__main__":
    main()
