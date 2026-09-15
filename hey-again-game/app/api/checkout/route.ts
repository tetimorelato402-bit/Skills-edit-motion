import Stripe from "stripe";
import { NextResponse } from "next/server";
export async function POST() {
  const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!);
  const site = process.env.NEXT_PUBLIC_SITE_URL!;
  const session = await stripe.checkout.sessions.create({
    mode: "payment",
    line_items: [{ price: process.env.STRIPE_PRICE_ID!, quantity: 1 }],
    success_url: `${site}/start?session_id={CHECKOUT_SESSION_ID}`,
    cancel_url: site,
  });
  return NextResponse.redirect(session.url!, 303);
}
