#!/usr/bin/env python3
"""hey again. — carousel builder.

Reads captions/posts.json (25 posts x 5 slides), finds a Pexels background for every
scene slide, downloads it into backgrounds/, and renders output/postXX/1..5.

Brand rules (CLAUDE.md) applied here:
  * every slide is 4:5, 2160x2700
  * background fills the frame, slightly blurred, tangerine #D8652B overlay at 35 %
  * caption in cream #F4EEE4, Inter Medium, centred
  * slides 1 and 3 are 3-second videos with a silent audio track
    (Pexels video, or the photo with a slow ffmpeg zoom when no good video exists)
  * "flat tangerine, no scene" slides are a solid tangerine card with the caption only
  * no logos, no mirror, no people, no visible text in backgrounds

Usage:
  python3 build.py                      # build everything
  python3 build.py --posts 3 7 25       # only some posts
  python3 build.py --no-fetch           # render from what is already in backgrounds/
  python3 build.py --dry-run            # search + pick + report, no downloads, no renders

Environment / config:
  PEXELS_API_KEY  in the environment or in .env next to this file
  FFMPEG          optional path to the ffmpeg binary (default: "ffmpeg" on PATH)
  picks.json      optional overrides: {"photos": {"3/1": 8387437}, "videos": {"3/1": 33931911},
                  "queries": {"2/1": ["vintage cassette recorder nightstand", ...]}}

Only the standard library + ffmpeg (with libfreetype and libx264) are required.
"""
from __future__ import annotations

import argparse
import http.client
import json
import os
import re
import shutil
import ssl
import subprocess
import sys
import textwrap
import time
import urllib.parse

HERE = os.path.dirname(os.path.abspath(__file__))
POSTS_JSON = os.path.join(HERE, "captions", "posts.json")
FONT = os.path.join(HERE, "assets", "Inter-Medium.ttf")
BG_DIR = os.path.join(HERE, "backgrounds")
OUT_DIR = os.path.join(HERE, "output")
PICKS_JSON = os.path.join(HERE, "picks.json")
FAILED_TXT = os.path.join(HERE, "failed.txt")
SUMMARY_MD = os.path.join(HERE, "summary.md")

# ---- brand constants ----------------------------------------------------------------
W, H = 2160, 2700
TANGERINE = "0xD8652B"
CREAM = "0xF4EEE4"
OVERLAY_ALPHA = 0.35
BLUR_SIGMA = 6            # "slightly blurred"
TARGET_LUMA = 96          # backgrounds are levelled to this mean before the overlay goes on
SATURATION = 0.90         # let the tangerine, not the photo, carry the colour
CAPTION_SHADOW = "0x1A0A04"   # near-black, warmed so it sits inside the tangerine palette
CAPTION_BORDER_W, CAPTION_BORDER_A = 5, 0.25
CAPTION_SHADOW_A, CAPTION_SHADOW_Y = 0.35, 4
VIDEO_SECONDS = 3
FPS = 30
CAPTION_SIZE = 120        # px, Inter Medium
CAPTION_SIZE_FLAT = 190   # "cream text large" on the flat cards
LINE_SPACING = 1.25
WRAP_CHARS = 24           # ~ what fits at CAPTION_SIZE with side margins
VIDEO_SLIDES = (1, 3)

# ---- Pexels selection rules ---------------------------------------------------------
MIN_PHOTO_WIDTH = 3840
MIN_VIDEO_HEIGHT = 1080
PER_PAGE = 10
UA = "Mozilla/5.0 (X11; Linux x86_64) heyagain-carousel/1.0"

STOP = set("""a an the of on in at with and or from to by for one two three four half out
frame blurred blurry close left right up down over under next into through face-down
face-up dent thrown pulled off like its it's that this""".split())
MOOD_WORDS = ["night", "dusk", "dawn", "sunset", "sunrise", "evening", "morning", "rain",
              "neon", "golden", "glow", "lamp", "dark", "light", "window"]
