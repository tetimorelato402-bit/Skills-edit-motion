# BLUEPRINT REELS · Production brief for Claude Code
Version 2026-11-26 · Owner: Vanessa · Four vertical reels that feel like native creator content and reveal Blueprint only at the end.

---

## 0. Read this first (instructions for Claude Code)

You are the director, editor, animator and sound designer for four short reels. Work through this file top to bottom. It is the single source of truth: if something here conflicts with your habits, this file wins. If something here is ambiguous, ask Vanessa one short question before spending credits.

**Hard gates (stop and show Vanessa before continuing):**
1. **Cost gate.** Before any paid generation (images or video), estimate the total cost for the step and show it. Generate only after she says go.
2. **Cast gate.** After the character sheets exist, show them as one contact sheet. No shot is generated until she approves the cast.
3. **Board gate.** After the shot stills for a film exist, show them as one contact sheet in story order. Animate only after she approves.
4. **Cut gate.** Show a rough cut (picture plus temp sound) of each film before final mix and render.

**Build order:** Film 01 first end to end, then 02, 03, 04. Reuse every asset you can (characters, UI kit, SFX, end card).

**Never:** put text, logos or brand names inside AI-generated images (all text is composited in post); show the Blueprint name, logo or wordmark before the end card; copy the character from the reference reel; use cash or money piles on screen.

---

## 1. Deliverables

| File | Length | Frames @30 fps | Hook caption |
|---|---|---|---|
| `blueprint-reel-01-group-chat.mp4` | 30 s | 900 | When you share your business idea in the group chat |
| `blueprint-reel-02-family-dinner.mp4` | 20 s | 600 | Telling my family my business idea |
| `blueprint-reel-03-ideas-guy.mp4` | 20 s | 600 | Everyone made fun of the ideas guy |
| `blueprint-reel-04-that-look.mp4` | 20 s | 600 | POV: she has that look again |

**Specs (all four):** 1080x1920 vertical, 30 fps constant, H.264 High, yuv420p, BT.709 tagged, CRF 14 to 16, `+faststart`. Audio stereo AAC 256 kbps, 48 kHz, integrated loudness -14 LUFS, true peak at or below -1 dBTP. Exact frame counts above, no more, no less.

**Also deliver:** one cover frame per film (PNG, 1080x1920, a strong character moment with the hook caption, no logo), and the project folder so every film can be re-rendered.

**Suggested folder layout:**
```
blueprint-reels/
  BRIEF.md                    (this file)
  assets/logo/                (SVGs from Appendix A)
  assets/fonts/               (Inter, Newsreader, Caveat; all OFL)
  characters/<ID>/            (sheet.png, element id, notes.txt)
  shots/<film>/<shot>/        (still.png, clip.mp4, prompt.txt)
  ui/                         (chat kit, app screens; built in code)
  audio/music/ audio/sfx/ audio/vo/
  edit/                       (Remotion project or ffmpeg graphs)
  out/                        (final MP4s, covers, contact sheets)
```

---

## 2. The idea behind all four

These must not feel like ads. They are relatable, ironic comedy reels about people who keep having business ideas, in the exact grammar of the meme reels people already share: a stylized 3D animated character, one deadpan caption pinned near the middle of the screen, cuts on the beat, a few seconds of tension, a satisfying payoff.

The product appears only as an unbranded, generic app on a phone or laptop. The viewer understands what happened (the idea got listed, a buyer found it, it sold once, there was a handover call) without seeing a name. In the last four seconds the screen turns Blueprint blue, the logo switches on, and the narrator says "Blueprint. Get paid for thinking."

**The emotional engine, every film:** tension (embarrassment, doubt, chaos) then a dopamine ladder (each step of listing the idea pops with a rising sound) then the payoff (a big CHING on "Sold", yellow light, a reaction) then a final comic beat that makes people rewatch, then the reveal.

**What the viewer should feel:** "Wait, that's it? I could do that." The process looks effortless and the payoff feels huge. We never promise how fast or how much anyone earns (see section 3).

---

## 3. Brand and claims rules (non-negotiable)

**Blueprint is a live product. Present tense only.** Never write or show: coming soon, launch, waitlist, beta, early access, offers, discounts, deadlines, urgency.

**Allowed product facts (use only these):**
- One fixed price; each idea is sold once, to one buyer.
- Every idea is reviewed and compared with every other idea before it is listed.
- A free short card is public; a buyer signs an NDA to read the full idea.
- Payment is held until handover.
- Every sale comes with a video call (the handover call).
- Keyword search, no categories.
- Google sign-in exists, but never show the Google logo.
- Every file gets a dated fingerprint.
- A "My Blueprint" page holds your ideas and their status, purchases, NDAs and keyword alerts.

**Claims guardrails:**
- No statistics, ratings, earnings, user counts, ideas-sold counts, time-to-sale numbers.
- Nothing implying a sale happens instantly. Before any buyer appears, insert a "Later." card (or, in film 02, show that the sale lands during a dinner long after the idea was listed). Never "3 days later" or any number.
- No payout screens, no balances, no Blueprint fee.
- Prices are small and never called out (no zoom on a price, no caption about it).
- Any idea card shown carries a small "Example idea" tag.
- The feeling is "this is easy and satisfying", never "easy money". These ads go through Meta and TikTok review; anything that reads as get-rich-quick gets rejected.

**Banned words (copy, captions, dialogue, comments, UI):** genius, unicorn, hustle, grind, 10x, disrupt, revolutionize, game-changer, easy money, passive income, get rich, guaranteed, risk-free, instant cash.

**Banned imagery:** cash, money piles, coins raining, credit-card swipes of money, rockets, handshake close-ups, light bulbs over heads (the bulb belongs to the logo), stock-photo looks, real people or look-alikes, real brands, real app UIs (no iMessage, WhatsApp, Instagram, LinkedIn chrome), any logo except Blueprint's on the end card.

**Names:** invented names and handles only (listed in section 6). No real people, companies or places by name.

**Disclosure:** when a creator posts these, use the platform's paid-partnership label. When Blueprint's own account posts them as ads, the platform labels them. This does not change the creative.

---

## 4. Look bible

### 4.1 The reference
Vanessa's reference is an Instagram reel in the "When bro call me at 3am with a new business idea" format: a stylized 3D animated character, feature-film render quality, extreme close-ups of hands and eyes, a low-angle full-body hero shot by a night window, quick cuts on the beat, and one serif caption pinned across the middle of the frame. We match its quality and grammar. We do not copy its character (the lanky man in sunglasses, oversized suit and white socks is off limits, including that outfit).

### 4.2 Render style
- **Medium:** stylized 3D animated feature-film still and motion. Sculpted, slightly exaggerated characters; physically based materials; cinematic lighting.
- **Skin:** visible texture (pores, light stubble, freckles where noted), soft subsurface scattering, no plastic sheen.
- **Hair:** sculpted chunky clumps with fine flyaway strands that catch the rim light.
- **Fabric:** tactile and specific (chunky knit, brushed fleece, corduroy, nylon tracksuit sheen, flannel).
- **Eyes:** large irises with a clear catchlight. At every "idea" moment the catchlight becomes a tiny Idea Yellow glint.
- **Proportions:** adults about 6.5 heads tall, slightly elongated limbs and necks for leads, hands about 15% larger than realistic (hands do half the acting), strong brows and heavy upper eyelids for deadpan.
- **Acting:** deadpan comedy. Small, precise micro-expressions, long holds, slow head turns. No mugging, no cartoon squash and stretch.

### 4.3 Light and color (mapped to the Blueprint palette)
| Role | Color | Use |
|---|---|---|
| Night shadows | Night Navy `#0A1446` | all shadow fill; dark scenes never go grey or black |
| Ambient | Blueprint Blue `#1F3DFF` | window light, screen spill, city glow |
| The idea | Idea Yellow `#F6E27A` | desk lamp, phone glow at payoff, eye glints, "Sold" burst |
| Rim | Spark Coral `#FF5A36` | a thin rim on hair and shoulders at hero moments only |
| Surfaces in UI | Sky Tint `#E8ECFF`, Paper White `#FFFFFF` | app screens only |

Rules: night interiors lit by practicals (screens, a lamp, a fridge, a city window). Strong rim light on hero shots. Never teal-and-orange. Warm amber is allowed only in film 02's dinner (candles), always balanced against cold blue window light.

### 4.4 Camera language
- **Lenses:** 24 mm low-angle hero shots, 50 mm mediums, 100 mm macro for hands, eyes and screens. Shallow depth of field, oval bokeh.
- **Moves:** slow push-ins on feelings, one dolly zoom per film maximum, whip pans between beats, handheld micro-shake for phone POVs, slow motion (as if 120 fps) for the payoff and for hair in wind.
- **Shot rhythm:** most shots on screen 0.5 to 1.5 s. Generate 3 to 5 s and cut the best part.
- **Signature shots to use across the series:** screen reflected in glasses or aviators; macro of thumbs on a phone; eyes peeking over frames; the yellow glint; a low-angle silhouette against a night window.

### 4.5 Captions and type
- **Hook caption (the meme caption):** Newsreader, weight 600, Idea Yellow `#F6E27A`, soft dark shadow (0 3 12 rgba(10,20,70,0.55)), sentence case, centered, two lines maximum, about 64 to 72 px, top of the text block at about 37% of frame height (y about 700). It stays on screen for most of the film, exactly like the reference.
- **Dialogue subtitles:** Inter 600, white, 44 px, inside a rounded pill `rgba(10,20,70,0.72)`, placed at y about 1180 to 1300, never covering a face.
- **UI text:** Inter (400 to 700).
- **Handwriting (notebooks, sketches):** Caveat 600.
- **Safe zone:** all text between x 108 and x 972 and above y 1440 (platform buttons cover the bottom and right).

### 4.6 Global prompt blocks
**Style prefix (put at the start of every still prompt):**
> Stylized 3D animated feature film still, cinematic, sculpted characters with slightly exaggerated proportions, realistic skin texture with soft subsurface scattering, chunky sculpted hair with fine flyaways, tactile fabrics, night scene lit by practical lights, deep navy shadows, saturated electric blue ambient light, warm soft yellow key light from the idea source, thin coral rim light, shallow depth of field, anamorphic oval bokeh, subtle film grain, vertical 9:16 composition, no text.

