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
  ends_at timestamptz
);
alter table games enable row level security;
-- the game id is the secret. anyone holding it can read/update that row only.
create policy "read by id" on games for select using (true);
create policy "update by id" on games for update using (true) with check (true);
alter publication supabase_realtime add table games;
-- seat claiming: first token becomes p1, second p2, anyone else is refused
create or replace function claim_seat(gid uuid, token text) returns text language plpgsql security definer as $$
declare g games;
begin
  select * into g from games where id = gid for update;
  if g is null then return 'none'; end if;
  if g.p1 = token then return 'p1'; end if;
  if g.p2 = token then return 'p2'; end if;
  if g.p1 is null then update games set p1 = token where id = gid; return 'p1'; end if;
  if g.p2 is null then update games set p2 = token, status = 'playing' where id = gid; return 'p2'; end if;
  return 'full';
end $$;
