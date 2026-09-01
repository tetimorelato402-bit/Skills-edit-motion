---
name: big-video-project
description: Deep creative-intake interview for major video work — asks 30–50 structured questions in rounds, then turns the answers into a creative brief, a beat sheet, an honest issues list, and a saved project record. Trigger IMMEDIATELY whenever the user says "big video project" in any casing or phrasing ("Big Video Project", "I have a big video project", "/big-video-project"), and also whenever they bring a major video undertaking described only vaguely — a first video for clients, a flagship reel, a brand film, a launch video, a new series. Interview first; never jump straight to concepts, scripts, or production.
---

# Big Video Project

Run a deep creative-intake interview before any big video gets made. The user is a motion editor; big videos are their client-facing work, and a vague idea that goes straight into production wastes days of After Effects time on the wrong concept. The interview exists to make the expensive thinking happen while it's still cheap — in conversation, before a single keyframe.

The deliverable of this skill is not a video. It is understanding, written down: a creative brief, a beat sheet, and an honest list of problems with the idea.

## The contract

When this skill triggers:

1. Acknowledge the project in one or two sentences — reflect back what you heard so the user knows you got it.
2. Interview in rounds (below). Ask **30–50 questions total** across the whole interview. Fewer than 30 means you probably accepted vague answers; more than 50 means you're interrogating, not understanding.
3. Only after the interview, synthesize: brief → beat sheet → issues → next actions.
4. Save the project record if a filesystem is available.

Do not skip to ideas, scripts, or storyboards before the interview is done, even if the user's opening message contains a concept. An early concept is an input to Round 1, not a substitute for it.

## How to interview

**Ask in rounds, not all at once.** Send 4–8 questions per message, numbered, then wait. A wall of 40 questions gets skimmed and half-answered; small rounds get real answers, and each round's answers should sharpen the next round's questions. If the `AskUserQuestion` tool is available, use it for questions with natural options (platform, aspect ratio, sound-on vs. sound-off) and plain numbered text for open questions; otherwise numbered text for everything.

**Adapt.** These question banks are the map, not the route:

- Skip anything the user already answered — re-asking signals you weren't listening. Credit answers found in their opening message.
- When an answer is vague ("it should feel premium"), follow up immediately in the next round: *premium like what — name a video, a brand, a shot.* Vague answers are where projects die; a follow-up that converts an adjective into a reference is worth three new questions.
- When an answer opens a door the bank doesn't cover, walk through it. Follow-ups count toward the 30–50.
- Keep the language plain. The user thinks in shots, cuts, and feelings — not in strategy jargon. Ask "what should someone do right after watching?" not "what is the conversion objective?"

**Number continuously across rounds** (Round 2 starts at the number after Round 1 ended) so both of you can see the running count.

## The rounds

### Round 1 — The spark (≈5 questions)

Why this video exists. Get the idea in the user's own words before shaping it.

1. What's the idea in one sentence — as if you were texting it to a friend?
2. Why this video, and why now? What triggered it?
3. What's the dream reaction — what do you want someone to feel, say, or type in the comments in the first 5 seconds after watching?
4. If everything else got cut and only one moment survived, what is that moment?
5. Is this video an argument, a demonstration, a story, or a vibe? (It can only lead with one.)

### Round 2 — Audience & platform (≈6 questions)

A video for "everyone" is a video for no one. Platform decides format, length, sound strategy, and the first-frame rules.

