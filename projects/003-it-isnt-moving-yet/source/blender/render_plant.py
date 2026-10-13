#!/usr/bin/env python3
"""
Render the film from plant.py — stills or a frame range, Cycles.

Cycles picks the GPU when one is there (OptiX on an RTX card, else CUDA, else
HIP/Metal/oneAPI) and falls back to CPU otherwise; `DEVICE=CPU` in the
environment forces CPU. The cloud container has no GPU (`/dev/dri` is absent)
and EEVEE only runs there through llvmpipe, which measured SLOWER than Cycles,
so on that machine CPU is the only real path — fine for stills and low-res
motion tests. A full-resolution sequence is a desktop job, and on a desktop this
same script uses the card.

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


def pick_device():
    """
    Enable the best GPU backend the build has, or CPU. Returns the name used.

    The preferences object is what decides; setting `scene.cycles.device =
    'GPU'` with no device enabled in preferences silently renders on CPU, so
    the two are set together here and reported once.
    """
    if os.environ.get("DEVICE", "").upper() == "CPU":
        return 'CPU'
    addon = bpy.context.preferences.addons.get('cycles')
    if addon is None:
        return 'CPU'
    cp = addon.preferences
    for kind in ('OPTIX', 'CUDA', 'HIP', 'METAL', 'ONEAPI'):
        try:
            cp.compute_device_type = kind
        except TypeError:
            continue                      # this build has no such backend
        cp.get_devices()
        gpus = [d for d in cp.devices if d.type == kind]
        if not gpus:
            continue
        for d in cp.devices:
            d.use = d.type == kind        # GPU only: hybrid CPU+GPU is slower
        return kind
    return 'CPU'


def configure(res, samples):
    sc = bpy.context.scene
    sc.render.engine = 'CYCLES'
    dev = pick_device()
    sc.cycles.device = 'CPU' if dev == 'CPU' else 'GPU'
    print(f"  cycles device: {dev}", flush=True)
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
    # Adaptive sampling with the denoiser behind it. The creased petals cost
    # about three times a smooth shell (bump plus transmission is a lot of
    # rays), and almost all of that is spent on the dark two-thirds of a frame
    # lit by one beam — where the variance is already below anything the
    # denoiser cannot finish. A 0.02 threshold with a 6-sample floor spends the
    # budget on the flower.
    sc.cycles.use_adaptive_sampling = True
    sc.cycles.adaptive_threshold = 0.02
    sc.cycles.adaptive_min_samples = 6
    # Thin petals; two transmission bounces is all one ever needs. The jar
    # keeps four via max_bounces above.
    sc.cycles.transmission_bounces = 3
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
    ap.add_argument("--t0", type=float, default=-1.0)
    ap.add_argument("--t1", type=float, default=-1.0)
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
        # The film has TWO Blender stretches, not one — Act I at the front and
        # the last four bars at the back — so a range is given in seconds and
        # frames are numbered from the film's own clock. That keeps f00000 the
        # film's first frame in both passes, which is what lets the two be
        # dropped into one ffmpeg sequence without renumbering anything.
        fps = args.fps or 30
        t0 = args.t0 if args.t0 >= 0 else 0.0
        t1 = args.t1 if args.t1 >= 0 else ACT_I_END
        a, b = int(round(t0 * fps)), int(round(t1 * fps))
        if args.start:
            a = max(a, args.start)
        if args.end >= 0:
            b = min(b, args.end)
        for i in range(a, b):
            el = shoot(i / fps, f"f{i:05d}.png")
            if i % 10 == 0:
                print(f"  {i}/{b}  {el:.1f}s/frame", flush=True)


if __name__ == "__main__":
    main()
