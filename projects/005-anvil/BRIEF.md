# Anvil — "Sit still. Keep up."

A brand film for **Anvil**. Not teti's studio work and not in teti's palette: this is a
client-facing piece for someone else's brand, so the warm family rule does not apply here.

## The idea

**The ad is a test, and the viewer either passes it or does not.**

A white studio. Text types itself out. The viewer has to keep reading while the film
actively tries to pull their eyes away — and the thing the text is *saying* is that being
able to do exactly that is the point. Form and argument are the same object, which is the
only reason this works as an ad rather than as a poster.

The copy, from teti:

> When you picked your friends you didn't get the choice between who you met first or who
> you met last. You chose who stayed. You chose who got to know the real you.
> Challenge yourself, let them see the real you. Don't sit still, don't let the
> distractions get to you. Pick a task, choose your friends. Download Anvil.

It opens on **SIT STILL. KEEP UP.** and it cuts to Anvil.

## The one rule that makes it work

**Distractions never obscure the text.** They arrive at the edges, they move, they flash,
they offer a second thing to read — but the sentence in the middle stays fully legible for
every frame it is on screen. Cover the words and the test stops being winnable, the viewer
disengages, and the argument collapses into an annoyance. The tension has to come from
*temptation*, not from obstruction.

The corollary: the strongest distraction is not a shape, it is **a second stream of text**.
Something else worth reading is far harder to ignore than something merely moving.

## Escalation

The film gets harder on purpose, then stops dead:

| bars | what distracts |
|---|---|
| 1 | nothing — the instruction, alone |
| 2–3 | one small drifting element, easy to dismiss |
| 4–5 | shapes entering from the edges, a two-frame colour flash |
| 6–7 | a notification card; the type speeds up |
| 8–10 | **a decoy text stream** in the corner, also typing |
| 11–12 | everything at once, the frame shaking |
| 13 | **total stop.** White, silent, still. The payoff line. |
| 14–16 | Pick a task. Choose your friends. Download Anvil. Cut. |

The stop at bar 13 is the whole film. Everything before it exists to make that silence
land, and if the escalation is not genuinely uncomfortable the silence is worth nothing.

## Load-bearing

- **Reading speed is the real constraint**, not taste. The type ramps from about 16 to 24
  characters per second — roughly 190 to 290 words per minute — so it is comfortably
  readable at the start and genuinely a push by the end. Check it at ~390 px wide, because
  that is a Reel, and a line that is easy on a laptop can be unreadable on a phone.
- **The film is on a 120 BPM grid**: a beat is 0.5 s, a bar 2 s, and it runs **16 bars =
  32 s**. Every distraction enters on a beat. Motion that lands off the grid reads as an
  accident rather than as pressure.
- **Fonts are self-hosted** (`source/fonts/`), for the reason 003 learned the hard way:
  this container has come back from restarts with an empty `/usr/local/share/fonts`, and a
  silent fallback to DejaVu would not be noticed until the film was assembled.

## Open — teti to confirm

1. **What Anvil actually is.** The middle of the film has to explain the idea and that
   explanation is not written yet; there is a marked slot for it in `video.html`. Everything
   around it is built and does not depend on the answer.
2. **Anvil's brand colours and logotype.** The film is currently black on white with one
   accent standing in. The end card is a placeholder.
3. **Black on white, or white on black?** teti asked for "full white" — read here as a white
   studio with black type, because white type on white cannot be read. Trivial to invert.
