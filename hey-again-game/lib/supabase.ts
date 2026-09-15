import { createClient, type SupabaseClient } from "@supabase/supabase-js";
export type { Game } from "./game";

// browser: anon key, used only to listen for "ping" broadcasts. it can't read or write the games table.
let _c: SupabaseClient | null = null;
export const client = (): SupabaseClient | null => {
  const url = process.env.NEXT_PUBLIC_SUPABASE_URL, key = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;
  if (!url || !key) return null;
  return (_c ??= createClient(url, key, { auth: { persistSession: false } }));
};

// server: service role, the only thing that touches the games table.
export const admin = () => createClient(process.env.NEXT_PUBLIC_SUPABASE_URL!, process.env.SUPABASE_SERVICE_ROLE_KEY!, { auth: { persistSession: false } });

export const channelFor = (id: string) => `game:${id}`;
