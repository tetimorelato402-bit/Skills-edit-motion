# hey again. the game

One link, two seats, 21 cards. Both players answer in secret; answers reveal together.

## Deploy in 20 minutes
1. **Supabase** (free): new project, open SQL editor, paste `supabase/schema.sql`, run. Copy the URL, anon key, service role key into `.env`.
2. **Stripe**: create a product "hey again. the game" at $2.99, copy the price id. Add a webhook to `https://YOURDOMAIN/api/webhook` for `checkout.session.completed`, copy its signing secret.
3. `cp .env.example .env`, fill it in. `npm install`, `npm run dev`.
4. Test with `DEV_FREE=true`: click "testing: start a free game", open the link on two phones.
5. **Vercel**: push to GitHub, import, paste the same env vars, set `DEV_FREE=false`. Point your domain at it.

## How it works
- `/` landing, pay button posts to `/api/checkout` (Stripe Checkout).
- Stripe webhook creates a `games` row keyed by the checkout session.
- `/start` shows the buyer their single link.
- `/play/[id]` claims a seat with a per-browser token (`claim_seat` in SQL). First token is p1, second is p2, anyone else is refused.
- Supabase realtime keeps both phones in sync. Answers only reveal when both exist.
- Game ends after 21 cards, link fades seven days later. Each player picks one answer for a shared tangerine card.

## Editing the cards
`lib/decks.ts`. Three modes, three rounds, seven cards each. Cards starting with `dare:` are typed dares.
