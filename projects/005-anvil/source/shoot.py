#!/usr/bin/env python3
"""
Shoot every artboard in screens.html at real iPhone resolution.

393 x 852 CSS px at deviceScaleFactor 3 is 1179 x 2556, which is exactly what
the TestFlight recording is, so a screen that comes out of here can be held up
against the build with no scaling in between.

    python3 source/shoot.py --out outputs/screens
"""
import argparse
import os
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

CHROME = os.environ.get("CHROME", "/opt/pw-browsers/chromium-1194/chrome-linux/chrome")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--html", default="source/screens.html")
    ap.add_argument("--out", default="outputs/screens")
    ap.add_argument("--scale", type=int, default=3)
    ap.add_argument("--only", default="")
    args = ap.parse_args()

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        launch = dict(args=["--force-color-profile=srgb", "--font-render-hinting=none"])
        if os.path.exists(CHROME):
            launch["executable_path"] = CHROME
        br = p.chromium.launch(**launch)
        pg = br.new_page(viewport={"width": 393, "height": 852},
                         device_scale_factor=args.scale)
        errors = []
        pg.on("pageerror", lambda e: errors.append(str(e)))
        pg.goto(Path(args.html).resolve().as_uri())
        pg.wait_for_function("window.READY === true")
        pg.evaluate("document.fonts.ready")
        pg.wait_for_timeout(400)

        ids = pg.eval_on_selector_all(".screen", "els => els.map(e => e.id)")
        if args.only:
            want = args.only.split(",")
            ids = [i for i in ids if any(w in i for w in want)]
        for sid in ids:
            pg.locator("#" + sid).screenshot(path=str(out / f"{sid}.png"))
            print("  " + sid, flush=True)
        br.close()

        if errors:
            print("PAGE ERRORS:", errors[:3], file=sys.stderr)
            sys.exit(1)
    print(f"{len(ids)} screens -> {out}")


if __name__ == "__main__":
    main()
