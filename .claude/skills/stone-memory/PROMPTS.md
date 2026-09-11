# Prompt scaffold for the base still

Fill the brackets from the piece brief. Keep the hidden detail in the prompt from the first generation; it must be composed in, not added later.

```
Extreme macro photograph of a polished cross-section of [material: banded agate / layered sandstone / marble],
horizontal sedimentary strata filling the whole frame, each band a slightly different era of colour and grain
([palette, e.g. warm ochre, umber, bone, iron-red]).
Buried in the [position: lower third / third band from the bottom] stratum is a faint fossil-like imprint of a
[motif: doorway / open hand / face in profile], rendered in almost exactly the same colour and value as the
surrounding rock, only readable by a subtle change in texture, nearly invisible at first glance.
Directional raking light from the [upper left], shallow depth, real mineral texture with crystalline pores and
micro-fractures, photographic, no glow, no highlights on the imprint yet.
Vertical 9:16 composition, no text, no people, no logos, no watermark.
```

Negative or avoid list (put in the prompt if the model form has no negative field): text, letters, watermark, people, hands holding the stone, glowing outlines, fantasy lighting, HDR look.

## Choosing the motif

Pick the one that reads as a memory trigger and also sits naturally in stone:

- Doorway: a threshold, something once passed through. Sits well as a rectangular void in a band.
- Hand: the most human trace, but risky for generators (extra fingers). If used, ask for a flat, pressed imprint, not a 3D hand.
- Face in profile: strongest emotional read, highest chance of drifting into "creepy". Keep it very faint.

## Mask prompt (image2image, optional)

```
Using the attached image, output a flat black image with a solid white silhouette exactly where the faint
[motif] imprint is, same dimensions, nothing else, no gradients, no text.
```

Threshold the result at 50% before saving as `mask.png`, then check it against the still by eye.

## What good looks like

- First viewing: a beautiful stone. The eye does not land on the imprint.
- Second viewing, after the reveal: the imprint is obviously there and always was.
- The imprint's position leaves room for the crack to enter from one frame edge.
