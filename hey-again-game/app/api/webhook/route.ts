import Stripe from "stripe";
import { NextResponse } from "next/server";
import { admin } from "@/lib/supabase";
export async function POST(req: Request) {
  const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!);
  const sig = req.headers.get("stripe-signature")!;
  const body = await req.text();
  let event: Stripe.Event;
  try { event = stripe.webhooks.constructEvent(body, sig, process.env.STRIPE_WEBHOOK_SECRET!); }
  catch { return NextResponse.json({ error: "bad signature" }, { status: 400 }); }
  if (event.type === "checkout.session.completed") {
    const s = event.data.object as Stripe.Checkout.Session;
    await admin().from("games").upsert({ session_id: s.id }, { onConflict: "session_id" });
  }
  return NextResponse.json({ ok: true });
}
