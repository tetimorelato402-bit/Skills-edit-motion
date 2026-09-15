# hey again. the game

One link, two seats, 21 cards. Both players answer in secret; answers reveal together.

## Deploy in 20 minutes
1. **Supabase** (free): new project, open SQL editor, paste `supabase/schema.sql`, run. From Project Settings > API copy the project URL and both keys into `.env`. New projects show `sb_publishable_...` and `sb_secret_...`; older ones show anon and service_role. Either naming works, see `.env.example`.
2. **Stripe**: create a product "hey again. the game" at $2.99, copy the price id. Add a webhook to `https://YOURDOMAIN/api/webhook` for `checkout.session.completed`, copy its signing secret.
3. `cp .env.example .env`, fill it in. `npm install`, `npm run dev`.
4. Test with `DEV_FREE=true`: click "testing: start a free game", open the link on two phones.
5. **Vercel**: push to GitHub, import, paste the same env vars, set `DEV_FREE=false`. Point your domain at it.

## How it works
- `/` landing, pay button posts to `/api/checkout` (Stripe Checkout).
- Stripe webhook creates a `games` row keyed by the checkout session.
- `/start` shows the buyer their single link.
- `/play/[id]` talks only to `/api/game/[id]`, sending a per-browser token in the `x-hg-token` header. The server claims a seat (`claim_seat` in SQL): first token is p1, second is p2, anyone else is refused. It then mirrors the token into an httpOnly cookie, so clearing localStorage or site data on one side does not strand a player mid-game.
- The server is the referee. `lib/game.ts` holds the rules as pure functions: one mode, one answer per card per seat, nothing reveals until both answers exist, next card only after both, share only your own answer. `view()` strips the other seat's unrevealed answer and both tokens before anything reaches a phone.
- The browser never reads or writes the `games` table (row level security, no policies). After every change the server broadcasts a `ping` on the Supabase realtime channel `game:<id>` and each phone refetches its own view; a four-second poll covers a dropped socket.
- Writes are optimistic-locked on `version`, so two phones tapping at once can't skip a card.
- Game ends after 21 cards, link fades seven days later. Each player picks one answer for a shared tangerine card.
- Missing keys produce a plain message, never a stack trace: the game routes answer 503 and `/start` says the game isn't plugged in. The free-game routes are rate limited to 5 per hour per address and are off unless `DEV_FREE=true`.

## Checks
```bash
npm test        # rules in lib/game.ts, runs on plain node 22
npm run typecheck
npm run build
```

## Editing the cards
`lib/decks.ts`. Three modes, three rounds, seven cards each. Cards starting with `dare:` are typed dares.
