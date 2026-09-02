# "It isn't moving yet" — Creative Brief

teti studio · the pitch film · 9:16 · 24.96s · 125 BPM · Instagram Reels, cold Explore

Produced from a full `big-video-project` interview (36 questions). Answers carried
forward from `001/BRIEF.md` are credited where they apply; where this film **departs**
from 001, that is a decision and it is marked as one.

> **This is not Study 003.** The numbered studies are the craft; this is the offer.
> The repo directory is numbered for ordering only — nothing on the grid says "003".

---

## The idea (one sentence)

A founder asks a machine how to market an idea that is still only an idea; the answer
detonates out of the send button, and five completely different films happen in ten
seconds — because the idea was never the problem, it just wasn't moving yet.

## What changed from 001, deliberately

001's brief is explicit: *"a debut of craft… not an ad aimed at a client's pain point"*,
and it retired the client-problem framing on purpose. **This film is the opposite and
that is intentional.** teti's reason, in their words: *"I want to make money and gain
clients… start posting on Instagram to see if I could gain commotion and lock in with a
client."* The viewer's problem comes first and teti arrives as the fix.

001 stays what it is. The two can coexist because they are addressed to different
moments — 001 introduces the craft, this one asks for the work.

## Audience & placement

- **Instagram Reels, 9:16, cold Explore.** Not a warm DM, not paid. A stranger's thumb
  decides in about a second, muted. This is the hardest distribution there is and every
  decision below is bent around it.
- **The buyer:** a founder with an idea and no way to show it — the person who has
  written the sentence *"how do I market my idea that's just an idea?"* and meant it.
- **What they should conclude:** *"I'm going to work with this guy."* (teti's own words.)
- **The action, and only this one: DM.** On-screen and in caption: **send me your idea.**
  Chosen over follow/save/silence because the stated goal is a locked-in client, and
  because "send me your idea" is the lowest-friction thing you can ask a founder for —
  they already have it typed somewhere.

## The message

- **Takeaway (locked):** **"Your idea is fine — it just isn't moving yet."**
- **The question, in the founder's own words (locked, and it is the only sustained type
  in the film):** **"how do i market my idea that's just an idea?"**
- **CTA line (locked):** **send me your idea**
- **Caption, first line:** *"How do you market an idea that's still just an idea?"* —
  asks the question back, then the offer on line two. (Departs from 001's rule that the
  caption mirrors the on-screen line; the question invites replies, and replies are the
  cheapest route to a DM.)
- **Dream comment (the bar this is judged against):** *"wow awesome i love the way you
  envisioned this video."* Note what that is — a comment about **authorship**, not about
  software. The film has to look *composed*, not just fast.

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

- **125 BPM, 13 bars, and the film is cut to it.** Beat 0.48s, bar 1.92s, 13 bars =
  **24.96s**. Same grid and same engine as 001, so cue times stay frame-exact by
  construction rather than by hand.
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
- **Two weeks. 20–30 hours.** The first real deadline across all three projects.
- **Formats:** 1080×1920 primary. Cover frame = frame 0 (the typed question — it must
  read as a deliberate title card, not a screenshot). Safe zones: keep everything clear of
  the right-side UI rail and the bottom caption band.
- **Approval: teti alone.**
- **Already exists and should be reused, not remade:** the paint engine and oil plates,
  the portrait and derived palette, `sound.py`'s house engine, the 125 BPM grid helpers.

## Success criteria & non-goals

