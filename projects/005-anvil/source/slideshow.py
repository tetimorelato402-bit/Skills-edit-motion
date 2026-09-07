#!/usr/bin/env python3
"""
The Anvil slideshow.

A slideshow, deliberately: one screen at a time, held long enough to read,
cut on a rhythm. No push-ins, no parallax, no device tilting in 3D. The
screens are the content and an effect would only be something in front of
them — teti asked for a deck, not a showreel.

The one piece of motion is a 5-frame dissolve between screens inside a
section, and a hard cut on the section cards. That is enough to say "next"
without saying "look at me".

Slides are built in HTML and screenshot, rather than composited in PIL,
because the captions have to be set in Playfair and Plex — the app's own
faces — and those are woff2, which PIL cannot open but a browser can.

    python3 source/slideshow.py --out outputs/anvil-slideshow.mp4
"""
import argparse
import os
import subprocess
from pathlib import Path

import imageio_ffmpeg
import numpy as np
from PIL import Image
from playwright.sync_api import sync_playwright

W, H, FPS = 1080, 1920, 30
CHROME = os.environ.get("CHROME", "/opt/pw-browsers/chromium-1194/chrome-linux/chrome")

# section title, then (screen id, caption, one line of what it is)
DECK = [
    ("Onboarding", "Four screens to a circle", [
        ("s01-welcome",    "Prove it",        "The whole pitch in two words and one sentence"),
        ("s02-name",       "Your name",       "The name your circle sees on everything you prove"),
        ("s03-circle",     "Your circle",     "Join with a code, or start one. Four to eight people"),
        ("s04-permission", "Location",        "Asked once, at the end, with the reason in plain terms"),
    ]),
    ("The promise", "Say it before you do it", [
        ("s06-commit",  "New commitment", "Where, how often, who sees it, and the deal in three clauses"),
        ("s07-place",   "New place",      "A drawn map and a 150m ring. Your circle only sees the name"),
        ("s08-promise", "It is binding",  "A receipt for the promise, and everyone has been told"),
    ]),
    ("The proof", "A place, and a photo taken in it", [
        ("s09-watching", "In range",   "Anvil knows you are there, and says so before you shoot"),
        ("s10-captured", "The proof",  "Location, distance and time attached. It cannot be deleted"),
        ("s05-home",     "Standings",  "Streaks with a number on them, and this week under each name"),
    ]),
    ("The consequence", "What a broken promise looks like", [
        ("s11-miss",   "A Miss",       "Announced, in rust, at the top of everybody's board"),
        ("s13-week",   "The week",     "Nobody is ranked mid-week. It settles on Sunday"),
        ("s12-streak", "The record",   "Every square is a day with a photo and a location behind it"),
    ]),
    ("The circle", "The people who notice", [
        ("s14-circle", "Geeked",     "Six people, and what each of them is carrying"),
        ("s15-invite", "The invite", "A code that dies in a day, and only two seats left"),
        ("s16-member", "A member",   "Their commitments, their record, their last proof"),
        ("s17-board",  "All time",   "Longest unbroken run. Volume is not the point"),
    ]),
    ("The routine", "What you owe this week", [
        ("s18-routine",     "Due today",    "One card, one action, and the week under it"),
        ("s20-commitments", "Promises",     "Three live, one retired, each with its own streak"),
        ("s19-detail",      "A commitment", "Eight weeks of it, and the way out if you need one"),
    ]),
    ("You", "Your own record", [
        ("s21-profile",  "You",       "Two misses in nine weeks. Both were Fridays"),
        ("s22-settings", "Settings",  "Short, because there is not much to configure"),
        ("s23-privacy",  "What Anvil knows", "Three things shared, two things never collected"),
    ]),
]

CARD_S, SCREEN_S, FADE = 1.5, 2.6, 5      # seconds, seconds, frames

CSS = """
@font-face{font-family:'Playfair';src:url('fonts/playfair.woff2') format('woff2');font-weight:400 900}
@font-face{font-family:'Inter';src:url('fonts/inter.woff2') format('woff2');font-weight:100 900}
@font-face{font-family:'Plex';src:url('fonts/plexmono.woff2') format('woff2');font-weight:400 700}
*{margin:0;padding:0;box-sizing:border-box}
body{background:#0E0B09}
.slide{width:1080px;height:1920px;position:relative;overflow:hidden;
  background:#151009;color:#E3DACD;font-family:Inter}
/* the ground is the app's own ink, one step darker, so a bone screen sitting
   on it reads as lit rather than as pasted onto a black rectangle */
.slide::after{content:'';position:absolute;inset:0;
  background:radial-gradient(120% 78% at 50% 36%, rgba(158,124,82,.16), transparent 68%)}
.in{position:absolute;inset:0;z-index:2;display:flex;flex-direction:column;
    align-items:center;padding:104px 0 92px}
.kick{font:500 20px Plex;letter-spacing:.34em;color:#9E7C52;text-transform:uppercase}
.ttl{font-family:Playfair;font-weight:500;font-size:62px;letter-spacing:-.015em;margin-top:22px}
.sub{font:400 25px/1.45 Inter;color:rgba(227,218,205,.62);margin-top:18px;max-width:760px;
     text-align:center}
.shot{margin-top:46px;width:648px;border-radius:90px;overflow:hidden;
      box-shadow:0 40px 90px rgba(0,0,0,.55), 0 0 0 1px rgba(227,218,205,.09)}
.shot img{width:100%;display:block}
.card .kick{font-size:24px}
.card .big{font-family:Playfair;font-weight:500;font-size:132px;line-height:1.02;
           letter-spacing:-.02em;margin-top:34px;text-align:center}
.card .sub{font-size:30px;margin-top:26px}
.mark{position:absolute;left:0;right:0;bottom:52px;text-align:center;z-index:3;
      font:700 26px Playfair;color:rgba(227,218,205,.34);letter-spacing:.02em}

"""


