#!/usr/bin/env python3
"""
Painted coverage per frame. A bloom may only ever grow.

This exists because of a failure that reports nothing and looks plausible:
with too many composited layers Chromium stops applying style updates and
screenshots come back showing an arbitrary earlier state. The bloom appeared
to grow, recede, and finally render as frame 0 with no paint at all — no
exception, no console error, and every individual still looked like a
reasonable frame of something. Only the sequence gives it away, so the
sequence is what gets checked.

Coverage is measured against frame 0, not against the palette's parchment:
the woven ground already sits ~40 levels off #EFE3CC, so an absolute
reference reports 100% before anything has happened.

  python3 scripts/check-bloom.py outputs/pv2
"""
import glob
import pathlib
import sys

import numpy as np
from PIL import Image

files = sorted(glob.glob(sys.argv[1] + '/*.png'))
if not files:
    sys.exit(f'no frames in {sys.argv[1]}')

base = np.asarray(Image.open(files[0]).convert('RGB'), dtype=float)
prev, backwards = -1.0, []

for f in files:
    a = np.asarray(Image.open(f).convert('RGB'), dtype=float)
    cov = (np.abs(a - base).max(axis=2) > 18).mean()
    # The bug this script exists for is a CLIFF, not a ripple: when Chromium
    # stops applying style updates a screenshot comes back as an arbitrary
    # EARLIER state, so coverage collapses by tens of points — the first time
    # it bit, a 90%-covered frame rendered as frame 0. Once the bloom
    # plateaus near full frame the paint skin and the petals' own edges move
    # coverage by half a point either way, and a 0.005 tolerance called that
    # a failure on a render that was completely healthy. A check that cries
    # wolf on good output is a check nobody runs. Five points is still far
    # below anything the compositor failure has ever produced.
    slipped = cov < prev - 0.05
    if slipped:
        backwards.append(pathlib.Path(f).stem)
    bar = '#' * round(cov * 40)
    print(f'  {pathlib.Path(f).stem:10s} {cov*100:5.1f}%  {bar}'
          + ('   <-- WENT BACKWARDS' if slipped else ''))
    prev = max(prev, cov)

if backwards:
    sys.exit(f'\ncoverage went backwards at: {", ".join(backwards)}\n'
             'the compositor is dropping updates — check layer count and will-change')
print('\n  monotonic')