- **Success (teti's honest answer): one DM about real work.** One inbound from someone
  with a budget. See Issue 5 — this is the right goal and the wrong metric for a single
  post, and the brief says so rather than pretending otherwise.
- **Leading indicators to actually watch:** non-follower reach (does the cold-Explore bet
  work at all) and saves (does it earn the next video's distribution).
- **Quality bar: the bloom is perfect; everything else may ship rough.** The hero gets the
  hours. A technique that reads at 80% still ships.
- **Non-goals:** not a tutorial, not a showreel, not a numbered study, not an argument
  about AI.

---

## Beat sheet — 13 bars at 125 BPM

Bar = 1.92s. Beat = 0.48s. `bt(n)` = beat n from frame 0, as in `video.html`.

| Bar | Time | Screen | Type | Sound |
|---|---|---|---|---|
| **1** | 0.00–1.92 | **The cover frame.** The question already sits finished in the box; cursor hovers the orange send button. Bone ground, canvas weave, no chrome beyond the box and the button. Held dead still for two beats — the only stillness in the film. Click on `bt(2)`. | **how do i market my idea that's just an idea?** | Room tone. Two dry key ticks. The click *is* the drop. |
| **2** | 1.92–3.84 | **THE BLOOM.** Colour detonates out of the button and eats the frame — the one moment the film leaves the palette entirely. Peaks by `bt(5)`, drains back to bone by `bt(7)`. `teti.` strobes once on `bt(7)` and is gone. | `teti.` — one frame group, lowercase | Drop lands on the ignition. Full arrangement in at once. |
| **3** | 3.84–5.76 | **T5 — white space editorial.** One word at enormous scale on near-empty bone. Motion enters from the left, exits right. | question pinned, MICRO, top left | Groove. Hit on the word landing. |
| **4** | 5.76–7.68 | **T6 — modular grid.** The frame becomes tiles; blocks slide in and out of cells, one passing across and briefly occluding the mark. Everything snaps, nothing floats. | question pinned | Tighter hats, hit per snap. |
| **5** | 7.68–9.60 | **T3 — torn collage.** Tape labels at 6–14°, torn edges, colour blocks wiping the whole frame between beats. The loudest bar. | question pinned | Peak energy, clap on 2 and 4. |
| **6** | 9.60–11.52 | **T9 — ink on one colour.** Black line drawings appearing and dissolving on flat mustard. Two colours, nothing else. The breather. | question pinned | Bass and hats pull out. Pen-scratch foley on the strokes. |
| **7** | 11.52–13.44 | **T7 — painted frame.** Brush-drawn, frame-to-frame, painted lettering. The film resolves into teti's own hand. | question pinned | Riser under it. |
| **8** | 13.44–15.36 | **All five at once.** Tiled, moving left and right, "showing everywhere" — the range stated in one image. | question pinned | Peak. |
| **9** | 15.36–17.28 | Everything drains off. The question returns **alone** on empty bone, exactly as it was in bar 1. | the question, full display scale | Breakdown. Near-silence by the last beat. |
| **10** | 17.28–19.20 | The answer lands over it, one line per two beats. | **your idea is fine —** / **it just isn't moving yet.** | Two hits, one per line. |
| **11** | 19.20–21.12 | `teti.` resolves out of the paint — the same mark as the profile picture, so the film and the account share a face. | `teti.` | Warm low tone. |
| **12** | 21.12–23.04 | The offer. | **send me your idea** · @handle | Last full bar of the track. |
| **13** | 23.04–24.96 | Hold, then cut to the empty chat box on the final frame so the Reel loops cleanly back into bar 1. | — | Thins to the last hit on the loop point. |

**Ratio check.** Bloom = 1.44s (5.8%). Five techniques = 9.60s (38%). That is the correct
split: the bloom buys the scroll-stop, the five buy the hire.

---

## Issues — read this section twice

**1. Your cold open is your own named failure mode.** teti's biggest fear is looking like
*"I asked AI to…"* content, and the film opens on a chat box. That genre is enormous and
Explore is full of it; being mistaken for it costs the whole video.
**Resolution:** the box is on screen for **under one second of total screen time** and is
never shown again until the loop frame. No logo, no wordmark, no product name, no UI
chrome beyond the field and the button. The question is set in **Inter display at title
scale**, so the cover frame reads as a typographic statement that happens to contain a
send button — not as a screen recording. If frame 0 could be mistaken for a screenshot,
it has failed and must be reset.

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

**5. "One DM about real work" is the right goal and the wrong metric for one post.** A
single cold-Explore Reel from an account with no history converting a stranger into a paid
inquiry is a low-probability event, and judging this film by it will read as failure even
if the film is excellent.
**Resolution:** the DM is the goal of **the series**; this post is judged on non-follower
reach and saves. Keep the DM ask because it costs nothing and occasionally works — but
write down now, before posting, that zero DMs on post one is the expected result, so the
number does not talk teti out of posting the second one. **The thing that produces clients
is the fourth video, and the fourth video only exists if the first three get posted.**

**6. The bloom is a transition, not a message.** It is the surviving moment and it is
spectacle — a viewer can love it completely and still not know what teti does or that
teti is for hire. The "how'd you do that" comment is not the DM.
**Resolution:** already structural — `teti.` strobes within one beat of the bloom
resolving, and the five techniques start 1.92s later. The bloom is never allowed to be the
last thing that happened before the viewer's attention returns.

**7. This has no visual identity of its own yet.** It is deliberately not a numbered study,
which frees it to be loud — but it also means it will sit on a grid of quiet craft studies
with nothing marking it as belonging to the same person or as a repeatable format.
**Resolution:** the **chat frame and the send button are the recurring mark.** If this
becomes a format ("send me your idea", one idea, five treatments), it already has an
identity and the cover frames will rhyme down the grid. Design frame 0 as though there
will be five of them.

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

1. **Today — build frame 0.** The cover frame, full size and at 390px. It is the cover,
   the cold open, the loop point and the recurring mark for a possible format, and it is
   the single highest-leverage image in the film. If it reads as a screenshot, iterate
   until it doesn't. Nothing else starts until this one is right.
2. **Day 2–4 — build the bloom alone**, as a standalone 2-second render on the 001 engine.
   It is the hero, it gets the perfect-quality budget, and it is the only part where "it
   rips" is decided. Judge it at 390px, muted. This is the stop gate.
3. **Day 3 — decide T9.** Draw the ink frames or cut to the four-technique 11-bar cut.
   Decide before any technique is built, not after.
4. **Day 5–10 — build the five in reverse expense order:** T7 (the paint engine already
   does it) → T5 → T6 → T3 → T9. Every stop leaves a shippable film.
5. **Day 11–12 — `sound.py` off the same constants**, then the Resolve finish: grade,
   texture pass, final cut. Post with the caption above.

---

*Interview: 36 questions, `big-video-project`. Palette, sound engine, grid and paint
pipeline carried forward from `001/BRIEF.md`; the ad-versus-craft framing deliberately
departs from it.*
