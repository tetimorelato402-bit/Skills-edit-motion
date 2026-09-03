#!/usr/bin/env python3
"""
Substitute the fall's two style-glitch frames into a rendered sequence.

This is a SUBSTITUTION, not a composite: for two frames the picture is not the
petal any more, it is one of the languages that is coming. Half-glitching the
petal inside an otherwise intact frame reads as a coloured light on a petal;
replacing the whole frame reads as the film faulting.

  python3 source/render_glitch.py --frames outputs/plant_hi --fps 24

Frame indices come from plant.py's own GLITCH_AT, so the glitches cannot drift
away from the timeline they belong to — move the constant and this follows.
"""
import argparse
import os
import sys

from playwright.sync_api import sync_playwright

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "blender"))
from plant import GLITCH_AT, GLITCH_FR                      # noqa: E402

CHROME = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--frames", required=True)
    ap.add_argument("--fps", type=int, default=24)
    ap.add_argument("--html", default=None)
    args = ap.parse_args()
    html = args.html or os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "glitch.html")

    with sync_playwright() as p:
        br = p.chromium.launch(executable_path=CHROME,
                               args=["--force-color-profile=srgb",
                                     "--font-render-hinting=none"])
        pg = br.new_page(viewport={"width": 1080, "height": 1920},
                         device_scale_factor=1)
        errors = []
        pg.on("pageerror", lambda e: errors.append(str(e)))
        pg.goto("file://" + html)
        pg.wait_for_function("window.renderFrame !== undefined")
        pg.evaluate("document.fonts.ready")
        # the plate has to be decoded before the first screenshot, or the first
        # glitch renders as empty cells — the same trap as the big textures in
        # render.py, and it only ever bites the first frame you take.
        pg.evaluate("""async () => {
            await Promise.all([...document.querySelectorAll('*')]
              .map(e => getComputedStyle(e).backgroundImage)
              .filter(v => v && v.startsWith('url('))
              .map(v => new Promise(r => {
                  const i = new Image();
                  i.onload = i.onerror = r;
                  i.src = v.slice(5, -2);
              })));
        }""")
        wrote = []
        for k, at in enumerate(GLITCH_AT):
            pg.evaluate(f"window.renderFrame({k})")
            first = int(round(at * args.fps))
            for j in range(GLITCH_FR):
                f = os.path.join(args.frames, f"f{first + j:05d}.png")
                if os.path.exists(f):
                    pg.screenshot(path=f)
                    wrote.append(first + j)
        br.close()
    if errors:
        raise SystemExit("page errors: " + "; ".join(errors[:3]))
    print("  glitched frames:", ", ".join(str(w) for w in wrote))


if __name__ == "__main__":
    main()