PEOPLE = re.compile(
    r"\b(man|men|woman|women|person|people|boy|girl|guy|lady|hand|hands|face|faces|couple|teen|"
    r"teenager|teenagers|child|children|kid|kids|adolescent|male|female|adult|adults|portrait|selfie|"
    r"model|crowd|someone|holding|sitting|standing|walking|wearing|feet|foot|legs|leg|arm|arms|finger|"
    r"fingers|silhouette|silhouettes|figure|figures|family|friends|baby|smiling|posing|player|worker|"
    r"businessman|businesswoman|driver|passenger|passengers|student|students|traveler|travelers|"
    r"tourist|tourists|nurse|doctor|patient|barista|chef|athlete|dancer|bride|groom|mother|father|"
    r"parent|parents|son|daughter|body|skin|lap|shoulder|hair|eye|eyes|reading|typing|writing|"
    r"working|cooking|drinking|relaxing|lying|sleeping|resting)\b", re.I)
TEXTY = re.compile(
    r"\b(sign|signs|signage|text|letters|lettering|words|word|writing|written|logo|logos|billboard|"
    r"billboards|poster|label|typography|quote|message|caption|title|headline|handwriting|handwritten|"
    r"note|notes|newspaper|magazine|menu|calendar|advertisement|neon sign|displays|slogan)\b"
    r"|['‘’\"“”][A-Za-z][^'‘’\"“”]{0,40}['‘’\"“”]", re.I)
MOODY = re.compile(
    r"\b(dark|night|dusk|evening|sunset|sunrise|dawn|dim|dimly|moody|shadow|shadows|low light|"
    r"warm light|golden|rain|rainy|fog|foggy|mist|misty|glow|glowing|lamp|candle|neon|twilight|cozy|"
    r"dramatic|atmospheric|blue hour|lit|light|soft light|natural light|monochrome)\b", re.I)


def log(msg: str) -> None:
    print(msg, flush=True)


# =====================================================================================
# Pexels
# =====================================================================================
class Pexels:
    """Tiny HTTP client with one persistent (keep-alive) connection per host.

    Reusing connections matters: every request otherwise opens a fresh TLS tunnel through the
    egress proxy, and a few hundred of those in a row is what gets a host throttled.
    """

    def __init__(self, key: str):
        self.key = key
        self.calls = 0
        self._conns: dict[str, http.client.HTTPSConnection] = {}
        proxy = os.environ.get("HTTPS_PROXY") or os.environ.get("https_proxy")
        self._proxy = urllib.parse.urlparse(proxy) if proxy else None
        self._ctx = ssl.create_default_context()      # honours SSL_CERT_FILE / system store

    def _conn(self, host: str) -> http.client.HTTPSConnection:
        c = self._conns.get(host)
        if c is None:
            if self._proxy:
                c = http.client.HTTPSConnection(self._proxy.hostname, self._proxy.port or 80,
                                                context=self._ctx, timeout=120)
                c.set_tunnel(host, 443)
            else:
                c = http.client.HTTPSConnection(host, 443, context=self._ctx, timeout=120)
            self._conns[host] = c
        return c

    def _drop(self, host: str) -> None:
        c = self._conns.pop(host, None)
        if c is not None:
            try:
                c.close()
            except Exception:  # noqa: BLE001
                pass

    def _get(self, url: str, binary: bool = False, dest: str | None = None):
        last = None
        for attempt in range(4):
            u = urllib.parse.urlparse(url)
            host, path = u.hostname, (u.path or "/") + (f"?{u.query}" if u.query else "")
            try:
                c = self._conn(host)
                c.request("GET", path, headers={"Authorization": self.key, "User-Agent": UA, "Accept": "*/*"})
                r = c.getresponse()
                self.calls += 1
                if r.status in (301, 302, 303, 307, 308):
                    r.read()
                    url = urllib.parse.urljoin(url, r.getheader("Location", ""))
                    continue
                if r.status == 429:
                    r.read()
                    time.sleep(15 * (attempt + 1))
                    last = f"HTTP 429"
                    continue
                if r.status != 200:
                    body = r.read()[:200]
                    raise RuntimeError(f"HTTP {r.status} {body!r}")
                if dest:
                    tmp = dest + ".part"
                    with open(tmp, "wb") as f:
                        shutil.copyfileobj(r, f, 1 << 20)
                    os.replace(tmp, dest)
                    return dest
                data = r.read()
                return data if binary else json.loads(data)
            except (http.client.HTTPException, OSError, ssl.SSLError) as e:
                # stale keep-alive, proxy hiccup, tunnel refused: reconnect and try again
                last = e
                self._drop(host)
                time.sleep(2 * (attempt + 1))
            except RuntimeError as e:
                last = e
                if str(e).startswith("HTTP 4"):
                    break
                time.sleep(2 * (attempt + 1))
        raise RuntimeError(f"pexels request failed: {url} ({last})")

    def search_photos(self, query: str):
        q = urllib.parse.urlencode({"query": query, "per_page": PER_PAGE, "orientation": "landscape"})
        return self._get(f"https://api.pexels.com/v1/search?{q}").get("photos", [])

    def search_videos(self, query: str):
        q = urllib.parse.urlencode({"query": query, "per_page": PER_PAGE, "orientation": "landscape"})
        return self._get(f"https://api.pexels.com/videos/search?{q}").get("videos", [])

    def photo(self, pid: int):
        return self._get(f"https://api.pexels.com/v1/photos/{pid}")

    def video(self, vid: int):
        return self._get(f"https://api.pexels.com/videos/videos/{vid}")

    def download(self, url: str, dest: str):
        return self._get(url, dest=dest)


