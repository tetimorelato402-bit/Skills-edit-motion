# ANVIL — Animated Product Walkthrough

Build a ~30 second animated product walkthrough for ANVIL, a location-verified
accountability app. It explains how the app works using real UI screens, with
Apple-caliber motion discipline rendered in Anvil's warm brand world.

---

## ASSETS IN THIS FOLDER

```
/screens/*.svg     15 production-clean vector UI screens
/audio/vo.mp3      voiceover (female, intense, measured delivery)
/audio/anvil-clang.mp3   metallic anvil strike SFX
```

Render screens as SVG — never rasterize. They must stay sharp at any zoom level.

---

## AUDIO PREP — DO THIS FIRST

The VO file needs two edits before use:

1. **Trim the lead.** First speech begins at **2.39s**. Cut everything before
   ~2.25s so the file starts essentially on the first word.

2. **Trim the tail.** The last spoken line to KEEP is *"Show up enough, and it
   compounds."* which ends at roughly **22.4s**. Everything after that —
   the spoken *"Anvil"* and *"Sharpen iron with iron"* — must be **cut out**.
   Those two beats appear on screen in SILENCE. That silence is intentional
   and is the ending of the film.

Working VO length after trimming: roughly **20 seconds**.

Then detect speech onsets in the trimmed file (energy envelope, 15ms window,
~3% of peak threshold; merge bursts under 0.22s apart; discard segments under
0.12s as breaths). Expect ~16 segments mapping in order to the lines below.

**PRINT the onset map and your line-to-segment assignment before building
anything.** This must be confirmed before a single frame is rendered.

---

## MANIFEST — screen : content : spoken line

| file | shows | VO line |
|---|---|---|
| `01_onboard_name.svg` | name entry | "It starts with your name." |
| `02_onboard_phone.svg` | phone verification | "Verified once. So your circle knows you're real." |
| `03_onboard_birthday.svg` | birthday | *(no line — quick pass, under 1s)* |
| `04_onboard_commitments.svg` | pick 3 commitments | "Choose what you're committing to." |
| `05_onboard_places.svg` | assign locations | "And exactly where you'll do it." |
| `06_home.svg` | home, commitments listed | "This is your word." |
| `07_tab_camera.svg` | camera **LOCKED** | "The camera stays locked." |
| `08_arrival_toast.svg` | arrival detected | "Until you actually arrive." |
| `09_camera_unlocked.svg` | camera unlocked | "Then it opens." |
| `11_circle_live.svg` | proof posted | "Proof, not words." |
| `10_friend_arrived.svg` | friend notification | "Your circle sees it. And you see them." |
| `07_tab_routine.svg` | streak / long game | "Show up enough, and it compounds." |
| — logo close — | anvil mark + ANVIL | **SILENT** |
| — tagline — | "Sharpen iron with iron." | **SILENT** |
| `07_tab_circle.svg` | circle empty state | b-roll, optional |
| `12_notification.svg` | iOS banner, wide format | floating overlay element |

---

## SYNC RULE (non-negotiable)

Each screen must be fully on-screen and **settled** before its line begins.
Derive each screen's entrance from `(VO onset − settle duration − 0.25s lead)`.

Never stretch, pitch, or reposition the VO. The visuals conform to the voice.

---

## STRUCTURE

- **Act 1 — SETUP** (01–05): quick, light, forward momentum
- **Act 2 — THE CONSTRAINT** (06, 07_tab_camera): slow down. The lock is the idea.
- **Act 3 — THE UNLOCK** (08, 09): the payoff. Give it weight.
- **Act 4 — THE LOOP** (11, 10): proof posts, circle responds
- **Act 5 — THE LONG GAME** (07_tab_routine) → silent logo close

---

## THE SILENT ENDING

After "and it compounds," the voice stops for good. What follows is silent:

1. Hold on the routine screen a beat
2. Everything recedes
3. The anvil mark forms, alone in the beige space
4. "ANVIL" settles beside it
5. "Sharpen iron with iron." fades in below
6. Hold. Let the silence sit. Fade out.

No music swell here either — let it go quiet. The silence is the ending.

---

## MOTION SYSTEM

Build as reusable config, not hand-animated keyframes.

Primary easing everywhere: `cubic-bezier(0.22, 1, 0.36, 1)`. **No linear motion.**

Primitives to define and reuse:

| name | behaviour |
|---|---|
| `settleIn` | enters at scale 1.04, settles to 1.0 with slight overshoot |
| `revealUp` | mask reveal from below, content slides up 24px |
| `crossDepth` | outgoing pushes back in z and fades; incoming comes forward |
| `focusPush` | camera pushes into one region of a screen |
| `holdBeat` | deliberate stillness — a first-class element, not dead air |
| `stagger` | children animate one at a time, 80ms apart |

Rules:
- One element moves at a time. Never stack simultaneous animations.
- Every screen settles before narration lands.
- Between acts, use `holdBeat`. Stillness carries the weight.
- Depth from soft shadow and scale. Never hard drop shadows.

---

## THE CAMERA-LOCK MOMENT (hero beat)

The most important seconds in the film. On `07_tab_camera`:

- Everything else stops moving
- Slow `focusPush` into the lock icon
- Hold. Longer than feels comfortable.
- `08_arrival_toast` slides in, the lock releases
- `crossDepth` into `09_camera_unlocked` with a warm light shift

Roughly 6 seconds. This is the product's entire thesis.

---

## BRAND

```
PAPER        #E7E0D2
CARD         #F2EDE4
INK          #15130E
BRONZE       #A8895E
BRONZE_DEEP  #7C6342
LINE         #D8CFBE
SOFT         #8B8475
BAR          #241C13
```

Fonts: **Fraunces** (display), **Inter** (body), **DM Mono** (labels).

The SVGs currently reference Georgia / Inter / Courier as stand-ins — swap the
`font-family` values to the real fonts.

Background: the beige PAPER world with a faint warm forge glow low in frame.
Screens float in that space with soft contact shadows. Warm and tactile, not a
dark tech void.

---

## AUDIO MIX

| layer | level |
|---|---|
| VO | 0 dB — master reference, never processed for timing |
| Piano bed | ducked −6 dB under VO, 200ms attack/release sidechain |
| Anvil clang | on the unlock only. Sits on top, never ducked. |
| Keyboard clicks | on typed UI moments, −8 dB |

Music fades out before the silent ending.

---

## DELIVERABLES

1. `src/motion.ts` — easing + primitives
2. `src/timeline.ts` — the whole video as declarative beats. All timing lives here.
3. Rendered MP4, 1920×1080, 30fps
4. `README.md` — how to preview, how to retime, how to render 720p–4K

---

## BUILD ORDER

1. **STOP** after trimming audio and printing the VO onset map. Show me that first.
2. Then build **Act 2 and Act 3 only** (the lock and the unlock). Show me that section.
3. Only then complete the rest.
