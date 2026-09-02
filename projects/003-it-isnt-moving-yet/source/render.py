#!/usr/bin/env python3
"""
Render video.html frame by frame to PNGs via headless Chromium.

Adapted from 001/source/render.py. Two differences, both deliberate:

  - Fonts are self-hosted in fonts/ and loaded by @font-face, not resolved
    through fontconfig. 001 asks for "Inter" by family name, which silently
    falls back to sans-serif on any machine that hasn't installed it — and
    then every measured line width in the film is wrong, with no error.
  - The texture plates are decoded explicitly before the first screenshot.
    CSS background images are not in document.images, so without this the
    first frames render before the paint is ready.

  python3 render.py --times 0,0.96,1.4,1.9,2.4      # preview stills
  python3 render.py --out frames --fps 60           # the range
  python3 render.py --start 60 --end 120            # re-render a range in place
"""
import argparse, os, time
from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
CHROME = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(HERE, "frames"))
    ap.add_argument("--fps", type=int, default=60)
    ap.add_argument("--times", default="")     # comma list -> preview stills
    ap.add_argument("--html", default=os.path.join(HERE, "video.html"))
    ap.add_argument("--start", type=int, default=0)
    ap.add_argument("--end", type=int, default=-1)
    args = ap.parse_args()

    os.makedirs(args.out, exist_ok=True)
    with sync_playwright() as p:
        br = p.chromium.launch(executable_path=CHROME,
                               args=["--force-color-profile=srgb",
                                     "--disable-lcd-text",
                                     "--font-render-hinting=none"])
        pg = br.new_page(viewport={"width": 1080, "height": 1920},
                         device_scale_factor=1)
        errors = []
        pg.on("pageerror", lambda e: errors.append(str(e)))
        pg.goto("file://" + args.html)
        pg.wait_for_function("window.renderFrame !== undefined")
        pg.evaluate("document.fonts.ready")
        pg.evaluate("""async () => {
            const files = ['weave.png','plate_paper.png','plate_ochre.png','plate_ink.png'];
            await Promise.all(files.map(f => {
                const i = new Image(); i.src = 'tex/' + f;
                return i.decode().catch(() => {});
            }));
        }""")
        time.sleep(0.8)

        dur = pg.evaluate("window.DUR")

        if args.times:
            for tv in [float(x) for x in args.times.split(",")]:
                pg.evaluate(f"window.renderFrame({tv})")
                name = f"t{tv:06.3f}".replace('.', '_') + ".png"
                pg.screenshot(path=os.path.join(args.out, name))
                print(f"  {tv:7.3f}s  {name}")
        else:
            n = int(round(dur * args.fps))
            end = n if args.end < 0 else min(args.end, n)
            t0 = time.time()
            for i in range(args.start, end):
                pg.evaluate(f"window.renderFrame({i}/{args.fps})")
                pg.screenshot(path=os.path.join(args.out, f"f{i:05d}.png"))
                if i and i % 20 == 0:
                    el = time.time() - t0
                    done = i - args.start
                    print(f"  {i}/{end}  {el/max(done,1):.2f}s/frame", flush=True)
            print(f"  {end-args.start} frames in {time.time()-t0:.0f}s")

        # A throw inside renderFrame leaves the last good frame on screen and
        # every subsequent screenshot looks plausible. Fail loudly instead.
        if errors:
            raise SystemExit("page errors:\n  " + "\n  ".join(errors))
        br.close()


if __name__ == "__main__":
    main()
