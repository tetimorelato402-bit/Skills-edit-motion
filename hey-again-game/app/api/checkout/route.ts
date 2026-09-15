import Stripe from "stripe";
import { NextResponse } from "next/server";
import { missingStripe, SITE_URL } from "@/lib/env";

export const dynamic = "force-dynamic";

// NextResponse.redirect needs an absolute url, and SITE_URL may be unset
const home = (req: Request, error?: string) => new URL(error ? `/?error=${error}` : "/", SITE_URL || req.url);

export async function POST(req: Request) {
  const missing = missingStripe();
  if (missing.length) {
    console.error("checkout: missing", missing.join(", "));
    return NextResponse.redirect(home(req, "checkout"), 303);
  }
  try {
    const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!);
    const session = await stripe.checkout.sessions.create({
      mode: "payment",
      line_items: [{ price: process.env.STRIPE_PRICE_ID!, quantity: 1 }],
      success_url: `${SITE_URL}/start?session_id={CHECKOUT_SESSION_ID}`,
      cancel_url: SITE_URL,
    });
    return NextResponse.redirect(session.url!, 303);
  } catch (e) {
    console.error("checkout", e);
    return NextResponse.redirect(home(req, "checkout"), 303);
  }
}