**Negative prompt (every still and clip):**
> text, letters, words, captions, logos, watermarks, brand names, app interfaces, real people, celebrity likeness, cash, banknotes, coins, money, light bulb above head, rocket, handshake, teal and orange grade, grey dull lighting, plastic skin, extra fingers, fused fingers, deformed hands, distorted face, crossed eyes, low resolution, blurry face, sunglasses with oversized suit and white socks outfit

**Motion prompt suffix (every clip):**
> subtle natural motion, cinematic camera, consistent character, no morphing, no new objects appearing, no text

---

## 5. Toolchain

**Generation (paid, use the Matheus AI connector if connected):**
- Character sheets: load the connector's character-sheet workflow first (`get_preset_instructions` with `/character-sheet`), then save each approved character as an Element so every shot references the same identity.
- Shot stills: image generation with the character Element(s) referenced in the prompt, the style prefix and the negative prompt. Keep seed, aspect 9:16 and lighting notes consistent per scene.
- Motion: image-to-video from each approved still, 3 to 5 s, using the motion prompt. One retake maximum per shot unless Vanessa asks.
- Always run the connector's cost estimate before a batch (cost gate). Use batch tools and wait for jobs, then show results together.
- If no generator is connected, stop and tell Vanessa; do not fake the look with flat 2D.

