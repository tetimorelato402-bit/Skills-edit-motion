// SERVER ONLY. holds the secret key and is the only thing that touches the
// games table. importing this from a client component would be a bug.
import { createClient, type SupabaseClient } from "@supabase/supabase-js";
import { serverSupabase } from "./env";
import { channelFor } from "./supabase";

export class NotConfigured extends Error {
  constructor(public missing: string[]) { super(`missing ${missing.join(", ")}`); }
}

export function admin(): SupabaseClient {
  const env = serverSupabase();
  if (!env) throw new NotConfigured(["NEXT_PUBLIC_SUPABASE_URL", "SUPABASE_SECRET_KEY"]);
  return createClient(env.url, env.key, { auth: { persistSession: false } });
}

export function adminOrNull(): SupabaseClient | null {
  try { return admin(); } catch { return null; }
}

// wake the other phone. carries nothing private; clients refetch their own view.
export async function ping(db: SupabaseClient, id: string, version: number) {
  try { await db.channel(channelFor(id)).send({ type: "broadcast", event: "ping", payload: { version } }); }
  catch { /* realtime is a nicety; polling covers it */ }
}
