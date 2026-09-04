# OpenArt restyle prompts — The Room → "Good Girl"

`the-room-v1.mp4` is the structure: camera moves, cuts, timing, the fisheye, and every
beat-locked shake. A video-to-video restyle should change the LOOK and keep all of that,
which is why the strength setting matters more than the wording.

## The palette, read off the single cover

The cover art is disciplined: **one saturated colour and nothing else.** Hot magenta-pink
does all the work; the rest is cold neutral, blown white, and near-black. That is the same
one-signal-colour rule this studio already uses — it just swaps the warm family for a cold
one, for this piece only.

| role | hex | where it comes from |
|---|---|---|
| signal | `#F5265A` | the paint-pen lettering |
| blown white | `#FFFFFF` | the flash hitting the phone and skin |
| cream | `#EDE6DA` | the corset top |
| cold charcoal | `#1A1B1F` | the shutter in shadow |
| steel grey | `#3A4048` | the corrugated metal |

## Settings that matter more than the prompt

- **Strength / denoise 0.45–0.60.** Below 0.4 it stays a render; above 0.7 it invents its
  own camera and the beat sync is gone, which is the one thing that cannot be regenerated.
- **Chunk it.** Most video models cap at 5–10 s. Cut on the section boundaries — 0.0, 5.6,
  13.1, 16.9, 24.4 — so a chunk never straddles a look change.
- **Sections 4 and 5 (paint, waveform) are graphic on purpose.** A photoreal pass will
  fight them. Either leave those chunks ungenerated, or use the variant below, which asks
  for a projection rather than a paint layer.

## Master prompt

> Photorealistic restyle of @video1. Keep the exact camera movement, framing, cuts and
> timing — change only the look. A packed underground warehouse club at 3am, shot on a
> fisheye lens with harsh direct on-camera flash, the way a nightlife photographer shoots
> it. Hot fluorescent magenta-pink wash lights and lasers cutting through thick haze; cold
> bare concrete and corrugated metal; blown-out white where the flash hits skin, sweat and
> chrome. A dense silhouetted crowd with hands up, real bodies, motion blur on them. A DJ
> booth with lit CDJs and a mixer glowing under the pink. Deep crushed blacks, hard flash
> falloff, very high contrast, slight chromatic aberration, lens flare, heavy 35mm grain.
> Colour palette strictly limited to fluorescent magenta-pink #F5265A, blown white, cream
> #EDE6DA, cold charcoal #1A1B1F and steel grey #3A4048 — magenta is the only saturated
> colour in frame. Gritty editorial nightlife photography, real, physical, shot not
> rendered.

## Negative prompt

> warm orange light, amber, sepia, golden hour, teal and orange, rainbow lighting,
> oversaturated, 3d render, cgi, videogame, cartoon, illustration, smooth plastic surfaces,
> clean empty room, daylight, text, watermark, logo, subtitles, distorted faces, extra
> limbs, melting hands

## Per-section variants — append to the master prompt

**0.0–5.6 · booth**
> Extreme close on the CDJ jog wheels and mixer, magenta cue rings and channel lights
> glowing, a DJ's hands riding the platter, flash catching the metal.

**5.6–13.1 · the room**
> Pulling back through the crowd, hands and phones up, the booth small at the end of the
> room, one blown magenta light source behind it, haze thick in the beam.

**13.1–16.9 · the build**
> The lights drop out to almost nothing, the crowd lit only by a single magenta strobe,
> smoke filling the frame, the moment before the drop.

**16.9–24.4 · the drop** (graphic on purpose — pick one)
> *Photoreal:* strobes hard on the beat, magenta and white only, confetti and CO2 jets,
> the crowd exploding, flash frozen mid-motion.
> *Keep the paint:* leave this chunk ungenerated and use the original — the brush strokes
> are the studio's own language and a photoreal pass will only smear them.

**24.4–30.0 · the waveform**
> The room's walls become tall magenta LED columns pulsing with the music, the camera
> flying down the corridor between them, haze and lens flare.

## If it drifts

The failure to watch for is the model re-timing the shake. If the kick stops landing,
drop strength by 0.1 and regenerate that chunk — the sync is the part that cost the work.