6. Who exactly is this for? Describe one real person who should see it and act.
7. What does that person already believe or feel about the topic before watching?
8. Where does it live — Reels, TikTok, YouTube, a client pitch deck, a website hero? (Each has different physics.)
9. What should the viewer *do* immediately after watching — follow, DM, save, share, visit, hire?
10. Will most viewers have sound on or off? (On Instagram, design for off unless there's a reason not to.)
11. How does this person find the video — following you already, Explore/algorithm, a share, a paid push?

### Round 3 — Message & story (≈7 questions)

12. What is the single takeaway — the one sentence a viewer should be able to repeat to someone else?
13. What happens in the first 1.5 seconds? (That's the whole audition — the scroll decision is made there, and the first frame is also the cover.)
14. Walk me through the beats as you imagine them now, even roughly — what's the order of moments?
15. How long should it be, and why that length?
16. Is there a payoff, reveal, or turn — a moment the video builds toward?
17. What's the call to action, in the actual words that will appear on screen or in the caption?
18. What are you deliberately leaving OUT of this video? (Scope is a decision, not an accident.)

### Round 4 — Style & references (≈7 questions)

References are the fastest honest communication about style. Adjectives lie; links don't.

19. Which reference videos are you drawing from? For each: what *specifically* are you taking — the type, the palette, the cutting rhythm, a transition, a texture?
20. What should this video NOT look like? Name the failure mode (generic template reel, corporate explainer, over-filtered AI look…).
21. Palette — which two or three colors own the video? Do they come from your brand or from the concept?
22. Typography — what role does type play: hero (the type IS the visual), captioning, or labels? Any typeface in mind?
23. What's the mix — live footage, screen recording, motion graphics, 3D, photos? Rough percentages.
24. Which texture passes, if any — grain, glitch/datamosh, print/halftone, scanlines, particles? (These read as style signature; pick deliberately.)
25. How close to the reference is too close? Where's the line between homage and copy — and what will make this recognizably *yours*?

### Round 5 — Sound (≈4 questions)

26. Music: do you have a track, a genre, or a tempo in mind? Does the cut follow the track or the other way around?
27. Voice-over, on-screen type only, or both carrying the message?
28. Sound design — do hits, whooshes, and UI ticks matter for this one, or is the track enough?
29. Captions/subtitles: burned in, platform-generated, or none — and does the design account for where they sit?

### Round 6 — Production reality (≈7 questions)

The gap between concept and shipped video is production. Find the constraints now, not at hour six.

30. What assets already exist — footage, logos, brand fonts, photos, past projects to pull from?
31. What has to be created from scratch, and what's the hardest piece on that list?
32. What tools will you cut this in (After Effects, Premiere, CapCut, Blender, DaVinci…), and how confident are you in each for what this concept needs?
33. How many hours can you realistically give this, and over how many days?
34. Is there a deadline or a moment it needs to land (launch, event, algorithm timing)?
35. Formats and versions — aspect ratio(s), duration limits, safe zones, a cover frame, alternate cuts?
36. Who has to approve it before it posts — just you, a client, anyone else?

### Round 7 — Brand & series (≈5 questions)

One video is a post; a repeatable format is a presence.

37. How does this video position *you* — what should a potential client conclude about you from it alone?
38. Is this a one-off or the first of a series? If a series: what's the repeatable format, and what changes per episode?
39. Does it get a name/numbering system (Study 001, Vol. 1…)? Named series read as intentional bodies of work.
40. How does it sit next to what's already on the profile grid — continuity or a deliberate reset?
41. What's the caption strategy — first line (it's the second hook), hashtags, and whether the caption adds context or stays minimal?

### Round 8 — Success & risk (≈5 questions)

42. What does success look like — a number (views, saves, DMs, one client inquiry) or a feeling? Be honest about which.
43. What is this video explicitly NOT trying to do? (Non-goals prevent scope creep mid-edit.)
44. What's your biggest fear about it — the comment or silence you're bracing for?
45. What would make you scrap or restart it halfway through? (Knowing the kill-criteria upfront usually prevents the kill.)
46. If v1 ships imperfect, what's allowed to be imperfect — and what absolutely is not?

## After the interview: synthesize

Produce these four things, in this order. Base every line on the user's actual answers — quote their own words back where they were good.

### 1. Creative brief

Use this exact structure:

```
# [Working title] — Creative Brief
## The idea (one sentence)
## Audience & placement
## The message (takeaway + CTA)
## Style DNA (references, palette, type, mix, textures — and the line between homage and copy)
## Sound
## Constraints (tools, hours, deadline, formats, approvals)
## Success criteria & non-goals
```

### 2. Beat sheet

Beat-by-beat timing table: timestamp range, what's on screen, what the type says, what the sound does. The first beat gets the most detail — it's the scroll decision. Keep total runtime honest against Round 3's answer.

### 3. Issues (always)

List **at least 5 concrete problems, risks, or tensions** in the idea — with a suggested resolution for each. This is the section the user explicitly wants pushback in; a brief with no issues means the interview failed. Look especially for: audience/message mismatch (talking about yourself when the viewer cares about their problem), telling instead of showing, style borrowed too literally from a reference, scope beyond the hour budget, missing CTA, platform mechanics ignored (sound-off, safe zones, first frame), and one-off thinking where a series format would compound.

Deliver issues bluntly but constructively. The user asked for this; softening it wastes it.

### 4. Next actions

Three to five ordered steps, sized to the user's real time budget from Round 6. First step should be startable today.

## Save the record

When a filesystem/repo is available, save the brief so future sessions can build on it:

```
projects/NNN-short-slug/BRIEF.md   (NNN = next number: 001, 002, …)
```

Write the full synthesis (brief + beat sheet + issues + next actions) into that file, commit if the user's workflow commits such things, and tell the user where it lives. Future invocations of this skill: check `projects/` first and read prior briefs — the user's answers about brand, tools, and style carry across projects, and re-asking settled questions wastes interview budget.

## After the brief

Offer — don't launch into — the natural next steps: storyboard frames, an asset/shot list, a scene-by-scene build plan for their editor of choice, or generating reference/mock frames. The brief is the deliverable of this skill; production help is the next conversation.
