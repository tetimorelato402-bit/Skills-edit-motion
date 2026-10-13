# THE IDEA WAS NEVER THE PROBLEM

**Project:** STILL. — positioning film
**Runtime:** 24.000 seconds
**Stack:** Remotion + TypeScript, 60fps
**Method:** 100% code. No footage, no generation, no people.
**Techniques:** T5 White Space Editorial (structure) + T1 Texture Pass (surface)

---

## ⛔ STOP GATE

Build **Act I only** — frames 0 to 480 — render it, and stop.

Act I is deliberately bad motion, and deliberately bad is the hardest thing in
this film to get right. It must read as *lifeless*, not as *broken* or *funny*.
If Act I reads as a mistake, the film has no argument. Approve it before building
anything else.

---

## 0. THE IDEA

A founder has an idea. The idea is fine. The idea is not the problem.

The problem is the distance between the thing in their head and the thing on the
screen — and that distance is invisible until someone shows it to you.

So the film shows the **same content twice.**

**First:** a sentence and a square. Correctly placed, correctly spelled,
completely dead. Nothing is wrong with it. Nothing happens to you when you watch it.

**Then:** the *identical* sentence and the *identical* square, with timing,
spacing, easing, weight and rhythm. Nothing has been added. No new words, no new
shapes, no new colour. It just moves correctly now.

**Closing line:** `The idea was never the problem.`

**Why a square and a sentence.** There is no brand to hide behind and no clever
content doing secret work. If a plain grey rectangle can be made to feel like
something, the argument is proven absolutely. Anything more interesting than a
square would weaken it.

The five principles demonstrated in Act II are the same five from the Anatomy of
Motion series: timing, spacing, easing, weight, rhythm. The film is that series'
thesis, performed instead of taught.

---

## 1. HARD SPECS

| | |
|---|---|
| Frame rate | **60fps.** A film about motion quality cannot ship at 30 |
| Duration | 1440 frames = **24.000s** |
| Primary | 1080 × 1920 |
| Also | 1080 × 1080 |
| Audio | 48kHz, synthesised only |

---

## 2. THE GRID

**90 BPM at 60fps.** Every subdivision is a whole number of frames.

| Unit | Frames |
|---|---|
| Bar | **160** |
| Beat | **40** |
| Eighth | **20** |
| Sixteenth | **10** |

**1440 frames = 9 bars exactly.**

Every event starts on a multiple of 5. `assertGrid()` throws otherwise.

**Important exception:** Act I deliberately violates the grid. See §5.

---

## 3. PALETTE

Sampled from `study001v10.mp4`. The warm direction, not the electric-blue v2.

```
BONE      #C8BFAA    the light ground
BONE_LIGHT #D6CFBE   raised surfaces
UMBER     #220C06    the dark ground
UMBER_MID #3A2418    panels on dark
RUST      #A03A22    the accent — one word at a time, never two
OCHRE     #B8843A    secondary accent, used twice in the whole film
GREY      #8B8475    captions and the square
```

**RUST is the only saturated colour and it appears on exactly one word at a time.**
That restraint is the STILL. signature — in v10, `MOTION` and `MOVE.` carried it
alone while everything around them stayed neutral.

---

## 4. TYPE

Two faces. Never a third. **Emotion comes from scale and silence, never from
switching typeface** — that was the failure in the last film.

| Token | Size (at 1080 wide) | Face | Use |
|---|---|---|---|
| `DISPLAY` | **180px** | Grotesk, bold | The sentence, the closing line |
| `MICRO` | **13px** | Mono, uppercase, tracking 0.22em | Eyebrow and captions |

**Nothing between 14px and 179px.** Verify it.

The eyebrow reads `STILL. — MOTION STUDIES` in the top left, `MICRO`, present the
entire film, never animated.

---

## 5. ACT I — DEAD · bars 1–3 · frames 0–480 · 0.00–8.00s

Ground is `BONE`. Everything sits on it.

**The content:**
- A grey square, 340 × 340px, centred horizontally, upper third
- Beneath it, `DISPLAY`, in `UMBER`: **We're launching something new.**

That sentence is deliberately the most generic thing a founder writes.

### The rules of bad motion

This is the craft of the whole film. Act I is not broken and not comedic — it is
what a template produces. Follow every one of these:

