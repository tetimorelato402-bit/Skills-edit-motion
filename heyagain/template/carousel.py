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
FF = os.environ.get("FFMPEG", f"{SP}/tools/ffmpeg-master-latest-linux64-gpl/bin/ffmpeg")
CHROME = os.environ.get("CHROME", "/opt/pw-browsers/chromium-1194/chrome-linux/chrome")
FONT_FILE = f"{HEY}/assets/Inter-Medium.ttf"
F = Font(FONT_FILE)

W, H = 2160, 2700
ORANGE, CREAM = "0xD8652B", "0xF4EEE4"

Q_SIZE, Q_MAX_W = 150, 1700          # 230px gutter either side
LOGO_SIZE = 264                      # the hero wordmark, on slide 1 and slide 7
SUB_SIZE = 92                        # the line under it — one size fits all eight decks
MARK_SIZE = 62                       # the quiet wordmark on the question slides
SUB_GAP = 96                         # from the wordmark's measured ink foot to that line

CTA_LINE = "play now with a friend for free."
REF_SUB = "questions for your partner"   # the yardstick for centring the hero lockup

Q_CY = H * 0.455                     # optical centre: a touch above true centre
MARK_Y = H - 340
OUT = f"{SP}/carousel"


def esc(s):
    s = s.replace("\\", "\\\\").replace(":", "\\:").replace("'", "’").replace("%", "\\%")
    return s.replace(",", "\\,").replace("[", "\\[").replace("]", "\\]").replace(";", "\\;")


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


def wordmark():
    """Geometry of the big 'hey again.' lockup, measured rather than calculated.

    Returns where to draw the word, where the 3D dot goes as its full stop, and the ink
    foot of the whole thing so the line underneath can hang off something real. The scan
    is a pure-Python sweep of a 2160x2700 gray plane, so it is cached: the lockup is
    identical on all sixteen hero slides.
    """
    global _dot_cache
    if _dot_cache:
        return _dot_cache
    lockup_w = F.width("hey again", LOGO_SIZE) + F.advance(".", LOGO_SIZE)
    x = (W - lockup_w) / 2
    y = H * 0.355
    word = ink_region("hey again", LOGO_SIZE, x, y, W=W, H=H)
    per = ink_region("hey again.", LOGO_SIZE, x, y, x_from=word[2] + 4, W=W, H=H)
    # Centre the whole lockup on the same optical line the question slides use, so the
    # seven slides of a post read as one set rather than the ends floating high. Measured
    # against one reference subline: every deck's line sits at the same y, so using its
    # own ink would move the logo from post to post.
    sub_ink = ink_region(REF_SUB, SUB_SIZE, (W - F.width(REF_SUB, SUB_SIZE)) / 2,
                         word[3] + SUB_GAP, W=W, H=H)
    shift = Q_CY - (word[1] + sub_ink[3]) / 2
    _dot_cache = dict(x=x, y=y + shift,
                      dot=((per[0] + per[2]) / 2, (per[1] + per[3]) / 2 + shift,
                           per[2] - per[0] + 1),
                      foot=word[3] + shift)
    return _dot_cache


def hero(subline, out, dot_png):
    """Slide 1 and slide 7: the wordmark, with one line under it.

    Deliberately the same lockup at both ends — the post opens on the brand and closes on
    it, and only the line underneath changes.
    """
    m = wordmark()
    texts = [("hey again", LOGO_SIZE, m["x"], m["y"], 1.0),
             centred(subline, SUB_SIZE, m["foot"] + SUB_GAP)]
    render(texts, out, dot=m["dot"], dot_png=dot_png)


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

    # --- 1. the title card ------------------------------------------------
    p = f"{d}/{key}_1_title.png"; hero(deck["sub"], p, dot_png); made.append(p)

    # --- 2..6. the five questions ----------------------------------------
    for i, q in enumerate(deck["questions"], start=2):
        lines = wrap(q, Q_SIZE, Q_MAX_W)
        t = block(lines, Q_SIZE, Q_CY) + [centred("hey again.", MARK_SIZE, MARK_Y, 0.55)]
        p = f"{d}/{key}_{i}_q{i - 1}.png"; render(t, p); made.append(p)

    # --- 7. the call to action -------------------------------------------
    p = f"{d}/{key}_7_cta.png"; hero(CTA_LINE, p, dot_png); made.append(p)
    return made


def make_dot(path):
    """The white sphere, same asset the reel uses as its full stop."""
    # Sizes are pinned in pixels against a relative body: an absolutely positioned
    # inset:0 resolves against the viewport, whose height in headless Chrome is not the
    # window height, which silently renders the sphere as an ellipse.
    html = """<meta charset=utf-8><style>
      html{margin:0}
      body{margin:0;position:relative;width:512px;height:512px;background:transparent}
      .s{position:absolute;left:0;top:0;width:512px;height:512px;border-radius:50%;
         background:
           radial-gradient(circle at 36% 30%, #FFFFFF 0%, #FFFFFF 42%, #FBF6EF 62%,
                           #F3EADD 80%, #EADFCE 93%, #E3D6C2 100%);
         box-shadow: inset -22px -26px 48px rgba(176,132,88,.22);}
      .g{position:absolute;left:123px;top:77px;width:154px;height:113px;border-radius:50%;
         background:radial-gradient(ellipse at center, rgba(255,255,255,1), rgba(255,255,255,0) 72%);
         filter:blur(4px);}
    </style><div class=s></div><div class=g></div>"""
    src = f"{path}.html"
    open(src, "w").write(html)
    subprocess.run([CHROME, "--headless", "--disable-gpu", "--no-sandbox", "--hide-scrollbars",
                    "--default-background-color=00000000", "--force-device-scale-factor=1",
                    "--window-size=512,760", f"--screenshot={path}.raw.png", f"file://{src}"],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.run([FF, "-v", "error", "-y", "-i", f"{path}.raw.png",
                    "-vf", "crop=512:512:0:0", path], check=True)
    os.remove(f"{path}.raw.png")
    return path


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    dot_png = make_dot(f"{OUT}/dot.png")
    total = 0
    for deck in DECKS:
        made = build(deck, dot_png)
        total += len(made)
        print(f"ok {deck['key']:14s} {len(made)} slides", flush=True)
    print(f"{total} PNGs -> {OUT}")
