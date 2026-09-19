#!/usr/bin/env python3
"""hey again. — the carousel slides.

Seven 2160x2700 PNGs per deck: the theme card, the five questions, then the call to
action. Same orange, same Inter, same quiet wordmark as the reel, re-proportioned for 4:5.
The full stop in the hero lockups is the 3D dot from the reel, placed by measuring where
the period glyph actually lands rather than by calculating it.
"""
import os, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fontmetrics import Font
from measure import ink_region
from decks import DECKS

HEY = "/home/user/Skills-edit-motion/heyagain"
SP = os.path.dirname(os.path.abspath(__file__))
FF = f"{SP}/tools/ffmpeg-master-latest-linux64-gpl/bin/ffmpeg"
FONT_FILE = f"{HEY}/assets/Inter-Medium.ttf"
F = Font(FONT_FILE)

W, H = 2160, 2700
ORANGE, CREAM = "0xD8652B", "0xF4EEE4"

Q_SIZE, Q_MAX_W = 150, 1700          # 230px gutter either side
LEAD_SIZE = 104
SUBJ_MAX, SUBJ_MAX_W = 264, 1840
LOGO_SIZE = 264
CTA_SIZE = 92
MARK_SIZE = 62

Q_CY = H * 0.455                     # optical centre: a touch above true centre
MARK_Y = H - 340
OUT = f"{SP}/carousel"


def esc(s):
    s = s.replace("\\", "\\\\").replace(":", "\\:").replace("'", "’").replace("%", "\\%")
    return s.replace(",", "\\,").replace("[", "\\[").replace("]", "\\]").replace(";", "\\;")


def fit(text, start, maxw):
    size = start
    while size > 40 and F.width(text, size) > maxw:
        size -= 4
    return size


def wrap(text, size, maxw):
    words, lines, cur = text.split(" "), [], ""
    for w in words:
        trial = w if not cur else cur + " " + w
        if F.width(trial, size) <= maxw or not cur:
            cur = trial
        else:
            lines.append(cur); cur = w
    if cur:
        lines.append(cur)
    return lines


def centred(text, size, y, alpha=1.0):
    return (text, size, (W - F.width(text, size)) / 2, y, alpha)


def block(lines, size, cy, lead=1.22):
    """Lines stacked and centred as a group on `cy`."""
    lh = F.line_h(size) * lead
    top = cy - (lh * (len(lines) - 1) + size) / 2
    return [centred(l, size, top + lh * i) for i, l in enumerate(lines)]


_dot_cache = None


def wordmark_dot():
    """Where the period of the big 'hey again.' lockup sits, measured not calculated.

    The scan is a pure-Python sweep of a 2160x2700 gray plane, so it is cached: the
    lockup is identical on all eight call-to-action slides.
    """
    global _dot_cache
    if _dot_cache:
        return _dot_cache
    lockup_w = F.width("hey again", LOGO_SIZE) + F.advance(".", LOGO_SIZE)
    x = (W - lockup_w) / 2
    y = H * 0.40
    word = ink_region("hey again", LOGO_SIZE, x, y, W=W, H=H)
    per = ink_region("hey again.", LOGO_SIZE, x, y, x_from=word[2] + 4, W=W, H=H)
    _dot_cache = (x, y, (per[0] + per[2]) / 2, (per[1] + per[3]) / 2, per[2] - per[0] + 1)
    return _dot_cache


def render(texts, out, dot=None, dot_png=None):
    draws = [f"drawtext=fontfile='{FONT_FILE}':text='{esc(s)}':fontcolor={CREAM}@{a:.3f}"
             f":fontsize={int(size)}:x={int(round(x))}:y={int(round(y))}"
             for s, size, x, y, a in texts if a > 0.004]
    cmd = [FF, "-v", "error", "-y", "-f", "lavfi", "-i", f"color=c={ORANGE}:s={W}x{H}"]
    if dot:
        cx, cy, d = dot
        d = max(2, int(round(d)))
        cmd += ["-i", dot_png]
        fc = (f"[1]scale={d}:{d},format=rgba[dd];"
              f"[0][dd]overlay={int(round(cx - d / 2))}:{int(round(cy - d / 2))}[v];"
              f"[v]" + ",".join(draws) + "[o]")
        cmd += ["-filter_complex", fc, "-map", "[o]"]
    else:
        cmd += ["-vf", ",".join(draws)]
    cmd += ["-frames:v", "1", out]
    subprocess.run(cmd, check=True)


def build(deck, dot_png):
    key = deck["key"]
    d = f"{OUT}/{key}"
    os.makedirs(d, exist_ok=True)
    made = []

    # --- 1. the theme card ------------------------------------------------
    subj_size = fit(deck["subject"], SUBJ_MAX, SUBJ_MAX_W)
    lead_h = F.line_h(LEAD_SIZE) * 1.05
    top = Q_CY - (lead_h + subj_size) / 2 - 40
    t = [centred(deck["lead"], LEAD_SIZE, top, 0.72),
         centred(deck["subject"], subj_size, top + lead_h),
         centred("hey again.", MARK_SIZE, MARK_Y, 0.55)]
    p = f"{d}/{key}_1_theme.png"; render(t, p); made.append(p)

    # --- 2..6. the five questions ----------------------------------------
    for i, q in enumerate(deck["questions"], start=2):
        lines = wrap(q, Q_SIZE, Q_MAX_W)
        t = block(lines, Q_SIZE, Q_CY) + [centred("hey again.", MARK_SIZE, MARK_Y, 0.55)]
        p = f"{d}/{key}_{i}_q{i - 1}.png"; render(t, p); made.append(p)

    # --- 7. the call to action -------------------------------------------
    lx, ly, pcx, pcy, pd = wordmark_dot()
    cta_y = ly + F.line_h(LOGO_SIZE) + 70
    t = [("hey again", LOGO_SIZE, lx, ly, 1.0),
         centred("play now for free.", CTA_SIZE, cta_y)]
    p = f"{d}/{key}_7_cta.png"; render(t, p, dot=(pcx, pcy, pd), dot_png=dot_png)
    made.append(p)
    return made


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    dot_png = f"{SP}/v6/dot_ex.png"          # the sphere the reels already rendered
    if not os.path.exists(dot_png):
        sys.exit(f"dot asset missing: {dot_png}")
    total = 0
    for deck in DECKS:
        made = build(deck, dot_png)
        total += len(made)
        print(f"ok {deck['key']:14s} {len(made)} slides", flush=True)
    print(f"{total} PNGs -> {OUT}")