1. **Linear easing on everything.** `linear`, no exceptions. No ease, no curve.
2. **No anticipation and no follow-through.** Objects start at full speed and stop dead.
3. **No overshoot. No settle. No weight.** The square has no mass.
4. **Everything moves at once.** The square and all four words animate simultaneously and identically.
5. **Uniform spacing.** All four words are equally spaced in time. There is no rhythm.
6. **Off-grid timing.** Events land at frames 37, 113, 189, 266, 344 — deliberately between beats. The audio will be on the grid and the picture will not be, and the viewer will feel wrong without knowing why.
7. **Fade in, fade out.** Opacity only. The laziest transition available.

| Frame | Event |
|---|---|
| 0 | `BONE` ground. Eyebrow present. Nothing else. |
| 37 | Square fades in over 20 frames, linear |
| 113 | `We're` fades in, 12 frames, linear |
| 189 | `launching` fades in, 12 frames, linear |
| 266 | `something` fades in, 12 frames, linear |
| 344 | `new.` fades in, 12 frames, linear |
| 400 | Everything sits. |
| 400–480 | **Nothing happens for 80 frames.** Held far too long. The viewer should start to feel restless. |

That restlessness is the film's setup. Do not shorten it.

---

## 6. THE TURN · bar 4 · frames 480–640 · 8.00–10.67s

| Frame | Event |
|---|---|
| **480** | **Everything cuts to black instantly.** One frame. No fade. Ground becomes `UMBER`. |
| 480–560 | Pure `UMBER`. Nothing on screen. **Total silence.** |
| 560 | `MICRO`, centred, in `GREY`, types on: `same words` |
| 600 | Beneath it: `same square` |
| 620 | Both fade out over 20 frames |

Two and a half seconds of near-nothing. This is the hinge of the film and it has
to be uncomfortable.

---

## 7. ACT II — ALIVE · bars 5–8 · frames 640–1280 · 10.67–21.33s

Ground returns to `BONE`. **Identical content. Identical position. Identical
colour.** Nothing is added.

### The rules of good motion

Every default from Act I, inverted:

1. **Easing on everything.** `cubic-bezier(0.22, 1, 0.36, 1)` as the default.
2. **Anticipation.** The square pulls back 8px before it moves forward.
3. **Weight.** It overshoots 12px, returns 4px, settles. Three stages, decelerating.
4. **One thing at a time.** The square resolves fully before the first word arrives.
5. **Rhythm.** Word spacing is uneven and musical: `launching` lands on a downbeat, `new.` arrives a full beat late after a deliberate gap.
6. **On grid.** Every event on a multiple of 5, most on multiples of 20.
7. **Motion, not opacity.** Words translate up 40px with a slight blur on entry. Nothing simply fades.

| Frame | Event | Principle |
|---|---|---|
| 640 | Square anticipates — pulls back 8px, 10 frames | anticipation |
| 660 | Square travels in, overshoots 12px, returns, settles by 720 | weight |
| 740 | `We're` rises 40px into place, 16 frames | timing |
| 780 | `launching` — lands hard on the downbeat | spacing |
| 800 | `something` — arrives quickly after, tight | rhythm |
| **860** | `new.` — arrives **a full beat late**, after a deliberate gap | rhythm |
| 880 | `new.` alone turns `RUST` over 12 frames | — |
| 920 | The square shifts 6px — a small settle, as though the whole layout breathed | weight |
| 960–1120 | Held. Everything still. **Let the audience compare it to what they saw at 400.** |
| 1120 | Square scales down and exits downward with follow-through, 40 frames | easing |
| 1180 | Words exit in reverse order, staggered 8 frames apart | rhythm |
| 1240–1280 | Empty `BONE` |

The gap before `new.` is the single most important timing decision in the film.
In Act I all four words arrived at identical intervals. Here, three arrive
together and the fourth waits. That gap is what "rhythm" means, and the audience
feels it without being told.

---

## 8. THE LINE · bar 9 · frames 1280–1440 · 21.33–24.00s

| Frame | Event |
|---|---|
| 1280 | Ground crossfades `BONE` → `UMBER` over 40 frames |
| 1340 | `DISPLAY`, lower left, bleeding toward the edge, in `BONE_LIGHT`, rises into place: **The idea was never** |
| 1380 | Second line: **the problem.** — `problem.` alone in `RUST` |
| 1420 | `MICRO` beneath, in `GREY`: `STILL. — MOTION STUDIES` |
| 1440 | End |

