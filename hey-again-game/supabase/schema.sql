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
  version int not null default 0
);
alter table games add column if not exists version int not null default 0;

-- the browser never touches this table. every read and write goes through the
-- next.js server with the service role, which applies the rules in lib/game.ts
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
-- called by the server only.
create or replace function claim_seat(gid uuid, token text) returns text language plpgsql security definer as $$
declare g games;
begin
  select * into g from games where id = gid for update;
  if g is null then return 'none'; end if;
  if g.p1 = token then return 'p1'; end if;
  if g.p2 = token then return 'p2'; end if;
  if g.p1 is null then update games set p1 = token, version = version + 1 where id = gid; return 'p1'; end if;
  if g.p2 is null then update games set p2 = token, status = 'playing', version = version + 1 where id = gid; return 'p2'; end if;
  return 'full';
end $$;
revoke execute on function claim_seat(uuid, text) from public, anon, authenticated;