def keywords(prompt: str) -> list[str]:
    """Turn a background_prompt into 2–4 Pexels keywords: first content nouns + one mood word."""
    p = prompt.lower().replace("2am", "night").replace("tv ", "television ")
    words = [w.strip(",.") for w in re.split(r"[ ,]+", p) if w.strip(",.")]
    words = [w for w in words if w not in STOP and not w.isdigit() and len(w) > 2]
    seen, kws = set(), []
    for w in words:
        if w not in seen:
            seen.add(w)
            kws.append(w)
    core = [w for w in kws if w not in MOOD_WORDS][:3]
    mood = [w for w in kws if w in MOOD_WORDS][:1]
    out = (core + mood)[:4]
    if len(out) < 2:
        out = kws[:2] if len(kws) >= 2 else kws + ["moody"]
    return out


def luminance(hexcol: str) -> float:
    h = hexcol.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def judge_photo(p: dict, kws: list[str]) -> tuple[float, list[str]]:
    alt = p.get("alt") or ""
    rejects = []
    if p["width"] < MIN_PHOTO_WIDTH:
        rejects.append(f"width {p['width']} < {MIN_PHOTO_WIDTH}")
    if p["width"] <= p["height"]:
        rejects.append("not landscape")
    m = PEOPLE.search(alt)
    if m:
        rejects.append(f"people ({m.group(0)})")
    m = TEXTY.search(alt)
    if m:
        rejects.append(f"text ({m.group(0)})")
    score = 2.0 * sum(1 for k in kws if k in alt.lower())
    score += 1.0 * len(set(x.lower() for x in MOODY.findall(alt)))
    score += max(0.0, (140 - luminance(p.get("avg_color") or "#808080")) / 40.0)   # darker = moodier
    return round(score, 2), rejects


def slug_words(url: str) -> str:
    s = url.rstrip("/").split("/")[-1]
    return re.sub(r"-\d+$", "", s).replace("-", " ")


def best_video_file(v: dict) -> dict | None:
    files = [f for f in v.get("video_files", [])
             if f.get("width") and f.get("height") and f["height"] >= MIN_VIDEO_HEIGHT
             and f["width"] > f["height"] and f.get("file_type") == "video/mp4"]
    files.sort(key=lambda f: (f["height"], f["width"]))       # smallest file that is still >= 1080p
    return files[0] if files else None


def judge_video(v: dict, kws: list[str]) -> tuple[float, list[str]]:
    desc = slug_words(v["url"])
    rejects = []
    if best_video_file(v) is None:
        rejects.append("no landscape file >= 1080p")
    if v.get("duration", 0) < VIDEO_SECONDS:
        rejects.append("shorter than 3 s")
    if v["width"] <= v["height"]:
        rejects.append("not landscape")
    m = PEOPLE.search(desc)
    if m:
        rejects.append(f"people ({m.group(0)})")
    m = TEXTY.search(desc)
    if m:
        rejects.append(f"text ({m.group(0)})")
    score = 2.0 * sum(1 for k in kws if k in desc) + 1.0 * len(set(x.lower() for x in MOODY.findall(desc)))
    return round(score, 2), rejects


# =====================================================================================
# ffmpeg rendering
# =====================================================================================
def ffmpeg_bin() -> str:
    return os.environ.get("FFMPEG") or shutil.which("ffmpeg") or "ffmpeg"


