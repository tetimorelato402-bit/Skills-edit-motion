#!/usr/bin/env python3
"""hey again. — reel.

A white 3D dot drops in, bounces twice, then shrinks into place as the full stop of the
wordmark. Three questions type out at the same pace. On the last one the dot climbs back
out of the question mark, returns to the wordmark, and the call to action lands under it.

1080x1920, 30fps, with a keystroke track synthesised per letter.
"""
import math, os, random, struct, subprocess, sys, wave
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fontmetrics import Font

random.seed(11)

HEY = "/home/user/Skills-edit-motion/heyagain"
SP = os.path.dirname(os.path.abspath(__file__))
FF = f"{SP}/tools/ffmpeg-master-latest-linux64-gpl/bin/ffmpeg"
CHROME = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"
FONT_FILE = f"{HEY}/assets/Inter-Medium.ttf"
F = Font(FONT_FILE)

W, H = 1080, 1920
FPS = 30
ORANGE, CREAM = "0xD8652B", "0xF4EEE4"

LOGO_SIZE = 132          # "hey again" at the top and tail of the reel
Q_SIZE = 70              # the questions
CTA_SIZE = 44            # "play with a partner for free now."
MARK_SIZE = 30           # the quiet wordmark under each question

DOT_BIG = 132            # diameter of the dot while it bounces
CPS = 10                 # keystrokes per second
SR = 44100

from decks import BY_KEY

DECK = BY_KEY[os.environ.get("DECK", "ex")]
SUBJECT = DECK["subject"]
QUESTIONS = DECK["reel"]                   # the post asks five different ones
THEME_LEAD = DECK["lead"]
CTA = "play now for free."


# ---------------------------------------------------------------- easing
def ease_out(x):  return 1 - (1 - x) ** 3
def ease_in(x):   return x * x
def ease_io(x):   return 4 * x ** 3 if x < 0.5 else 1 - (-2 * x + 2) ** 3 / 2
def clamp01(x):   return 0.0 if x < 0 else (1.0 if x > 1 else x)


def seg(t, a, b):
    """Progress of t through the window [a,b]."""
    return clamp01((t - a) / (b - a)) if b > a else 1.0


# ---------------------------------------------------------------- geometry
LOGO_TEXT = "hey again"                     # the full stop is the dot itself, never a glyph
LOGO_W = F.width(LOGO_TEXT, LOGO_SIZE)
DOT_ADV = F.advance(".", LOGO_SIZE)
LOCKUP_W = LOGO_W + DOT_ADV
LOGO_X = (W - LOCKUP_W) / 2
LOGO_Y = H * 0.40
LOGO_BASE = F.baseline(LOGO_Y, LOGO_SIZE)
# drawtext anchors y to the drawn string's own ink box, not to the font ascender, so the
# only reliable way to place the dot is to render the glyph once and look at it.
from measure import ink_region as _ink

_word = _ink(LOGO_TEXT, LOGO_SIZE, LOGO_X, LOGO_Y)
_per = _ink(LOGO_TEXT + ".", LOGO_SIZE, LOGO_X, LOGO_Y, x_from=_word[2] + 3)
PERIOD_CX = (_per[0] + _per[2]) / 2
PERIOD_CY = (_per[1] + _per[3]) / 2
PERIOD_D = _per[2] - _per[0] + 1

CTA_Y = LOGO_Y + F.line_h(LOGO_SIZE) + 46
Q_Y = H * 0.41
MARK_Y = H - 190
Q_MAX_W = 880            # keeps a 100px gutter either side at 1080 wide
THEME_MAX_W = 920
THEME_LEAD_SIZE = 52


def fit_size(text, start, maxw):
    """Largest size at or below `start` that keeps `text` inside `maxw`."""
    size = start
    while size > 24 and F.width(text, size) > maxw:
        size -= 2
    return size


THEME_SIZE = fit_size(SUBJECT, LOGO_SIZE, THEME_MAX_W)


def wrap(text, size, maxw):
    """Greedy wrap on measured width rather than character count."""
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


def q_block_top(lines):
    """Top y of a wrapped question block, so the block sits centred on Q_Y."""
    lh = F.line_h(Q_SIZE) * 1.22
    return Q_Y - (lh * (len(lines) - 1)) / 2


_qcache = {}


