// client-safe. the browser only ever uses this to listen for "ping" broadcasts;
// the publishable key has no access to the games table (see supabase/schema.sql).
import { createClient, type SupabaseClient } from "@supabase/supabase-js";
import { SUPABASE_URL, SUPABASE_PUBLISHABLE_KEY, realtimeConfigured } from "./env";
export type { Game } from "./game";

let _c: SupabaseClient | null = null;
export const client = (): SupabaseClient | null => {
  if (!realtimeConfigured()) return null;
  return (_c ??= createClient(SUPABASE_URL, SUPABASE_PUBLISHABLE_KEY, { auth: { persistSession: false } }));
};

export const channelFor = (id: string) => `game:${id}`;
