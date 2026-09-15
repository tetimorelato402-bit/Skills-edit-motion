// Checks a real Supabase project against what the app expects.
//
//   node scripts/check-db.mjs          (or: npm run check-db)
//
// Reads .env, proves the table and claim_seat behave, and proves the
// publishable key cannot read the games table. Creates one throwaway game and
// deletes it again. Safe to run against production.
import { readFileSync } from "node:fs";
import { createClient } from "@supabase/supabase-js";

const env = (() => {
  const out = { ...process.env };
  try {
    for (const line of readFileSync(new URL("../.env", import.meta.url), "utf8").split("\n")) {
      const t = line.trim();
      if (!t || t.startsWith("#")) continue;
      const i = t.indexOf("=");
      if (i < 0) continue;
      out[t.slice(0, i).trim()] ??= t.slice(i + 1).trim().replace(/^["']|["']$/g, "");
    }
  } catch { /* no .env: fall back to the real environment */ }
  return out;
})();

const URL_ = env.NEXT_PUBLIC_SUPABASE_URL || env.SUPABASE_URL;
const SECRET = env.SUPABASE_SECRET_KEY || env.SUPABASE_SERVICE_ROLE_KEY;
const PUBLISHABLE = env.NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY || env.NEXT_PUBLIC_SUPABASE_ANON_KEY || env.SUPABASE_PUBLISHABLE_KEY;

if (!URL_ || !SECRET) {
  console.error("Set NEXT_PUBLIC_SUPABASE_URL and SUPABASE_SECRET_KEY in .env first.");
  process.exit(2);
}

const fails = [];
const warns = [];
// tell "your schema is wrong" apart from "I never reached Supabase"
let unreachable = false;
const looksLikeNetwork = (m = "") => /fetch failed|ENOTFOUND|EAI_AGAIN|ECONNREFUSED|ETIMEDOUT|allowlist|proxy|certificate|socket hang up/i.test(m);
const check = (name, ok, detail = "") => {
  console.log((ok ? "  ok   " : "  FAIL ") + name + (ok || !detail ? "" : `  <- ${detail}`));
  if (!ok) fails.push(name);
};
const warn = (name, detail) => { console.log("  warn " + name + `  <- ${detail}`); warns.push(name); };

const db = createClient(URL_, SECRET, { auth: { persistSession: false } });
const seat = async (id, token) => (await db.rpc("claim_seat", { gid: id, token })).data;

let id = null;
try {
  console.log(`\nchecking ${URL_}\n`);

  const cols = "id,session_id,mode,p1,p2,round,idx,answers,shared,status,created_at,ends_at,version";
  const { error: tableErr } = await db.from("games").select(cols).limit(1);
  if (tableErr && looksLikeNetwork(tableErr.message)) {
    unreachable = true;
    throw new Error(tableErr.message);
  }
  check("games table exists with every column the app uses", !tableErr, tableErr?.message);
  if (tableErr) throw new Error("stop: the schema did not run");

  const { data: made, error: insErr } = await db.from("games").insert({}).select("*").single();
  check("the server can create a game", !insErr && !!made, insErr?.message);
  if (insErr) throw new Error("stop: cannot insert");
  id = made.id;
  check("a new game starts at version 0, waiting, no seats",
    made.version === 0 && made.status === "waiting" && made.p1 === null && made.p2 === null,
    `version=${made.version} status=${made.status}`);

  const A = "aaaaaaaaaaaaaaaaaaaa", B = "bbbbbbbbbbbbbbbbbbbb", C = "cccccccccccccccccccc";
  const first = await seat(id, A);
  check("claim_seat returns {seat, claimed}",
    !!first && typeof first === "object" && "seat" in first && "claimed" in first,
    `got ${JSON.stringify(first)} (an old schema returns a bare string: re-run schema.sql)`);
  check("the first token takes seat p1", first?.seat === "p1" && first?.claimed === true, JSON.stringify(first));

  const again = await seat(id, A);
  check("the same token keeps its seat without re-claiming",
    again?.seat === "p1" && again?.claimed === false, JSON.stringify(again));

  const second = await seat(id, B);
  check("the second token takes seat p2", second?.seat === "p2" && second?.claimed === true, JSON.stringify(second));

  const third = await seat(id, C);
  check("a third token is refused", third?.seat === "full" && third?.claimed === false, JSON.stringify(third));

  const missing = await seat("00000000-0000-0000-0000-000000000000", A);
  check("an unknown game is not found", missing?.seat === "none", JSON.stringify(missing));

  const { data: after } = await db.from("games").select("*").eq("id", id).single();
  check("taking both seats starts the game", after.status === "playing", after.status);
  check("each claim bumps the version", after.version === 2, `version=${after.version}`);

  const { data: won } = await db.from("games").update({ mode: "couples", version: after.version + 1 })
    .eq("id", id).eq("version", after.version).select().maybeSingle();
  check("an update with the current version wins", !!won && won.mode === "couples");

  const { data: lost } = await db.from("games").update({ mode: "exes", version: after.version + 1 })
    .eq("id", id).eq("version", after.version).select().maybeSingle();
  check("an update with a stale version writes nothing", lost === null, JSON.stringify(lost));

  // the point of the whole design: the key shipped to browsers must be useless here
  if (!PUBLISHABLE) {
    warn("publishable key not checked", "set NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY to check it");
  } else {
    const pub = createClient(URL_, PUBLISHABLE, { auth: { persistSession: false } });
    const { data: leak, error: leakErr } = await pub.from("games").select("*").limit(1);
    check("the browser key cannot read the games table",
      !!leakErr || (Array.isArray(leak) && leak.length === 0),
      `read back ${JSON.stringify(leak)}`);
    if (!leakErr && Array.isArray(leak) && leak.length === 0) {
      warn("the browser key got an empty list rather than a refusal",
        "no data leaked, but check no SELECT policy was added to games");
    }
    const { error: rpcErr } = await pub.rpc("claim_seat", { gid: id, token: "zzzzzzzzzzzzzzzzzzzz" });
    check("the browser key cannot call claim_seat", !!rpcErr, "it was allowed to run");
  }
} catch (e) {
  if (unreachable || looksLikeNetwork(e.message)) {
    unreachable = true;
    console.error(`\nCould not reach Supabase: ${e.message}`);
    console.error("Nothing was checked. Confirm NEXT_PUBLIC_SUPABASE_URL and that this machine can reach it.");
  } else {
    check("ran to completion", false, e.message);
  }
} finally {
  if (id && !unreachable) {
    const { error } = await db.from("games").delete().eq("id", id);
    console.log(error ? `\n  note: could not delete test game ${id}: ${error.message}` : "\n  cleaned up the test game");
  }
}

console.log();
if (unreachable) process.exit(2);
if (fails.length) {
  console.log("FAILED: " + fails.join(", "));
  console.log("Re-run supabase/schema.sql in the SQL editor, then try again.");
  process.exit(1);
}
console.log(warns.length ? `passed, with ${warns.length} thing to look at` : "all checks passed. the database is ready.");
