import Stripe from "stripe";
import { NextResponse } from "next/server";
import { storeFor } from "@/lib/store-for";

export const dynamic = "force-dynamic";

export async function POST(req: Request) {
  const sig = req.headers.get("stripe-signature");
  if (!sig || !process.env.STRIPE_WEBHOOK_SECRET) {
    return NextResponse.json({ error: "not configured" }, { status: 400 });
  }
  // constructEvent verifies the signature locally: it uses the signing secret,
  // never the api key, so a payment link setup needs no secret key at all.
  const stripe = new Stripe(process.env.STRIPE_SECRET_KEY || "sk_unused");
  const body = await req.text();
  let event: Stripe.Event;
  try { event = stripe.webhooks.constructEvent(body, sig, process.env.STRIPE_WEBHOOK_SECRET); }
  catch { return NextResponse.json({ error: "bad signature" }, { status: 400 }); }

  if (event.type === "checkout.session.completed") {
    const s = event.data.object as Stripe.Checkout.Session;
    const store = storeFor();
    if (!store) return NextResponse.json({ error: "database not configured" }, { status: 500 });
    try {
      // stripe retries on a non-2xx, so a failed write is not lost
      // set when the buyer came from a finished game's "hey again" link, so the
      // new deck can skip everything that chain has already spent.
      const parent = typeof s.client_reference_id === "string" ? s.client_reference_id : undefined;
      await store.ensureForSession(s.id, { tier: "paid", parent });
    } catch (e) {
      console.error("webhook", e);
      return NextResponse.json({ error: "could not record the game" }, { status: 500 });
    }
  }
  return NextResponse.json({ ok: true });
}
