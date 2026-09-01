# Handoff — what happened, and what to build next

Written at the end of the cloud session that produced Study 001, for whichever Claude picks
this up on teti's desktop. `CLAUDE.md` has the operational detail (how to rebuild the film,
the load-bearing rules, the bugs already paid for). This file is the story and the roadmap.

## What happened, briefly

teti is becoming a motion editor and needed a first client-facing Reel. The reference was
yuk.aji's *LILIUM — Experimental Motion Study*: a specimen dissected with labels, oversized
type interleaved with imagery, one texture per beat, editorial numbering.

The idea went through four honest revisions:

1. **"Why do we need motion editors?"** — kept, but recast. Not an argument; the *title of a
   study*, answered by demonstration and signed. teti explicitly rejected making it an ad
   aimed at a client's pain point: this is a debut of craft, "show my work, what I do is here."
2. **Palette from teti's own oil portrait**, extracted by k-means rather than picked by eye.
3. **The design language followed the palette** — the film was rebuilt as a painted object,
   with a stroke-stamping paint engine, canvas weave, and brush-edged type.
4. **The film stopped naming the craft and started performing it.** This was the biggest
   change and the one that mattered most — see below.

## The critique that drove the last pass

Tested at real phone size (~390 px wide), the beats built from **big type** read perfectly and
the beats built from **small UI** failed completely — the five specimen cells were ~58 px on a
real phone. That was 42% of the runtime spent on content nobody could perceive.

More fundamentally: the film **named** the principles (timing, spacing, easing, weight, rhythm)
without demonstrating any of them. That is why it read as designed rather than animated.

The fix, now in place:
- **Beat 3** performs three principles full-frame, one at a time: a real spacing chart (marks
  dropped at even slices of *time*, so they crowd where it is slow), a weight study with
  stretch-into-fall, squash on contact and a bounce far lower than the drop, and a stagger
  where the delay between elements is the content.
- **Beat 4** is the showcase: dragging the ease curve makes the dead post **come apart into its
  layers in 3D** and rebuild itself with staggered timing and overshoot. "IT IS MADE OF LAYERS"
  → "THIS IS THE JOB".
- **Beat 5** is per-character kinetic type — every letter its own masked layer, MOVE. overshooting.
- **The Reel loops seamlessly** — the canvas turns back to the dark ground so the last frame
  matches the first.
- **The end card jokes**: the cursor returns, handles snap around MOVE., and it slides out of
  the sentence and springs home.

Two later passes, both at teti's request:
- **The signature resolves into the mark.** "teti." cycles through eleven typefaces — serif,
  grotesk, mono, script, slab — each hold a little longer than the last, settles on Inter, then
  shrinks into the circular portrait that is live as the profile picture. Film and profile now
  share one mark.
- **Two transitions that belong to a painting, not a slideshow.** STILL. breaks up through the
  tooth of the canvas into the study title (a grain dissolve — thresholded noise, not a fade),
  and the ochre band is revealed by a loaded brush dragged across the frame (a paint wipe —
  gradient mask displaced into bristles). Every other cut is still a match cut or a hard cut.

## Still open

- ~~The profile picture~~ — **decided and live: the full-colour circular portrait**
  (`brand/pfp/opt1_portrait.png`). teti chose it over the recommended duotone; the end card
  was then rebuilt to resolve into it. The other seven options stay as a record.
- **Beat 4 is simulated UI.** A real screen recording of teti dragging a real curve in Resolve's
  Spline editor would be more honest and more impressive. Highest-value upgrade available and
  only teti can shoot it — help set up the exact comp worth recording.
- **Hours and deadline** were never pinned down.

---

# What to make better

Ranked by value per hour.

**1. Swap in a real Resolve capture for beat 4.** Build the comp for teti to record (a simple
solid with two position keyframes and a visible Spline editor), then cut the capture in place
of the simulated panel. The rest of the film needs no changes.

**2. Multi-format exports.** The film is 9:16 only. A 4:5 feed crop and a 1:1 need safe-zone
adjustments, not a re-render from scratch — `video.html` is parametric, so add a size mode
rather than hand-cropping. Worth doing once and reusing for every study.

**3. Cheaper iteration.** At ~0.8 s/frame a full pass is ~30 minutes, almost all of it the
brush-edge displacement filter. Bake the type-edge treatment into pre-rendered PNGs for static
strings and the render drops by roughly half. Worth it before Study 002, not before shipping 001.

**4. Sound design in Fairlight.** The current bed is synthesised by `sound.py` — clean, frame-exact,
and deliberately sparse. With Resolve connected it could be re-voiced with real sampled
material and properly mixed.

# What to create

**Study 002 — ARC, in Blender.** The strongest next move. Arcs are the one principle that is
genuinely hard to prove in flat 2D and trivial to prove with a camera in space, so using 3D
becomes a real flex instead of decoration. Render with a toon/NPR shader and composite the same
canvas weave over it, so it stays inside the visual system. `bpy` is fully scriptable and headless.

Later studies with the same test — *does this principle need dimension?* — are FOLLOW-THROUGH
and OVERLAP (a cloth or hair sim), and WEIGHT redone as an actual physics simulation.

**A series template.** Study 001 took a full session. `video.html` should be refactored so a new
study is a data file — beats, labels, copy — against a shared engine. Study 002 should take an
hour. This is the difference between one good post and a body of work.

**The profile grid.** Covers are currently an afterthought. Design them as a system so the grid
reads as one intentional shelf of studies as it fills.

**A portfolio page.** The paint engine already renders to a browser; the same system could
generate a site that looks like nothing else in the field, and gives teti somewhere to send
clients that is not Instagram.

**Case-study carousels.** Each study has a genuine "here is how this was made" post inside it —
the spacing chart alone is a carousel. Cheap to produce from work already done, and it is what
makes other designers follow.

## One judgement to carry forward

The strongest thing about this film is that it *performs* its argument instead of stating it, and
its second strongest is restraint — one signal colour, one idea, one joke. When adding to it, the
question is not "what else could go in" but "what would this earn." Study 001 got better every
time something was made bigger and fewer, and worse every time something was added.
