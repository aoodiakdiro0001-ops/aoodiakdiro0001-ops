-- ============================================================
-- Voice-ZeroBaran — Project #36 | © 2026 Baran Avisat
-- Support: Baranavisat@gmail.com · WhatsApp 00905313263722
-- Supabase (free tier) schema + storage bucket. Run in SQL Editor.
-- ============================================================

create table if not exists public.vzb_jobs (
  id            text primary key,
  type          text not null check (type in ('tts','enhance','script','transcribe','video')),
  title         text,
  voice         text,
  speed         numeric default 1.0,
  preset        text,
  quality_grade text,
  duration_s    numeric,
  asset_url     text,
  asset_sha     text,
  brain         text,
  issues        jsonb default '[]'::jsonb,
  created_at    timestamptz not null default now()
);

create index if not exists vzb_jobs_type_idx   on public.vzb_jobs (type);
create index if not exists vzb_jobs_created_idx on public.vzb_jobs (created_at desc);

-- Row Level Security: service-role only (bot/backend), no public writes.
alter table public.vzb_jobs enable row level security;
drop policy if exists "service full" on public.vzb_jobs;
create policy "service full" on public.vzb_jobs
  for all using (auth.role() = 'service_role');

-- Storage bucket for generated media (public read so Telegram links work).
insert into storage.buckets (id, name, public)
values ('vzb-assets', 'vzb-assets', true)
on conflict (id) do nothing;

drop policy if exists "vzb public read" on storage.objects;
create policy "vzb public read" on storage.objects
  for select using (bucket_id = 'vzb-assets');

drop policy if exists "vzb service write" on storage.objects;
create policy "vzb service write" on storage.objects
  for insert with check (bucket_id = 'vzb-assets' and auth.role() = 'service_role');

-- Daily usage view (free-tier quota guard)
create or replace view public.vzb_daily_usage as
select date_trunc('day', created_at) as day, type, count(*) as jobs
from public.vzb_jobs group by 1, 2 order by 1 desc;