def q_mark_dot(lines):
    """Measured centre of the dot at the foot of the trailing '?'."""
    key = tuple(lines)
    if key in _qcache:
        return _qcache[key]
    last = lines[-1]
    x0 = (W - F.width(last, Q_SIZE)) / 2
    lh = F.line_h(Q_SIZE) * 1.22
    top = q_block_top(lines) + lh * (len(lines) - 1)
    noq = _ink(last[:-1], Q_SIZE, x0, top)
    qm = _ink(last, Q_SIZE, x0, top, x_from=noq[2] + 3)
    ylo = qm[1] + int((qm[3] - qm[1]) * 0.72)          # the bowl sits above; take the foot
    d = _ink(last, Q_SIZE, x0, top, x_from=noq[2] + 3, y_from=ylo)
    out = ((d[0] + d[2]) / 2, (d[1] + d[3]) / 2, d[2] - d[0] + 1)
    _qcache[key] = out
    return out


# ---------------------------------------------------------------- the dot asset
def make_dot(path):
    """A white sphere with a soft key light, rendered once and scaled per frame."""
    # Sizes are pinned in pixels and positioned against a relative body: an absolutely
    # positioned inset:0 resolves against the viewport, whose height in headless Chrome is
    # not the window height, which silently rendered the sphere as an ellipse.
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
    src = f"{path}.html"          # per-deck, so eight renders can run side by side
    open(src, "w").write(html)
    subprocess.run([CHROME, "--headless", "--disable-gpu", "--no-sandbox", "--hide-scrollbars",
                    "--default-background-color=00000000", "--force-device-scale-factor=1",
                    "--window-size=512,760", f"--screenshot={path}.raw.png", f"file://{src}"],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    # headless Chrome's viewport height is not the window height, so the shot is taller or
    # shorter than asked for; crop back to the square the sphere was drawn in.
    subprocess.run([FF, "-v", "error", "-y", "-i", f"{path}.raw.png",
                    "-vf", "crop=512:512:0:0", path], check=True)
    os.remove(f"{path}.raw.png")
    return path


# ---------------------------------------------------------------- timeline
class Reel:
    def __init__(self):
        self.audio = []      # (time, kind)
        self.marks = {}      # named timestamps, for readability
        self.build()

    def build(self):
        t = 0.0
        # --- dot drops and bounces twice -------------------------------------
        self.t_fall = (t, t + 0.40); t += 0.40
        self.t_up1 = (t, t + 0.26); t += 0.26
        self.t_dn1 = (t, t + 0.26); t += 0.26
        self.t_up2 = (t, t + 0.17); t += 0.17
        self.t_dn2 = (t, t + 0.17); t += 0.17
        self.audio += [(self.t_fall[1], "thud"), (self.t_dn1[1], "thud2"), (self.t_dn2[1], "thud3")]
        t += 0.22                                        # a beat, sitting still
        # --- dot shrinks into the full stop, wordmark arrives -----------------
        self.t_form = (t, t + 0.70); t += 0.70
        self.audio.append((self.t_form[0] + 0.10, "swell"))
        self.t_logo_hold = (t, t + 0.50); t += 0.50
        self.t_logo_out = (t, t + 0.25); t += 0.25

        # --- the deck announces itself ----------------------------------------
        self.t_theme_in = (t, t + 0.42); t += 0.42
        self.audio.append((self.t_theme_in[0] + 0.02, "swell"))
        self.t_theme_hold = (t, t + 1.15); t += 1.15
        self.t_theme_out = (t, t + 0.30); t += 0.30

        # --- three questions, identical pace ----------------------------------
        self.qs = []
        for i, q in enumerate(QUESTIONS):
            start = t
            lines = wrap(q, Q_SIZE, Q_MAX_W)
            keys = "".join(lines)          # the break space is not a keystroke
            for k, ch in enumerate(keys):
                self.audio.append((start + k / CPS + random.uniform(-0.014, 0.014),
                                   "space" if ch == " " else "key"))
            type_end = start + len(keys) / CPS
            hold_end = type_end + 0.90
            last = i == len(QUESTIONS) - 1
            out_end = hold_end if last else hold_end + 0.22
            self.qs.append(dict(q=q, lines=lines, keys=keys, start=start, type_end=type_end,
                                hold_end=hold_end, out_end=out_end, last=last))
            t = out_end

        # --- the dot climbs out of the '?' and rebuilds the wordmark ----------
        self.t_emerge = (t, t + 0.34); t += 0.34
        self.audio.append((self.t_emerge[0], "pop"))
        self.t_travel = (t, t + 0.62); t += 0.62
        self.t_cta = (t, t + 0.40); t += 0.40
        self.audio.append((self.t_travel[1] - 0.05, "chime"))
        self.t_end = t + 1.55
        self.total = self.t_end

    # ---- per-frame state ------------------------------------------------
    def state(self, t):
        texts, dot = [], None
        rest_y = H * 0.42

        # dot bouncing
        if t < self.t_form[0]:
            if t <= self.t_fall[1]:
                p = ease_in(seg(t, *self.t_fall))
                y = -DOT_BIG + (rest_y + DOT_BIG) * p
            elif t <= self.t_up1[1]:
                y = rest_y - 0.20 * H * ease_out(seg(t, *self.t_up1))
            elif t <= self.t_dn1[1]:
                y = rest_y - 0.20 * H * (1 - ease_in(seg(t, *self.t_dn1)))
            elif t <= self.t_up2[1]:
                y = rest_y - 0.075 * H * ease_out(seg(t, *self.t_up2))
            elif t <= self.t_dn2[1]:
                y = rest_y - 0.075 * H * (1 - ease_in(seg(t, *self.t_dn2)))
            else:
                y = rest_y
            dot = (W / 2, y, DOT_BIG, 1.0)

        # dot shrinking into the full stop while the wordmark fades up
        elif t < self.t_logo_out[1]:
            if t < self.t_form[1]:
                p = ease_io(seg(t, *self.t_form))
                cx = W / 2 + (PERIOD_CX - W / 2) * p
                cy = rest_y + (PERIOD_CY - rest_y) * p
                d = DOT_BIG + (PERIOD_D - DOT_BIG) * p
                a_logo = clamp01((p - 0.35) / 0.5)
            else:
                cx, cy, d, a_logo = PERIOD_CX, PERIOD_CY, PERIOD_D, 1.0
            fade = 1 - ease_in(seg(t, *self.t_logo_out))
            dot = (cx, cy, d, fade)
            if a_logo > 0:
                texts.append((LOGO_TEXT, LOGO_SIZE, LOGO_X, LOGO_Y, a_logo * fade))

        # the deck title: "questions for" over the subject, rising as it fades up
        if self.t_theme_in[0] <= t < self.t_theme_out[1]:
            a_in = ease_out(seg(t, *self.t_theme_in))
            a_out = 1 - ease_in(seg(t, *self.t_theme_out))
            a = a_in * a_out
            rise = (1 - a_in) * 42
            lead_y = Q_Y - 96 + rise
            subj_y = Q_Y - 96 + F.line_h(THEME_LEAD_SIZE) * 1.05 + rise
            texts.append((THEME_LEAD, THEME_LEAD_SIZE,
                          (W - F.width(THEME_LEAD, THEME_LEAD_SIZE)) / 2, lead_y, a * 0.72))
            texts.append((SUBJECT, THEME_SIZE,
                          (W - F.width(SUBJECT, THEME_SIZE)) / 2, subj_y, a))
            texts.append((LOGO_TEXT + ".", MARK_SIZE,
                          (W - F.width(LOGO_TEXT + ".", MARK_SIZE)) / 2, MARK_Y, 0.55 * a))

        # questions
        for qi in self.qs:
            if qi["start"] <= t < qi["out_end"]:
                keys, lines = qi["keys"], qi["lines"]
                n = len(keys) if t >= qi["type_end"] else min(len(keys), int((t - qi["start"]) * CPS) + 1)
                a = 1.0 if t < qi["hold_end"] else 1 - ease_in(seg(t, qi["hold_end"], qi["out_end"]))
                lh = F.line_h(Q_SIZE) * 1.22
                top = q_block_top(lines)
                used = 0
                for li, line in enumerate(lines):
                    vis = max(0, min(len(line), n - used))
                    used += len(line)
                    if vis:
                        shown = line[:vis]
                        # each line stays centred on its own finished width, so the
                        # text does not creep sideways as it is typed
                        x = (W - F.width(line, Q_SIZE)) / 2
                        texts.append((shown, Q_SIZE, x, top + lh * li, a))
                texts.append((LOGO_TEXT + ".", MARK_SIZE,
                              (W - F.width(LOGO_TEXT + ".", MARK_SIZE)) / 2, MARK_Y, 0.55 * a))

        # the dot leaves the '?' and travels back to the wordmark
        if self.t_emerge[0] <= t:
            last_lines = self.qs[-1]["lines"]
            qx, qy, qd = q_mark_dot(last_lines)
            if t < self.t_emerge[1]:
                p = ease_out(seg(t, *self.t_emerge))
                lh = F.line_h(Q_SIZE) * 1.22
                top = q_block_top(last_lines)
                for li, line in enumerate(last_lines):
                    texts.append((line, Q_SIZE, (W - F.width(line, Q_SIZE)) / 2, top + lh * li, 1 - p))
                texts.append((LOGO_TEXT + ".", MARK_SIZE,
                              (W - F.width(LOGO_TEXT + ".", MARK_SIZE)) / 2, MARK_Y, 0.55 * (1 - p)))
                dot = (qx, qy, qd + (DOT_BIG * 0.42 - qd) * p, 1.0)
            else:
                p = ease_io(seg(t, *self.t_travel))
                d0 = DOT_BIG * 0.42
                cx = qx + (PERIOD_CX - qx) * p
                cy = qy + (PERIOD_CY - qy) * p
                # arcs up on the way across rather than sliding flat
                cy -= math.sin(math.pi * p) * 120
                d = d0 + (PERIOD_D - d0) * p
                dot = (cx, cy, d, 1.0)
                a_logo = clamp01((p - 0.3) / 0.5)
                if a_logo > 0:
                    texts.append((LOGO_TEXT, LOGO_SIZE, LOGO_X, LOGO_Y, a_logo))
                a_cta = ease_out(seg(t, *self.t_cta))
                if a_cta > 0:
                    texts.append((CTA, CTA_SIZE, (W - F.width(CTA, CTA_SIZE)) / 2, CTA_Y, a_cta))
        return texts, dot


# ---------------------------------------------------------------- rendering
def esc(s):
    s = s.replace("\\", "\\\\").replace(":", "\\:").replace("'", "’").replace("%", "\\%")
    return s.replace(",", "\\,").replace("[", "\\[").replace("]", "\\]").replace(";", "\\;")


def render_frame(texts, dot, dot_png, out):
    draws = [f"drawtext=fontfile='{FONT_FILE}':text='{esc(s)}':fontcolor={CREAM}@{a:.3f}"
             f":fontsize={int(size)}:x={int(round(x))}:y={int(round(y))}"
             for s, size, x, y, a in texts if a > 0.004]
    cmd = [FF, "-v", "error", "-y", "-f", "lavfi", "-i", f"color=c={ORANGE}:s={W}x{H}"]
    if dot and dot[2] >= 1 and dot[3] > 0.004:
        cx, cy, d, a = dot
        d = max(2, int(round(d)))
        cmd += ["-i", dot_png]
        fc = (f"[1]scale={d}:{d},format=rgba,colorchannelmixer=aa={a:.3f}[d];"
              f"[0][d]overlay={int(round(cx - d / 2))}:{int(round(cy - d / 2))}[v]")
        fc += (";[v]" + ",".join(draws) + "[o]") if draws else ";[v]null[o]"
        cmd += ["-filter_complex", fc, "-map", "[o]"]
    else:
        cmd += ["-vf", ",".join(draws) if draws else "null"]
    cmd += ["-frames:v", "1", out]
    subprocess.run(cmd, check=True)


# ---------------------------------------------------------------- audio
import sfx

# The approved level. One identical cached clack per letter is what made the first pass
# sound like a machine, so every strike now comes from a 14-variant bank at its own
# velocity; these numbers put the typing at roughly -17 dBFS, under the read rather than
# over it.
SFX_LEVELS = dict(master=0.47, key_level=0.17, space_level=0.11)


def build_audio(events, total, path):
    return sfx.render(events, total, path, bank=sfx.Bank(seed=5, **SFX_LEVELS))


# ---------------------------------------------------------------- main
def main():
    out_dir = f"{SP}/v6"; key = DECK["key"]; frames = f"{out_dir}/frames_{key}"
    os.makedirs(frames, exist_ok=True)
    dot_png = make_dot(f"{out_dir}/dot_{key}.png")

    reel = Reel()
    n = int(round(reel.total * FPS))
    print(f"timeline {reel.total:.2f}s  {n} frames  {len(reel.audio)} audio events", flush=True)
    for i in range(n):
        t = i / FPS
        texts, dot = reel.state(t)
        render_frame(texts, dot, dot_png, f"{frames}/f{i:05d}.png")
        if i % 60 == 0:
            print(f"  frame {i}/{n}  t={t:.2f}", flush=True)

    wav = build_audio(reel.audio, reel.total, f"{out_dir}/track_{key}.wav")
    mp4 = f"{out_dir}/heyagain_reel_{key}.mp4"
    subprocess.run([FF, "-v", "error", "-y", "-framerate", str(FPS), "-i", f"{frames}/f%05d.png",
                    "-i", wav, "-map", "0:v", "-map", "1:a",
                    "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
                    "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", "-shortest", mp4],
                   check=True)
    print(f"ok {mp4} {os.path.getsize(mp4)//1024} KB  {reel.total:.2f}s")


if __name__ == "__main__":
    main()
