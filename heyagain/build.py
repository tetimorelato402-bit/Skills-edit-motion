#!/usr/bin/env python3
"""hey again. carousel builder.

Reads captions/posts.json (25 posts x 5 slides), finds a Pexels background for
every slide, and renders output/postXX/1..5 following the brand rules in
CLAUDE.md:

  * every slide is 4:5 (2160x2700)
  * slides 1 and 3 are 3-second videos with a silent audio track
    (Pexels video, or the Pexels photo with a slow ffmpeg zoom)
  * background fills the frame, slightly blurred, tangerine #D8652B overlay
    at ~35% opacity; caption in cream #F4EEE4, Inter-Medium, centered
  * "flat tangerine, no scene" slides are a solid #D8652B card + caption
  * no logos, no mirror, no people, no visible text in backgrounds

usage:
  python3 build.py                 build everything (resumes finished slides)
  python3 build.py --posts 1,7,25  build only these posts
  python3 build.py --force         rebuild slides that already exist
  python3 build.py --dry-run       print the Pexels queries, touch no network
  python3 build.py --workers 2     parallel ffmpeg renders (default: cpus-1)

Pexels key: PEXELS_API_KEY in .env (or the environment).
Outputs: output/postXX/{1.mp4,2.jpg,3.mp4,4.jpg,5.jpg}, backgrounds/,
         manifest.json, summary.md, failed.txt, build.log
"""
import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from io import BytesIO

import requests
from PIL import Image, ImageDraw, ImageFont

# --------------------------------------------------------------------------
# brand constants (CLAUDE.md — never change)
# --------------------------------------------------------------------------
ROOT = os.path.dirname(os.path.abspath(__file__))
W, H = 2160, 2700                       # 4:5
TANGERINE_HEX = "D8652B"
TANGERINE = (0xD8, 0x65, 0x2B)
CREAM = (0xF4, 0xEE, 0xE4)
FONT = os.path.join(ROOT, "assets", "Inter-Medium.ttf")
OVERLAY_ALPHA = 0.35                    # tangerine overlay opacity
BLUR_SIGMA = 6                          # "slightly blurred"
VIDEO_SECONDS = 3
FPS = 30
VIDEO_SLIDES = {1, 3}
FONT_SIZE = 128
FONT_SIZE_LARGE = 220                   # "cream text large"
TEXT_MAX_WIDTH = 1760
TEXT_LINE_SPACING = 1.22

# subtle per-post grade applied under the tangerine overlay (posts.json "tint")
TINTS = {
    "warm sepia": "eq=saturation=0.72:contrast=1.03,colortemperature=temperature=4600:mix=0.55",
    "faded denim": "eq=saturation=0.68:contrast=0.94:brightness=0.02,colortemperature=temperature=7200:mix=0.5",
    "faded denim tint": "eq=saturation=0.68:contrast=0.94:brightness=0.02,colortemperature=temperature=7200:mix=0.5",
    "cream heavy": "eq=saturation=0.78:contrast=0.9:brightness=0.06",
    "rust and cream": "eq=saturation=0.85:contrast=1.05,colortemperature=temperature=5000:mix=0.5",
    "golden hour": "eq=saturation=1.05:gamma=1.04,colortemperature=temperature=4400:mix=0.65",
    "tangerine only": "",
}

# --------------------------------------------------------------------------
# pexels selection rules
# --------------------------------------------------------------------------
PEXELS_PHOTOS = "https://api.pexels.com/v1/search"
PEXELS_VIDEOS = "https://api.pexels.com/videos/search"
PER_PAGE = 10
MIN_PHOTO_WIDTH = 3840
MIN_VIDEO_HEIGHT = 1080
MAX_VIDEO_HEIGHT = 2160
MIN_VIDEO_SECONDS = VIDEO_SECONDS + 1
RETRIES = 2                              # retry failures twice
HTTP_TIMEOUT = (20, 120)

PEOPLE_WORDS = set("""
person people man woman men women girl girls boy boys guy guys lady ladies child children kid kids
baby babies toddler family couple friend friends crowd face faces portrait selfie model models
hand hands finger fingers arm arms leg legs feet foot body bride groom worker workers student
students teacher doctor nurse businessman businesswoman player dancer athlete tourist tourists
human humans adult adults teen teens teenager male female him her he she someone somebody
silhouette photographer chef barista driver passenger passengers team group holding smiling
wearing hugging kissing running jumping cooking eating dancing sleeping shopping walking sitting
standing lying talking reading writing typing working praying wedding crew audience
""".split())
TEXT_WORDS = set("""
text texts sign signs signage lettering letters typography poster posters billboard billboards
banner banners logo logos brand branding label labels newspaper newspapers magazine magazines menu
quote quotes words word handwriting calendar license plate graffiti caption headline flyer
""".split())
MIRROR_WORDS = {"mirror", "mirrors"}
REJECT_PHRASES = ["neon sign", "book cover", "screen showing", "road sign", "street sign", "shop sign"]

