# The Polish Layer

The "after" side of every pitch is one injectable stylesheet (plus, rarely, a few lines of JS). It is not a redesign. It corrects the motion the prospect already has so the page feels faster and more deliberate, and it must be droppable into their codebase as-is — that is the deliverable they buy.

Build it per site from this skeleton. Keep every value on the standards in `../review-animations/STANDARDS.md` and `../improve-animations/AUDIT.md`; never approximate a number that appears there.

## Skeleton (`polish.css`)

```css
/* ==== Motion polish layer — <site> — <date> ==== */
:root {
  --ease-out: cubic-bezier(0.23, 1, 0.32, 1);      /* enters, exits, hover */
  --ease-in-out: cubic-bezier(0.77, 0, 0.175, 1);  /* on-screen movement */
  --ease-drawer: cubic-bezier(0.32, 0.72, 0, 1);   /* sheets and drawers */
  --dur-hover: 120ms;   /* hover/color: 100–150ms */
  --dur-press: 80ms;    /* press feedback: ≤100ms */
  --dur-enter: 200ms;   /* enters/exits: 150–250ms */
  --dur-move: 300ms;    /* moving/morphing: 250–400ms */
}

/* 1. Hover: fast, eased, only compositor properties. Replaces `transition: all`. */
nav a, .btn, .card, button, [role="button"] {
  transition-property: background-color, color, border-color, box-shadow, transform, opacity;
  transition-duration: var(--dur-hover);
  transition-timing-function: var(--ease-out);
}

/* 2. Scale on hover: 1.02–1.04 max on large surfaces; none on text links. */
nav a:hover { transform: none; }
.btn:hover  { transform: translateY(-1px); }
.card:hover { transform: translateY(-2px); }

/* 3. Press feedback: instant, slight. */
.btn:active, button:active { transform: scale(0.98); transition-duration: var(--dur-press); }

/* 4. Shadows: layered, low-alpha, moving with the element. */
.card:hover { box-shadow: 0 1px 2px rgba(0,0,0,.04), 0 8px 24px -8px rgba(0,0,0,.12); }

/* 5. Enters that were ease-in or > 300ms: retime, keep the intent. */
.reveal { animation-duration: var(--dur-enter); animation-timing-function: var(--ease-out); }

/* 6. Everything long-running that is decoration, not feedback: stop it. */
.marquee, .float, .pulse-decor { animation: none; }

/* 7. Respect the OS. Always last, never optional. */
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}
```

Replace the selectors with the prospect's real ones from `inventory.json` (the `selector` field gives tag, id, and the first three classes). Prefer their class names over element selectors so the layer has the same specificity as their own rules; add `:where()` if you need to lose a specificity fight without `!important`.

## What the layer fixes, mapped to `findings.json` rules

| Rule in findings | Fix in the layer |
| --- | --- |
| `ease-in-on-ui`, `ease-in-in-css` | Swap to `--ease-out` (enter/hover) or `--ease-in-out` (movement). |
| `too-slow`, `hover-too-slow` | Hover to 100–150ms, enters to 150–250ms, movement ≤ 400ms. |
| `transition-all`, `transition-all-in-css` | Enumerate the properties that actually change. |
| `layout-property-animated` | Move the effect to `transform`/`opacity`; if it is a width/height reveal, use `grid-template-rows: 0fr → 1fr` or measure once and animate `transform`. |
| `hover-scale-too-big` | Cap scale at 1.02–1.04, or replace with `translateY(-1px…-2px)`. |
| `weak-builtin-curve` | Replace built-in `ease`/`ease-in-out` with the strong tokens above when the duration is ≥ 250ms. |
| `infinite-animation` | Keep only if it communicates state (a spinner while loading). Decorative loops go. |
| `no-reduced-motion` | Add block 7. Non-negotiable. |
| `no-pointer-cursor` | `cursor: pointer` on actionable elements. |
| `no-transitions-at-all` | Add block 1 only — 120ms `ease-out` hover on background/color. Do not invent motion the page didn't ask for. |

## What the layer must not do

- No new animations that weren't there in some form. The pitch is "your site, done right", not "your site with more stuff moving". If a page genuinely has no motion and hovers feel dead, block 1 is the entire layer.
- No scroll-triggered reveals, parallax, or hero entrance sequences. They lengthen the first meaningful interaction and are the thing this repo exists to prevent.
- No `!important` outside the reduced-motion block. If you need it, the selector is wrong.
- No touching layout, color, typography, or copy. Motion only. If the site's problems are not motion problems, this is not a prospect — see the qualification rules in `SKILL.md`.

## When you need JS (`polish.js`)

Only for two cases, both small:

1. **Exit animations that don't exist** (a menu that pops out of existence): add a `data-closing` attribute on close, remove the node after `animationend`. ~15 lines.
2. **Spring-driven drag surfaces** (a bottom sheet on mobile): out of scope for a pitch. Note it as an upsell in the DM; do not build it for the preview.
