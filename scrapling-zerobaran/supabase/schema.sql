-- =====================================================================
--  Scrapling-ZeroBaran — Supabase Schema (PostgreSQL Free Tier)
--  Project #38 | Author: Baran Avisat
--  الدعم: Baranavisat@gmail.com | واتساب: 00905313263722
--  الصق هذا الملف في SQL Editor بمشروع Supabase الخاص بك.
-- =====================================================================

create table if not exists scraped_records (
  id            text primary key,
  target        text not null,
  source_url    text,
  data          jsonb not null default '{}'::jsonb,   -- raw extracted fields
  values        jsonb not null default '{}'::jsonb,   -- tracked numerics (price/rating)
  category      text default 'general',               -- AI classification
  first_seen    bigint not null,
  last_seen     bigint not null
);

create table if not exists crawl_runs (
  run_id           text primary key,
  ts               bigint not null,
  targets          jsonb not null default '[]'::jsonb,
  pages_fetched    int  not null default 0,
  records_new      int  not null default 0,
  records_changed  int  not null default 0,
  blocks_detected  int  not null default 0,
  engines_used     jsonb not null default '{}'::jsonb,
  status           text not null default 'ok'
);

create index if not exists idx_records_target   on scraped_records (target);
create index if not exists idx_records_category on scraped_records (category);
create index if not exists idx_records_lastseen on scraped_records (last_seen desc);
create index if not exists idx_runs_ts          on crawl_runs (ts desc);

-- View: latest crawl health per target
create or replace view target_health as
select target,
       count(*)                                   as records_total,
       max(last_seen)                             as last_updated_ts,
       avg((data->>'ai_confidence')::numeric)     as avg_confidence
from scraped_records group by target;

-- View: most recent runs dashboard feed
create or replace view run_feed as
select run_id, to_timestamp(ts) as when_ran, status,
       pages_fetched, records_new, records_changed, blocks_detected,
       engines_used
from crawl_runs order by ts desc limit 200;

-- Row Level Security: service-role only (bot writes, human reads via dashboard)
alter table scraped_records enable row level security;
alter table crawl_runs     enable row level security;

comment on table scraped_records is 'Scrapling-ZeroBaran © Baran Avisat — extracted & AI-structured web records';
comment on table crawl_runs     is 'Scrapling-ZeroBaran © Baran Avisat — crawl session audit log';
