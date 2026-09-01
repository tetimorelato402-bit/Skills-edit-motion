# Connecting Claude to DaVinci Resolve Studio

## The honest shape of it

There is no DaVinci Resolve connector in the Claude connector directory (checked — the
registry has nothing for Resolve, Blackmagic, or NLEs in general), and a cloud session
cannot reach a desktop app. So a session running in the cloud will never drive Resolve.

What *does* work: **Resolve Studio ships a Python scripting API**, and Claude Code can run
**locally on your desktop**. Run it there and Claude can create projects, import media,
build timelines, place markers, drive Fusion comps, and kick off renders — by writing and
running scripts against the Resolve that is open on your screen.

So the answer is not a connector. It's moving the session to the machine that has Resolve.

## Setting it up (one time)

1. **Install Claude Code on the desktop** — https://claude.com/claude-code
2. **Open Resolve**, then: `Preferences > System > General >`
   **"External scripting using" → Local**. Without this the bridge refuses every connection.
3. **Set the environment variables** so Python can find Resolve's module.

**macOS** — add to `~/.zshrc`:
```sh
export RESOLVE_SCRIPT_API="/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting"
export RESOLVE_SCRIPT_LIB="/Applications/DaVinci Resolve/DaVinci Resolve.app/Contents/Libraries/Fusion/fusionscript.so"
export PYTHONPATH="$PYTHONPATH:$RESOLVE_SCRIPT_API/Modules/"
```

**Windows** — PowerShell, user-level:
```powershell
setx RESOLVE_SCRIPT_API "%PROGRAMDATA%\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting"
setx RESOLVE_SCRIPT_LIB "C:\Program Files\Blackmagic Design\DaVinci Resolve\fusionscript.dll"
setx PYTHONPATH "%PYTHONPATH%;%RESOLVE_SCRIPT_API%\Modules\"
```

4. **Check the bridge** (Resolve open, new terminal so the vars are loaded):
```sh
python3 -c "import DaVinciResolveScript as d; print(d.scriptapp('Resolve').GetProjectManager().GetCurrentProject().GetName())"
```
It should print your current project's name. If it prints `None` or raises, step 2 or 3 is wrong.

## Then run this

```sh
python3 build_timeline.py --media ../study-001-v9.mp4
```

It creates the project, sets 1080×1920 @ 30p, imports the render, builds the timeline and
drops a named marker on every beat — including a red one at **9.6s, the downbeat of bar 4,
where the ease is dragged and the bend lands** (the film runs at 75 BPM, six bars exactly). From there Claude (running locally) can keep going: cut alternates, rebuild a beat
in Fusion, set up the render queue.

**Untested against a live Resolve** — it was written in a cloud session with no Resolve to
run against, and follows Blackmagic's documented scripting API (`Developer/Scripting/README.txt`
inside your Resolve install is the reference). If a call signature differs on your version,
the error will name it and it's a quick fix.

## What Claude can actually do once connected

- Build and version timelines, import and organise media, set project/timeline settings
- Place and read markers, cut and trim clips on the timeline
- Drive **Fusion** comps — add tools, set inputs, wire node graphs, animate parameters
- Apply LUTs and grades, and queue and start renders
- Read back timeline state, so it can check its own work

What it cannot do: click the interface. Everything goes through the API, which means
anything scriptable is fair game and anything GUI-only is not.
