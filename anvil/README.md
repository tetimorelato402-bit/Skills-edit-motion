# Anvil website

Static site, no build step. Open `index.html` or serve the folder (`python3 -m http.server`).

```
index.html            homepage
privacy / terms / plan / cancel .html
css/texture.css       grain, vignette, glow, motion: the one file to tune the feel
css/site.css          homepage layout and components
css/legal.css         shared styles for the legal pages
js/config.js          App Store, Stripe, support email, form endpoint
js/site.js            homepage behaviour
js/legal.js           fills config links on the legal pages
js/tune.js            live texture tuner (only with ?tune in the URL)
img/grain.png         the paper grain tile (was inlined as base64 before)
media/                the app film
```

## Before going live: fill in `js/config.js`

| Key | What happens if it's empty |
| --- | --- |
| `appStore` | "Get the app" buttons scroll to plans; the free plan says "Coming soon to the App Store". |
| `stripeMonthly`, `stripeYearly` | "Start free trial" goes to the App Store instead, or reads "Coming soon". Set the trial length on each Stripe Payment Link (7 / 21 days) so it matches the page. |
| `stripePortal` | Cancel and pause buttons on the legal pages are greyed out. |
| `supportEmail` | The "Something else?" question and footer Contact link are hidden. |
| `formEndpoint` | Creator submissions open an email to `supportEmail` instead. |

No visitor ever sees a "draft" or "not connected" note on the homepage any more.

## Textures and effects

Everything lives at the top of `css/texture.css`:

- `--grain-light`, `--grain-dark`: grain strength on paper and on the dark sections
- `--grain-size`: coarseness of the grain
- `--vignette`: darkened edges on the dark sections
- `--glow`: warm light behind the phone
- `--motion`: 1 normal, .5 calmer, 0 still (also forced to 0 for people with reduced motion on)
- `--rise`, `--reveal-time`: how far and how slowly things fade up as you scroll

To tune by eye, open any page with `?tune` (e.g. `index.html?tune`). Drag the sliders, press **Copy values**, and paste over the block in `texture.css`. Your slider values are remembered in that browser until you press Reset.

Effects on the page, all deliberately small: fade-up on scroll (once per element), button press, underlines that draw out on hover, price flip on the monthly/yearly switch, FAQ open, checkout sheet spring.

## Legal checklist (conversion + compliance)

Done in this pass:
- Auto-renewal terms are stated right next to the trial button and inside checkout, with an unticked consent box that must be ticked before payment.
- Checkout says a confirmation email with terms and how to cancel will follow. **Make sure that email is actually sent** (Stripe receipts plus your own message).
- Yearly plan: the reminder is now promised 15 to 45 days before each renewal (California's window). **Set this up in Stripe/your mailer.**
- Pause or cancel page: cancel is now first and just as prominent as pause. The old page labelled pause "Recommended" and made cancel the secondary button, which California's 2025 auto-renewal rules treat as a problem.
- Cancel instructions now say the same thing in every place (tap your photo, then Plan).

Needs a decision from you or your lawyer (we wrote the site assuming the answers below, so change it if they're different):
1. **Leaving a circle.** The old terms said leaving needs the circle to agree. The site and terms now say the circle can let you go at once, otherwise you're out after [7 days], and blocking takes effect immediately. Confirm the app really works this way.
2. **Teens.** Anvil collects always-on location from 13-year-olds and up, and the company is in Florida. Have counsel check Florida HB 3 and other state teen social-media and age-appropriate-design laws. Raising the minimum age to 16 or 18 at launch is the simplest option.
3. **Disputes** (courts or arbitration), the company name and address, and the other `[bracketed]` items on the legal pages.
4. Pausing isn't built into the Stripe customer portal. Either build pause yourself or point the pause button somewhere that handles it.

## Not added on purpose
No testimonials, user counts or ratings: there aren't real ones yet, and made-up ones are an FTC problem. When you have real quotes from real users (with their permission), they're the single best thing to add under "How a week works". A short note from the founder, with a name and face, would do the most to make the site feel less AI-made.
