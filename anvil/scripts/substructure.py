#!/usr/bin/env python3
"""Finer pass: no merging, to expose word-level pauses inside each kept segment."""
import sys
import numpy as np
sys.path.insert(0, "scripts")
from onsets import decode, envelope, SR

x = decode(sys.argv[1])
env, hop = envelope(x)
thr = 0.03 * env.max()
active = env >= thr
segs, start = [], None
for i, a in enumerate(active):
    if a and start is None: start = i
    elif not a and start is not None:
        segs.append((start*hop/SR, i*hop/SR)); start = None
if start is not None: segs.append((start*hop/SR, len(active)*hop/SR))
# merge only micro-gaps (<80ms = within-word stop consonants)
m = []
for s in segs:
    if m and s[0]-m[-1][1] < 0.08: m[-1][1] = s[1]
    else: m.append(list(s))
print(f"raw bursts (>=0.05s, micro-gaps<80ms merged): {len([s for s in m if s[1]-s[0]>=0.05])}")
for a, b in m:
    if b-a >= 0.05:
        print(f"  {a:7.3f} → {b:7.3f}  ({b-a:5.3f}s)")