def build_html(path: Path):
    parts = [f"<meta charset='utf-8'><style>{CSS}</style>"]
    n = 0
    for sec, blurb, screens in DECK:
        parts.append(
            f"<div class='slide card' id='c{n}'><div class='in' style='justify-content:center'>"
            f"<div class='kick'>Anvil</div><div class='big'>{sec}</div>"
            f"<div class='sub'>{blurb}</div></div></div>")
        n += 1
        for sid, cap, line in screens:
            parts.append(
                f"<div class='slide' id='s{n}'><div class='in'>"
                f"<div class='kick'>{sec}</div><div class='ttl'>{cap}</div>"
                f"<div class='sub'>{line}</div>"
                f"<div class='shot'><img src='../outputs/screens/{sid}.png'></div>"
                f"</div><div class='mark'>Anvil</div></div>")
            n += 1
    path.write_text("\n".join(parts))
    return n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="outputs/anvil-slideshow.mp4")
    ap.add_argument("--slides", default="outputs/slides")
    args = ap.parse_args()

    here = Path(__file__).resolve().parent
    html = here / "slides.html"
    total = build_html(html)
    sl = Path(args.slides)
    sl.mkdir(parents=True, exist_ok=True)

    order = []
    with sync_playwright() as p:
        launch = dict(args=["--force-color-profile=srgb", "--font-render-hinting=none"])
        if os.path.exists(CHROME):
            launch["executable_path"] = CHROME
        br = p.chromium.launch(**launch)
        pg = br.new_page(viewport={"width": W, "height": H}, device_scale_factor=1)
        pg.goto(html.as_uri())
        pg.evaluate("document.fonts.ready")
        pg.wait_for_timeout(700)
        ids = pg.eval_on_selector_all(".slide", "e => e.map(x => x.id)")
        for sid in ids:
            f = sl / f"{sid}.png"
            pg.locator("#" + sid).screenshot(path=str(f))
            order.append((f, CARD_S if sid.startswith("c") else SCREEN_S,
                          sid.startswith("c")))
        br.close()
    print(f"  {len(order)} slides of {total}", flush=True)

    # --- assemble. Frames are piped straight to the encoder: 2000 frames of
    # 1080x1920 PNG on disk is a couple of gigabytes and this container's
    # writable allowance is not that big.
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    wr = imageio_ffmpeg.write_frames(
        str(out), (W, H), fps=FPS, codec="libx264", quality=None,
        macro_block_size=1, ffmpeg_log_level="error",
        output_params=["-crf", "18", "-preset", "slow", "-pix_fmt", "yuv420p",
                       "-profile:v", "high", "-movflags", "+faststart"])
    wr.send(None)
    imgs = [np.asarray(Image.open(f).convert("RGB")) for f, _, _ in order]
    nframes = 0
    for i, (arr, (_, secs, is_card)) in enumerate(zip(imgs, order)):
        hold = int(round(secs * FPS))
        # a section card cuts hard; screens inside a section dissolve, which is
        # what tells you a section has ended without a caption saying so
        if i and not is_card and not order[i - 1][2]:
            prev = imgs[i - 1]
            for k in range(FADE):
                a = (k + 1) / (FADE + 1)
                wr.send(np.ascontiguousarray(
                    (prev * (1 - a) + arr * a).astype(np.uint8)))
            hold -= FADE
            nframes += FADE
        buf = np.ascontiguousarray(arr)
        for _ in range(hold):
            wr.send(buf)
        nframes += hold
    wr.close()
    print(f"  {nframes} frames, {nframes / FPS:.1f}s -> {out}")
    print(subprocess.run(
        [imageio_ffmpeg.get_ffmpeg_exe(), "-hide_banner", "-i", str(out)],
        capture_output=True, text=True).stderr.strip().split("Duration")[1][:78])


if __name__ == "__main__":
    main()
