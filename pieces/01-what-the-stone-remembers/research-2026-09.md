# Reference research, September 2026 (piece 1)

Standing instruction 1: done fresh before generating. Redo this note if the piece is generated in a later month.

## 1. Macro / texture motion design

- [Texture, warmth and tactile rebellion: the big graphic design trends for 2026 (Creative Bloq)](https://www.creativebloq.com/design/graphic-design/texture-warmth-and-tactile-rebellion-the-big-graphic-design-trends-for-2026): the year's texture push is toward surfaces that look touchable, with visible grain and imperfection as a reaction to smooth AI output.
  - Borrow: keep real mineral pores and micro-fractures in the still; add a constant low film grain (the `grain.base` value) so the piece never reads as a clean render.
  - Do not copy: any specific paper or ink texture treatment; ours is stone, and the grain should read as mineral, not print.
- [11 Motion Design Trends for 2026 (Envato)](https://elements.envato.com/learn/motion-design-trends) and [Design Trends 2026: Imperfect, Intelligent and In Motion (Renderforest)](https://www.renderforest.com/blog/design-trends-in-2026): motion that feels crafted rather than computed, small irregularities on purpose.
  - Borrow: the barely visible breathing wobble on the push (`wobble_px`), so the camera feels held, not keyframed.
  - Do not copy: hand-drawn or painterly overlays; they fight the photographic stone.
- [16 Animation Trends to Watch in 2026 (GarageFarm)](https://garagefarm.net/blog/animation-trends-to-watch): hybrid 2D/3D layering and depth from parallax in otherwise flat imagery.
  - Borrow: a small parallax offset between the surface and the buried layer (`motion.parallax`) so the imprint sits physically deeper.

## 2. Symbolic short film

- [Storm, 2026 musical short film by Gener8ion, dir. Romain Gavras (Wikipedia)](https://en.wikipedia.org/wiki/Storm_(music_video)): a single sustained idea carried by the music's structure, with the visual escalation tied to the score rather than to cuts.
  - Borrow: one idea, one escalation, no cuts. Our piece is a single shot; the "edit" is the crack.
  - Do not copy: choreography, human bodies, or any of the film's imagery. This lane is faceless.

## 3. Sound-synced VFX reveals

- [Synced Up VFX: Beat Reactor (Toolfarm)](https://www.toolfarm.com/tutorial/tutorial_beat_reactor_vegas_pro/) and [How to synchronize video effects to music beat (VSDC)](https://www.videosoftdev.com/how-to-sync-video-to-music-beat): effects driven by amplitude envelopes land on transients; the reveal lives on the onset, not on the bar line.
  - Borrow: put the hard step of the reveal on the transient frame (`light.hit`), and let everything after it ease out. That is what `pipeline/cue.py` refines toward (the steepest rise, not the window centre).
  - Do not copy: continuous beat-reactive pulsing. One cue, one reveal; anything more turns the piece into a visualizer.
- [The Power of Rhythm: syncing audio and visuals (Movavi)](https://www.movavi.io/syncing-audio-and-visuals-to-create-engaging-videos/): anticipation before a hit makes the hit read as intended rather than accidental.
  - Borrow: the pre-cue tremor (`vfx.tremor`), a faint grain flicker growing over the last 0.6 s before the crack.

## 4. Dominant trend this month

- [Top Motion Graphics Trends for 2026 (Videobolt)](https://blog.videobolt.net/post/top-motion-graphics-trends-2026), [Motion Design Trends 2026 (Genesis)](https://genesismotiondesign.com/motion-design-trends-2026/), [Top 12 Motion Design Trends 2026 (MonkyVision)](https://monkyvision.com/blog/motion-design-trends/): tactile, handmade, story-first work is what stands out against the volume of polished AI clips; cinematic emotional arcs over flashy transitions.
  - Borrow: restraint. The whole-frame flash stays tiny (`flash.amount` 0.08) and the light on the imprint carries the reveal. No lens flares, no particle bursts.
  - Do not copy: the "imperfect linework" look; imperfection here comes from real rock and grain, not from drawn strokes.

## Three decisions applied to piece 1

1. Single unbroken shot, slow push slightly downward into the deep stratum, with a breathing wobble and a small parallax on the buried layer (`pieces/01-what-the-stone-remembers/preset.json`).
2. The reveal is a hard on-frame step at the transient, followed by ease-out curves only: light attack 0.3 s, crack draw 0.35 s, chromatic split fading over 0.4 s. Anticipation is a grain tremor, not a camera move.
3. Warm, low-saturation raking light on the imprint (RGB 1.0, 0.84, 0.58), constant mineral grain, no flash beyond 8 percent. Restraint is the trend signal this month, and it also matches the meaning (a memory surfacing, not an explosion).
