// SERVER ONLY. the real store, over PostgREST with the secret key.
import type { SupabaseClient } from "@supabase/supabase-js";
import { admin, ping as broadcast } from "./supabase-admin.ts";
import type { Claim, NewGame, Store } from "./store.ts";
import { usedBy } from "./pick.ts";
import type { Game } from "./game.ts";

export class SupabaseStore implements Store {
  readonly db: SupabaseClient;
  constructor(db: SupabaseClient = admin()) {
    this.db = db;
  }

  // the row a replay continues from, reduced to the cards it may not deal again
  private async inherited(parent?: string): Promise<{ parent: string; seen: string[] } | null> {
    if (!parent) return null;
    const { data } = await this.db.from("games").select("cards,seen").eq("id", parent).maybeSingle();
    return data ? { parent, seen: usedBy(data as Partial<Game>) } : null;
  }

  private async row(opts: NewGame): Promise<Record<string, unknown>> {
    const chain = await this.inherited(opts.parent);
    return { tier: opts.tier ?? "paid", ...(chain ?? {}) };
  }

  async create(opts: NewGame = {}): Promise<string> {
    const { data, error } = await this.db.from("games").insert(await this.row(opts)).select("id").single();
    if (error) throw error;
    return data.id as string;
  }

  async ensureForSession(sessionId: string, opts: NewGame = {}): Promise<void> {
    const { error } = await this.db
      .from("games")
      .upsert({ session_id: sessionId, ...(await this.row(opts)) }, { onConflict: "session_id" });
    if (error) throw error;
  }

  async findBySession(sessionId: string): Promise<string | null> {
    const { data, error } = await this.db.from("games").select("id").eq("session_id", sessionId).maybeSingle();
    if (error) throw error;
    return (data?.id as string) ?? null;
  }

  async claim(id: string, token: string): Promise<Claim> {
    const { data, error } = await this.db.rpc("claim_seat", { gid: id, token });
    if (error) throw error;
    const r = data as { seat?: Claim["seat"]; claimed?: boolean } | null;
    return { seat: r?.seat ?? "none", claimed: !!r?.claimed };
  }

  async load(id: string): Promise<Game | null> {
    const { data, error } = await this.db.from("games").select("*").eq("id", id).maybeSingle();
    if (error) throw error;
    return (data as Game | null) ?? null;
  }

  async save(id: string, version: number, patch: Partial<Game>): Promise<Game | null> {
    const { data, error } = await this.db
      .from("games")
      .update({ ...patch, version: version + 1 })
      .eq("id", id)
      .eq("version", version)
      .select()
      .maybeSingle();
    if (error) throw error;
    return (data as Game | null) ?? null;
  }

  async ping(id: string, version: number): Promise<void> {
    await broadcast(this.db, id, version);
  }
}
