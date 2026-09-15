import { createClient, type SupabaseClient } from "@supabase/supabase-js";
let _c: SupabaseClient | null = null;
export const client = () => _c ??= createClient(process.env.NEXT_PUBLIC_SUPABASE_URL!, process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!);
export const admin = () => createClient(process.env.NEXT_PUBLIC_SUPABASE_URL!, process.env.SUPABASE_SERVICE_ROLE_KEY!);
export type Game = { id: string; mode: string | null; p1: string | null; p2: string | null; round: number; idx: number; answers: Record<string, Record<string, string>>; shared: Record<string, string>; status: "waiting" | "playing" | "done"; ends_at: string | null };