**Post (local, free):**
- Edit and compositing: Remotion (React) or ffmpeg filtergraphs. All captions, chat bubbles, app screens, cards and the end card are built in code, not generated.
- Voice: Kokoro TTS (kokoro-onnx). Narrator voice `af_bella`, pitch +1 semitone with formants following (ffmpeg `rubberband=pitch=1.06:formant=shifted:pitchq=quality`). This is the same narrator as the earlier Blueprint films.
- Music: original only. Compose in code (Python synthesis) or a DAW. No library tracks, no trending sounds.
- SFX: licensed (the connector's sound-effect search and download, if available) or synthesized (Appendix C). Never rip sounds from apps or films.
- Mix: Python (numpy, scipy, soundfile) or a DAW. Loudness check with ffmpeg `ebur128`.

---

## 6. Cast bible

Every character is original. Build one character sheet per character: front, three-quarter, profile, back, full body in costume, and six expressions (neutral, deadpan, smug, horrified, laughing, the idea glint). Plain mid-grey background, even light, no text. Then save as an Element named with the ID.

**Rosa is the recurring buyer in all four films.** It quietly connects the series: the same warm stranger shows up on every handover call.

### C01 · Jordan (film 01 lead)
- 28, lanky and tall, long neck, slight slouch, big expressive hands.
- Medium-brown skin, light stubble, thick brows, heavy upper lids made for deadpan.
- Messy dark curls with flyaways; round thin wire glasses that reflect whatever screen he looks at.
- Cream heavyweight hoodie under a slouchy navy blazer, charcoal joggers, Idea Yellow socks, black slides.
- Prop: a beat-up Idea Yellow notebook with a pen clipped on.
- Signature expressions: unbothered deadpan; one-corner smug smile; eyes over the glasses.
- Handle: @lowlampnotes · Idea: **Larder Ring** · "A swap shelf for neighbors' spare pantry items" · small price · Example idea.
- Never: big grins, sunglasses, suits.

### C02 · Tay (film 01 friend)
- 26, deep brown skin, long box braids, small hoops, oversized sleep tee.
- Lives in bed, fairy lights behind her (blue and soft yellow).
- Signature: laughing so hard she drops her phone on her face; later bolts upright.

### C03 · Marcus (film 01 friend)
- 29, broad gym build, light olive skin, buzz cut, faded tank top, sweatband.
- Always mid-set at a dim neon-blue gym, phone balanced on a dumbbell rack.
- Signature: typing one-handed with a shaker in the other.

### C04 · Priya (film 01 friend)
- 30, warm brown skin, sharp chin-length bob, oversized tinted glasses, trench coat.
- Always in a parked car at night, dashboard light on her face.
- Signature: bone-dry deadpan; glasses slide down her nose at the end.

### C05 · Rosa (the buyer, all four films)
- Mid-40s, warm tan skin, laugh lines, dark wavy shoulder-length hair with one silver streak.
- Soft cardigan in muted blue, reading glasses on a chain.
- Always at a calm kitchen table at night or on a video call, a mug beside her.
- Signature: eyebrows rise with genuine interest; a slow approving nod; holds up the printed idea page to the camera on calls.
- Never shown with money. She is kind, curious, normal.

### C06 · Maya (film 02 lead)
- 27, light brown skin with freckles, big curly hair piled up and held with a pencil.
- Oversized oatmeal knit sweater with sleeves over her hands.
- Signature: polite smile hiding pure suffering; an eye twitch; drinking water for far too long; a slow turn to the camera.
- Handle: @quietfern · Idea: **Stillroom Hours** · "A quiet room you can book by the hour" · Example idea.

### C07 · Uncle Ray (film 02)
- 55, ruddy fair skin, big mustache, receding hair, round belly.
- Argyle sweater vest over a checked shirt, reading glasses pushed up on his head.
- Carves the roast while talking and gesturing with the carving knife (comic, never threatening).
- Signature: confident wrongness; later a conspiratorial whisper.

### C08 · Cousin Dani (film 02)
- 24, light tan skin, bleached fringe, earbuds in, phone always in hand.
- Never once looks up from his phone, face lit by its glow.

### C09 · Grandma Lu (film 02)
- 80, tiny, East Asian, short silver perm, pearl earrings, cardigan with a brooch.
- Moves slowly, speaks rarely, devastating every time.
- Signature: a slow head turn and a flat stare over her glasses.

### C10 · Theo (film 03 lead, "the ideas guy")
- 31, long and lean, olive skin, curly mullet, thin mustache.
- Tinted Idea Yellow aviators worn indoors at night (the running joke; he even sleeps in them).
- Oversized Blueprint-blue nylon tracksuit with a cream stripe, white tee, chunky sneakers.
- Gestures as if pitching to the universe. Points at skylines.
- Handle: @theoideas · Idea: **Hallway Gym** · "A fold-down workout rack for studio apartments" · Example idea.
- Never: a suit, white socks with no shoes, all-black sunglasses (keep him clearly distinct from the reference character).

### C11 · Kip (film 03, the coder)
- 27, pale skin, shaggy blond hair under over-ear headphones, grey hoodie.
- Lit only by two monitors (blue code glow, no readable text). Never stops typing.

### C12 · Grant (film 03, the investor)
- 45, tan skin, slicked silver hair, quilted vest over a crisp shirt, a tumbler of ice water.
- Signature: one eyebrow permanently raised.

### C13 · Nia (film 04 lead)
- 34, deep brown skin, sharp cheekbones, claw-clip messy bun with a pen stuck through it, stacked thin gold rings.
- Oversized cream button-down with rolled sleeves, black leggings.
- "The look": eyes narrow slowly, a tiny Idea Yellow glint in both pupils, the camera dolly-zooms.
- Handle: @tidewren · Idea: **Flatfold Cart** · "A laundry cart that folds flat for tiny apartments" · Example idea.

### C14 · Sam (film 04, Nia's partner)
- 36, big soft bear of a man, light skin, full ginger beard, round glasses, flannel shirt, socks with holes.
- Horror-movie reactions played completely straight. Hides the credit card in a bag of frozen peas.

---

## 7. Shared building blocks

### 7.1 The generic app (unbranded until the end card)
Built in code. Sky Tint `#E8ECFF` background, white cards with 24 px radius, Blueprint Blue `#1F3DFF` primary buttons with white Inter 600 text, Night Navy `#0A1446` headers, Inter throughout. No app name, no logo, no wordmark anywhere.

Screens to build once and reuse:
1. **New idea form:** fields "What it is", "Who it's for", "Why it matters"; typing animation with caret.
2. **Fingerprint stamp:** a dated stamp lands on the idea: "Fingerprinted · Nov 26, 2026" (date of the shoot is fine).
3. **Review:** a card with status pill "In review", then two checks: "Reviewed" and "Compared with every other idea".
4. **Live:** status pill flips "In review" to "Live" with a pop.
5. **Search (buyer side):** keyword field typing a word, the idea card appears (name, one-line pitch, small price, seller handle, "Example idea" tag).
6. **NDA:** short NDA sheet, signature written in Caveat with a stylus stroke, then the chip "Payment held until handover" (lock icon).
7. **Buy:** a "Buy this idea" button tap (buyer side). CHING (light) on the tap.
8. **Sold:** status becomes "Sold" (big, Idea Yellow on Night Navy), with the chip "Payment held until handover" and a small line "Sold once. One owner." CHING (full).
9. **Call frame:** generic video call with a main tile, a small self tile and three round controls (mic, camera, coral end-call). No brand.

### 7.2 The generic chat (film 01)
Dark mode, background `#0B0D16`, incoming bubbles `#262A3A` with white text, Jordan's outgoing bubbles Blueprint Blue `#1F3DFF`, 22 px radius, Inter 500 at 34 px on a 1080 frame, small round avatars with initials, group name "the council 💀" in the header. Typing indicator (three dots). It must not resemble iMessage, WhatsApp or any real app beyond being a chat.

### 7.3 Cards
- "Later." card: Night Navy full frame, Inter 700 white, 0.6 s, a soft whoosh.
- "Next family dinner." card (film 02 only): same style.

### 7.4 End card (identical in all four films)
- **Starts:** film 01 at frame 780 (26.0 s), films 02 to 04 at frame 480 (16.0 s). Call this frame `AT`. The bulb switches on at `ON = AT + 10` (film 01: 790; films 02 to 04: 489).
- **Entry:** a match cut from the film's last Idea Yellow light (a phone glow, a glint, a lens flare) into the bulb. 3 frames of Idea Yellow flash, then the Blueprint Blue field.
- **Field:** exactly `#1F3DFF`, full frame. No grain, no vignette, no grade on the end card.
- **Logo:** the lockup SVG from Appendix A, unmodified, scaled so the visible lockup is about 800 px wide, centered horizontally, visible center at y 812. Clear space at least the width of the bulb.
- **Logo animation:** the bulb starts dim (bulb fill `#4E61E2`, rays hidden), switches to `#F6E27A` over 2 frames at `ON`, then the five rays appear left to right, ray `i` (1 to 5) fully visible at `ON + 8 + 5*(i-1)`, each over 2 frames. After the last ray the SVG is exactly its original self. No glow, shadow, blur, rotation, stretch or recolor at any time.
- **Tagline:** "Get paid for thinking." Inter 800, white, 60 px, centered, top at y 1050, rises in at `ON + 36`.
- **Button:** white pill, Blueprint Blue text "Sell an idea" (Inter 700, 40 px, no trailing period), centered, top at y 1176, pops in at `ON + 48`.
- **VO:** narrator says "Blueprint." starting at `ON`, "Get paid for thinking." starting about 1.15 s later. VO must finish at least 1.0 s before the last frame. The final full second is a clean hold.
- **Sound signature:** analog switch click at `ON`, a warm rising tone under the logo (about 0.9 s rise, sustain, fade), and a glassy tick on each ray reveal.

### 7.5 The CHING rule
Every time "sell", "sold", "selling" or "buy" appears (spoken, in a caption, in a chat bubble, on a button or as a status), a CHING lands on the first frame of that word.
- **Full CHING:** the main payoff ("Sold" status). Loud, bright, slight stereo spread.
- **Light CHING:** secondary hits (a "Buy" button tap, "sell" in a chat bubble or subtitle). About 6 dB quieter and shorter.
- Never two full CHINGs within 2 s. If two triggers collide, keep the first full and make the second light.
- Each film lists its CHING frames in its script. Verify them in QA.

### 7.6 The dopamine ladder
Each listing step (form, fingerprint, review, live) gets a pop or tick that rises in pitch: start at E5 and climb a major scale (E, F#, G#, A, B), each 1/16 note apart in feel, landing on the beat. The final "Live" pop is the brightest. Then the "Sold" CHING sits on top of the musical drop.

---

## 8. Film 01 · "The group chat" (30 s, 900 frames)

**Logline:** Jordan shares a business idea in the group chat and gets roasted. He goes quiet, lists it, it sells, and he drops the screenshot. The chat flips.

**Hook caption (on screen 0.20 s to 26.0 s):** "When you share your business idea in the group chat"

**Music:** original, 140 bpm half-time feel (70 bpm pocket), soft trap drums, a plucky synth hook that mimics a notification rhythm. Full energy 0 to 6.0 s, cut to silence at 6.0, ticking clock and soft pad build from 7.5, dopamine ladder 7.5 to 12.0, minimal underscore 12.0 to 19.0, the drop lands exactly on the "Sold" frame (570), ride out to 26.0, then the end signature.

**CHING frames:** 445 light ("Buy this idea" tap) · 570 full ("Sold") · 680 light ("can I sell mine" bubble).

### Shots
**F01-S01 · 0.00 to 1.20 s (f0 to 36) · Macro, handheld**
- Picture: a phone face-up on a dark nightstand buzzing itself sideways, screen glow lighting a cold mug and a yellow notebook.
- UI overlay: notifications stacking on the phone screen (chat previews, unreadable at this size).
- SFX: buzz, buzz, buzz (each a little closer), three notification pops rising.
- Still prompt: [style prefix] macro shot of a smartphone lying face-up on a dark wooden nightstand at night, the screen glowing electric blue and lighting a ceramic mug and a worn yellow notebook, a lamp off in the background, shallow depth of field.
- Motion: the phone vibrates and slides a few millimetres, slow push-in.

**F01-S02 · 1.20 to 2.40 s (f36 to 72) · Extreme close-up**
- Picture: Jordan's eyes behind round wire glasses, the chat reflected in the lenses (composite the reflection in post), one eyebrow slowly rising.
- UI overlay: bubble from Tay pops near his face: "LMAOOO 💀"
- SFX: pop (pitch 1).
- Still prompt: [style prefix] extreme close-up of C01 Jordan's eyes behind round thin wire glasses, phone glow on his face from below, deadpan heavy-lidded expression, one eyebrow starting to rise.
- Motion: the eyebrow rises slowly, glasses glint.

**F01-S03 · 2.40 to 2.90 s (f72 to 87) · Medium, top-down**
- Picture: Tay in bed laughing so hard her phone drops onto her face.
- Overlay bubble: "a SHELF?? 😭"
- SFX: phone thud on face, muffled laugh, pop (pitch 2).
- Still prompt: [style prefix] top-down medium shot of C02 Tay lying in bed under fairy lights, laughing hysterically, phone falling toward her face, blanket messy.
- Motion: phone drops onto her face, she keeps laughing.

**F01-S04 · 2.90 to 3.40 s (f87 to 102) · Medium**
- Picture: Marcus at a neon-blue gym typing one-handed, shaker in the other hand.
- Overlay bubble: "a WHAT shelf"
- SFX: weights clank, pop (pitch 3).
- Still prompt: [style prefix] C03 Marcus in a dim gym lit by electric blue neon, sitting on a bench typing on his phone with one thumb, protein shaker in his other hand, incredulous face.
- Motion: thumb typing, head shake.

**F01-S05 · 3.40 to 4.00 s (f102 to 120) · Medium close**
- Picture: Priya in a parked car at night, dashboard glow, completely deadpan.
- Overlay bubble: "who would pay for that"
- SFX: car indicator tick, pop (pitch 4).
- Still prompt: [style prefix] C04 Priya sitting in the driver's seat of a parked car at night, dashboard light on her face, tinted oversized glasses, flat unimpressed expression, phone in hand.
- Motion: slow blink, tiny head tilt.

**F01-S06 · 4.00 to 6.00 s (f120 to 180) · Full-screen chat (built in code)**
- Top message (Jordan, blue): "ok hear me out. a swap shelf for neighbors' spare pantry stuff"
- Replies stack fast: "bro 😭" (126), "just say you're hungry" (138), "who would pay for that" (150), "next idea pls" (162), Tay sends a skull sticker (172).
- SFX: each bubble pops a semitone higher; light whoosh as the list scrolls.

**F01-S07 · 6.00 to 7.50 s (f180 to 225) · Low-angle hero, 24 mm**
- Picture: Jordan standing in his dark apartment by the window, slowly lowering the phone, face calm. City lights behind. Typing dots appear above his phone and vanish (overlay).
- Music: cut to silence at f180. Room tone, distant city.
- Still prompt: [style prefix] low-angle full-body shot of C01 Jordan standing by a tall night window in a dark apartment, city lights behind him in blue bokeh, holding his phone at chest height, calm deadpan expression, coral rim light on his curls.
- Motion: he slowly lowers the phone, looks out of the window.

**F01-S08 · 7.50 to 12.00 s (f225 to 360) · The quiet montage (cuts on the beat)**
| Frames | Picture | SFX (ladder) |
|---|---|---|
| 225 to 244 | macro: the yellow notebook opens, lamp clicks on (Idea Yellow) | lamp click, E5 pop |
| 244 to 263 | macro: pen sketches a little shelf with arrows (handwriting: "swap shelf" in Caveat, composited) | pen scratch, F#5 |
| 263 to 282 | app: New idea form, typing "A swap shelf for neighbors' spare pantry items" | key ticks, G#5 |
| 282 to 301 | app: fingerprint stamp lands "Fingerprinted · Nov 26, 2026" | stamp thud, A5 |
| 301 to 320 | app: "Reviewed" and "Compared with every other idea" checks | two dings, B5 |
| 320 to 340 | app: status flips to "Live" | bright pop |
| 340 to 360 | Jordan sits back in his desk chair, exhales | chair creak |
- Still prompts (AI shots only): notebook macro; pen hand macro; Jordan sitting back at his desk lit by a yellow lamp, laptop screen glowing (blank).

**F01-S09 · 12.00 to 12.60 s (f360 to 378) · "Later." card**
- SFX: soft whoosh.

**F01-S10 · 12.60 to 14.00 s (f378 to 420) · Medium, Rosa's kitchen**
- Picture: Rosa at her kitchen table at night with a mug, laptop open. Cut to app insert: search field types "pantry", the Larder Ring card appears (Example idea tag, small price, @lowlampnotes). Back on Rosa: eyebrows rise.
- SFX: key ticks, soft ding when the card appears.
- Still prompt: [style prefix] C05 Rosa sitting at a calm kitchen table at night with a mug of tea, laptop open in front of her, blue screen light on her face, reading glasses on a chain, curious expression.
- Motion: eyebrows rise, she leans in.

**F01-S11 · 14.00 to 15.50 s (f420 to 465) · App inserts**
- NDA sheet, stylus signature "Rosa M." in Caveat (420 to 438), "Buy this idea" button tapped at f445, chip "Payment held until handover" slides in (448).
- SFX: stylus scratch, button tap, **light CHING at f445**, soft lock click at 448.

**F01-S12 · 15.50 to 19.00 s (f465 to 570) · The handover call**
- Picture: call frame (built in code). Main tile: Rosa smiling, nodding (AI clip). Small tile: Jordan holding his notebook page up to the webcam (AI clip). Small label above the frame: "Handover call".
- SFX: call-connect two-note chime at 466, room tone, a soft laugh.
- No lip-sync: Rosa listens and nods; Jordan's mouth is hidden behind the notebook page.
- Still prompts: [style prefix] webcam view of C05 Rosa on a video call at her kitchen table, smiling and nodding warmly, holding a printed page; and [style prefix] webcam view of C01 Jordan holding a page of sketches up to the camera, only his eyes and glasses visible above the page, desk lamp glow.

**F01-S13 · 19.00 to 20.00 s (f570 to 600) · The payoff, slow motion**
- Picture: app insert "Sold" (big Idea Yellow on Night Navy) with "Payment held until handover" and "Sold once. One owner." (570 to 582), then Jordan's face in slow motion as Idea Yellow light washes over it, curls lifting, coral rim (582 to 600).
- Caption change at f570: hook caption gets a second line: "…and then you sell it".
- SFX: **full CHING at f570**, music drop, a soft whoosh of light.
- Still prompt: [style prefix] close-up of C01 Jordan in slow motion, warm yellow light washing over his face from his laptop, a tiny smug smile, curls lifting slightly, coral rim light, glasses reflecting yellow.
- Motion: slow motion, hair lifts, light intensifies.

**F01-S14 · 20.00 to 24.00 s (f600 to 720) · The chat flips (built in code, with two reaction cutaways)**
- Jordan posts a screenshot of the Sold card (f600, attachment animation).
- Silence for half a second (600 to 615).
- Bubbles cascade, each a semitone higher: "wait" (618), "WAIT" (630), "how" (642), "teach me 😭" (654), "ok so I have an idea too" (666), Marcus: "can I sell mine" (680, **light CHING**).
- Cutaway 690 to 705: Priya's glasses slide down her nose (AI clip).
- Cutaway 705 to 720: Tay bolts upright in bed (AI clip).

**F01-S15 · 24.00 to 26.00 s (f720 to 780) · Close-up, push-in**
- Picture: Jordan reads the chat, the corner of his mouth lifts. The phone glow turns Idea Yellow. Push into the glow until it fills the frame (770 to 780).
- SFX: a soft rising air whoosh into the end card.

**End card · 26.00 to 30.00 s (f780 to 900):** section 7.4, `AT` 780, `ON` 790. Hook caption ends at f780.

---

## 9. Film 02 · "Telling my family my business idea" (20 s, 600 frames)

**Logline:** Maya's family roasts her idea at dinner. Under the table, her listing sells. At the next family dinner, her uncle wants to sell his.

**Hook caption (0.20 s to 16.0 s):** "Telling my family my business idea" (second line from f270: "(meanwhile, under the table)").

**Music:** warm brushed-jazz dinner music, 96 bpm, upright bass and soft Rhodes. It stops dead at every awkward line (comic silence), returns as quiet lo-fi under the table, swells with the CHING, plays a playful pizzicato for "Next family dinner", then hands over to the end signature.

**CHING frames:** 300 full ("Sold" under the table) · 430 light (Uncle: "how do I sell mine?").

### Shots
**F02-S01 · 0.00 to 1.00 s (f0 to 30) · Macro**
- Picture: a fork tapping a wine glass (water in it), warm candlelight, steam from dishes.
- Subtitle (Uncle Ray, from f8): "So! What's the new idea?"
- SFX: glass clink clink clink, table murmur.
- Still prompt: [style prefix with warm candlelight balanced by cold blue window light] macro of a fork tapping a glass of water at a family dinner table, candles, steaming dishes, a roast in the background, no faces.
- Motion: the fork taps twice.

**F02-S02 · 1.00 to 2.40 s (f30 to 72) · Medium close, slow push**
- Picture: Maya with a frozen polite smile, gripping her fork; her eye twitches at f60.
- SFX: murmur cuts out at f30, a loud clock tick, one cricket (comic).
- Still prompt: [style prefix] C06 Maya at a family dinner table, frozen polite smile, holding her fork, candlelight on one side and blue window light on the other.
- Motion: slow push-in, a tiny eye twitch.

**F02-S03 · 2.40 to 4.00 s (f72 to 120) · Over the shoulder**
- Picture: Maya explaining with her hands, seen past the candles and Uncle Ray's shoulder (her mouth partly hidden by a candle flame in the foreground).
- Subtitle (Maya): "Quiet rooms you can book by the hour."
- SFX: music returns softly.

**F02-S04 · 4.00 to 5.20 s (f120 to 156) · Medium**
- Picture: Uncle Ray, carving knife paused in the air mid-gesture, confident.
- Subtitle: "So it's a hotel… but tiny?"
- SFX: knife scrape on the plate, music stops.
- Still prompt: [style prefix] C07 Uncle Ray at the head of a dinner table holding a carving knife and fork over a roast, mid-gesture, confident expression, reading glasses on his head.

**F02-S05 · 5.20 to 6.40 s (f156 to 192) · Medium close**
- Picture: Cousin Dani, earbuds in, never looks up from his phone.
- Subtitle: "That already exists."
- SFX: a single phone tap.

**F02-S06 · 6.40 to 8.00 s (f192 to 240) · Close-up, slow head turn**
- Picture: Grandma Lu slowly turns her head toward Maya, stares over her glasses.
- Subtitle (f210): "Is it a pyramid thing?"
- SFX: a comic three-note organ sting at f222.
- Still prompt: [style prefix] close-up of C09 Grandma Lu at a dinner table, slowly turning her head, flat stare over her glasses, pearl earrings catching candlelight.

**F02-S07 · 8.00 to 9.00 s (f240 to 270) · Close-up**
- Picture: Maya drinking water for far too long, eyes dead.
- SFX: long gulps, a clock tick.

**F02-S08 · 9.00 to 12.50 s (f270 to 375) · Under the table**
- Picture: her phone in her lap glowing (AI shot), then app inserts: a notification "Stillroom Hours · NDA signed" (276), then "Stillroom Hours · Sold" with the chip "Payment held until handover" (300). Back to Maya's face lit from below in Idea Yellow, a tiny smile she can't hide (315 to 375). Uncle Ray keeps talking, muffled.
- Note: the sale lands long after she listed it (that is the joke: it sells while they mock it). No time numbers.
- SFX: phone vibration, **full CHING at f300**, the room sound muffles as if underwater, then returns.
- Still prompts: [style prefix] macro of a phone glowing in a woman's lap under a dinner table, knit sleeves, candlelight above; and [style prefix] C06 Maya's face lit from below by a warm yellow phone glow, a tiny suppressed smile, family blurred behind her.

**F02-S09 · 12.50 to 13.10 s (f375 to 393) · "Next family dinner." card**
- SFX: soft whoosh, pizzicato starts.

**F02-S10 · 13.10 to 15.30 s (f393 to 459) · Medium, by the coat rack**
- Picture: Uncle Ray corners Maya by the coat rack, hand on her shoulder, whispering. At f440 Maya turns slowly to the camera (fourth-wall look).
- Subtitle (Uncle, from f420): "So… how do I sell mine?"
- SFX: **light CHING at f430** (on "sell"), comic beat of silence as she turns.
- Still prompt: [style prefix] C07 Uncle Ray and C06 Maya by a coat rack in a hallway, he leans in conspiratorially with a hand on her shoulder, she stares ahead with a deadpan face, warm hallway light and blue window light.
- Motion: he leans in, she slowly turns her head to the camera.

**F02-S11 · 15.30 to 16.00 s (f459 to 480) · Push into her phone's yellow glow → end card.**

**End card · 16.00 to 20.00 s (f480 to 600):** `AT` 480, `ON` 489.

---

## 10. Film 03 · "The ideas guy" (20 s, 600 frames)

**Logline:** Everyone mocks Theo for "just having ideas". At 3 a.m. he lists one, it sells, and he lowers his aviators: "Execution is so overrated."

**Hook caption (0.20 s to 16.0 s):** "Everyone made fun of the ideas guy"

**Music:** cinematic trap, 150 bpm (75 bpm feel), 808s and a choir pad. Hard cut to silence at the 3 a.m. shot (f165), heartbeat build, dopamine ladder montage, a brass stab and full drop on "Sold" (f360), a smug sax sting on his line (f400).

**CHING frames:** 360 full ("Sold").

### Shots
**F03-S01 · 0.00 to 1.50 s (f0 to 45) · Low-angle hero, 24 mm**
- Picture: Theo on a night rooftop, wind in his mullet, pointing at the skyline like he invented it. Yellow aviators.
- SFX: wind, a big cinematic whoosh, beat starts.
- Still prompt: [style prefix] low-angle full-body shot of C10 Theo on a rooftop at night, pointing confidently at the city skyline, wind blowing his curly mullet, tinted yellow aviators, blue tracksuit, coral rim light.
- Motion: wind in hair and tracksuit, slow push-in.

**F03-S02 · 1.50 to 2.70 s (f45 to 81) · Medium**
- Picture: Kip at his desk, headphones on, never stops typing, doesn't look up.
- Subtitle: "Ideas are worthless. Execution is everything."
- SFX: mechanical keyboard clatter.
- Still prompt: [style prefix] C11 Kip at a dark desk lit only by two blue monitors (no readable text), over-ear headphones, typing, not looking up, unimpressed.

**F03-S03 · 2.70 to 3.90 s (f81 to 117) · Medium close**
- Picture: Grant with a tumbler of ice water, one eyebrow raised.
- Subtitle: "So… no product. Just… ideas?"
- SFX: ice clink.

**F03-S04 · 3.90 to 5.50 s (f117 to 165) · Phone screen (built in code)**
- A generic social post by @theoideas: "new idea: a fold-down gym rack for studio apartments". Comments flood in: "ideas guy spotted 🚨", "build it then", "bro thinks thinking is a job", "ratio".
- SFX: rapid pops, a crowd "ooooh".

**F03-S05 · 5.50 to 7.00 s (f165 to 210) · Overhead, then slow motion**
- Picture: 3 a.m., Theo in bed staring at the ceiling, aviators still on. A tiny yellow glint in the lenses (f180). He sits up in slow motion.
- SFX: total silence at f165, then a heartbeat, a single bass note at f180.
- Still prompt: [style prefix] overhead shot of C10 Theo lying in bed at night staring at the ceiling, still wearing tinted yellow aviators, blue moonlight through blinds, a tiny yellow glint in the lenses.

**F03-S06 · 7.00 to 10.00 s (f210 to 300) · Montage (dopamine ladder)**
| Frames | Picture | SFX |
|---|---|---|
| 210 to 228 | macro: pen sketching a fold-down rack (Caveat note "folds up, saves the hallway") | pen scratch, E5 |
| 228 to 246 | app: New idea form typing "A fold-down workout rack for studio apartments" | key ticks, F#5 |
| 246 to 264 | app: fingerprint stamp | stamp thud, G#5 |
| 264 to 282 | app: "Reviewed" checks | dings, A5 |
| 282 to 300 | app: "Live" | bright pop, B5 |

**F03-S07 · 10.00 to 10.60 s (f300 to 318) · "Later." card**

**F03-S08 · 10.60 to 12.00 s (f318 to 360) · The call**
- Picture: Theo's aviators reflect the call (composite); cut to the call frame: Rosa nodding, holding his printed page; small tile Theo, aviators on, perfectly still.
- SFX: call chime, a soft "mm" of approval from Rosa.

**F03-S09 · 12.00 to 13.00 s (f360 to 390) · Payoff, slow motion**
- Picture: "Sold" app insert (360 to 370), then Theo in slow motion, Idea Yellow light washing over him, mullet lifting, coral rim.
- SFX: **full CHING at f360**, brass stab, drop.

**F03-S10 · 13.00 to 15.40 s (f390 to 462) · Close-up to camera**
- Picture: Theo turns to camera and slowly lowers his aviators.
- Subtitle (f400): "Execution is so overrated."
- Cutaway 440 to 462: Kip stops typing for the first time and peeks over his monitor.
- SFX: smug sax sting at f400, keyboard stops dead at f440.

**F03-S11 · 15.40 to 16.00 s (f462 to 480) · A yellow lens flare in the aviators → end card.**

**End card · 16.00 to 20.00 s (f480 to 600):** `AT` 480, `ON` 489.

---

## 11. Film 04 · "POV: she has that look again" (20 s, 600 frames)

**Logline:** Sam sees "the look" on Nia's face and panics: another company, another LLC. He hides the credit card in the freezer. Twist: she just sells the idea. Then she gets the look again.

**Hook caption (0.20 s to 16.0 s):** "POV: she has that look again"

**Music:** horror-parody strings (original, detuned string cluster, slow tremolo, a heartbeat kick) from 0 to 8.6 s. At the twist (f258) the lamp stops flickering and the music flips to a warm 90 bpm R&B groove. A horror sting returns for the last gag (f450).

**CHING frames:** 270 light (Nia: "I'm just going to sell it.") · 396 full ("Sold").

### Shots
**F04-S01 · 0.00 to 1.20 s (f0 to 36) · Medium**
- Picture: Sam on the couch eating cereal in the dark, freezes mid-bite, slowly looks toward the kitchen.
- SFX: cereal crunch stops, a violin screech at f18.
- Still prompt: [style prefix] C14 Sam sitting on a couch at night eating cereal from a bowl, frozen mid-bite, eyes slowly turning sideways in fear, TV glow on his face.

**F04-S02 · 1.20 to 2.60 s (f36 to 78) · Dolly zoom**
- Picture: Nia at the kitchen counter, backlit by the open fridge, slowly turning her head. Dolly zoom.
- SFX: horror riser, heartbeat.
- Still prompt: [style prefix] C13 Nia standing at a kitchen counter at night, backlit by an open fridge, slowly turning her head toward camera, eyes narrowing, pen stuck in her messy bun.

**F04-S03 · 2.60 to 3.60 s (f78 to 108) · Extreme close-up**
- Picture: Nia's eyes narrow; a tiny Idea Yellow glint appears in both pupils at f90.
- Subtitle (whisper, f92): "What if…"
- SFX: glint shimmer, whispered reverb.

**F04-S04 · 3.60 to 5.00 s (f108 to 150) · Medium, frantic**
- Picture: Sam opens the freezer and hides a credit card (blank, no logo, no numbers) inside a bag of frozen peas.
- SFX: freezer door, ice crackle, a comic stab.
- Still prompt: [style prefix] C14 Sam in a dark kitchen hiding a blank card inside a bag of frozen peas in an open freezer, frosty blue light, panicked expression.

**F04-S05 · 5.00 to 6.20 s (f150 to 186) · Close, behind a curtain**
- Picture: Sam whispering into his phone, half hidden by a curtain.
- Subtitle: "She's starting another LLC."
- SFX: whisper, distant thunder (comic).

**F04-S06 · 6.20 to 7.60 s (f186 to 228) · Medium, lamp flicker**
- Picture: Nia writing frantically in a notebook, possessed energy, hair moving, the lamp flickering.
- SFX: fast pen scratch, lamp buzz and flicker.
- Still prompt: [style prefix] C13 Nia at a desk writing frantically in a notebook under a flickering lamp, intense focus, strands of hair falling loose, horror-movie lighting with deep navy shadows.

**F04-S07 · 7.60 to 8.60 s (f228 to 258) · Medium**
- Picture: Sam peeking around the corner, terrified.

**F04-S08 · 8.60 to 11.40 s (f258 to 342) · The twist**
- Picture: over Nia's shoulder: not LLC paperwork, just the app on her laptop (built in code). The lamp stops flickering and settles warm (f258).
- Subtitle (Nia, f262): "Relax. I'm just going to sell it."
- App inserts: "One fixed price" field (282), "Reviewed" checks (300), "Live" (318).
- SFX: **light CHING at f270** (on "sell"), music flips to the R&B groove at f258, ladder pops at 282, 300, 318.

**F04-S09 · 11.40 to 12.00 s (f342 to 360) · "Later." card**

**F04-S10 · 12.00 to 13.20 s (f360 to 396) · The call**
- Picture: call frame on Nia's laptop: Rosa holds up the Flatfold Cart sketch and nods; Nia holds her notebook. In the background, Sam rises slowly from behind the couch.
- SFX: call chime.

**F04-S11 · 13.20 to 14.20 s (f396 to 426) · Payoff**
- Picture: "Sold" app insert (396 to 406), then Sam pulls the frozen card out of the peas and holds it up like a trophy, exhaling.
- SFX: **full CHING at f396**, relieved exhale, ice crack.

**F04-S12 · 14.20 to 15.60 s (f426 to 468) · Close-up**
- Picture: Nia looks straight at the camera; the yellow glint returns in her eyes (f440).
- Subtitle (Sam, off-screen, f446): "…no."
- SFX: horror sting at f450, cut to silence.

**F04-S13 · 15.60 to 16.00 s (f468 to 480) · Push into the glint → end card.**

**End card · 16.00 to 20.00 s (f480 to 600):** `AT` 480, `ON` 489.

---

## 12. Sound bible

### 12.1 Voice
- **Narrator (end card only):** Kokoro `af_bella`, speed about 0.86 to 0.94 (slowest that fits), pitch +1 semitone with formants following. Warm, close, unhurried. Stress "Blue" in Blueprint. Lines: "Blueprint." then "Get paid for thinking."
- **Character lines are subtitles by default.** Optional character voices (Kokoro) only where the speaker's mouth is hidden or off-screen: Uncle Ray `am_michael`, Dani `am_puck`, Grandma Lu `bf_emma` (slow), Kip `am_echo`, Grant `bm_george`, Theo `am_fenrir` (smug, slow), Nia whisper `af_nicole`, Sam whisper `am_adam`. If a line needs visible lip-sync, keep it subtitle-only instead.

### 12.2 Music
Original compositions only, per the film sections above. Structure every cue to the frame map: silences and drops are part of the joke. End each film's music by `AT` and let the end-card signature take over.

### 12.3 SFX list
CHING (full and light), notification pop (with the rising ladder), phone buzz, keyboard and phone typing ticks, pen scratch, rubber stamp thud, check ding, "Live" pop, NDA stylus stroke, lock click, call-connect chime, whoosh and whip, "Later." whoosh, glint shimmer, slow-motion air swell, record stop, horror violin screech, horror riser, heartbeat, comic organ sting, comic stab, sax sting, brass stab, crowd "ooooh", ice clink, freezer door and ice crackle, cereal crunch, lamp buzz and flicker, clock tick, cricket, room tones (apartment, dinner, gym, car, rooftop wind), and the end signature (switch click, warm rise, glassy ray ticks). Recipes for the synthesized ones are in Appendix C.

### 12.4 Mix
- Dialogue and VO on top. Music ducked about 8 dB under any voice (sidechain from the VO and dialogue stems, 70 ms attack, 250 ms release).
- CHING full peaks about 3 dB under the VO peak; light CHING 6 dB under that.
- SFX bed about 9 to 10 LU under the voice.
- Master: -14 LUFS integrated, true peak at or below -1 dBTP (4x oversampled limiter), 0.5 s fade on the very end.
- Every film must make sense on mute: captions and subtitles carry every joke.

---

## 13. Production steps (do them in this order)

1. **Setup:** create the folder layout; save the SVGs from Appendix A; install fonts (Inter, Newsreader, Caveat from Fontsource or Google Fonts, all OFL).
2. **Build the code kit first (free):** chat kit, app screens, cards, captions, subtitle pills and the end card with the logo animation. Render a still of each and of the end card at `ON + 40`. Check the logo against the SVG.
3. **Cost gate:** estimate character sheets (14), stills (about 60), clips (about 45). Show the estimate.
4. **Characters:** generate the 14 character sheets, save each as an Element, show one contact sheet (cast gate).
5. **Stills:** for each film, generate the shot stills in story order using the Elements and the prompt blocks. Show one contact sheet per film (board gate). Fix any off-model faces or hands before animating.
6. **Motion:** image-to-video for every AI shot, 3 to 5 s each. Pick the best 0.5 to 1.5 s.
7. **Edit:** cut to the frame maps in sections 8 to 11. Composite UI, captions, subtitles, reflections and cards. Color-match every shot to section 4.3.
8. **Sound:** music, SFX (with the CHING and ladder frames), VO, mix to spec.
9. **Rough cut gate:** show each film.
10. **Final:** render, run the QA checklist, export covers, deliver.

---

## 14. QA checklist (every film)

- [ ] Exact frame count (900 or 600) and duration; 1080x1920; 30 fps; -14 LUFS; true peak at or below -1 dBTP.
- [ ] Hook caption readable in the first 0.5 s, inside the safe zone, never covering a face.
- [ ] No Blueprint name, logo, wordmark or brand UI before `AT`.
- [ ] No text, logos or watermarks inside any AI-generated frame; all text is composited and spelled correctly.
- [ ] A CHING on every sell / sold / selling / buy, on the listed frames; no two full CHINGs within 2 s.
- [ ] "Later." card (or the dinner logic in film 02) before any buyer appears; no time numbers anywhere.
- [ ] Every idea card shows "Example idea"; prices small and never called out.
- [ ] Only allowed product facts; present tense; none of the banned words; no cash, bulbs over heads, real brands, real people or Google logo.
- [ ] Characters on-model in every shot (faces, outfits, props); Theo is clearly different from the reference character.
- [ ] Hands: correct finger count in every frame.
- [ ] End card: field exactly `#1F3DFF`; logo is the unmodified SVG at about 800 px visible width; bulb dim to on at `ON`; rays left to right; tagline and button readable for the final full second; VO finished at least 1 s before the end.
- [ ] Watch once on mute: every joke still lands.

---

## Appendix A · Logo SVGs (traced from Vanessa's files, not redrawn)

These are vector traces of `blueprint-lockup-blue.png` (1600x600) and `blueprint-mark.png` (1000x1000). Rendered back, they match the source files with a mean pixel difference under 0.6 out of 255. Every piece has an id so it can be animated: `ray-1` to `ray-5` (left to right), `bulb` (`bulb-glass` plus the yellow counter inside the B), `base-1` to `base-3`, and one path per letter in `wordmark`.

**Rules:** use as-is. Never change paths, colors or proportions; scale uniformly only. For a transparent version of the lockup, delete the `field` rect (the wordmark is white, so it needs a dark or blue background).

Brand colors: Blueprint Blue `#1F3DFF`, Idea Yellow `#F6E27A`, Paper White `#FFFFFF`, Night Navy `#0A1446`, Sky Tint `#E8ECFF`, Spark Coral `#FF5A36`.

### A.1 Lockup on Blueprint Blue (save as `assets/logo/blueprint-lockup.svg`)
```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1600 600" width="1600" height="600">
  <title>Blueprint lockup</title>
  <rect id="field" width="1600" height="600" fill="#1F3DFF"/>
  <g id="mark">
    <g id="rays" fill="#F6E27A">
      <path id="ray-1" d="M294.08 273.25 L294.08 274.92 L294.92 276.92 L297.25 277.92 L307.25 277.92 L309.25 277.25 L310.42 275.08 L310.08 272.25 L307.75 270.58 L296.92 270.58 L294.92 271.58 Z"/>
      <path id="ray-2" d="M318.92 215.58 L318.08 217.08 L318.58 219.75 L325.92 227.25 L328.58 228.25 L331.42 226.25 L332.08 224.08 L331.25 222.25 L324.75 215.58 L322.08 214.08 L320.42 214.42 Z"/>
      <path id="ray-3" d="M387.58 191.42 L385.75 192.42 L384.75 194.75 L384.75 203.92 L386.08 206.92 L387.58 207.58 L389.42 207.58 L390.92 206.92 L392.08 204.92 L392.25 195.08 L390.75 191.92 Z"/>
      <path id="ray-4" d="M456.92 214.58 L454.92 214.08 L453.25 214.75 L445.75 222.25 L444.92 224.75 L446.75 227.42 L449.08 228.25 L451.08 227.25 L458.42 219.75 L458.92 217.25 Z"/>
      <path id="ray-5" d="M466.58 273.08 L466.75 275.92 L467.75 277.25 L469.75 277.92 L479.75 277.92 L481.42 277.42 L482.92 274.75 L482.42 271.92 L480.08 270.58 L469.25 270.58 L467.92 271.25 Z"/>
    </g>
    <g id="bulb" fill="#F6E27A" fill-rule="evenodd">
      <path id="bulb-glass" d="M368.25 219.75 L360.92 222.75 L349.92 229.58 L340.58 239.08 L334.58 248.25 L330.75 258.58 L329.58 263.58 L328.75 271.08 L328.75 277.92 L329.58 284.75 L332.75 295.75 L336.75 303.75 L341.75 310.92 L346.75 316.75 L355.42 324.92 L358.42 328.92 L360.58 333.08 L361.58 336.42 L362.42 347.42 L414.25 347.58 L414.92 346.92 L414.92 339.08 L415.42 336.08 L417.75 330.25 L421.42 325.08 L430.42 316.25 L437.42 307.92 L441.25 301.75 L445.25 292.75 L447.25 285.42 L448.25 277.42 L447.42 263.92 L445.25 255.42 L440.42 245.08 L433.25 235.58 L425.92 228.75 L415.58 222.58 L404.75 218.75 L399.08 217.58 L389.92 216.75 L377.92 217.58 Z M399.58 242.58 L404.42 244.58 L408.25 247.42 L411.58 251.08 L414.42 257.25 L414.92 261.75 L414.42 267.92 L412.42 272.92 L409.08 277.75 L415.42 283.92 L418.25 289.08 L419.58 295.42 L419.25 301.75 L417.42 307.42 L413.58 312.75 L409.42 316.42 L405.58 318.58 L397.08 320.42 L379.92 320.42 L379.42 320.92 L379.42 341.58 L378.42 343.75 L376.58 345.25 L373.08 345.42 L370.58 343.25 L370.08 341.42 L370.25 245.08 L372.08 242.58 L374.25 241.92 L394.75 241.92 Z"/>
      <path id="bulb-inner-1" d="M379.92 251.42 L379.42 251.92 L379.58 310.58 L397.25 310.92 L401.58 310.08 L405.58 307.58 L409.25 302.75 L410.25 298.92 L410.25 295.42 L409.25 291.92 L406.58 287.92 L402.42 284.75 L399.42 283.75 L393.75 283.58 L391.42 282.42 L389.58 279.75 L389.58 277.92 L390.42 276.08 L392.08 274.58 L398.75 273.25 L403.08 269.92 L405.42 265.75 L405.25 259.25 L403.25 255.58 L401.08 253.58 L397.92 251.75 Z"/>
    </g>
    <g id="base" fill="#FFFFFF">
      <path id="base-1" d="M358.25 357.92 L358.75 360.58 L360.58 361.92 L416.25 361.92 L418.25 360.58 L418.75 358.25 L418.25 355.92 L417.08 354.75 L415.75 354.42 L361.25 354.42 L359.92 354.75 L358.58 356.08 Z"/>
      <path id="base-2" d="M362.75 369.25 L363.42 372.08 L364.92 373.42 L412.08 373.42 L413.58 372.08 L414.25 370.42 L413.42 367.08 L410.75 365.75 L366.25 365.75 L364.08 366.58 Z"/>
      <path id="base-3" d="M370.92 380.08 L371.08 382.92 L371.58 383.92 L373.08 384.92 L403.92 384.92 L405.42 383.92 L406.08 382.08 L406.08 380.25 L405.42 378.75 L404.08 377.58 L374.08 377.42 L372.58 377.75 Z"/>
    </g>
  </g>
  <g id="wordmark" fill="#FFFFFF" fill-rule="evenodd">
    <path id="letter-B" d="M556.25 234.92 L555.92 235.42 L555.92 365.08 L556.58 365.42 L624.92 365.42 L632.25 365.08 L641.58 363.42 L648.75 361.08 L657.75 356.25 L660.42 354.25 L666.42 347.75 L668.25 344.75 L670.25 339.75 L671.25 335.58 L671.75 329.75 L671.25 321.42 L670.25 317.42 L667.42 311.42 L664.25 307.58 L660.08 303.75 L652.75 299.92 L646.75 297.92 L641.08 297.08 L642.58 295.92 L644.92 295.42 L649.92 293.08 L654.42 290.25 L659.25 284.92 L661.25 281.75 L662.92 277.58 L664.25 269.92 L664.25 264.42 L663.42 259.25 L661.08 252.92 L657.42 247.75 L653.08 243.75 L647.92 240.58 L640.58 237.75 L631.08 235.75 L618.25 234.75 Z M583.42 308.25 L584.08 307.58 L617.92 307.58 L627.42 308.42 L634.58 310.42 L638.25 312.58 L640.58 314.92 L643.42 319.25 L644.42 324.92 L644.42 327.42 L643.58 332.42 L642.58 335.08 L640.58 338.08 L636.75 341.58 L632.75 343.42 L628.25 344.58 L618.92 345.42 L584.08 345.42 L583.25 343.92 Z M583.42 255.58 L584.08 254.92 L614.58 254.92 L621.75 255.42 L627.92 256.92 L632.25 259.58 L635.58 264.08 L636.58 267.25 L636.75 269.75 L636.58 275.08 L635.58 278.25 L633.42 281.75 L631.42 283.58 L627.92 285.58 L624.92 286.58 L616.58 287.58 L583.92 287.58 L583.25 286.92 Z"/>
    <path id="letter-l" d="M688.75 227.75 L688.08 228.08 L687.92 364.92 L688.58 365.42 L713.58 365.42 L714.25 364.75 L714.08 228.25 L713.42 227.75 Z"/>
    <path id="letter-u" d="M734.08 265.25 L733.58 265.92 L733.58 330.75 L733.92 336.58 L735.75 345.92 L738.75 352.92 L741.58 356.92 L747.75 362.25 L751.25 364.25 L757.08 366.25 L764.92 367.25 L771.58 367.08 L777.08 366.25 L782.08 364.25 L785.42 362.42 L788.42 360.08 L793.25 355.08 L796.25 350.58 L798.42 346.08 L799.25 345.75 L799.58 346.25 L799.75 357.92 L800.58 365.25 L825.08 365.25 L824.42 346.58 L824.42 265.75 L823.92 265.25 L799.08 265.25 L798.58 265.75 L798.58 319.92 L797.42 329.42 L794.42 337.08 L792.58 339.92 L789.25 343.58 L786.75 345.42 L781.75 347.42 L776.25 347.92 L772.92 347.58 L769.92 346.58 L767.08 344.75 L763.58 340.75 L761.58 336.58 L760.58 333.08 L759.58 324.75 L759.42 265.75 L758.92 265.25 Z"/>
    <path id="letter-e" d="M877.92 263.75 L866.25 266.75 L859.08 270.58 L855.08 273.58 L852.42 276.25 L848.75 280.75 L845.92 285.25 L843.75 290.08 L841.75 296.42 L839.75 309.42 L839.75 320.42 L841.58 333.42 L844.58 342.58 L848.75 350.08 L851.58 353.75 L855.25 357.42 L862.42 362.25 L870.08 365.25 L880.42 367.25 L892.42 366.92 L902.08 365.42 L908.58 363.25 L913.92 360.42 L918.25 357.08 L923.42 351.58 L926.42 347.25 L929.25 341.75 L929.42 340.08 L905.75 338.08 L903.42 342.58 L901.75 344.75 L898.92 347.25 L896.42 348.58 L893.25 349.58 L889.75 349.92 L882.25 349.42 L879.42 348.42 L875.25 345.58 L872.58 342.75 L870.75 339.75 L868.42 333.92 L867.42 328.58 L867.08 320.92 L867.92 320.25 L931.08 320.25 L931.42 319.58 L931.25 311.75 L929.25 297.75 L927.08 290.25 L923.25 282.08 L918.58 275.92 L912.92 270.75 L905.75 266.58 L899.92 264.75 L890.25 263.42 Z M867.42 299.08 L868.58 293.42 L870.42 289.08 L872.25 286.25 L874.75 283.58 L877.75 281.58 L880.42 280.58 L887.75 279.75 L891.92 280.42 L894.75 281.42 L898.08 283.58 L900.42 285.75 L902.58 288.92 L904.58 293.58 L905.58 297.75 L906.08 303.25 L904.92 304.08 L868.08 304.08 L867.25 303.08 Z"/>
    <path id="letter-p" d="M1019.92 266.75 L1012.08 263.75 L1005.75 263.08 L998.25 263.25 L990.75 264.75 L985.25 266.92 L979.75 270.58 L975.75 274.75 L973.75 277.42 L972.42 280.42 L971.58 280.75 L971.08 279.25 L970.42 266.42 L969.75 265.42 L946.08 265.25 L944.92 265.75 L945.58 278.92 L945.58 404.42 L946.08 405.08 L970.92 405.08 L971.42 404.58 L971.42 350.08 L972.42 350.58 L974.75 354.75 L977.92 358.42 L981.25 361.25 L986.42 364.25 L991.92 366.25 L997.08 367.08 L1007.08 367.25 L1015.42 365.25 L1019.92 363.25 L1022.92 361.25 L1026.25 358.42 L1030.25 354.08 L1034.25 347.42 L1038.08 336.92 L1040.08 324.92 L1040.42 308.92 L1039.25 298.08 L1037.25 289.58 L1033.42 280.42 L1028.25 273.25 L1023.25 268.75 Z M991.25 281.08 L997.58 281.42 L1000.92 282.58 L1004.92 285.42 L1008.42 289.75 L1010.58 294.25 L1012.58 302.92 L1013.42 313.08 L1012.42 328.08 L1010.58 335.58 L1008.42 340.25 L1005.58 344.08 L1001.25 347.58 L997.08 349.08 L993.42 349.58 L987.92 349.08 L983.58 347.58 L978.58 343.25 L976.75 340.92 L974.58 336.58 L972.42 329.58 L971.42 323.42 L971.58 306.58 L972.42 301.08 L975.58 292.25 L978.58 287.42 L983.08 283.42 L987.75 281.42 Z"/>
    <path id="letter-r" d="M1113.08 264.42 L1110.58 263.58 L1108.25 263.42 L1101.08 263.58 L1094.75 265.58 L1091.92 267.58 L1087.75 272.42 L1084.75 278.08 L1082.58 284.25 L1081.58 285.25 L1081.08 284.75 L1080.08 266.25 L1079.42 265.42 L1056.08 265.25 L1055.08 265.92 L1055.75 279.42 L1055.92 365.25 L1081.25 365.42 L1081.75 365.08 L1081.75 315.42 L1082.42 306.25 L1084.42 297.92 L1086.58 293.75 L1088.58 291.08 L1091.25 288.58 L1094.42 286.58 L1097.58 285.42 L1101.08 285.08 L1108.08 285.25 L1112.58 286.25 L1113.42 285.92 L1113.58 265.25 Z"/>
    <path id="letter-i" d="M1125.08 265.25 L1123.92 266.25 L1123.92 364.92 L1124.58 365.42 L1149.58 365.42 L1150.25 364.75 L1150.08 265.92 L1148.92 265.25 Z"/>
    <path id="letter-i-dot" d="M1124.08 228.08 L1123.92 245.75 L1124.25 246.75 L1125.08 247.08 L1148.92 247.08 L1149.92 246.75 L1149.92 227.92 L1124.58 227.75 Z"/>
    <path id="letter-n" d="M1249.75 269.75 L1242.75 265.58 L1236.75 263.75 L1225.58 263.42 L1218.42 264.58 L1213.08 266.75 L1206.75 270.92 L1202.58 275.25 L1198.75 281.08 L1197.58 283.92 L1196.75 284.42 L1196.25 283.75 L1195.42 267.25 L1194.75 265.42 L1171.08 265.25 L1170.58 265.58 L1171.08 284.75 L1170.92 364.92 L1171.25 365.25 L1196.58 365.42 L1197.08 365.08 L1197.08 311.08 L1197.42 304.92 L1198.42 300.08 L1201.42 293.25 L1206.25 287.08 L1210.08 284.42 L1212.75 283.42 L1217.08 282.75 L1223.25 283.42 L1226.58 284.75 L1229.08 286.42 L1231.58 289.25 L1233.58 292.92 L1234.58 295.92 L1235.58 300.75 L1236.08 308.25 L1236.08 365.08 L1236.75 365.42 L1261.42 365.42 L1262.08 364.92 L1262.08 301.58 L1261.42 292.08 L1260.25 286.08 L1257.08 278.25 L1253.92 273.58 Z"/>
    <path id="letter-t" d="M1293.08 241.58 L1291.75 244.08 L1284.58 264.92 L1283.92 265.42 L1271.25 265.25 L1270.58 265.92 L1270.75 282.42 L1271.25 282.75 L1281.92 282.58 L1282.92 282.75 L1283.42 283.58 L1283.42 343.92 L1283.75 348.58 L1284.75 353.08 L1286.58 357.08 L1289.75 361.25 L1294.25 364.42 L1298.25 366.08 L1306.08 367.25 L1309.75 367.25 L1325.25 365.25 L1328.58 364.25 L1329.25 363.25 L1329.08 348.42 L1322.25 349.25 L1319.08 349.25 L1315.58 348.42 L1313.42 347.25 L1311.58 345.42 L1309.42 340.42 L1309.08 336.25 L1309.08 283.42 L1310.08 282.58 L1326.92 282.75 L1327.92 282.42 L1328.08 265.92 L1326.92 265.25 L1310.08 265.42 L1309.08 264.58 L1309.08 241.92 L1308.58 241.58 Z"/>
  </g>
</svg>
```

### A.2 App icon (save as `assets/logo/blueprint-app-icon.svg`)
```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 1000" width="1000" height="1000">
  <title>Blueprint app icon</title>
  <path id="tile" fill="#1F3DFF" d="M120.42 105.58 L105.58 120.25 L91.58 137.42 L79.75 155.25 L69.75 174.08 L61.92 193.25 L55.58 214.58 L53.58 223.25 L51.08 239.25 L49.58 258.42 L49.58 737.25 L50.58 754.42 L53.58 775.92 L56.58 788.58 L61.75 805.42 L68.75 822.75 L76.75 838.58 L86.75 854.75 L95.75 867.08 L108.92 882.25 L120.08 893.25 L137.25 907.25 L155.42 919.25 L176.58 930.25 L193.58 937.08 L210.92 942.42 L224.08 945.42 L235.58 947.25 L256.25 949.42 L737.58 949.42 L756.58 948.25 L774.92 945.42 L792.58 941.25 L815.75 933.25 L826.75 928.25 L843.58 919.25 L858.92 909.25 L871.58 899.58 L886.25 886.25 L900.42 870.58 L912.25 854.75 L924.25 834.92 L932.42 817.75 L940.42 795.75 L945.25 776.42 L948.42 754.42 L949.42 737.25 L949.42 258.92 L948.08 240.75 L945.25 222.58 L940.42 203.25 L936.25 190.92 L929.25 174.08 L920.42 157.25 L912.25 144.25 L900.42 128.42 L890.08 116.75 L871.92 99.75 L856.25 87.92 L839.92 77.58 L820.25 67.75 L807.92 62.75 L795.75 58.75 L775.92 53.75 L756.58 50.75 L737.58 49.58 L259.08 49.58 L241.92 50.75 L223.08 53.75 L210.08 56.75 L191.08 62.75 L174.25 69.75 L162.25 75.75 L146.08 85.58 L136.08 92.58 Z"/>
  <g id="mark">
    <g id="rays" fill="#F6E27A">
      <path id="ray-1" d="M129.75 398.25 L129.92 403.58 L132.75 409.42 L137.42 413.42 L143.25 414.92 L180.75 414.92 L184.92 414.25 L191.25 409.42 L193.42 405.92 L194.25 402.75 L194.08 397.42 L191.42 391.75 L187.08 387.75 L180.75 386.08 L139.92 386.58 L135.92 388.42 L132.58 391.75 Z"/>
      <path id="ray-2" d="M230.42 167.92 L225.75 173.25 L224.25 178.08 L224.92 184.75 L228.42 190.25 L254.08 216.08 L257.25 218.25 L260.42 219.42 L267.08 219.42 L273.75 215.58 L277.42 209.75 L278.08 205.58 L277.25 200.25 L274.58 195.92 L246.08 167.58 L241.42 165.75 L236.92 165.58 Z"/>
      <path id="ray-3" d="M498.08 75.58 L491.42 77.75 L488.08 81.25 L485.58 86.08 L485.25 126.92 L486.75 132.75 L490.58 137.25 L494.42 139.58 L500.25 140.42 L504.58 139.42 L508.92 136.92 L513.25 130.25 L513.75 88.25 L512.08 83.08 L507.58 77.92 L502.42 75.75 Z"/>
      <path id="ray-4" d="M769.92 169.25 L765.75 166.75 L761.42 165.58 L757.58 165.75 L752.92 167.58 L725.42 194.75 L722.58 198.25 L720.92 204.58 L721.75 210.25 L725.25 215.58 L731.92 219.42 L738.58 219.42 L741.92 218.08 L745.42 215.42 L770.42 190.42 L774.08 184.75 L774.75 178.25 L773.08 173.08 Z"/>
      <path id="ray-5" d="M804.75 398.25 L804.92 403.58 L807.75 409.42 L812.42 413.42 L818.25 414.92 L855.75 414.92 L859.92 414.25 L866.25 409.42 L868.42 405.92 L869.25 402.75 L869.08 397.42 L866.42 391.75 L862.08 387.75 L855.75 386.08 L814.92 386.58 L810.92 388.42 L807.58 391.75 Z"/>
    </g>
    <g id="bulb" fill="#F6E27A" fill-rule="evenodd">
      <path id="bulb-glass" d="M397.08 196.58 L373.25 208.92 L354.08 221.75 L343.08 230.42 L324.75 247.92 L309.58 266.08 L297.75 283.42 L286.75 303.75 L279.75 320.25 L273.58 339.25 L267.58 368.25 L265.58 389.92 L265.58 408.42 L266.58 423.92 L270.75 449.75 L276.58 471.08 L282.75 487.42 L289.75 502.25 L298.58 517.92 L314.08 540.42 L337.75 567.92 L368.42 598.08 L377.42 609.08 L383.42 618.42 L390.42 633.25 L394.58 648.58 L396.08 664.92 L396.25 688.25 L602.75 688.25 L603.58 652.58 L606.58 638.58 L613.58 621.92 L625.75 603.58 L634.42 593.92 L661.42 567.58 L671.25 556.92 L685.42 539.75 L700.42 517.92 L712.25 495.75 L717.25 484.58 L724.25 464.75 L729.25 444.75 L732.25 424.92 L733.42 407.92 L733.25 391.42 L731.25 368.58 L727.42 347.92 L722.25 329.08 L715.25 310.58 L705.25 290.42 L692.08 269.75 L680.25 254.75 L663.58 237.42 L645.92 222.58 L626.92 209.58 L606.58 198.75 L584.75 189.75 L560.58 182.58 L534.75 177.58 L509.92 175.58 L484.75 175.75 L459.25 178.58 L442.08 181.75 L420.42 187.58 Z M540.58 276.58 L550.58 279.58 L559.42 283.58 L569.25 289.75 L578.25 297.25 L585.42 304.92 L590.58 312.08 L595.58 321.42 L599.58 331.75 L602.42 344.92 L603.08 354.42 L602.42 366.42 L600.25 376.92 L596.42 387.75 L590.42 399.08 L578.58 414.08 L588.92 421.42 L600.42 432.92 L609.42 446.08 L614.58 456.58 L618.42 468.42 L620.58 480.25 L620.58 500.92 L618.58 511.75 L614.58 524.42 L611.42 531.42 L606.42 540.08 L601.25 547.08 L587.75 560.58 L581.25 565.42 L570.92 571.42 L554.92 577.58 L539.92 580.42 L463.92 580.58 L463.25 665.42 L460.58 671.58 L455.75 676.42 L449.08 679.42 L441.92 679.42 L436.75 677.42 L431.58 673.08 L428.58 668.25 L427.42 662.92 L427.75 288.92 L428.75 285.42 L431.58 280.92 L436.75 276.58 L441.92 274.58 L526.08 274.42 Z"/>
      <path id="bulb-inner-1" d="M463.92 310.58 L463.58 544.08 L533.92 544.42 L542.25 543.42 L552.58 540.25 L559.92 536.25 L568.58 529.25 L576.25 520.08 L580.25 513.08 L583.25 504.75 L584.92 491.92 L584.25 481.08 L581.25 470.25 L578.25 464.08 L573.25 456.75 L568.58 451.75 L561.08 445.58 L552.42 440.75 L542.25 437.58 L533.92 436.58 L520.08 436.58 L515.08 435.42 L509.58 431.58 L506.42 427.92 L504.42 423.25 L503.92 418.08 L505.75 410.42 L508.58 406.42 L511.92 403.42 L518.42 400.58 L526.92 400.25 L539.25 397.25 L549.25 391.25 L559.25 380.92 L564.08 371.75 L566.42 363.08 L566.42 348.08 L564.08 339.25 L559.25 330.25 L552.75 322.75 L546.25 317.58 L536.75 312.75 L524.25 310.58 Z"/>
    </g>
    <g id="base" fill="#FFFFFF">
      <path id="base-1" d="M380.75 727.08 L381.08 732.42 L383.58 737.92 L388.42 742.25 L395.25 744.25 L603.75 744.25 L608.25 743.25 L613.25 740.25 L617.25 734.58 L618.25 730.08 L617.25 723.25 L614.08 718.58 L608.92 714.75 L603.75 713.75 L395.25 713.75 L390.08 714.75 L385.75 717.75 L381.75 723.25 Z"/>
      <path id="base-2" d="M398.75 772.08 L399.08 777.42 L401.58 782.92 L406.42 787.25 L413.25 789.25 L585.75 789.25 L590.25 788.25 L595.25 785.25 L599.25 779.58 L600.25 775.08 L599.25 768.25 L596.08 763.58 L590.92 759.75 L585.75 758.75 L413.25 758.75 L408.08 759.75 L403.92 762.58 L399.75 768.25 Z"/>
      <path id="base-3" d="M430.42 816.75 L430.58 822.75 L432.75 827.42 L437.75 832.08 L444.75 834.25 L555.92 834.08 L561.25 832.08 L565.42 828.42 L568.08 823.75 L568.58 820.75 L568.08 814.25 L565.25 809.42 L559.58 804.92 L554.25 803.75 L443.08 803.92 L438.08 805.58 L434.75 808.25 L431.92 812.08 Z"/>
    </g>
  </g>
</svg>
```

### A.3 End-card logo animation (Remotion sketch)
```tsx
// Inline the lockup SVG as a React component so its parts can be driven per frame.
// Visible lockup in the source spans x 294..1329 and y 191..405 (center 811.5, 298).
// Scale so that span is 800 px wide, visible center at (540, 812) on the 1080x1920 frame.
const S = 800 / 1035;                       // 1035 = 1329 - 294
const DIM = "#4E61E2";                       // 22% Idea Yellow over Blueprint Blue
const hex = (h: string) => [1, 3, 5].map((i) => parseInt(h.slice(i, i + 2), 16));
const mix = (a: string, b: string, t: number) => {
  const A = hex(a), B = hex(b);
  return "#" + A.map((v, i) => Math.round(v + (B[i] - v) * t).toString(16).padStart(2, "0")).join("");
};
export const EndLogo: React.FC<{ f: number; on: number }> = ({ f, on }) => {
  const k = Math.min(1, Math.max(0, (f - on) / 2));                 // bulb: dim -> on over 2 frames
  const ray = (i: number) => Math.min(1, Math.max(0, (f - (on + 8 + 5 * i)) / 2));  // i = 0..4
  return (
    <svg viewBox="0 0 1600 600" style={{ position: "absolute", width: 1600 * S, height: 600 * S, left: 540 - 811.5 * S, top: 812 - 298 * S }}>
      {/* paste the lockup paths here (without the field rect; the end card draws #1F3DFF full-frame) */}
      {/* set fill of #bulb to mix(DIM, "#F6E27A", k); set opacity of #ray-(i+1) to ray(i) */}
    </svg>
  );
};
// When f >= on + 30 every override must be gone: the SVG renders exactly as in Appendix A.
```

---

## Appendix B · Ideas used on screen (all fictional)

| Film | Seller | Idea name | One-line pitch | Handle |
|---|---|---|---|---|
| 01 | Jordan | Larder Ring | A swap shelf for neighbors' spare pantry items | @lowlampnotes |
| 02 | Maya | Stillroom Hours | A quiet room you can book by the hour | @quietfern |
| 03 | Theo | Hallway Gym | A fold-down workout rack for studio apartments | @theoideas |
| 04 | Nia | Flatfold Cart | A laundry cart that folds flat for tiny apartments | @tidewren |

Buyer in every film: Rosa (signature "Rosa M." in Caveat on the NDA).

---

## Appendix C · SFX recipes (synthesized, 48 kHz)

Use licensed effects if the generator's sound library is available; otherwise synthesize these. Keep every one original.

- **CHING (full, about 0.9 s):** (1) register bell: two modal tones at 2637 Hz and 3136 Hz, each with partials at x2.76 (amp 0.4) and x5.40 (amp 0.18), decay tau 0.35 s, slight stereo spread (L 2637, R 3136 louder); (2) drawer: a low thunk at 120 Hz with a 30 ms pitch drop, plus a 40 ms band-passed noise burst (800 to 3000 Hz) at +30 ms; (3) coin shimmer: six tiny metallic ticks (modal 4.5 to 7.5 kHz, tau 25 ms) scattered over 0 to 250 ms, panned randomly; (4) a 40 ms bright transient at 0 ms. Short plate reverb, 0.8 s.
- **CHING (light, about 0.45 s):** the bell only, one tone (3136 Hz), tau 0.18 s, plus two shimmer ticks, -6 dB.
- **Notification pop:** sine with a 40 ms pitch glide up a fifth (start at the ladder note), soft 3 ms click on top, 60 ms decay.
- **Dopamine ladder:** pops on E5, F#5, G#5, A5, B5 (MIDI 76, 78, 80, 81, 83); the "Live" pop doubles an octave up.
- **Phone buzz:** 172 Hz square wave low-passed at 1.8 kHz, gated 150 ms on / 90 ms off, plus a little rattle noise.
- **Typing ticks:** 4 ms high-passed noise bursts plus a 1.6 to 1.9 kHz ping (8 ms), random 70 to 140 ms gaps.
- **Pen scratch:** pink noise band-passed 1.8 to 7.5 kHz, amplitude-modulated by stroke rhythm (8 to 13 Hz, randomized).
- **Stamp thud:** 130 Hz sine with a fast pitch drop and a 15 ms noise click.
- **Check ding:** glockenspiel-like modal tone (fundamental plus x2.76, x5.40), tau 0.4 s.
- **Call connect:** two soft vibraphone notes a fifth apart, 120 ms apart.
- **Switch click (end card):** press click (modal 2.9 and 4.3 kHz, tau 6 ms) plus a mechanical thunk (190, 430, 980 Hz, tau 20 to 30 ms), a quieter release click 70 ms later.
- **Warm rising tone (end card):** three sines on the tonic triad with 2nd and 3rd harmonics, gliding up 5 semitones into pitch over 0.3 s (exponential), sustain, fade by the last frame, low-passed at 2.4 kHz.
- **Glassy ray tick:** modal tone at 2637 Hz x 2^(2i/12) for ray i, partials x2.32 and x4.1, tau 90 ms.
- **Horror screech (film 04):** detuned saw cluster (8 voices within 40 cents) with fast tremolo, high-passed at 900 Hz, 0.6 s.
- **Comic organ sting (film 02):** three descending organ chords (additive sine drawbars), 0.25 s each.
- **Sax sting / brass stab (film 03):** use licensed if possible; otherwise a saw-plus-noise "brass" with a filter envelope opening fast, 0.4 s.

---

*End of brief. Start at section 0, build the free code kit first, then stop at the cost gate.*