def run(cmd: list[str]) -> None:
    r = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"ffmpeg failed ({r.returncode}): {r.stderr.strip()[-2000:]}")


def ff_escape(s: str) -> str:
    """Escape a string for use inside a drawtext text= option."""
    s = s.replace("\\", "\\\\").replace(":", "\\:").replace("'", "’").replace("%", "\\%")
    return s.replace(",", "\\,").replace("[", "\\[").replace("]", "\\]").replace(";", "\\;")


def caption_filter(caption: str, size: int) -> str:
    """One drawtext per wrapped line, block centred in the frame."""
    lines = textwrap.wrap(caption, width=WRAP_CHARS if size == CAPTION_SIZE else 14) or [caption]
    line_h = int(size * LINE_SPACING)
    block_h = line_h * (len(lines) - 1) + size
    top = (H - block_h) // 2
    parts = []
    for i, line in enumerate(lines):
        y = top + i * line_h
        parts.append(f"drawtext=fontfile='{FONT}':text='{ff_escape(line)}':fontcolor={CREAM}"
                     f":fontsize={size}:x=(w-text_w)/2:y={y}"
                     f":borderw={CAPTION_BORDER_W}:bordercolor={CAPTION_SHADOW}@{CAPTION_BORDER_A}"
                     f":shadowcolor={CAPTION_SHADOW}@{CAPTION_SHADOW_A}:shadowx=0:shadowy={CAPTION_SHADOW_Y}")
    return ",".join(parts)


