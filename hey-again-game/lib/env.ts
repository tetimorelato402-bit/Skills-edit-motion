// Supabase renamed its keys: anon -> publishable (sb_publishable_...), service
// role -> secret (sb_secret_...). Both namings work here; new projects only show
// the new ones. NEXT_PUBLIC_* are written as literals so Next can inline them.
export const SUPABASE_URL = process.env.NEXT_PUBLIC_SUPABASE_URL || "";
export const SUPABASE_PUBLISHABLE_KEY =
  process.env.NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY || process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || "";
export const SITE_URL = process.env.NEXT_PUBLIC_SITE_URL || "";

// true when the browser can open a realtime socket. the app still works without
// it: every phone polls its own view.
export const realtimeConfigured = () => !!(SUPABASE_URL && SUPABASE_PUBLISHABLE_KEY);

export type Missing = string[];

// server-only. never call from a client component.
export function serverSupabase(): { url: string; key: string } | null {
  const url = process.env.NEXT_PUBLIC_SUPABASE_URL || "";
  const key = process.env.SUPABASE_SECRET_KEY || process.env.SUPABASE_SERVICE_ROLE_KEY || "";
  return url && key ? { url, key } : null;
}

export function missingSupabase(): Missing {
  const out: Missing = [];
  if (!process.env.NEXT_PUBLIC_SUPABASE_URL) out.push("NEXT_PUBLIC_SUPABASE_URL");
  if (!(process.env.SUPABASE_SECRET_KEY || process.env.SUPABASE_SERVICE_ROLE_KEY)) out.push("SUPABASE_SECRET_KEY");
  return out;
}

export function missingStripe(): Missing {
  const out: Missing = [];
  if (!process.env.STRIPE_SECRET_KEY) out.push("STRIPE_SECRET_KEY");
  if (!process.env.STRIPE_PRICE_ID) out.push("STRIPE_PRICE_ID");
  if (!process.env.NEXT_PUBLIC_SITE_URL) out.push("NEXT_PUBLIC_SITE_URL");
  return out;
}

export const devFree = () => process.env.DEV_FREE === "true";

// a stripe payment link. when set, the pay button points straight at it and
// /api/checkout is not used, so no api key or price id is needed to sell.
// server only, so it applies on redeploy without a rebuild.
export const paymentLink = () => process.env.PAYMENT_LINK || "";

// buying again from a finished game. stripe passes client_reference_id through
// to the webhook, which is how the next game learns what this one already
// spent without anyone having an account.
export function againLink(gameId: string): string {
  const base = paymentLink();
  if (!base) return "";
  return base + (base.includes("?") ? "&" : "?") + "client_reference_id=" + encodeURIComponent(gameId);
}
