# "It isn't moving yet" — Creative Brief

teti studio · **the master** · 9:16 · **27 bars = 50.23s** · **129 BPM** · no post date

Cut to Luifer, *Gracias a Ti*, from **46.555s** — the track's bar 25. The tempo, the
section boundaries and the two quietest moments in the film are all measured off that
recording rather than chosen; `audio/README.md` has the numbers and `scripts/track.py`
re-derives them. **The film ends where it began and loops.**

**Act I is 3D.** A dead plant in a mason jar, in the dark, that grows and blooms —
Blender/Cycles, eleven bars. Then the 2D paint world for twelve. Then **Blender again for
the last four**, because the film closes into a loop: one more petal falls, back into the
jar it grew from, and the last frame is the first frame.

Produced from a full `big-video-project` interview (36 questions), then **substantially
re-briefed** when teti corrected the premise. Read the revision note below before
anything else — an earlier version of this file described a conversion ad with a
two-week deadline, and every one of those decisions has been pulled.

> **This is not Study 003, and it is not a post.** The repo directory is numbered for
> ordering only. Nothing on the grid says "003", and nothing is scheduled.

---

## REVISED — what teti actually asked for

In teti's words: *"this video is not going to get posted now. it is the master of my
current skill level. its everything i can do on display."*

That reframes the whole thing. **This is a capability piece, not a campaign.** It is the
single artefact that says what teti can currently do, built without a clock and without a
conversion job. The marketing is what teti called an **underhand** — the film sells by
being undeniable, not by asking for anything.

**Pulled from the earlier brief, and they should stay pulled:**

| Pulled | Because |
|---|---|
| "send me your idea" CTA on screen | Nothing is being asked for. An ask undercuts a master. |
| Two-week deadline, 20–30 hours | Explicitly withdrawn. It is done when it is right. |
| "One DM about real work" as success | There is no post, so there is no inbound to count. |
| Cold-Explore first-1.5-seconds pressure | Not the distribution. The cover frame can be composed rather than defensive. |
| The answer line on screen | See below — this is the biggest change of all. |

## The jar — Act I

teti's direction: *"a plant in a cup. dark lighting made on blender. the plant is in a
mason jar. its slowly growing and its dark and dead and then it blooms. from that bloom
we start making our video in faster pace different styles."*

This is the single best structural decision the film has had, for a reason worth stating:
**it makes the question literal instead of metaphorical.** "How do you make ideas that
aren't alive, alive?" — and the first seven bars are a dead thing becoming alive. Nothing
on screen explains that and nothing should.

It also disposes of the film's biggest named risk. The chat box is **cut entirely** — no
field, no send button, no interface of any kind. The question appears as pure type over
the dark. There is now no way to mistake this for "I asked AI to…" content, because
there is no AI on screen.

- **The flower is a POPPY**, and every reason is a production reason. Its bud is a
  nodding grey-green pod that genuinely reads as dead, where a tulip bud already looks
  like a flower. Its head **lifts before it opens** — anticipation performed by the plant
  rather than applied to it, which is the exact principle the whole series is about. Its
  petals emerge **creased and open by uncreasing**, which is the film's thesis carried out
  by a flower. They are translucent, so a backlight makes them glow in a dark frame. And
  poppy red is already the accent, so the 2D paint does not have to match the flower — it
  is the same colour because it came from it. *(Runner-up, banked: a hyacinth bulb forced
  in the jar neck, roots growing down into the water.)*
- **Eight bars, `bt(0)`–`bt(32)`, 15.36s.** Nearly half the film is dark and slow before
  anything fast happens. That is the contrast the second half is spending.
