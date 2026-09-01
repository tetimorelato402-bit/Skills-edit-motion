# Study 001 — DaVinci Resolve build plan

Companion to `BRIEF.md`. Tool: DaVinci Resolve Studio. Everything below uses only Resolve — the Edit page for assembly, the Fusion page for motion graphics. Where a beat has a simpler fallback, it's noted.

## Project setup

- Timeline: **1080 × 1920** (9:16), **30 fps** (Reels standard; 60 only if the micro-loops need it), sRGB/Rec.709.
- Bring in a muted reference copy of the track ONLY for timing the cut (see "Music & export" — the song itself gets added inside Instagram).
- Build the **end card first** (Beat 6). It forces the palette, typeface, and layout system that every other beat inherits.

## Palette & type (pending the color decision)

- Three swatches only: signal color (TBD) + cream `#F2EFE9`-ish + near-black `#0D0D0D`. Save them as Fusion background nodes you copy between comps.
- One typeface, two cases: ALL CAPS for the big statements, lowercase for "teti." — set both as saved Text+ presets.

## Beat by beat

### Beat 1 — STILL. (0–1.5s)
- A static "generic brand post" frame: design it directly in Fusion (Background + Text+ + a stock-ish photo) or import a PNG. Deliberately ordinary.
- Selection handles: eight small white squares (Rectangle masks on a Background node) around the frame + a 1px border. Group them — you'll reuse this "handles" element in Beats 3 and 4.
- Blinking cursor: a thin Rectangle with opacity keyframed 100 → 0 → 100 every ~0.5s (or an Anim Curves modifier set to a square wave).
- Giant "STILL." in caps, static. Nothing in this beat moves except the cursor blink — the discomfort is the point.
- Export this frame as a still: it's the Reel cover.

### Beat 2 — Study title (1.5–4s)
- Fusion comp on cream: Text+ set like a journal cover — small caps "STUDY 001" above, the question large below.
- The word MOTION is its own Text+ node so it can misbehave: keyframe Y-position dropping in with overshoot. Do the ease in the **Spline editor** — select the keyframes, use Ease Out on the fall, then a couple of diminishing bounce keyframes. Add Directional Blur tied to its movement frames for the smear.
- The 1.5s cut from Beat 1 to this beat is the video's first movement — make the cut land exactly where the track's first phrase starts.

### Beat 3 — Specimen board (4–8s)
- Letterboxed band: signal-color Background across the middle ~40% of frame, black above and below.
- Five small rectangles in a row, each holding a 0.5s looping clip (crop/scale in a Transform node): one per label — TIMING, SPACING, EASING, WEIGHT, RHYTHM. These are real work samples: tiny animations you make (a ball drop for WEIGHT, a stagger for RHYTHM…) or crops of past work.
- Reuse the handles group on one or two of the boxes; add dashed guide lines (Rectangle mask, dash pattern) and a hand-drawn bezier scribble (Paint node or a Polygon mask stroked).
- Small caps Text+ labels above each box. Stagger everything's entrance left to right, ~4 frames apart.

### Beat 4 — The editor's hand (8–12s) ← the signature beat
- **Don't fake it: screen-record the real thing.** Put the Beat-1 frame in its own Fusion comp, open the Spline editor, and screen-record yourself (macOS: Cmd+Shift+5 / Windows: Game Bar or OBS) selecting the layer, dropping two keyframes, and dragging the ease handle — while the viewer shows the frame coming alive.
- Cut the recording tight: cursor selects → keyframes appear → curve bends → frame moves. Punch in (scale up the capture) so the curve and the viewer are both readable on a phone.
- The bend-up in the song lands exactly where the curve gets dragged. This sync is the whole video; place this beat on the timeline first and cut everything else around it.
- Fallback if the capture looks messy: rebuild the UI elements (keyframe diamonds, curve) as Fusion shapes — but try the real capture first; authenticity is the flex.

### Beat 5 — Hero line (12–15s, on the sustain)
- Full-bleed: the now-moving frame centered, "SOMEONE HAS TO DECIDE HOW THINGS MOVE." in oversized caps behind AND in front of it.
- Depth interleave in Fusion: duplicate the Text+ node, put one copy under the image and one above, and mask the top copy (Polygon mask around the image) so only some letters overlap in front. Cheap, looks expensive.
- The line lands ON the bend-up, holds through the sustain, cuts on its release. No other motion during the sustain — hold with the note.

### Beat 6 — End card (15–18s)
- Journal-cover layout: "I'M TETI. I DECIDE HOW THINGS MOVE." / MOTION STUDIES — 001 / new study weekly / @handle. Lowercase "teti." wordmark against the caps.
- Elements settle in with small, quick eases (6–8 frames, ease out) as the phrase resolves. Then hold a full second — people screenshot end cards.

## Music & export (important)

- **Do not burn the song into the export.** Instagram licenses the track only when you add it inside the app. Workflow: cut against the muted reference locally → export the video with sound design only (or silent) → in the Reel editor, add "Parisienne Walkways" (studio version) and slide its start point until the bend lands on Beat 4. Verify sync on your phone before posting.
- Sound design (optional but on-brand, and it survives even for sound-off viewers who tap in): cursor click, keyframe tick, soft whoosh on the Beat 5 reveal. Fairlight page, keep it -18dB-ish under where the track will sit.
- Export: H.264, 1080×1920, high bitrate (30–50 Mbps), upload the cover still separately.

## Build order (not timeline order)

1. End card (locks the system) → 2. Beat 1 still + cover → 3. Beat 4 screen capture (locks the sync) → 4. Beats 2 & 5 type work → 5. Beat 3 specimen board (the most labor; first candidate to simplify if hours run out — the 4-beat spine is 1, 2, 5, 6).