STOPWORDS = set("""
a an the and or of on in at to from with one two three four half left right out frame face up
down blurred blurry blur close next it its into onto by over under through as is are still
""".split())

# --------------------------------------------------------------------------
# small utilities
# --------------------------------------------------------------------------
LOG_LOCK = threading.Lock()
LOG_FILE = None


def log(msg):
    line = f"[{time.strftime('%H:%M:%S')}] {msg}"
    with LOG_LOCK:
        print(line, flush=True)
        if LOG_FILE:
            LOG_FILE.write(line + "\n")
            LOG_FILE.flush()


def load_env():
    path = os.path.join(ROOT, ".env")
    if os.path.exists(path):
        for raw in open(path, encoding="utf-8"):
            raw = raw.strip()
            if not raw or raw.startswith("#") or "=" not in raw:
                continue
            k, v = raw.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def sha(s):
    return hashlib.sha1(s.encode("utf-8")).hexdigest()[:16]


def run(cmd):
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if p.returncode != 0:
        raise RuntimeError(f"{os.path.basename(cmd[0])} failed ({p.returncode}): {p.stderr.strip()[-800:]}")
    return p.stdout


def ffprobe(path):
    out = run(["ffprobe", "-v", "error", "-print_format", "json", "-show_streams", "-show_format", path])
    return json.loads(out)


def tokens(s):
    return re.findall(r"[a-z]+", (s or "").lower())


# --------------------------------------------------------------------------
# keywords: background_prompt -> 2..4 pexels keywords
# --------------------------------------------------------------------------
def load_keyword_map():
    path = os.path.join(ROOT, "captions", "keywords.json")
    if not os.path.exists(path):
        return {}
    data = json.load(open(path, encoding="utf-8"))
    return {k: v for k, v in data.items() if not k.startswith("_")}


def auto_keywords(prompt):
    """Fallback extraction when a prompt is not in keywords.json."""
    out = []
    for seg in prompt.split(","):
        words = [w for w in tokens(seg) if w not in STOPWORDS and len(w) > 2]
        if not words:
            continue
        out.append(" ".join(words[:2]))
        if len(out) == 4:
            break
    if len(out) < 2:
        words = [w for w in tokens(prompt) if w not in STOPWORDS and len(w) > 2]
        out = words[:3] if len(words) >= 2 else (words + ["room"])[:2]
    return out


def keywords_for(prompt, kmap):
    kws = kmap.get(prompt)
    if not kws:
        kws = auto_keywords(prompt)
    return kws[:4]


def query_ladder(kws):
    """all keywords first, then drop from the end, never below 2 while possible."""
    ladder = []
    for n in range(len(kws), 1, -1):
        ladder.append(" ".join(kws[:n]))
    if kws:
        ladder.append(kws[0])
    ladder += ["dark room window light", "empty room dusk"]
    seen, out = set(), []
    for q in ladder:
        if q not in seen:
            seen.add(q)
            out.append(q)
    return out


# --------------------------------------------------------------------------
# pexels client
# --------------------------------------------------------------------------
class NetworkDown(Exception):
    pass


def net_reason(e):
    """'api.pexels.com: Tunnel connection failed: 403 Forbidden' instead of the whole urllib3 dump."""
    s = str(e)
    host = re.search(r"host='([^']+)'", s)
    cause = re.search(r"Caused by (.+?)\)*$", s)
    detail = cause.group(1) if cause else s
    inner = re.findall(r"'([^']+)'", detail)
    detail = inner[-1] if inner else detail
    return f"{host.group(1) + ': ' if host else ''}{detail}"[:200]


