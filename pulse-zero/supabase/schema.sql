-- ============================================================
-- Pulse-Zero :: Supabase Schema (طبقة الأرشيف — PostgreSQL مجاني)
-- الصق هذا الملف في: Supabase Dashboard → SQL Editor → Run
-- ============================================================

create table if not exists public.mentions (
  id            text primary key,              -- بصمة SHA1 لمنع التكرار نهائياً
  source        text not null,                 -- rss | google_news | html | demo
  source_name   text,
  title         text,
  body          text,
  url           text,
  author        text,
  published     timestamptz,
  lang_hint     text default 'auto',
  meta          jsonb default '{}'::jsonb,
  -- نتائج العقل الذكي:
  sentiment     text check (sentiment in ('positive','negative','neutral')) default 'neutral',
  score         real check (score between -1 and 1) default 0,
  category      text default 'other',          -- praise|complaint_delivery|complaint_technical|question|spam|other
  issue_root    text,
  severity      text check (severity in ('low','medium','high','crisis')) default 'low',
  reply_draft   text,                          -- الرد المقترح الجاهز من الـ AI
  engine        text default 'mock',
  analyzed_at   timestamptz not null default now()
);

create index if not exists idx_mentions_sentiment  on public.mentions (sentiment);
create index if not exists idx_mentions_severity   on public.mentions (severity);
create index if not exists idx_mentions_analyzed   on public.mentions (analyzed_at desc);
create index if not exists idx_mentions_category   on public.mentions (category);

-- ── مؤشر السمعة العام عبر الزمن (نظرة سريعة من SQL مباشرة) ──
create or replace view public.reputation_daily as
select
  date_trunc('day', analyzed_at)::date as day,
  count(*)                             as mentions,
  round(avg(score), 3)                 as avg_score,
  round((avg(score)+1)/2*100, 1)       as reputation_index,   -- 0..100
  count(*) filter (where sentiment='positive') as positive,
  count(*) filter (where sentiment='neutral')  as neutral,
  count(*) filter (where sentiment='negative') as negative,
  count(*) filter (where severity in ('high','crisis')) as alerts
from public.mentions
group by 1
order by 1 desc;

-- ── الصفوة: كل ما يحتاج تدخلاً بشرياً فوراً ──
create or replace view public.crisis_feed as
select analyzed_at, source_name, author, category, severity, score,
       left(body, 200) as complaint, reply_draft, url
from public.mentions
where sentiment = 'negative' and severity in ('high','crisis')
order by analyzed_at desc;

-- ============================================================
-- Row Level Security
-- الخيار أ (موصى به للـ Cron): استخدم service_role key في GitHub
--   Secrets — يتجاوز الـ policies بشكل آمن لأنه لا يخرج للعامة.
-- الخيار ب (لو استخدمت anon key): فعّل السياسة التالية للسماح بالكتابة من CI فقط.
-- ============================================================
alter table public.mentions enable row level security;

create policy "anon read for dashboard"
  on public.mentions for select using (true);

-- ⚠️ افتح الكتابة فقط إن كنت مضطراً لاستخدام anon key في Actions:
-- create policy "ci write"
--   on public.mentions for insert with check (true);
-- create policy "ci upsert"
--   on public.mentions for update using (true);
