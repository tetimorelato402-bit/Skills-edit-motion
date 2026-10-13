#!/usr/bin/env python3
"""Read an Instagram data export and print the accounts you follow, grouped by day.

Usage: parse_following.py <export.zip | export folder | following.html | following.json>

Prints JSON: [{"date": "2026-10-12", "accounts": [{"u": "name", "at": "2026-10-12T18:12"}]}]
newest day first, newest follow first within a day.
"""
import json
import re
import sys
import zipfile
from collections import defaultdict
from datetime import datetime, timezone
from html import unescape
from pathlib import Path

HTML_NAME = "connections/followers_and_following/following.html"
JSON_NAME = "connections/followers_and_following/following.json"


def read_source(path):
    p = Path(path)
    if p.suffix == ".zip":
        with zipfile.ZipFile(p) as z:
            names = z.namelist()
            for want in (JSON_NAME, HTML_NAME):
                hit = next((n for n in names if n.endswith(want)), None)
                if hit:
                    return want, z.read(hit).decode("utf-8")
        sys.exit("No following.html or following.json in the export.")
    if p.is_dir():
        for want in (JSON_NAME, HTML_NAME):
            f = p / want
            if f.exists():
                return want, f.read_text("utf-8")
        sys.exit("No following.html or following.json in the export folder.")
    return (JSON_NAME if p.suffix == ".json" else HTML_NAME), p.read_text("utf-8")


def from_html(text):
    pattern = re.compile(
        r'href="https://www\.instagram\.com/(?:_u/)?([^"/?]+)/?"[^>]*>[^<]*</a></div><div>([^<]+)</div>'
    )
    for user, stamp in pattern.findall(text):
        at = datetime.strptime(unescape(stamp).strip(), "%b %d, %Y %I:%M %p")
        yield user, at


def from_json(text):
    data = json.loads(text)
    items = data.get("relationships_following", data) if isinstance(data, dict) else data
    for item in items:
        sld = item.get("string_list_data") or [{}]
        user = item.get("title") or sld[0].get("value")
        if not user and sld[0].get("href"):
            user = sld[0]["href"].rstrip("/").rsplit("/", 1)[-1]
        ts = sld[0].get("timestamp")
        if user and ts:
            yield user, datetime.fromtimestamp(ts, tz=timezone.utc).replace(tzinfo=None)


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    kind, text = read_source(sys.argv[1])
    rows = from_json(text) if kind == JSON_NAME else from_html(text)
    days = defaultdict(dict)
    for user, at in rows:
        days[at.strftime("%Y-%m-%d")][user] = at.strftime("%Y-%m-%dT%H:%M")
    out = [
        {
            "date": day,
            "accounts": [
                {"u": u, "at": at}
                for u, at in sorted(accts.items(), key=lambda kv: kv[1], reverse=True)
            ],
        }
        for day, accts in sorted(days.items(), reverse=True)
    ]
    json.dump(out, sys.stdout, indent=1)
    print()


if __name__ == "__main__":
    main()
