import Stripe from "stripe";
import { NextResponse } from "next/server";
import { admin } from "@/lib/supabase-admin";

export const dynamic = "force-dynamic";

export async function POST(req: Request) {
  const sig = req.headers.get("stripe-signature");
  if (!sig || !process.env.STRIPE_SECRET_KEY || !process.env.STRIPE_WEBHOOK_SECRET) {
    return NextResponse.json({ error: "not configured" }, { status: 400 });
  }
  const stripe = new Stripe(process.env.STRIPE_SECRET_KEY);
  const body = await req.text();
  let event: Stripe.Event;
  try { event = stripe.webhooks.constructEvent(body, sig, process.env.STRIPE_WEBHOOK_SECRET); }
  catch { return NextResponse.json({ error: "bad signature" }, { status: 400 }); }

  if (event.type === "checkout.session.completed") {
    const s = event.data.object as Stripe.Checkout.Session;
    // stripe retries on a non-2xx, so a failed insert is not lost
    const { error } = await admin().from("games").upsert({ session_id: s.id }, { onConflict: "session_id" });
    if (error) {
      console.error("webhook upsert", error);
      return NextResponse.json({ error: "could not record the game" }, { status: 500 });
    }
  }
  return NextResponse.json({ ok: true });
}