- **THE FALL IS THE TRANSITION.** *(This replaced the birds-eye arc. The arc is described
  in the revision note at the bottom of this section, with why it went.)*

  The flower opens, and then the room goes out around it — the fill and the bounce to
  nothing, the beam closing from 7° to 4° — until there is one lit flower in a black
  frame. On `bt(37)` a single petal starts to peel. On `bt(38)` it lets go, **and the
  music stops in the same frame.** It falls for six beats through total silence, lit by a
  beam that has narrowed to just it, and on `bt(44)` the music slams back on the downbeat
  and the paint detonates out of the petal.

  The silence is not an effect added to the film. It is *in the track* — a hard,
  sample-exact stop running its beats 138 to 144 — and the film was moved onto it.

  Twice on the way down the **whole frame glitches into one of the languages that is
  coming** for two frames and snaps back: the modular grid, then the torn collage. It is
  the fault the stem had in bar 2, arrived at the flower, and this time it is not a colour,
  it is a whole language.

  **Why this and not the arc.** The arc was the *camera* doing something. A petal letting
  go is the *flower* doing something — and in a film about dead things becoming alive,
  every beat handed to the subject instead of the rig argues its own case. It also leaves
  an object that can come back: the film ends on a second petal, falling into the jar. You
  cannot loop a camera move.

- **One light: a direct beam from above, landing on the floor.** The camera starts across
  a dark room, small, outside the light, and travels into it over the whole act. There is
  no second lamp in the room — the only other light is a rim linked to the glass alone so
  it cannot touch the table.
- **The last beat of Act I is BLACK.** The lights cut on `bt(27)` — two frames, a switch
  and not a dimmer — and the film holds on nothing for one beat before the bloom. That
  beat is what makes the paint an event rather than a transition: it detonates out of a
  hole in the film, on the downbeat.
- **The bloom erupts from the flower head, and both the position and the palette are
  extracted rather than typed.** `scripts/handoff.py` projects the flower head through
  Act I's actual camera — (540, 450), dead centre, 23% down — so nudging the Blender
  camera cannot silently leave the paint starting somewhere that is not the flower. It
  then k-means clusters the rendered poppy and lifts the result **in value only**, which
  is the same method that produced 001's palette from teti's oil portrait and the same
  rule stated in `CLAUDE.md`. The paint is the flower's colour because it *is* the
  flower's colour.
- **The plant is not cut away from — it is covered.** That is why the Blender act never
  needs compositing against the 2D world: they share exactly one frame, and the paint
  takes it.

## The question — and why it is never answered

The question changed, and it changed for the better:

> ### how do you make ideas that aren't alive, alive?

This is not a founder's marketing question. It is **teti's craft question**, and it is
the one the whole body of work is already circling. 001 answers *someone has to decide
how things move.* 002 answers *the idea was never the problem.* This one asks the thing
both of those are answers to — it is the parent of the series, not a sibling.

And teti's hardest instruction: **"the why is clearly answered by the viewer themselves."**

That kills the answer line. The earlier brief ended on *"your idea is fine — it just
isn't moving yet"*, which answers the question **for** the viewer and turns a
demonstration into a caption. The film ends instead on **the question, returning
unchanged** — the same words, the same place, the same size as the cover. By then the
viewer has watched twenty seconds of dead type become alive, so they have already
answered it, and the film never says the thing out loud. The title of the film keeps the
retired line, because it is a good line and it belongs on the folder, not on the screen.

## Audience & placement

- **9:16, and eventually Instagram** — but not now, and not designed around a stranger's
  thumb. The cover frame gets to be composed rather than defensive.
- **Who it is for, in this order:** teti first (it is the proof of a level), then anyone
  teti chooses to show it to — a prospective client, a studio, a peer.
