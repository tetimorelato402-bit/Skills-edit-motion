-- hey again. the game: database schema. safe to re-run on an existing project.
create extension if not exists pgcrypto;

create table if not exists games (
  id uuid primary key default gen_random_uuid(),
  session_id text unique,
  mode text,
  p1 text, p2 text,
  round int not null default 0,
  idx int not null default 0,
  answers jsonb not null default '{}'::jsonb,
  shared jsonb not null default '{}'::jsonb,
  status text not null default 'waiting',
  created_at timestamptz not null default now(),
  ends_at timestamptz,
  version int not null default 0,
  -- the deck this game was dealt, once the mode is picked. null on rows written
  -- before decks were shuffled: those keep playing the old fixed deck.
  cards jsonb,
  tier text not null default 'paid',
  -- every card this replay chain has already spent, so a new game skips them
  seen jsonb not null default '[]'::jsonb,
  parent uuid
);
alter table games add column if not exists version int not null default 0;
alter table games add column if not exists cards jsonb;
alter table games add column if not exists tier text not null default 'paid';
alter table games add column if not exists seen jsonb not null default '[]'::jsonb;
alter table games add column if not exists parent uuid;

-- the browser never touches this table. every read and write goes through the
-- next.js server with the secret key, which applies the rules in lib/game.ts
-- (seat ownership, answers reveal only when both exist, one answer per card).
alter table games enable row level security;
drop policy if exists "read by id" on games;
drop policy if exists "update by id" on games;
revoke all on games from anon, authenticated;

-- the table is not published over realtime; the server broadcasts a "ping" on
-- the channel game:<id> after every change and phones refetch their own view.
do $$ begin
  if exists (select 1 from pg_publication_tables where pubname = 'supabase_realtime' and tablename = 'games') then
    alter publication supabase_realtime drop table games;
  end if;
end $$;

-- seat claiming: first token becomes p1, second p2, anyone else is refused.
-- returns {"seat":"p1|p2|full|none","claimed":bool}; claimed is true only on the
-- call that took the seat, so the server knows when to wake the other phone.
-- called by the server only.
drop function if exists claim_seat(uuid, text);
create or replace function claim_seat(gid uuid, token text) returns jsonb language plpgsql security definer as $$
declare g games;
begin
  select * into g from games where id = gid for update;
  if g is null then return jsonb_build_object('seat', 'none', 'claimed', false); end if;
  if g.p1 = token then return jsonb_build_object('seat', 'p1', 'claimed', false); end if;
  if g.p2 = token then return jsonb_build_object('seat', 'p2', 'claimed', false); end if;
  if g.p1 is null then
    update games set p1 = token, version = version + 1 where id = gid;
    return jsonb_build_object('seat', 'p1', 'claimed', true);
  end if;
  if g.p2 is null then
    update games set p2 = token, status = 'playing', version = version + 1 where id = gid;
    return jsonb_build_object('seat', 'p2', 'claimed', true);
  end if;
  return jsonb_build_object('seat', 'full', 'claimed', false);
end $$;
revoke execute on function claim_seat(uuid, text) from public, anon, authenticated;

-- housekeeping: faded games keep nothing worth keeping. run from the dashboard
-- or a scheduled job if you want the rows gone.
-- delete from games where ends_at is not null and ends_at < now() - interval '30 days';
