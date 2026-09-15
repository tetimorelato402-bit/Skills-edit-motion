// SERVER ONLY. picks the store for this deployment.
import type { Store } from "./store.ts";
import { SupabaseStore } from "./store-supabase.ts";
import { sharedMemoryStore } from "./store-memory.ts";
import { serverSupabase } from "./env.ts";

export const demoMemoryDb = () => process.env.DEMO_MEMORY_DB === "true";

// null means "not configured": the caller turns that into a plain message.
export function storeFor(): Store | null {
  // local play with no Supabase project. one process, wiped on restart.
  if (demoMemoryDb()) return sharedMemoryStore();
  if (!serverSupabase()) return null;
  return new SupabaseStore();
}
