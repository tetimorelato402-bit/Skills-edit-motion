#!/usr/bin/env python3
"""Render room.html frame by frame via headless Chromium + WebGL 2."""
import argparse, os, sys, time, json
from playwright.sync_api import sync_playwright
HERE=os.path.dirname(os.path.abspath(__file__))
CHROME="/opt/pw-browsers/chromium-1194/chrome-linux/chrome"

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(HERE,"frames"))
    ap.add_argument("--fps", type=int, default=60)
    ap.add_argument("--times", default="")
    ap.add_argument("--html", default=os.path.join(HERE,"room.html"))
    ap.add_argument("--bands", default="")          # bands.json from analyse.py
    ap.add_argument("--start", type=int, default=0)
    ap.add_argument("--end", type=int, default=-1)
    a=ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    errs=[]
    with sync_playwright() as p:
        br=p.chromium.launch(executable_path=CHROME, args=["--force-color-profile=srgb"])
        pg=br.new_page(viewport={"width":1080,"height":1920}, device_scale_factor=1)
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.goto("file://"+a.html)
        pg.wait_for_function("window.renderFrame!==undefined")
        if errs: sys.exit("shader/page error:\n"+"\n".join(errs))
        if a.bands:
            pg.evaluate("j=>window.loadBands(j)", json.load(open(a.bands)))
        dur=pg.evaluate("window.DUR")
        if a.times:
            for tv in [float(x) for x in a.times.split(",")]:
                pg.evaluate(f"window.renderFrame({tv})")
                pg.screenshot(path=os.path.join(a.out,f"t{tv:06.2f}.png"))
                print("still",tv,flush=True)
        else:
            n=int(round(dur*a.fps)); end=n if a.end<0 else min(n,a.end)
            t0=time.time()
            for i in range(a.start,end):
                pg.evaluate(f"window.renderFrame({i/a.fps})")
                pg.screenshot(path=os.path.join(a.out,f"f{i:05d}.png"))
                if i%60==0: print(f"{i}/{n}  {time.time()-t0:.0f}s",flush=True)
            print(f"done {end-a.start} frames in {time.time()-t0:.0f}s",flush=True)
        if errs: print("PAGE ERRORS:","\n".join(errs[:5]))
        br.close()

if __name__=="__main__": main()