- **What it should produce:** *"I'm going to work with this guy."* (teti's own words.)
  Not this week, and not from a metric.
- **Dream comment (the bar it is judged against):** *"wow awesome i love the way you
  envisioned this video."* Note what that is — a comment about **authorship**, not about
  software. It has to look *composed*, not just fast.

## Style DNA

**Structure: T5 White Space Editorial. Surface: T1 Texture Pass.** Same pair as 002 —
and never a third, per the technique library's own rule.

**The five techniques on display** (chosen for maximum visual distance, so no two read
alike for even a second):

| Bar | Technique | Accent | Why it earns its place |
|---|---|---|---|
| 3 | **T5** white space editorial | RUST `#A03A22` | The opening answer is restraint — one word owning an empty frame. Sets the ceiling for how quiet this can be before it never is again. |
| 4 | **T6** modular grid | signal blue | Everything snaps. Objects travel *across* the wordmark and briefly occlude it — the occlusion trick the library says to steal outright. |
| 5 | **T3** torn collage | hot red on cream | Elements arrive at 6–14° off-axis, tape and torn edges. The loudest bar in the film. |
| 6 | **T9** ink on one colour | mustard `#B8843A` | Two colours total, black line on flat mustard. The intimate one, and the breather before the last. |
| 7 | **T7** painted frame | full portrait colour | Brush-drawn, painted type. Placed last so the film resolves **into teti's own hand** one beat before teti's name. |

**T1 is not one of the five — it is the skin over all of them.** This is what stops five
palettes from reading as five different films: colour varies, surface and timing never do.

**What holds it together (teti's answer to "what makes this yours"): the paint engine and
the grid.** Every technique is skinned in the oil plates and canvas weave from
`001/source/paint.py`, and every event lands on a sixteenth of the 125 BPM grid. Nobody
else's showreel is painted, and nobody else's is frame-exact by construction.

**The palette rule, amended.** `CLAUDE.md` says colour *"may move in value; it must not
leave the warm family."* Five accents cannot all be warm and still be distinct. The rule
is therefore split: **the ground never leaves the family** — BONE `#C8BFAA` and UMBER
`#220C06` are constant under all five — **the accent may.** Brand lives in the ground.

**Type.** Two faces, as always: Inter display + IBM Plex Mono micro. **Type carries the
question and nothing else.** No labels naming the techniques — 002's brief bans exactly
that (*"labels turn it into a tutorial"*) and it applies here. The five are legible as
answers purely from placement and from the question staying pinned above them.

**The interface: recognisable but unbranded.** The shape of a chat box and a warm-orange
send button. No logo, no wordmark, no product name — everyone who uses one recognises it
instantly, and nothing in the film claims a relationship with anybody's product. The
question is set in **Inter display, not UI type**, so it reads as a typographic frame that
happens to have a send button, rather than as a screen recording.

**What it must not look like (teti's named fear): "I asked AI to…" content.** The
counter-measures are structural, not stylistic — see Issue 1.

## Sound

Synthesised, never licensed — the house rule since 001, and `sound.py` already does this.

- **125 BPM, and the film is cut to it.** Beat 0.48s, bar 1.92s. Same grid and same
  engine as 001, so cue times stay frame-exact by construction rather than by hand.
- **Runtime: 17 bars = 32.64s.** Decided. 13 bars was sized for a cold-Explore Reel;
  with no post date it was simply too tight for a 2.4s bloom, five techniques and a
  question that has to come back and sit there. The four extra bars go to the techniques
  and to the silence at the end — **never to new content.**
- **The bloom is 5 beats — `bt(2)` to `bt(7)`, 2.4 seconds.** Decided, and it is the
  longest single gesture in the film by a wide margin.
- **Designed both ways, deliberately.** Burned-in type carries the argument muted; the
  synthesised house track carries the rip when someone taps.
- **The drop is the click.** No long build — the film opens *on* the drop at 0.96s. Bar 1
  is diegetic riser only (cursor, key ticks), bars 3–7 groove one technique per bar, bar 8
  is the peak, bars 9–11 the breakdown, 12–13 the outro to the loop point.
- Target loudness matches 001: **−14 LUFS integrated, true peak under −1 dBFS.**

## Constraints

- **Pipeline: code the film, finish in Resolve.** The five techniques, the bloom and the
  T1 skin are built as code in this repo (the 001 engine — `video.html` + `render.py` +
  `paint.py` + `sound.py` — which already has the paint engine and the 125 BPM grid);
  grade, texture and final cut happen in DaVinci Resolve Studio on the desktop.
- **Render at 120fps, tmix down to 30.** The house shutter. Do not shortcut it.
- **No deadline.** Withdrawn by teti along with the post date. This is the one project
  in the repo where "ship soon" does not apply, and that is a deliberate choice, not
  drift. The risk that comes with it is Issue 10.
- **Formats:** 1080×1920 primary. Cover frame = frame 0 (the question — it must read as
  a deliberate title card, not a screenshot). Safe zones still observed, so that posting
  it later never requires re-cutting it.
- **Approval: teti alone.**
- **Already exists and should be reused, not remade:** the paint engine and oil plates,
  the portrait and derived palette, `sound.py`'s house engine, the 125 BPM grid helpers.

## Success criteria & non-goals

- **Success: teti can point at it.** It is the master — the answer to "what can you
  actually do." There is no number, because there is no post. The test is whether teti
  would send this file to someone they wanted to work with, unaccompanied.
- **Quality bar: the bloom is perfect; everything else may be rough.** The hero gets the
  hours. Unchanged from the interview, and the only quality rule that survives.
- **Non-goals:** not a tutorial, not a numbered study, not an argument about AI, and —
  now — not a conversion asset. Nothing in it asks for anything.

---

## Beat sheet — 27 bars at 129 BPM

A bar is **1.86047s**, a beat **0.46512s**, a sixteenth **0.11628s**. Nothing may be
re-timed to a value that is not a multiple of a sixteenth. Every boundary below is written
in `bt()` in both engines, so the tempo lives in exactly two constants.

Track column is where that bar sits in *Gracias a Ti*, which starts at 46.555s.

| Bar | Beats | Screen | Track |
|---|---|---|---|
| **1** | `bt(0)`–`bt(4)` | **Black, then a shaft.** A beam drops from above and lands on the table as a pool; the jar stands in it, small, far away, in a dark room. Nothing moves. The question fades up over the dark, one line per beat. | groove |
| **2–6** | `bt(4)`–`bt(24)` | **The stem climbs**, slow and continuous over five bars — never cut to, it simply does not stop. Leaves unfurl on the eighths as it passes them. Dead brown warms toward living olive so gradually that no frame is the change. **The stem glitches through the five accent colours** on a thirty-second grid, violent at the base and gone by the bud. The question leaves at `bt(8)`; the film is wordless from here to the end of it. | groove |
| **7** | `bt(24)`–`bt(27)` | **The bud swells and opens, in the beam.** The head lifts, the sepals split back and are shed, the petals uncrease. The camera has arrived — it started across the room and ends inside the light. | groove |
| **7–10** | `bt(27)`–`bt(37)` | **The room goes out around it.** Fill and bounce to nothing, the beam closing to 4°. One lit flower, black frame. | groove thinning |
| **10** | `bt(37)`–`bt(38)` | **One petal peels**, on the last beat of music there is. | last beat |
| **10–11** | `bt(38)`–`bt(44)` | **THE FALL.** It lets go and the music stops in the same frame. Six beats, one petal, one beam, nothing else — the quietest the film gets, immediately before the loudest. Twice the whole frame glitches into a language that is coming (`bt(40)` the grid, `bt(42)` the collage), two frames each. | **HARD SILENCE** — the track's beats 138–144 |
| **12** | `bt(44)`–`bt(48)` | **THE DROP — THE ROOM WAS A STUDIO THE WHOLE TIME.** The petal touches the table, the music slams back, and every light comes on *inside a sixteenth* — a switch, not a fade. The walls are a white cyclorama. The camera pulls back from the fallen petal to a wide of the flower on the cyc. Nothing is cut to: the same room, the same flower, with the lights on. | — | music returns |
| **13–15** | `bt(48)`–`bt(58)` | **THE FIVE, STATED.** Two beats each, on the flower, in the room: **EDITORIAL** — white cyc, one soft key, *how* two metres tall standing behind the flower, the camera dollying past. **GRID** — the flower's geometry voxelises, snapping between block resolutions on the sixteenths, *do you* lying flat on the floor. **COLLAGE** — the petals tear off the head and hang in the air as red paper with tape across them, *make* in cut-out white, handheld. **INK** — Freestyle draws the flower as a black line on a mustard field, *ideas that aren't* hand-set lower left. **PAINTED** — impasto plum off the brush plate under a raking key, *alive,* brush-lettered **on the face of a petal**. | one word per look | groove |
| **16–17** | `bt(58)`–`bt(68)` | **CUTTING.** The five looks cut against each other — six on the beat, then eight on the eighths — in a fixed sequence, never the same look twice in a row. | — | building |
| **18–19** | `bt(68)`–`bt(76)` | **THE STROBE.** One flower, all five languages, on the eighths. Identical content, five voices, nothing else changes — the film's claim made as loudly as it can be made. *alive?* held behind it the whole time, in each look's own material. The question completes here. | *alive?* | **peak** |
| **20–22** | `bt(76)`–`bt(88)` | **THE COLLAPSE.** The looks go out in reverse — painted, ink, collage, grid, editorial — and the rig dims across each so the room is *arriving* at the dark. Over the last bar the Act I beam comes back, narrowing onto the flower. | — | thinning |
| **23** | `bt(88)`–`bt(92)` | **THE BREAK.** The picture leaves with the music and drains to black over one bar. | **near-silence** — beats 188–192 |
| **24–26** | `bt(92)`–`bt(105)` | **One more petal falls.** Out of the black, in Blender again, the same object and the same light. The camera holds close for two bars, then pulls back — and the room opens out around it to reveal it is falling into the jar. | quiet outro |
| **27** | `bt(105)`–`bt(108)` | **It lands, and the beam dies** the way it arrived in bar 1. The last frame is the first frame. The film loops, and asks again. | quiet outro |

**The question is asked once as a sentence**, in bar 1, and never answered. Its words come
back one per look in the studio — around the flower, on the floor, on a petal — and *alive?*
lands on all five at once. By the end of the studio the whole question has been restated in
five voices on one flower, and the answer is what the viewer just watched. teti chose a
pure loop — no returning question, no `teti.`, no card. Every loop restates it, which is
more times than a closing card would have managed; the cost is that the film no longer
carries the mark, and the end card no longer resolves into the profile picture. That was a
decided thing and it has been un-decided deliberately, not forgotten.

## Issues — read this section twice

**1. The cold open is still your own named failure mode, even without Explore.** teti's
biggest fear is looking like *"I asked AI to…"* content, and the film opens on a text
field and a send button. Losing the Explore deadline lowers the stakes; it does not
remove them, because a master gets looked at *harder* than a Reel does.
**Resolution, and it is already built:** the box is on screen for under a second of total
screen time and never returns until the loop. No logo, no wordmark, no product name, no
panel — a hairline rule and a button, nothing else. The question is set in **Inter
display at title scale on the painted ground**, so frame 0 reads as a typographic
statement that happens to contain a send button. If it could be mistaken for a
screenshot, it has failed and gets reset.

**2. Five palettes is the exact thing that makes a showreel look like a showreel.** teti
chose one palette per technique *and* named "generic showreel" as a thing to avoid. Those
pull against each other.
**Resolution, and it must hold:** the **ground never changes** (bone/umber under all
five), the **surface never changes** (the same oil plates and canvas weave over all five),
and the **timing never changes** (every event on a sixteenth of the same grid). Only the
accent moves. If a technique ever gets its own ground or its own texture, the film breaks
into five clips and the argument dies with it.

**3. T9 is the one that will blow the two weeks.** Ink-on-one-colour needs real hand-drawn
line work — it is the only asset in the film that cannot be generated by code teti already
owns. T7, counterintuitively, is *cheap* here: the technique library says a painted frame
"needs either a painter or a heavily art-directed pipeline", and `paint.py` already is one.
**Resolution:** draw T9's frames **in the first three days or cut it.** The fallback is a
four-technique cut at 11 bars (21.12s), which is still on the grid and still loops. Decide
by day four, not day twelve.

**4. A vibe piece with a problem-and-solution spine is two films fighting.** teti asked for
"watch this it rips" *and* for the viewer's struggle shown first. The moment you show
someone struggling you have started a story, and a story wants explanation that a vibe
piece cannot afford.
**Resolution:** the problem is **stated once, in one readable sentence, and never
explained.** No second beat of setup, no cut back to the founder, no resolution scene.
That is why the return-to-the-founder ending was rejected. Hold that line in the edit —
the temptation to add "context" at 15s will be strong and it will kill the film.

**5. A master with no audience and no date is a project that can run forever.** This is
the real risk of the re-brief, and it is bigger than anything the ad version carried. The
deadline is gone, the metric is gone, and the standard is now "everything I can do" —
which is a bar that rises every time teti learns something. 001 took a full session and
shipped; 002 is parked at a gate; this one has no forcing function at all.
**Resolution:** the gate structure is the substitute for a deadline. Frame 0 and the
bloom are approved or rejected as a unit before any technique is built, each technique is
approved on its own bar, and **"everything I can do" is frozen to the five techniques
already chosen** — anything learned mid-build goes into the next film, not this one. If
that rule is not held, the five becomes six and the film never finishes.

**6. The bloom is a transition, not a message.** It is the surviving moment and it is
spectacle — a viewer can love it completely and still not have registered a single thing
about what teti can *do*. Admiration for one effect is not the same as belief in a level,
and this film exists to establish a level.
**Resolution:** already structural — `teti.` strobes within one beat of the bloom
resolving, and the five techniques start 1.92s later. The bloom is never allowed to be the
last thing that happened before the viewer's attention returns.

**7. This has no visual identity of its own yet.** It is deliberately not a numbered study,
which frees it to be loud — but it also means it will sit on a grid of quiet craft studies
with nothing marking it as belonging to the same person or as a repeatable format.
**Resolution:** the **question frame and the send button are the recurring mark.** If
this ever becomes a format — one question, five treatments — it already has an identity
and the cover frames will rhyme down the grid. Design frame 0 as though there will be
five of them.

**8. Twenty to thirty hours is tight for five techniques, a hero bloom and a dual sound
design.** Two weeks is real, and it is the first real deadline across all three projects —
which means it is also the one most likely to slip.
**Resolution:** build in the order below, so the cut is **shippable at every point** and
the thing that falls off the end is the thing that was always most expendable.

**9. Two open ends the interview did not close.** Nobody real was named as the target
viewer, and their prior belief about video was never pinned down. Everything above is
built on the *description* of that person rather than an actual one.
**Resolution:** before building, open one real account belonging to someone who fits and
watch the film's plan against them. If nothing about it would stop their thumb, the
problem is in this brief, not in the render.

---

## Next actions

There are no dates, by teti's decision. The gates below replace them, and they are what
stops "everything I can do" from becoming a film that is never finished.

1. **DONE — frame 0 and the bloom are built and rendered.** `source/video.html` on the
   001 engine, 125 BPM, deterministic `renderFrame(t)`. See `BUILD.md` for what they
   cost and what broke on the way.
2. **GATE 1 — approve or reject frame 0 and the bloom as a unit.** They are the cover
   and the hero; every technique is built on top of them. Judge the bloom moving, not as
   stills, and judge frame 0 at 390px. Nothing else starts until this passes.
3. **Decide the runtime — 13 bars or 17.** It only affects how much room the five
   techniques get, and it is cheaper to decide now than after two of them are built.
4. **Decide T9.** Draw the ink frames or drop to four techniques. It is the only asset in
   the film that code teti already owns cannot produce, and it is the piece most likely
   to stall the build. Decide before any technique is started, not after.
5. **Build the five in reverse expense order:** T7 (the paint engine already does it) →
   T5 → T6 → T3 → T9, each approved on its own bar. **The five are frozen.** Anything
   teti learns during the build goes into the next film.
6. **`sound.py` off the same constants**, then the Resolve finish: grade, texture pass,
   final cut.

---

*Interview: 36 questions, `big-video-project`. Palette, sound engine, grid and paint
pipeline carried forward from `001/BRIEF.md`; the ad-versus-craft framing deliberately
departs from it.*