class Pexels:
    def __init__(self, api_key, cache_dir):
        self.s = requests.Session()
        self.s.headers["Authorization"] = api_key or ""
        self.s.headers["User-Agent"] = "heyagain-carousel-builder/2.0"
        self.cache_dir = cache_dir
        os.makedirs(os.path.join(cache_dir, "search"), exist_ok=True)
        os.makedirs(os.path.join(cache_dir, "previews"), exist_ok=True)
        self.consecutive_conn_failures = 0
        self.down_reason = None
        self.lock = threading.Lock()

    # ---- low level -------------------------------------------------------
    def _request(self, url, params=None, stream=False, what="request"):
        """GET with 2 retries and 429 handling.

        After 9 consecutive connection failures the client is marked down and
        every later request gets a single probe instead of the full retry
        ladder; the first probe that succeeds clears the flag."""
        last = None
        attempts = 1 if self.down_reason else RETRIES + 1
        for attempt in range(attempts):
            try:
                r = self.s.get(url, params=params, timeout=HTTP_TIMEOUT, stream=stream)
                if r.status_code == 429:
                    wait = int(r.headers.get("Retry-After", "20") or 20)
                    log(f"    rate limited on {what}, sleeping {wait}s")
                    time.sleep(min(wait, 120))
                    last = RuntimeError("429 rate limited")
                    continue
                if r.status_code in (401, 403) and "api.pexels.com" in url:
                    raise RuntimeError(f"pexels api refused the key (HTTP {r.status_code})")
                if r.status_code >= 500:
                    last = RuntimeError(f"HTTP {r.status_code} on {what}")
                    time.sleep(2 * (attempt + 1))
                    continue
                r.raise_for_status()
                with self.lock:
                    self.consecutive_conn_failures = 0
                    self.down_reason = None
                return r
            except (requests.ConnectionError, requests.Timeout) as e:
                last = RuntimeError(net_reason(e))
                with self.lock:
                    self.consecutive_conn_failures += 1
                    if self.consecutive_conn_failures >= 9:
                        self.down_reason = f"network unavailable ({net_reason(e)})"
                if attempt + 1 < attempts:
                    time.sleep(1.5 * (attempt + 1))
        if self.down_reason:
            raise NetworkDown(self.down_reason)
        raise RuntimeError(f"{what} failed after {attempts} attempts: {str(last)[:300]}")

    def _search(self, endpoint, query):
        key = sha(endpoint + "|" + query)
        cpath = os.path.join(self.cache_dir, "search", key + ".json")
        if os.path.exists(cpath):
            return json.load(open(cpath, encoding="utf-8"))
        params = {"query": query, "per_page": PER_PAGE, "orientation": "landscape"}
        r = self._request(endpoint, params=params, what=f"search '{query}'")
        data = r.json()
        json.dump(data, open(cpath, "w", encoding="utf-8"))
        return data

    def search_photos(self, query):
        return self._search(PEXELS_PHOTOS, query).get("photos", [])

    def search_videos(self, query):
        return self._search(PEXELS_VIDEOS, query).get("videos", [])

    def preview_stats(self, url):
        """mean luminance / contrast of a small preview, cached on disk."""
        cpath = os.path.join(self.cache_dir, "previews", sha(url) + ".json")
        if os.path.exists(cpath):
            return json.load(open(cpath, encoding="utf-8"))
        r = self._request(url, what="preview")
        im = Image.open(BytesIO(r.content)).convert("L").resize((64, 40))
        px = list(im.getdata())
        mean = sum(px) / len(px) / 255.0
        var = sum((p / 255.0 - mean) ** 2 for p in px) / len(px)
        stats = {"lum": round(mean, 4), "std": round(var ** 0.5, 4)}
        json.dump(stats, open(cpath, "w", encoding="utf-8"))
        return stats

    def download(self, url, dest):
        if os.path.exists(dest) and os.path.getsize(dest) > 0:
            return dest
        tmp = dest + ".part"
        r = self._request(url, stream=True, what="download")
        with open(tmp, "wb") as f:
            for chunk in r.iter_content(1 << 20):
                if chunk:
                    f.write(chunk)
        os.replace(tmp, dest)
        return dest


# --------------------------------------------------------------------------
# candidate filtering + scoring
# --------------------------------------------------------------------------
def reject_reason(*texts):
    toks = set()
    joined = " ".join(t or "" for t in texts).lower()
    for t in texts:
        toks.update(tokens(t))
    hit = toks & PEOPLE_WORDS
    if hit:
        return "people: " + ",".join(sorted(hit)[:3])
    hit = toks & TEXT_WORDS
    if hit:
        return "text: " + ",".join(sorted(hit)[:3])
    hit = toks & MIRROR_WORDS
    if hit:
        return "mirror"
    for p in REJECT_PHRASES:
        if p in joined:
            return "text: " + p
    return None


def mood_score(stats):
    """moody lighting: mid-dark, with some contrast. 0..1"""
    if not stats:
        return 0.5
    lum, std = stats["lum"], stats["std"]
    s = 1.0 - min(1.0, abs(lum - 0.32) / 0.35)
    if lum > 0.62:
        s -= 0.5          # bright, flat, not our mood
    if lum < 0.07:
        s -= 0.4          # basically black
    if std < 0.08:
        s -= 0.2          # no depth
    return max(0.0, s)


