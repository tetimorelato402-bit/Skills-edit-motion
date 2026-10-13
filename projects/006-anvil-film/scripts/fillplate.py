#!/usr/bin/env python3
"""Build source/ui/fill.png — the plate that fills the type at the clip moments.

The raw check-in photo is a cool indoor snapshot. Poured into letterforms at
Reel size it reads as "the text went pale grey", not as "the text is a
photograph of somebody who turned up" — the whole point of the device. Two
things fix it and both are the same discipline as 001's palette rule:

  * DUOTONE, not the original. Luminance is remapped across INK -> GOLD, so the
    brightest thing inside a letter is gold rather than white. The photo stays a
    photograph and the frame stays in the family.
  * CONTRAST FIRST. Letterforms sample tiny areas; a flat mid-grey crop gives
    every letter the same value and the fill disappears. The plate is stretched
    to its 2nd/98th percentile before it is toned.

    python3 scripts/fillplate.py
"""
import os
import numpy as np
from PIL import Image, ImageOps

HERE=os.path.dirname(os.path.abspath(__file__))
SRC =os.path.join(HERE,'..','source','ui','proof_a.png')
OUT =os.path.join(HERE,'..','source','ui','fill.png')

INK =np.array([0x23,0x1C,0x15], float)
GOLD=np.array([0x9E,0x7C,0x52], float)

im=Image.open(SRC).convert('RGB')
# the body, not the room: the person sits centre-right of the frame and the
# left third is a wall that would fill half the word with nothing
w,h=im.size
im=im.crop((int(w*0.18), int(h*0.02), w, int(h*0.80)))
im=im.resize((1600, int(1600*im.size[1]/im.size[0])), Image.LANCZOS)

g=np.asarray(ImageOps.grayscale(im), float)
lo,hi=np.percentile(g,2), np.percentile(g,98)
u=np.clip((g-lo)/max(1e-6,hi-lo), 0, 1)
u=u**0.86                                   # lift the mids so limbs stay readable
rgb=INK[None,None,:]+(GOLD-INK)[None,None,:]*u[:,:,None]

os.makedirs(os.path.dirname(OUT), exist_ok=True)
Image.fromarray(rgb.astype('uint8')).save(OUT)
print("wrote", OUT, Image.open(OUT).size, round(os.path.getsize(OUT)/1024), "KB")