No logo animation. No call to action. No website. The line is the whole ending.

---

## 9. TEXTURE — T1

Applied over the entire film as a single top layer, never per element.

- Paper grain at 6% opacity, multiply blend, on the `BONE` sections
- A subtle crumple or fold texture at 3%, overlay blend, static and unmoving
- On `UMBER` sections, switch to screen blend at 4% so texture lifts the blacks
- 1.5% fine film grain over everything, animated

**The texture never moves with the content.** It sits on the lens, not on the
objects. That's what makes it read as a printed surface rather than a filter.

Without this the film looks like a Keynote template. With it, it looks made.

---

## 10. AUDIO

Synthesised in Python. No licensed music.

| Section | Sound |
|---|---|
| Act I | A dry, flat mechanical tick on each element's arrival. Identical every time, no variation, no low end. **All ticks are exactly on the 90 BPM grid** — but the picture is off-grid, so sound and image never agree. The viewer feels the misalignment without identifying it. |
| 400–480 | Ticks stop. Thin room tone. Uncomfortable. |
| The turn | **Absolute silence, frames 480–560.** True digital zero. |
| Act II | Each arrival gets a soft, warm, pitched tone with real low end and a short tail. Pitches descend across the four words. The gap before `new.` is silent, and the tone that follows is the lowest and warmest in the film. |
| 960–1120 | Room tone only. Let it sit. |
| The line | One low tone at 1340. Silence after. |

The Act I / Act II sound difference does as much work as the picture. Do not
skip it and do not use the same tick in both halves.

---

## 11. BUILD ORDER

1. `src/grid.ts` — constants, `assertGrid`, plus an `OFF_GRID` escape used *only*
   by Act I. Unit-test both.
2. `src/theme.ts` — palette, type scale, easing tokens.
3. `src/components/` — `Square`, `Word`, `Eyebrow`, `TextureLayer`.
4. **Act I. Render. STOP.** Present it.
5. The turn.
6. Act II. Render both acts back to back and watch them together — the film only
   works as a comparison.
7. The line.
8. Audio.
9. 1080×1080 variant.
10. Verify.

---

## 12. VERIFICATION

`scripts/verify.mjs` fails the build on any of:

- Total frames exactly 1440
- Every Act II and Act III event on a multiple of 5
- Every Act I event **off** the grid (this is inverted on purpose)
- No text rendered between 14px and 179px
- `RUST` never appears on more than one word in any single frame
- Audio RMS between frames 480 and 560 is exactly zero
- Act I contains no easing function other than `linear`

---

## 13. THINGS THAT WILL GO WRONG

**Act I will be tempting to make funny.** It must not be. Comedy lets the viewer
off the hook. It should be quietly, plausibly lifeless — the kind of thing they
have made themselves and not noticed.

**Act II will be tempting to overdo.** If it becomes flashy, the argument breaks,
because the claim is *nothing was added*. Every move in Act II must be
justifiable by one of the five principles. No extra flourishes, no particles, no
camera moves.

**The two halves must be pixel-identical in layout.** Same square size, same
position, same type size, same colour. If anything differs in composition, a
viewer can say "well, you changed it." Diff the two held frames — 400 and 1000 —
and they should be nearly identical images.

**Do not add labels naming the principles.** The temptation will be strong since
this is the Anatomy of Motion series. Labels turn it into a tutorial. The film's
power is that the viewer feels the difference and cannot articulate why.

---

## 14. DELIVERABLES

```
outputs/
  idea-1080x1920.mp4
  idea-1080x1080.mp4
  idea-silent.mp4
  idea-comparison.mp4      Act I and Act II side by side, for testing only
  idea-contact-sheet.png
  idea-verify-report.txt
  audio/idea-bed.wav
```

---

## 15. THE ONE THING THAT MATTERS

Frame 400 and frame 1000 show the same square and the same four words in the same
place in the same colours.

If a viewer can look at those two frames side by side and see no difference — but
felt completely different watching each one arrive — the film has worked and the
business case is made.

Everything else is in service of that.