def slug_text(url):
    m = re.search(r"pexels\.com/(?:photo|video)/([^/]+?)-\d+/?$", url or "")
    return m.group(1).replace("-", " ") if m else ""


def pick_photo(px, photos, query):
    scored, rejected = [], []
    for idx, p in enumerate(photos):
        w, h = p.get("width", 0), p.get("height", 0)
        if w < MIN_PHOTO_WIDTH:
            rejected.append((p["id"], f"width {w}<{MIN_PHOTO_WIDTH}"))
            continue
        if w <= h:
            rejected.append((p["id"], "not landscape"))
            continue
        why = reject_reason(p.get("alt", ""), slug_text(p.get("url", "")))
        if why:
            rejected.append((p["id"], why))
            continue
        preview = (p.get("src") or {}).get("medium") or (p.get("src") or {}).get("small")
        try:
            stats = px.preview_stats(preview) if preview else None
        except NetworkDown:
            raise
        except Exception as e:  # preview problems only cost the mood signal
            log(f"    preview failed for photo {p['id']}: {str(e)[:120]}")
            stats = None
        relevance = 1.0 - 0.6 * idx / max(1, PER_PAGE - 1)
        bonus = 0.1 if w >= 5000 else 0.0
        score = 0.5 * relevance + 0.4 * mood_score(stats) + bonus
        scored.append((score, idx, p, stats))
    if not scored:
        return None, rejected
    scored.sort(key=lambda t: (-t[0], t[1]))
    score, idx, p, stats = scored[0]
    return {
        "kind": "photo",
        "id": p["id"],
        "url": p["url"],
        "credit": p.get("photographer", ""),
        "credit_url": p.get("photographer_url", ""),
        "width": p["width"],
        "height": p["height"],
        "download": p["src"]["original"],
        "alt": p.get("alt", ""),
        "score": round(score, 3),
        "stats": stats,
        "query": query,
        "rank": idx + 1,
    }, rejected


def best_video_file(v):
    files = []
    for f in v.get("video_files", []):
        if f.get("file_type") != "video/mp4":
            continue
        fw, fh = f.get("width") or 0, f.get("height") or 0
        if fh < MIN_VIDEO_HEIGHT or fw <= fh:
            continue
        if fh > MAX_VIDEO_HEIGHT:
            continue
        size = f.get("size") or 0
        if size and size > 400 * 1024 * 1024:
            continue
        files.append((fh, -size, f))
    if not files:
        return None
    files.sort(key=lambda t: (-t[0], t[1]))
    return files[0][2]


def pick_video(px, videos, query):
    scored, rejected = [], []
    for idx, v in enumerate(videos):
        w, h = v.get("width", 0), v.get("height", 0)
        if w <= h:
            rejected.append((v["id"], "not landscape"))
            continue
        if (v.get("duration") or 0) < MIN_VIDEO_SECONDS:
            rejected.append((v["id"], f"duration {v.get('duration')}s too short"))
            continue
        f = best_video_file(v)
        if not f:
            rejected.append((v["id"], "no mp4 file >= 1080p landscape"))
            continue
        why = reject_reason(slug_text(v.get("url", "")))
        if why:
            rejected.append((v["id"], why))
            continue
        try:
            stats = px.preview_stats(v["image"]) if v.get("image") else None
        except NetworkDown:
            raise
        except Exception as e:
            log(f"    preview failed for video {v['id']}: {str(e)[:120]}")
            stats = None
        relevance = 1.0 - 0.6 * idx / max(1, PER_PAGE - 1)
        bonus = 0.15 if f["height"] >= 2160 else (0.08 if f["height"] >= 1440 else 0.0)
        score = 0.5 * relevance + 0.4 * mood_score(stats) + bonus
        scored.append((score, idx, v, f, stats))
    if not scored:
        return None, rejected
    scored.sort(key=lambda t: (-t[0], t[1]))
    score, idx, v, f, stats = scored[0]
    return {
        "kind": "video",
        "id": v["id"],
        "url": v["url"],
        "credit": (v.get("user") or {}).get("name", ""),
        "credit_url": (v.get("user") or {}).get("url", ""),
        "width": f["width"],
        "height": f["height"],
        "duration": v.get("duration"),
        "download": f["link"],
        "alt": slug_text(v.get("url", "")),
        "score": round(score, 3),
        "stats": stats,
        "query": query,
        "rank": idx + 1,
    }, rejected


