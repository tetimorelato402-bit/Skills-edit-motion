#!/usr/bin/env python3
"""
Study 001 -> DaVinci Resolve.

Builds the project, imports the render and the sound design, lays a 1080x1920 30p
timeline and drops a named marker on every beat boundary so the edit is navigable
from the first frame.

RUN THIS ON THE DESKTOP THAT HAS RESOLVE — it talks to a running Resolve over its
local scripting bridge, so it cannot work from a cloud session.

Prerequisites
  1. DaVinci Resolve is OPEN.
  2. Resolve > Preferences > System > General >
     "External scripting using" = Local
  3. Environment variables set (see resolve/README.md).

  python3 build_timeline.py --media /path/to/study-001-v2.mp4 \
                            --audio /path/to/sound.wav
"""
import argparse, os, sys

FPS = 30
BEATS = [                      # (seconds, marker name, colour)
    (0.0,  "B1 STILL — the frozen post",        "Blue"),
    (1.6,  "B2 Study title — MOTION drops",     "Cyan"),
    (4.2,  "B3 The anatomy of motion",          "Green"),
    (8.2,  "B4 The editor's hand",              "Yellow"),
    (9.6,  "*** GUITAR BEND LANDS HERE ***",    "Red"),
    (12.2, "B5 Someone has to decide",          "Purple"),
    (15.8, "B6 teti. — end card",               "Pink"),
]

def connect():
    """Resolve's own module, or the documented fallback path."""
    try:
        import DaVinciResolveScript as dvr
    except ImportError:
        api = os.environ.get("RESOLVE_SCRIPT_API")
        if not api:
            sys.exit("RESOLVE_SCRIPT_API is not set — see resolve/README.md")
        sys.path.append(os.path.join(api, "Modules"))
        try:
            import DaVinciResolveScript as dvr
        except ImportError:
            sys.exit("Could not import DaVinciResolveScript. Check the paths in resolve/README.md")
    r = dvr.scriptapp("Resolve")
    if r is None:
        sys.exit("Resolve is not running, or external scripting is not set to Local "
                 "(Preferences > System > General).")
    return r

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--media", required=True, help="study-001-v2.mp4")
    ap.add_argument("--audio", help="sound.wav (optional — the mp4 already carries it)")
    ap.add_argument("--project", default="Motion Studies 001")
    ap.add_argument("--timeline", default="Study 001")
    a = ap.parse_args()

    for p in [a.media] + ([a.audio] if a.audio else []):
        if not os.path.isfile(p):
            sys.exit(f"No such file: {p}")

    resolve = connect()
    pm = resolve.GetProjectManager()
    proj = pm.CreateProject(a.project) or pm.LoadProject(a.project)
    if proj is None:
        sys.exit(f"Could not create or open project {a.project!r}")

    # vertical, 30p
    for k, v in [("timelineResolutionWidth", "1080"),
                 ("timelineResolutionHeight", "1920"),
                 ("timelineFrameRate", str(FPS)),
                 ("timelinePlaybackFrameRate", str(FPS))]:
        proj.SetSetting(k, v)

    paths = [os.path.abspath(a.media)] + ([os.path.abspath(a.audio)] if a.audio else [])
    clips = resolve.GetMediaStorage().AddItemListToMediaPool(paths)
    if not clips:
        sys.exit("Nothing imported — is the path reachable from Resolve?")

    mp = proj.GetMediaPool()
    tl = mp.CreateTimelineFromClips(a.timeline, clips)
    if tl is None:
        sys.exit("Timeline creation failed (a timeline of that name may already exist).")
    proj.SetCurrentTimeline(tl)

    start = tl.GetStartFrame()
    for secs, name, colour in BEATS:
        # AddMarker takes a frame offset from the timeline start
        tl.AddMarker(int(round(secs * FPS)), colour, name, "", 1)

    print(f"Project  : {a.project}")
    print(f"Timeline : {a.timeline}  ({tl.GetStartFrame()}–{tl.GetEndFrame()} @ {FPS}p)")
    print(f"Markers  : {len(BEATS)} beats, red one at 9.6s is the guitar bend")
    print("\nOpen the Edit page — the markers are on the timeline ruler.")

if __name__ == "__main__":
    main()
