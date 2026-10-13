#!/usr/bin/env python3
"""
Assembles the stills written by contact-sheet.mjs into one sheet.

The contact sheet is the artefact the stop gate is judged on, so it is built at
thumbnail scale on purpose: ~300px wide is about what a Reel occupies on a
phone, and several things that look right at 1080 do not survive the downscale.

  node scripts/contact-sheet.mjs ActI 0 37 47 113 ...
  python3 scripts/sheet.py ActI "ACT I - DEAD" outputs/idea-contact-sheet.png
"""
import glob
import pathlib
import sys
from PIL import Image, ImageDraw

comp = sys.argv[1]
title = sys.argv[2]
out = sys.argv[3]
FPS = 60
COLS, TW, PAD, LAB, HEAD = 5, 300, 16, 30, 40

files = sorted(glob.glob(f'outputs/frames/{comp}/*.png'))
if not files:
    sys.exit(f'no frames in outputs/frames/{comp} — run contact-sheet.mjs first')

first = Image.open(files[0])
th = round(TW * first.height / first.width)
rows = (len(files) + COLS - 1) // COLS
sheet = Image.new('RGB', (COLS * TW + PAD * (COLS + 1),
                          HEAD + rows * (th + LAB + PAD) + PAD), '#171310')
d = ImageDraw.Draw(sheet)
frames = [int(pathlib.Path(f).stem) for f in files]
d.text((PAD, 14),
       f'STILL.  {title}   frames {frames[0]}-{frames[-1]}  '
       f'{frames[0]/FPS:.3f}-{frames[-1]/FPS:.3f}s  {FPS}fps',
       fill='#C8BFAA')

for i, (f, n) in enumerate(zip(files, frames)):
    x = PAD + (i % COLS) * (TW + PAD)
    y = HEAD + PAD + (i // COLS) * (th + LAB + PAD)
    sheet.paste(Image.open(f).resize((TW, th), Image.LANCZOS), (x, y))
    d.text((x, y + th + 8), f'frame {n}   {n/FPS:.3f}s', fill='#8B8475')

sheet.save(out)
print(f'{out}  {sheet.size[0]}x{sheet.size[1]}  {len(files)} frames')