def resolve_background(px, kws, want_video):
    """Returns (choice, notes). choice None when nothing acceptable exists."""
    notes = []
    ladder = query_ladder(kws)
    if want_video:
        for q in ladder:
            videos = px.search_videos(q)
            choice, rejected = pick_video(px, videos, q)
            notes.append(f"video '{q}': {len(videos)} results, {len(rejected)} rejected")
            if choice:
                return choice, notes
        notes.append("no acceptable pexels video, falling back to photo + zoom")
    for q in ladder:
        photos = px.search_photos(q)
        choice, rejected = pick_photo(px, photos, q)
        notes.append(f"photo '{q}': {len(photos)} results, {len(rejected)} rejected")
        if choice:
            return choice, notes
    return None, notes


# --------------------------------------------------------------------------
# rendering
# --------------------------------------------------------------------------
def _greedy_wrap(draw, words, font, max_width):
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=font) <= max_width or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def wrap_lines(draw, text, font, max_width):
    """Greedy wrap, then tighten the width so no line is left with a lone word."""
    words = text.split()
    lines = _greedy_wrap(draw, words, font, max_width)
    width = max_width
    while len(lines) > 1 and len(lines[-1].split()) == 1 and width > max_width * 0.6:
        width *= 0.95
        trial = _greedy_wrap(draw, words, font, width)
        if len(trial) > len(lines):
            break
        lines = trial
    return lines


def caption_layer(caption, large, cache_dir):
    """Transparent 2160x2700 PNG with the caption centered (cached)."""
    os.makedirs(os.path.join(cache_dir, "text"), exist_ok=True)
    path = os.path.join(cache_dir, "text", sha(f"{caption}|{large}|{FONT_SIZE}|{FONT_SIZE_LARGE}") + ".png")
    if os.path.exists(path):
        return path
    size = FONT_SIZE_LARGE if large else FONT_SIZE
    font = ImageFont.truetype(FONT, size)
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    lines = wrap_lines(d, caption, font, TEXT_MAX_WIDTH if not large else 1900)
    line_h = int(size * TEXT_LINE_SPACING)
    block_h = line_h * len(lines)
    y = (H - block_h) // 2
    for line in lines:
        tw = d.textlength(line, font=font)
        d.text(((W - tw) / 2, y), line, font=font, fill=CREAM + (255,))
        y += line_h
    im.save(path)
    return path


def bg_chain(tint):
    """scale-to-cover, subtle tint, slight blur (rgba out, ready for the overlay)."""
    parts = [f"scale={W}:{H}:force_original_aspect_ratio=increase:flags=lanczos", f"crop={W}:{H}", "setsar=1"]
    t = TINTS.get((tint or "").strip().lower(), "")
    if t:
        parts.append(t)
    parts.append("eq=brightness=-0.04")
    parts.append(f"gblur=sigma={BLUR_SIGMA}")
    parts.append("format=rgba")
    return ",".join(parts)


def compose(bg_label="bg", text_input="1:v"):
    """tangerine overlay at OVERLAY_ALPHA (true RGB alpha blend), then the caption."""
    return (f"color=c=0x{TANGERINE_HEX}@{OVERLAY_ALPHA}:s={W}x{H}:r={FPS},format=rgba[tint];"
            f"[{bg_label}][tint]overlay=0:0:format=rgb:shortest=1[bgt];"
            f"[bgt][{text_input}]overlay=0:0:format=rgb,format=yuv420p")


VIDEO_OUT = ["-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
             "-r", str(FPS), "-c:a", "aac", "-b:a", "128k", "-ar", "48000",
             "-movflags", "+faststart", "-t", str(VIDEO_SECONDS)]
SILENCE = ["-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo"]


def render_photo(src, text_png, tint, out):
    fc = f"[0:v]{bg_chain(tint)}[bg];{compose()}"
    run(["ffmpeg", "-v", "error", "-y", "-i", src, "-i", text_png, "-filter_complex", fc,
         "-frames:v", "1", "-update", "1", "-q:v", "2", out])


def render_video_from_video(src, text_png, tint, out):
    fc = f"[0:v]fps={FPS},setpts=PTS-STARTPTS,{bg_chain(tint)}[bg];{compose()}[v]"
    run(["ffmpeg", "-v", "error", "-y", "-ss", "0", "-t", str(VIDEO_SECONDS + 1), "-i", src,
         "-i", text_png, *SILENCE, "-filter_complex", fc, "-map", "[v]", "-map", "2:a", *VIDEO_OUT, out])


def render_video_from_photo(src, text_png, tint, out):
    frames = VIDEO_SECONDS * FPS
    zw, zh = W * 2, H * 2   # zoom on a 2x canvas to avoid zoompan jitter
    fc = (f"[0:v]scale={zw}:{zh}:force_original_aspect_ratio=increase:flags=lanczos,crop={zw}:{zh},"
          f"zoompan=z='1+0.07*on/{frames - 1}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
          f":d={frames}:s={W}x{H}:fps={FPS},{bg_chain(tint)}[bg];{compose()}[v]")
    run(["ffmpeg", "-v", "error", "-y", "-i", src, "-i", text_png, *SILENCE,
         "-filter_complex", fc, "-map", "[v]", "-map", "2:a", *VIDEO_OUT, out])


