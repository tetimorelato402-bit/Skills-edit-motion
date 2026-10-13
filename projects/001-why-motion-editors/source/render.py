#!/usr/bin/env python3
"""Render video.html frame by frame to PNGs via headless Chromium."""
import argparse, os, sys, time
from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
CHROME = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(HERE, "frames"))
    ap.add_argument("--fps", type=int, default=30)
    ap.add_argument("--times", default="")   # comma list -> preview stills instead
    ap.add_argument("--html", default=os.path.join(HERE, "video.html"))
    ap.add_argument("--signal", default="")  # override --signal colour
    ap.add_argument("--start", type=int, default=0)   # frame range, for re-rendering
    ap.add_argument("--end", type=int, default=-1)    # a fix without a full pass
    args = ap.parse_args()

    os.makedirs(args.out, exist_ok=True)
    with sync_playwright() as p:
        br = p.chromium.launch(executable_path=CHROME, args=["--force-color-profile=srgb",
                                                             "--disable-lcd-text",
                                                             "--font-render-hinting=none"])
        pg = br.new_page(viewport={"width": 1080, "height": 1920}, device_scale_factor=1)
        pg.goto("file://" + args.html)
        pg.wait_for_function("window.renderFrame !== undefined")
        pg.evaluate("document.fonts.ready")
        # background images are not in document.images, so decode the plates
        # explicitly — otherwise early frames can render before they are ready
        pg.evaluate("""async () => {
            const files=['plate_ink.png','plate_paper.png','plate_ochre.png','weave.png','pfp.png'];
            await Promise.all(files.map(f => {
                const i = new Image(); i.src = 'tex/' + f;
                return i.decode().catch(() => {});
            }));
        }""")
        time.sleep(1.0)
        if args.signal:
            pg.evaluate(f"document.documentElement.style.setProperty('--signal','{args.signal}')")

        dur = pg.evaluate("window.DUR")

        if args.times:
            for tv in [float(x) for x in args.times.split(",")]:
                pg.evaluate(f"window.renderFrame({tv})")
                pg.screenshot(path=os.path.join(args.out, f"t{tv:05.2f}.png"))
                print("still", tv, flush=True)
        else:
            n = int(round(dur * args.fps))
            end = n if args.end < 0 else min(n, args.end)
            t0 = time.time()
            for i in range(args.start, end):
                pg.evaluate(f"window.renderFrame({i/args.fps})")
                pg.screenshot(path=os.path.join(args.out, f"f{i:05d}.png"))
                if i % 30 == 0:
                    el = time.time() - t0
                    print(f"{i}/{n}  {el:.0f}s elapsed", flush=True)
            print(f"done {end-args.start} frames in {time.time()-t0:.0f}s", flush=True)
        br.close()

if __name__ == "__main__":
    main()
