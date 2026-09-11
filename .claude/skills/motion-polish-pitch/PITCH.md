# Pitch Playbook

How the clip becomes money. Every message here is written to be sent by a person, one at a time, to someone whose product they just improved on video. Use the templates as-is and change only the bracketed parts; the tone is the product.

## The offer ladder

Three tiers, priced as starting points for a solo design engineer selling to funded startups and profitable small products. Raise them the moment two prospects in a row say yes without negotiating.

| Tier | What they get | Turnaround | Price |
| --- | --- | --- | --- |
| **Patch** | The `polish.css` from the clip as a PR to their repo, plus the written audit (every finding, the exact value it should be, why). | 48 hours | $400–$900 one-off |
| **Motion pass** | Patch, plus proper enter/exit animations on menus, dialogs, toasts and sheets, press feedback everywhere, mobile pass, reduced-motion done right. Built with `animate`, reviewed with `review-animations`. | 1–2 weeks | $1,500–$5,000 |
| **Retainer** | A motion pass on every new feature before it ships; you're the design engineer they don't have. | Monthly | $1,000–$3,000 / month |

Pitch the **Patch** in the DM. It's cheap enough to say yes to over chat, the work is already 80% done, and it is the natural door to the other two. Never pitch the retainer cold.

## The DM (under 60 words)

Platform doesn't matter — X, LinkedIn, Instagram, email — the structure is the same: the clip attached, then:

> Hi [first name] — I spent 20 minutes on [product]'s motion and recorded a before/after (attached, left is live, right is a 40-line CSS patch). The three biggest: [finding 1], [finding 2], [finding 3]. Happy to send the patch as a PR for [$price] if useful. Either way, hope the clip is interesting.

Rules:

- **First name, product name, three specifics.** If any of those is generic the message is spam and will be read as spam.
- The findings are plain words with one number each, e.g. "the Start-trial button eases *in* over 800ms so the hover lands late — 120ms ease-out fixes it", "cards animate `width` so they repaint on every hover", "no reduced-motion support, so the spinner runs for people who turned animations off".
- Price in the first message. It signals this is a product, not a fishing trip.
- "Either way, hope the clip is interesting" is the whole close. No "let me know your thoughts", no calendar link.

## Follow-up (one, after 3 days)

> Quick bump in case the clip got buried — no worries if not a fit. If it is, I can have the PR open by [day].

Then stop. Not replying is an answer.

## Objections

| They say | You say |
| --- | --- |
| "We have a designer." | "Great — the patch is a PR they can review in ten minutes. Most of it is timing and easing they'd agree with on sight." |
| "Can you do the whole site / app?" | Move to the Motion pass. Scope it from the same audit; quote a range, not a number, until you've seen the repo. |
| "It's just hover effects." | "It is, and they fire hundreds of times a day. The clip is what your users feel every session." Don't argue further. |
| "Send the CSS and I'll just apply it." | Yes, for the Patch price — the audit and the guarantee that it drops in cleanly are the product, not the secret. Don't send it free. |
| "Why is it so cheap?" | "Because the tooling does the mechanical part. You're paying for the judgment and the PR." |

## What to post publicly

The pipeline also produces content, which is where the cold DMs start finding *you*. Post before/after clips only of (a) your own demo sites, (b) clients who said yes, or (c) open-source projects where you've actually opened the PR. Never a prospect's site without consent.

Caption structure, every time:

1. One line naming the surface: "The pricing toggle on [product], before and after."
2. The three findings as three lines, same wording discipline as the DM.
3. The one rule that generalises: "Enter and hover → ease-out. Always."
4. No call to action. The clip is the call to action.

Post one a day. Consistency beats reach; the fiftieth clip is the one that gets shared.

## Never

- Never invent a metric. No "increases conversions", no "40% faster feel". You don't know, and the people who buy this can tell.
- Never post or reference a prospect's internal details (traffic, stack you inferred, team size).
- Never imply Emil Kowalski or animations.dev endorse the work. The standards are public; the service is yours.
- Never run the DM through a bulk tool. If the volume is too high to send by hand, you have enough clients.

## Tracking

Keep one sheet, one row per domain:

`domain · date · platform · person · findings (H/M/L) · clip sent? · replied? · tier sold · price · notes`

Review it weekly. The ratio that matters is *clips watched → replies*; if it's below one in ten, the clips are the problem (wrong surfaces, wrong prospects), not the message.