def render_card_photo(text_png, out):
    card = Image.new("RGB", (W, H), TANGERINE)
    card.paste(Image.open(text_png).convert("RGBA"), (0, 0), Image.open(text_png).convert("RGBA"))
    card.save(out, quality=95)


def render_card_video(text_png, out):
    fc = f"[0:v][1:v]overlay=0:0:format=auto,format=yuv420p[v]"
    run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i",
         f"color=c=0x{TANGERINE_HEX}:s={W}x{H}:r={FPS}:d={VIDEO_SECONDS}", "-i", text_png, *SILENCE,
         "-filter_complex", fc, "-map", "[v]", "-map", "2:a", *VIDEO_OUT, out])


def verify_output(path, is_video):
    if not os.path.exists(path) or os.path.getsize(path) == 0:
        raise RuntimeError("output missing or empty")
    info = ffprobe(path)
    vs = [s for s in info["streams"] if s["codec_type"] == "video"]
    if not vs or int(vs[0]["width"]) != W or int(vs[0]["height"]) != H:
        raise RuntimeError(f"wrong size: {vs[0].get('width')}x{vs[0].get('height')}" if vs else "no video stream")
    if is_video:
        aud = [s for s in info["streams"] if s["codec_type"] == "audio"]
        if not aud:
            raise RuntimeError("video has no audio track")
        dur = float(info["format"].get("duration", 0))
        if abs(dur - VIDEO_SECONDS) > 0.15:
            raise RuntimeError(f"duration {dur:.2f}s, expected {VIDEO_SECONDS}s")


# --------------------------------------------------------------------------
# pipeline
# --------------------------------------------------------------------------
def is_flat(prompt):
    return "flat tangerine" in (prompt or "").lower()


def is_large(prompt):
    return "text large" in (prompt or "").lower()


def slide_filename(n):
    return f"{n}.mp4" if n in VIDEO_SLIDES else f"{n}.jpg"


def with_retries(fn, what, retries=RETRIES):
    last = None
    for attempt in range(retries + 1):
        try:
            return fn()
        except NetworkDown:
            raise
        except Exception as e:
            last = e
            log(f"    {what} attempt {attempt + 1}/{retries + 1} failed: {str(e)[:200]}")
            time.sleep(1)
    raise RuntimeError(f"{what}: {str(last)[:300]}")