def mean_luma(src: str) -> float:
    """Average luminance (0-255) of the first frame, via signalstats. 128 if it cannot be read."""
    r = subprocess.run([ffmpeg_bin(), "-v", "error", "-i", src, "-vf",
                        "scale=320:-1,signalstats,"
                        "metadata=print:key=lavfi.signalstats.YAVG:file=-",
                        "-frames:v", "1", "-f", "null", "-"],
                       stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
    m = re.search(r"YAVG=([\d.]+)", r.stdout or "")
    return float(m.group(1)) if m else 128.0


def exposure(src: str) -> float:
    """Gain that brings this background to TARGET_LUMA before the tangerine goes on.

    A 35 % overlay over a near-white photo reads as pale peach rather than tangerine, so the
    backgrounds are levelled first: that is what makes all 125 slides read as the same orange.
    The correction is multiplicative, like a camera exposure, because an additive shift moves
    the shadows just as much as the highlights and leaves bright photos looking washed out.
    """
    y = mean_luma(src)
    # colorlevels' output white point tops out at 1.0, so this only ever darkens; a background
    # that is already below the target is left alone (it reads as deep tangerine as it is).
    return round(max(0.45, min(1.0, TARGET_LUMA / max(y, 1.0))), 3)


def bg_filter(gain: float = 1.0) -> str:
    """Cover-fit to 2160x2700, slight blur, levelled exposure, tangerine 35 % overlay."""
    return (f"scale={W}:{H}:force_original_aspect_ratio=increase:flags=lanczos,crop={W}:{H},"
            f"gblur=sigma={BLUR_SIGMA},"
            f"colorlevels=romax={gain}:gomax={gain}:bomax={gain},eq=saturation={SATURATION},"
            f"format=rgba,"
            f"drawbox=x=0:y=0:w=iw:h=ih:color={TANGERINE}@{OVERLAY_ALPHA}:t=fill,format=yuv420p")


def render_photo(src: str, caption: str, out: str) -> None:
    vf = f"{bg_filter(exposure(src))},{caption_filter(caption, CAPTION_SIZE)}"
    run([ffmpeg_bin(), "-v", "error", "-y", "-i", src, "-vf", vf, "-frames:v", "1", "-q:v", "2", out])


def render_flat(caption: str, out: str) -> None:
    vf = f"format=yuv420p,{caption_filter(caption, CAPTION_SIZE_FLAT)}"
    run([ffmpeg_bin(), "-v", "error", "-y", "-f", "lavfi", "-i", f"color=c={TANGERINE}:s={W}x{H}:d=1",
         "-vf", vf, "-frames:v", "1", "-q:v", "2", out])


def _encode_args(out: str) -> list[str]:
    return ["-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-r", str(FPS),
            "-c:a", "aac", "-b:a", "96k", "-shortest", "-movflags", "+faststart", "-t", str(VIDEO_SECONDS), out]


def render_video(src: str, caption: str, out: str, start: float = 0.0) -> None:
    """3-second video slide from a Pexels clip + silent stereo track."""
    fc = f"[0:v]fps={FPS},{bg_filter(exposure(src))},{caption_filter(caption, CAPTION_SIZE)}[v]"
    run([ffmpeg_bin(), "-v", "error", "-y", "-ss", f"{start:.2f}", "-t", str(VIDEO_SECONDS + 0.5), "-i", src,
         "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo", "-filter_complex", fc,
         "-map", "[v]", "-map", "1:a", *_encode_args(out)])


def render_photo_zoom(src: str, caption: str, out: str) -> None:
    """3-second slow push-in on a photo (fallback when no good Pexels video exists)."""
    frames = VIDEO_SECONDS * FPS
    zoom = f"min(1+0.06*on/{frames},1.06)"
    big_w, big_h = W * 2, H * 2       # oversample so zoompan does not jitter
    fc = (f"[0:v]scale={big_w}:{big_h}:force_original_aspect_ratio=increase:flags=lanczos,crop={big_w}:{big_h},"
          f"zoompan=z='{zoom}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={frames}:s={W}x{H}:fps={FPS},"
          f"gblur=sigma={BLUR_SIGMA},"
          f"colorlevels=romax={exposure(src)}:gomax={exposure(src)}:bomax={exposure(src)},"
          f"eq=saturation={SATURATION},format=rgba,"
          f"drawbox=x=0:y=0:w=iw:h=ih:color={TANGERINE}@{OVERLAY_ALPHA}:t=fill,format=yuv420p,"
          f"{caption_filter(caption, CAPTION_SIZE)}[v]")
    run([ffmpeg_bin(), "-v", "error", "-y", "-loop", "1", "-framerate", str(FPS), "-i", src,
         "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo", "-filter_complex", fc,
         "-map", "[v]", "-map", "1:a", *_encode_args(out)])


# =====================================================================================
# per-slide pipeline
# =====================================================================================
def is_flat(prompt: str) -> bool:
    return prompt.strip().lower().startswith("flat tangerine")


def meta_path(post: int, slide: int) -> str:
    return os.path.join(BG_DIR, f"post{post:02d}_s{slide}.json")


def load_meta(post: int, slide: int) -> dict | None:
    p = meta_path(post, slide)
    if os.path.exists(p):
        try:
            m = json.load(open(p))
            if m.get("file") and os.path.exists(os.path.join(BG_DIR, m["file"])):
                return m
        except Exception:
            pass
    return None


def pick_photo(px: Pexels, post: int, slide: int, prompt: str, picks: dict) -> tuple[dict | None, dict]:
    """Returns (chosen photo dict or None, search report)."""
    key = f"{post}/{slide}"
    report = {"queries": [], "considered": 0, "rejected": {}}
    kws = keywords(prompt)
    queries = [" ".join(kws)] + list(picks.get("queries", {}).get(key, []))
    forced = picks.get("photos", {}).get(key)
    seen: dict[int, dict] = {}
    if forced:
        # a reviewed pick needs no search: fetch it straight by id
        try:
            p = px.photo(forced)
            p["_score"], p["_forced"] = judge_photo(p, kws)[0], True
            report["forced_direct"] = True
            return p, report
        except Exception as e:  # noqa: BLE001
            report["forced_error"] = str(e)
    for q in queries:
        photos = px.search_photos(q)
        report["queries"].append({"query": q, "results": len(photos)})
        for p in photos:
            seen.setdefault(p["id"], p)
        if forced and forced in seen:
            break
        # stop at the first query that yields at least one usable photo unless a pick is forced
        if not forced and any(not judge_photo(p, kws)[1] for p in photos):
            break
    if forced and forced not in seen:
        try:
            seen[forced] = px.photo(forced)
        except Exception as e:  # noqa: BLE001
            report["forced_error"] = str(e)
    report["considered"] = len(seen)
    scored = []
    for p in seen.values():
        s, rej = judge_photo(p, kws)
        if rej:
            report["rejected"][p["id"]] = rej
        else:
            scored.append((s, p))
    if forced and forced in seen:
        p = seen[forced]
        p["_score"], p["_forced"] = judge_photo(p, kws)[0], True
        return p, report
    if not scored:
        return None, report
    scored.sort(key=lambda t: -t[0])
    p = scored[0][1]
    p["_score"] = scored[0][0]
    return p, report


def pick_video(px: Pexels, post: int, slide: int, prompt: str, picks: dict) -> tuple[dict | None, dict]:
    key = f"{post}/{slide}"
    report = {"queries": [], "considered": 0, "rejected": {}}
    kws = keywords(prompt)
    queries = [" ".join(kws)] + list(picks.get("video_queries", {}).get(key, []))
    forced = picks.get("videos", {}).get(key)
    if forced == 0:                      # explicit "use the photo zoom" override
        report["skipped"] = "picks.json says no video for this slide"
        return None, report
    seen: dict[int, dict] = {}
    if forced:
        try:
            v = px.video(forced)
            v["_score"], v["_forced"] = judge_video(v, kws)[0], True
            report["forced_direct"] = True
            return v, report
        except Exception as e:  # noqa: BLE001
            report["forced_error"] = str(e)
    for q in queries:
        vids = px.search_videos(q)
        report["queries"].append({"query": q, "results": len(vids)})
        for v in vids:
            seen.setdefault(v["id"], v)
        if forced and forced in seen:
            break
        if not forced and any(not judge_video(v, kws)[1] for v in vids):
            break
    if forced and forced not in seen:
        try:
            seen[forced] = px.video(forced)
        except Exception as e:  # noqa: BLE001
            report["forced_error"] = str(e)
    report["considered"] = len(seen)
    scored = []
    for v in seen.values():
        s, rej = judge_video(v, kws)
        if rej:
            report["rejected"][v["id"]] = rej
        else:
            scored.append((s, v))
    if forced and forced in seen:
        v = seen[forced]
        v["_score"], v["_forced"] = judge_video(v, kws)[0], True
        return v, report
    if not scored:
        return None, report
    scored.sort(key=lambda t: -t[0])
    v = scored[0][1]
    v["_score"] = scored[0][0]
    return v, report


def fetch_background(px: Pexels, post: int, slide: int, prompt: str, picks: dict, dry_run: bool) -> dict:
    """Search, pick and download the background for one slide. Returns the meta dict."""
    cached = load_meta(post, slide)
    if cached and not dry_run:
        return cached
    meta = {"post": post, "slide": slide, "prompt": prompt, "keywords": keywords(prompt)}
    want_video = slide in VIDEO_SLIDES
    video, vreport = (None, None)
    if want_video:
        video, vreport = pick_video(px, post, slide, prompt, picks)
        meta["video_search"] = vreport
    photo, preport = (None, None)
    if not video:
        photo, preport = pick_photo(px, post, slide, prompt, picks)
        meta["photo_search"] = preport
    if video:
        f = best_video_file(video)
        meta.update(kind="video", pexels_id=video["id"], pexels_url=video["url"], credit=video["user"]["name"],
                    source_url=f["link"], source_size=f"{f['width']}x{f['height']}", duration=video["duration"],
                    file=f"post{post:02d}_s{slide}.mp4", score=video.get("_score"), forced=video.get("_forced", False))
    elif photo:
        meta.update(kind="photo", pexels_id=photo["id"], pexels_url=photo["url"], credit=photo["photographer"],
                    source_url=photo["src"]["original"], source_size=f"{photo['width']}x{photo['height']}",
                    alt=photo.get("alt", ""), file=f"post{post:02d}_s{slide}.jpg", score=photo.get("_score"),
                    forced=photo.get("_forced", False))
    else:
        raise RuntimeError(f"no usable Pexels result for post{post:02d}/{slide} ({prompt!r})")
    if dry_run:
        return meta
    dest = os.path.join(BG_DIR, meta["file"])
    if not os.path.exists(dest) or os.path.getsize(dest) < 1000:
        px.download(meta["source_url"], dest)
    with open(meta_path(post, slide), "w") as fh:
        json.dump(meta, fh, indent=1)
    return meta


def build_slide(post: int, slide: int, caption: str, prompt: str, meta: dict | None) -> str:
    out_dir = os.path.join(OUT_DIR, f"post{post:02d}")
    os.makedirs(out_dir, exist_ok=True)
    if is_flat(prompt):
        if slide in VIDEO_SLIDES:
            # a flat card that must be a video: 3 s of solid tangerine + caption + silent track
            out = os.path.join(out_dir, f"{slide}.mp4")
            fc = f"[0:v]format=yuv420p,{caption_filter(caption, CAPTION_SIZE_FLAT)}[v]"
            run([ffmpeg_bin(), "-v", "error", "-y", "-f", "lavfi", "-i", f"color=c={TANGERINE}:s={W}x{H}:r={FPS}",
                 "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo", "-filter_complex", fc,
                 "-map", "[v]", "-map", "1:a", *_encode_args(out)])
            return out
        out = os.path.join(out_dir, f"{slide}.jpg")
        render_flat(caption, out)
        return out
    assert meta is not None
    src = os.path.join(BG_DIR, meta["file"])
    if slide in VIDEO_SLIDES:
        out = os.path.join(out_dir, f"{slide}.mp4")
        if meta["kind"] == "video":
            # start a little into the clip so we skip any fade-in, but never past the end
            start = 0.0
            dur = float(meta.get("duration") or 0)
            if dur >= VIDEO_SECONDS + 2:
                start = 1.0
            render_video(src, caption, out, start=start)
        else:
            render_photo_zoom(src, caption, out)
        return out
    out = os.path.join(out_dir, f"{slide}.jpg")
    render_photo(src, caption, out)
    return out


def verify_output(path: str, slide: int) -> None:
    """Cheap sanity check with ffprobe (if present): size and, for videos, duration + audio."""
    probe = shutil.which("ffprobe") or os.path.join(os.path.dirname(ffmpeg_bin()), "ffprobe")
    if not os.path.exists(probe):
        return
    r = subprocess.run([probe, "-v", "error", "-show_entries", "stream=codec_type,width,height,duration",
                        "-of", "json", path], stdout=subprocess.PIPE, text=True)
    info = json.loads(r.stdout or "{}").get("streams", [])
    vid = [s for s in info if s.get("codec_type") == "video"]
    if not vid or int(vid[0]["width"]) != W or int(vid[0]["height"]) != H:
        raise RuntimeError(f"bad output geometry for {path}: {vid}")
    if slide in VIDEO_SLIDES:
        if not any(s.get("codec_type") == "audio" for s in info):
            raise RuntimeError(f"video slide has no audio track: {path}")
        d = float(vid[0].get("duration") or 0)
        if not (VIDEO_SECONDS - 0.2 <= d <= VIDEO_SECONDS + 0.2):
            raise RuntimeError(f"video slide duration {d:.2f}s != {VIDEO_SECONDS}s: {path}")


# =====================================================================================
# main
# =====================================================================================
def load_key() -> str:
    key = os.environ.get("PEXELS_API_KEY", "").strip()
    env_file = os.path.join(HERE, ".env")
    if not key and os.path.exists(env_file):
        for line in open(env_file):
            line = line.strip()
            if line.startswith("PEXELS_API_KEY="):
                key = line.split("=", 1)[1].strip().strip('"').strip("'")
    if not key or key == "paste_your_key_here":
        sys.exit("PEXELS_API_KEY missing: export it or put it in .env")
    return key


def write_summary(posts: list[dict], results: dict, failed: list[str]) -> None:
    lines = ["# hey again. — build summary", ""]
    n_ok = sum(1 for r in results.values() if r.get("ok"))
    lines.append(f"Slides built: **{n_ok} / {len(results)}**" + (f" — {len(failed)} failed (see failed.txt)" if failed else ""))
    lines.append("")
    lines.append("Every scene background is a Pexels asset (photo or video) used under the Pexels licence; the URL")
    lines.append("links to the asset page and the photographer/videographer is credited in the last column.")
    lines.append("")
    for post in posts:
        pid = post["post"]
        lines.append(f"## post{pid:02d} — {post['title']}  ({post['emotion']}, {post['tint']})")
        lines.append("")
        lines.append("| slide | type | file | caption | keywords | background | Pexels URL | credit |")
        lines.append("|---|---|---|---|---|---|---|---|")
        for i, sl in enumerate(post["slides"], 1):
            r = results.get((pid, i), {})
            m = r.get("meta") or {}
            typ = "video" if i in VIDEO_SLIDES else "photo"
            if is_flat(sl["background_prompt"]):
                bg, url, credit, kw = "flat tangerine card", "—", "—", "—"
            elif m:
                bg = f"Pexels {m['kind']} #{m['pexels_id']} ({m.get('source_size', '')})"
                if i in VIDEO_SLIDES and m["kind"] == "photo":
                    bg += ", slow zoom"
                url = m["pexels_url"]
                credit = m.get("credit", "")
                kw = ", ".join(m.get("keywords", []))
            else:
                bg, url, credit, kw = "**FAILED**", "—", "—", ", ".join(keywords(sl["background_prompt"]))
            fname = os.path.relpath(r["out"], HERE) if r.get("out") else ("**FAILED**: " + r.get("error", "")[:120])
            lines.append(f"| {i} | {typ} | {fname} | {sl['caption']} | {kw} | {bg} | {url} | {credit} |")
        lines.append("")
    with open(SUMMARY_MD, "w") as fh:
        fh.write("\n".join(lines))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--posts", nargs="*", type=int, help="post numbers to build (default all)")
    ap.add_argument("--no-fetch", action="store_true", help="do not touch Pexels; render from backgrounds/")
    ap.add_argument("--dry-run", action="store_true", help="search and pick only; print the plan")
    ap.add_argument("--retries", type=int, default=2, help="extra attempts per slide (default 2)")
    args = ap.parse_args()

    posts = json.load(open(POSTS_JSON))
    if args.posts:
        posts = [p for p in posts if p["post"] in set(args.posts)]
    picks = json.load(open(PICKS_JSON)) if os.path.exists(PICKS_JSON) else {}
    os.makedirs(BG_DIR, exist_ok=True)
    os.makedirs(OUT_DIR, exist_ok=True)
    px = None if args.no_fetch else Pexels(load_key())

    results: dict[tuple[int, int], dict] = {}
    failed: list[str] = []
    t0 = time.time()
    for post in posts:
        pid = post["post"]
        for i, sl in enumerate(post["slides"], 1):
            caption, prompt = sl["caption"], sl["background_prompt"]
            tag = f"post{pid:02d}/{i}"
            rec: dict = {"ok": False}
            for attempt in range(args.retries + 1):
                try:
                    meta = None
                    if not is_flat(prompt):
                        if args.no_fetch:
                            meta = load_meta(pid, i)
                            if meta is None:
                                raise RuntimeError("no cached background (run without --no-fetch)")
                        else:
                            meta = fetch_background(px, pid, i, prompt, picks, args.dry_run)
                    rec["meta"] = meta
                    if args.dry_run:
                        desc = "flat card" if meta is None else f"{meta['kind']} #{meta['pexels_id']} {meta['pexels_url']}"
                        log(f"{tag}: {desc}")
                        rec["ok"] = True
                        break
                    out = build_slide(pid, i, caption, prompt, meta)
                    verify_output(out, i)
                    rec.update(ok=True, out=out)
                    what = "flat" if meta is None else f"{meta['kind']} #{meta['pexels_id']}"
                    log(f"ok  {tag}  {what}  -> {os.path.relpath(out, HERE)}")
                    break
                except Exception as e:  # noqa: BLE001
                    rec["error"] = str(e)
                    log(f"!!  {tag}  attempt {attempt + 1} failed: {str(e)[:300]}")
                    # a broken download should be re-fetched on the next attempt
                    if not is_flat(prompt) and "ffmpeg" in str(e) and os.path.exists(meta_path(pid, i)):
                        m = load_meta(pid, i)
                        if m and m.get("kind") == "video" and attempt == 0:
                            # second try with the same clip; third try falls back to a photo zoom
                            pass
                        elif m and attempt >= 1:
                            for f in (meta_path(pid, i), os.path.join(BG_DIR, m["file"])):
                                if os.path.exists(f):
                                    os.remove(f)
                    time.sleep(1)
            if not rec["ok"]:
                failed.append(f"{tag}\t{prompt}\t{rec.get('error', '')}")
            results[(pid, i)] = rec

    if failed:
        with open(FAILED_TXT, "w") as fh:
            fh.write("\n".join(failed) + "\n")
    elif os.path.exists(FAILED_TXT) and not args.posts:
        os.remove(FAILED_TXT)
    if not args.dry_run:
        write_summary(posts, results, failed)
    n_ok = sum(1 for r in results.values() if r["ok"])
    log(f"\n{n_ok}/{len(results)} slides ok, {len(failed)} failed, {time.time() - t0:.0f}s"
        + (f", {px.calls} Pexels requests" if px else ""))
    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())
