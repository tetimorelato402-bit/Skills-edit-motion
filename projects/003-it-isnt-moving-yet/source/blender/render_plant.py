#!/usr/bin/env python3
"""
Render Act I from plant.py — stills or a frame range, Cycles on CPU.

There is no GPU in this container (`/dev/dri` is absent) and EEVEE only runs
through llvmpipe, which measured SLOWER than Cycles on a trivial scene, so
Cycles CPU is the only real path here. That is fine for stills and for low-res
motion tests; a full-resolution sequence is a desktop job.

  python3 render_plant.py --times 0,4,8,11.5,13.4 --res 540 --samples 48
  python3 render_plant.py --fps 30 --res 1080 --samples 128 --out frames
"""
import argparse
import os
import sys
import time

import bpy

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from plant import ACT_I_END, Scene


def configure(res, samples):
    sc = bpy.context.scene
    sc.render.engine = 'CYCLES'
    sc.cycles.device = 'CPU'
    sc.cycles.samples = samples
    sc.cycles.use_denoising = True
    # Glass is the expensive part of this shot. Four transmission bounces is
    # enough for a jar with water in it; the default twelve costs a lot and
    # changes nothing anyone can see at Reel size.
    sc.cycles.transmission_bounces = 4
    sc.cycles.max_bounces = 6
    # VOLUME BOUNCES DEFAULTS TO ZERO, and that is not "no indirect volume
    # light" — it is no scattering events at all, so a camera ray crossing the
    # beam can only be absorbed. The shaft rendered as nothing at density 15
    # through a correctly capped, correctly lit cone, which looks identical to
    # a texture bug and is not one.
    sc.cycles.volume_bounces = 2
    # The haze is sampled far finer than it needs to be at this density; a
    # coarser step is free speed and visually identical. Measured at 540:
    # 48 samples 19.9s, 24 samples 11.1s, and the denoiser closes the gap.
    sc.cycles.volume_step_rate = 8.0
    sc.render.resolution_x = res
    sc.render.resolution_y = round(res * 16 / 9)
    sc.render.image_settings.file_format = 'PNG'
    sc.render.film_transparent = False
    sc.view_settings.view_transform = 'AgX'   # filmic highlights on the rim light
    sc.view_settings.look = 'AgX - Medium High Contrast'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="../../outputs/plant")
    ap.add_argument("--times", default="")
    ap.add_argument("--fps", type=int, default=0)
    ap.add_argument("--start", type=int, default=0)
    ap.add_argument("--end", type=int, default=-1)
    ap.add_argument("--res", type=int, default=540)
    ap.add_argument("--samples", type=int, default=48)
    args = ap.parse_args()

    here = os.path.dirname(os.path.abspath(__file__))
    out = os.path.abspath(os.path.join(here, args.out))
    os.makedirs(out, exist_ok=True)

    scene = Scene()
    configure(args.res, args.samples)

    def shoot(t, name):
        scene.set_time(t)
        bpy.context.scene.render.filepath = os.path.join(out, name)
        t0 = time.time()
        bpy.ops.render.render(write_still=True)
        return time.time() - t0

    if args.times:
        for tv in [float(x) for x in args.times.split(",")]:
            el = shoot(tv, f"t{tv:06.3f}".replace('.', '_') + ".png")
            print(f"  {tv:7.3f}s  {el:6.1f}s", flush=True)
    else:
        fps = args.fps or 30
        n = int(round(ACT_I_END * fps))
        end = n if args.end < 0 else min(args.end, n)
        for i in range(args.start, end):
            el = shoot(i / fps, f"f{i:05d}.png")
            if i % 10 == 0:
                print(f"  {i}/{end}  {el:.1f}s/frame", flush=True)


if __name__ == "__main__":
    main()
