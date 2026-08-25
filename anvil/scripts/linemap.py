#!/usr/bin/env python3
"""Group detected segments into VO lines and emit the line->segment map."""
import json

segs = json.load(open("audio/onsets.json"))
# line -> segment indices (1-based), from substructure analysis of the source VO
LINES = [
    ("01_onboard_name.svg",      "It starts with your name.",                    [1]),
    ("02_onboard_phone.svg",     "Verified once. So your circle knows you're real.", [2, 3]),
    ("03_onboard_birthday.svg",  "(no line — quick pass, under 1s)",             []),
    ("04_onboard_commitments.svg","Choose what you're committing to.",           [4]),
    ("05_onboard_places.svg",    "And exactly where you'll do it.",              [5]),
    ("06_home.svg",              "This is your word.",                           [6]),
    ("07_tab_camera.svg",        "The camera stays locked.",                     [7]),
    ("08_arrival_toast.svg",     "Until you actually arrive.",                   [8]),
    ("09_camera_unlocked.svg",   "Then it opens.",                               [9]),
    ("11_circle_live.svg",       "Proof, not words.",                            [10, 11]),
    ("10_friend_arrived.svg",    "Your circle sees it. And you see them.",       [12, 13]),
    ("07_tab_routine.svg",       "Show up enough, and it compounds.",            [14, 15]),
    ("— logo close —",           "SILENT",                                       []),
    ("— tagline —",              "SILENT",                                       []),
]
by_i = {s["i"]: s for s in segs}
rows, prev_end = [], 0.0
out = []
for screen, line, idx in LINES:
    if idx:
        on = by_i[idx[0]]["start"]
        off = by_i[idx[-1]]["end"]
        gap = on - prev_end
        prev_end = off
        out.append(dict(screen=screen, line=line, segs=idx, onset=on, end=off, gap=gap))
    else:
        out.append(dict(screen=screen, line=line, segs=[], onset=None, end=None, gap=None))

w = max(len(r["screen"]) for r in out)
print(f"{'screen':<{w}}  segs      onset      end    dur    gap-before")
print("-" * (w + 48))
for r in out:
    if r["segs"]:
        s = ",".join(map(str, r["segs"]))
        print(f"{r['screen']:<{w}}  {s:<7} {r['onset']:7.3f}  {r['end']:7.3f}  "
              f"{r['end']-r['onset']:5.3f}   {r['gap']:5.3f}")
    else:
        print(f"{r['screen']:<{w}}  {'—':<7} {'—':>7}  {'—':>7}  {'—':>5}   {'—':>5}")
json.dump(out, open("audio/line-map.json", "w"), indent=2)