class Builder:
    def __init__(self, args):
        self.args = args
        self.out_dir = os.path.join(ROOT, "output")
        self.bg_dir = os.path.join(ROOT, "backgrounds")
        self.cache_dir = os.path.join(ROOT, "cache")
        for d in (self.out_dir, self.bg_dir, self.cache_dir):
            os.makedirs(d, exist_ok=True)
        self.manifest_path = os.path.join(ROOT, "manifest.json")
        self.manifest = {}
        if os.path.exists(self.manifest_path) and not args.force:
            try:
                self.manifest = json.load(open(self.manifest_path, encoding="utf-8"))
            except Exception:
                self.manifest = {}
        self.failed = []        # (post, slide, reason)
        self.lock = threading.Lock()
        self.kmap = load_keyword_map()
        self.posts = json.load(open(os.path.join(ROOT, "captions", "posts.json"), encoding="utf-8"))
        if args.posts:
            wanted = {int(x) for x in args.posts.split(",") if x.strip()}
            self.posts = [p for p in self.posts if p["post"] in wanted]
        self.px = Pexels(os.environ.get("PEXELS_API_KEY", ""), self.cache_dir)

    # ---- bookkeeping -----------------------------------------------------
    def key(self, post, slide):
        return f"post{post:02d}/{slide}"

    def record(self, post, slide, entry):
        with self.lock:
            self.manifest[self.key(post, slide)] = entry
            json.dump(self.manifest, open(self.manifest_path, "w", encoding="utf-8"), indent=1)

    def fail(self, post, slide, reason):
        with self.lock:
            self.failed.append((post, slide, reason))
            self.manifest[self.key(post, slide)] = {"status": "failed", "reason": reason,
                                                    **{k: v for k, v in self.manifest.get(self.key(post, slide), {}).items()
                                                       if k in ("caption", "background_prompt", "keywords", "type")}}
            json.dump(self.manifest, open(self.manifest_path, "w", encoding="utf-8"), indent=1)
        log(f"  FAILED post{post:02d} slide {slide}: {reason}")

    def done_already(self, post, slide):
        e = self.manifest.get(self.key(post, slide))
        if not e or e.get("status") != "ok":
            return False
        path = os.path.join(self.out_dir, f"post{post:02d}", slide_filename(slide))
        try:
            verify_output(path, slide in VIDEO_SLIDES)
            return True
        except Exception:
            return False

    # ---- per slide -------------------------------------------------------
    def build_slide(self, post, slide_no, slide, pool):
        pid = post["post"]
        caption = slide["caption"]
        prompt = slide.get("background_prompt", "")
        tint = post.get("tint", "")
        is_video = slide_no in VIDEO_SLIDES
        post_dir = os.path.join(self.out_dir, f"post{pid:02d}")
        os.makedirs(post_dir, exist_ok=True)
        out = os.path.join(post_dir, slide_filename(slide_no))
        entry = {"status": "pending", "caption": caption, "background_prompt": prompt,
                 "type": "video" if is_video else "photo", "output": os.path.relpath(out, ROOT)}

        if not self.args.force and self.done_already(pid, slide_no):
            log(f"  post{pid:02d} slide {slide_no}: already built, skipping")
            return

        text_png = caption_layer(caption, is_large(prompt), self.cache_dir)

        # flat tangerine card ------------------------------------------------
        if is_flat(prompt):
            entry.update({"type": "flat-video" if is_video else "flat-photo", "keywords": [], "pexels_url": None})
            if self.args.dry_run:
                log(f"  post{pid:02d} slide {slide_no} [{entry['type']}] no search <- {prompt}")
                return
            self.record(pid, slide_no, entry)

            def job():
                try:
                    with_retries(lambda: (render_card_video if is_video else render_card_photo)(text_png, out),
                                 f"render post{pid:02d} slide {slide_no}")
                    verify_output(out, is_video)
                    entry["status"] = "ok"
                    self.record(pid, slide_no, entry)
                    log(f"  post{pid:02d} slide {slide_no}: flat card -> {os.path.relpath(out, ROOT)}")
                except Exception as e:
                    self.fail(pid, slide_no, str(e)[:300])
            pool.submit(job)
            return

        # pexels background ------------------------------------------------
        kws = keywords_for(prompt, self.kmap)
        entry["keywords"] = kws
        self.record(pid, slide_no, entry)
        if self.args.dry_run:
            log(f"  post{pid:02d} slide {slide_no} [{'video' if is_video else 'photo'}] {kws} <- {prompt}")
            return
        try:
            choice, notes = with_retries(lambda: resolve_background(self.px, kws, is_video),
                                         f"search post{pid:02d} slide {slide_no}")
        except Exception as e:
            self.fail(pid, slide_no, f"pexels search failed: {str(e)[:250]}")
            return
        entry["search_notes"] = notes
        if not choice:
            self.fail(pid, slide_no, "no acceptable pexels result (" + "; ".join(notes[-3:]) + ")")
            return
        ext = ".mp4" if choice["kind"] == "video" else os.path.splitext(choice["download"].split("?")[0])[1] or ".jpg"
        bg_path = os.path.join(self.bg_dir, f"post{pid:02d}_s{slide_no}{ext}")
        try:
            with_retries(lambda: self.px.download(choice["download"], bg_path),
                         f"download post{pid:02d} slide {slide_no}")
        except Exception as e:
            self.fail(pid, slide_no, f"download failed: {str(e)[:250]}")
            return
        entry.update({
            "pexels_url": choice["url"], "pexels_id": choice["id"], "pexels_kind": choice["kind"],
            "credit": choice["credit"], "credit_url": choice["credit_url"],
            "source_size": f"{choice['width']}x{choice['height']}", "query_used": choice["query"],
            "rank": choice["rank"], "score": choice["score"], "background": os.path.relpath(bg_path, ROOT),
        })
        if is_video:
            entry["type"] = "video" if choice["kind"] == "video" else "video (photo + zoom)"
        self.record(pid, slide_no, entry)

        def job():
            try:
                if is_video and choice["kind"] == "video":
                    fn = lambda: render_video_from_video(bg_path, text_png, tint, out)
                elif is_video:
                    fn = lambda: render_video_from_photo(bg_path, text_png, tint, out)
                else:
                    fn = lambda: render_photo(bg_path, text_png, tint, out)
                with_retries(fn, f"render post{pid:02d} slide {slide_no}")
                verify_output(out, is_video)
                entry["status"] = "ok"
                self.record(pid, slide_no, entry)
                log(f"  post{pid:02d} slide {slide_no}: {entry['type']} <- {choice['url']}")
            except Exception as e:
                self.fail(pid, slide_no, f"render failed: {str(e)[:300]}")
        pool.submit(job)

    # ---- run -------------------------------------------------------------
    def run(self):
        workers = self.args.workers or max(1, (os.cpu_count() or 2) - 1)
        with ThreadPoolExecutor(max_workers=workers) as pool:
            for post in self.posts:
                log(f"post{post['post']:02d} — {post['title']} ({post['emotion']}; {post['tint']})")
                for i, slide in enumerate(post["slides"], start=1):
                    try:
                        self.build_slide(post, i, slide, pool)
                    except NetworkDown as e:
                        self.fail(post["post"], i, str(e))
                    except Exception as e:
                        self.fail(post["post"], i, f"unexpected: {str(e)[:250]}")
        if self.args.dry_run:
            return
        self.write_failed()
        self.write_summary()

    # ---- reports ---------------------------------------------------------
    def write_failed(self):
        path = os.path.join(ROOT, "failed.txt")
        rows = []
        for post in self.posts:
            for i in range(1, 6):
                e = self.manifest.get(self.key(post["post"], i), {})
                if e.get("status") != "ok":
                    rows.append(f"post{post['post']:02d} slide {i}: {e.get('reason', 'not built')}")
        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(rows) + ("\n" if rows else ""))
        log(f"failed.txt: {len(rows)} slide(s) not built")

    def write_summary(self):
        ok = sum(1 for p in self.posts for i in range(1, 6)
                 if self.manifest.get(self.key(p["post"], i), {}).get("status") == "ok")
        total = 5 * len(self.posts)
        lines = ["# hey again. — build summary", "",
                 f"Built {ok} of {total} slides on {time.strftime('%Y-%m-%d %H:%M %Z')}.",
                 "Slides 1 and 3 are 3-second videos with a silent audio track; 2, 4 and 5 are photos.",
                 "All backgrounds are from Pexels (photos and videos); the Pexels page of every background is linked.", ""]
        if total - ok:
            lines += [f"**{total - ok} slide(s) did not build — see failed.txt.**", ""]
        for post in self.posts:
            pid = post["post"]
            lines += [f"## post{pid:02d} — {post['title']}", "",
                      f"emotion: {post['emotion']} · tint: {post['tint']}", "",
                      "| # | type | caption | keywords | Pexels background | credit | file |",
                      "|---|------|---------|----------|-------------------|--------|------|"]
            for i, slide in enumerate(post["slides"], start=1):
                e = self.manifest.get(self.key(pid, i), {})
                status = e.get("status", "not built")
                typ = e.get("type", "video" if i in VIDEO_SLIDES else "photo")
                kws = ", ".join(e.get("keywords") or []) or "—"
                if e.get("pexels_url"):
                    bg = f"[{e.get('pexels_kind', 'pexels')} {e.get('pexels_id', '')}]({e['pexels_url']}) ({e.get('source_size', '')})"
                elif typ.startswith("flat"):
                    bg = "flat tangerine card (no background)"
                else:
                    bg = "—"
                credit = f"[{e['credit']}]({e['credit_url']})" if e.get("credit") else "—"
                fname = f"output/post{pid:02d}/{slide_filename(i)}"
                cell = fname if status == "ok" else f"FAILED: {e.get('reason', 'not built')}"
                cap = slide["caption"].replace("|", "\\|")
                lines.append(f"| {i} | {typ} | {cap} | {kws} | {bg} | {credit} | {cell} |")
            lines.append("")
        with open(os.path.join(ROOT, "summary.md"), "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        log(f"summary.md written ({ok}/{total} slides ok)")


def main():
    global LOG_FILE
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--posts", help="comma separated post numbers, e.g. 1,7,25")
    ap.add_argument("--force", action="store_true", help="rebuild slides that already exist")
    ap.add_argument("--dry-run", action="store_true", help="print keywords/queries only, no network")
    ap.add_argument("--workers", type=int, default=0, help="parallel ffmpeg renders")
    args = ap.parse_args()
    load_env()
    if not args.dry_run and not os.environ.get("PEXELS_API_KEY"):
        sys.exit("PEXELS_API_KEY missing: put it in .env (see .env.example)")
    for tool in ("ffmpeg", "ffprobe"):
        if not shutil.which(tool):
            sys.exit(f"{tool} not found on PATH")
    if not os.path.exists(FONT):
        sys.exit(f"font missing: {FONT}")
    LOG_FILE = open(os.path.join(ROOT, "build.log"), "a", encoding="utf-8")
    Builder(args).run()


if __name__ == "__main__":
    main()
