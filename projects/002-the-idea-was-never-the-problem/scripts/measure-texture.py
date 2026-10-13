#!/usr/bin/env python3
"""
What the T1 pass actually does to the ground, in 8-bit levels.

The texture opacities in theme.ts are calibrated against this, not guessed: a
percentage in a blend mode is not a look until you measure what comes out the
other side. Sample windows are flat ground only — no square, no type.

  python3 scripts/measure-texture.py outputs/stills/f400.png
"""
import sys
import numpy as np
from PIL import Image

WINDOWS = {
    'ground above the square': (140, 170, 940, 380),
    'ground beside the square': (60, 480, 340, 740),
    'ground below the type':   (140, 1640, 940, 1860),
}

im = np.asarray(Image.open(sys.argv[1]).convert('RGB'), dtype=float)
print(f'{sys.argv[1]}   {im.shape[1]}x{im.shape[0]}')
for name, (x0, y0, x1, y1) in WINDOWS.items():
    w = im[y0:y1, x0:x1]
    lum = w @ [0.2126, 0.7152, 0.0722]
    print(f'  {name:26s} mean RGB {w.reshape(-1,3).mean(0).round(1)}  '
          f'luma sigma {lum.std():5.2f}  p2p {lum.max()-lum.min():5.1f}')
