# teti studio — colour system

Extracted from the oil portrait (`portrait-source.png`) by k-means over the image,
not picked by eye. The painting was already a complete, coherent system; the brand
just adopts it.

| Token | Hex | Where it comes from | Where it goes |
|---|---|---|---|
| `--ink` | `#2B100A` | the darkest shadow | grounds, backgrounds, body type on parchment |
| `--signal` | `#8C2A11` | the bow tie | the accent: MOTION, MOVE., `teti.`, one word per frame |
| `--field` | `#B07A3F` | the ochre ground | large flat fields — the specimen band |
| `--cream` | `#EFE3CC` | the highlights on the face | paper, type on dark, UI marks |

Full ramp, darkest to lightest — for gradients, duotones and posterisation:

`#331009` · `#5D1E0F` · `#783A1F` · `#935730` · `#A67545` · `#B48B56` · `#CEA471` · `#E4CBA0`

## Two rules that carry the system

**The warm palette is teti's world; cold grey is everyone else's.** The generic brand
post inside Study 001 is deliberately neutral grey and stays that way. The contrast
between the cold dead post and the warm living world is doing the argument's work —
never warm up the card.

**The band is ochre, not oxblood.** A full-frame field of saturated red is the single
most recognisable thing about the LILIUM reference. Ochre fields with oxblood accents
read as the same *grammar* in a different voice, which is the line between homage and
copy. Keep oxblood for type and small marks.

## Profile picture

Options rendered in `pfp/` at the sizes Instagram actually uses (110px profile, 32px
comments) — see `pfp/pfp-options.png`. Regenerate or restyle via `pfp/pfp.html`.

**Chosen: `portrait`** — the painting itself, full colour, circular. It is warm, it is
unmistakably teti's own, and it still reads as a face at 32px. Study 001's end card now
resolves into it: `teti.` cycles through ten typefaces, comes home to Inter, then collapses
and the portrait opens out of it. The wordmark and the mark are the same gesture.

(`duotone` was the earlier recommendation and `t-inverted` the most legible at every size;
both stay in `pfp/` in case a one-colour or small-format lockup is ever needed.)

`wordmark` and `poster` are documented but not recommended: "teti." turns to mush at
32px, and the hard posterisation breaks into unreadable patches.
