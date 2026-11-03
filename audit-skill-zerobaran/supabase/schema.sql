-- =====================================================================
-- Audit-Skill-ZeroBaran (Project #35) — Supabase schema (Postgres free tier)
-- (c) 2026 Baran Avisat · ZeroBaran Studio · Baranavisat@gmail.com
-- Run this once in the Supabase SQL editor. Tables are prefixed asz_.
-- =====================================================================

create table if not exists asz_scans (
  scan_id            text primary key,
  project_tag        text not null default 'default',
  target             text not null,
  ran_at             timestamptz not null default now(),
  files_scanned      int  not null default 0,
  findings_total     int  not null default 0,
  counts_by_severity jsonb not null default '{}'::jsonb,
  security_score     int  not null check (security_score between 0 and 100),
  verdict            text not null check (verdict in ('APPROVED','APPROVED_WITH_WARNINGS','REJECTED','BLOCKED')),
  engines            jsonb not null default '[]'::jsonb,
  ai_brains          jsonb not null default '[]'::jsonb,
  executive_summary_ar text,
  stored_at          timestamptz not null default now()
);

create table if not exists asz_findings (
  fingerprint      text primary key,           -- sha256(rule|file|line|snippet)[:16]
  scan_id          text references asz_scans(scan_id) on delete set null,
  rule_id          text not null,
  title            text not null,
  severity         text not null check (severity in ('CRITICAL','HIGH','MEDIUM','LOW','INFO')),
  category         text not null,
  file             text not null,
  line             int  not null,
  cwe              text,
  owasp            text,
  engine           text not null default 'native',
  explanation_ar   text,
  secure_fix_code  text,
  status           text not null default 'open' check (status in ('open','fixed','wontfix','false_positive')),
  first_seen       timestamptz not null default now(),
  last_seen        timestamptz not null default now(),
  fixed_at         timestamptz
);
create index if not exists asz_findings_status_sev_idx on asz_findings (status, severity);
create index if not exists asz_findings_rule_idx       on asz_findings (rule_id);
create index if not exists asz_scans_tag_time_idx      on asz_scans (project_tag, ran_at desc);

-- لوحة الاتجاه: متوسط درجة الأمان أسبوعياً لكل مشروع
create or replace view asz_weekly_posture as
select project_tag,
       date_trunc('week', ran_at) as week,
       count(*)                    as scans,
       round(avg(security_score))  as avg_score,
       sum((counts_by_severity->>'CRITICAL')::int) as criticals
from asz_scans group by 1,2 order by 1,2;

-- طابور الإصلاح: أخطر الثغرات المفتوحة مرتبة
create or replace view asz_fix_queue as
select f.*, s.project_tag
from asz_findings f left join asz_scans s on s.scan_id = f.scan_id
where f.status = 'open'
order by case f.severity when 'CRITICAL' then 0 when 'HIGH' then 1
                         when 'MEDIUM' then 2 else 3 end, f.first_seen;

-- أكثر القواعد تكراراً (توجّه جهود التدريب/التطوير)
create or replace view asz_top_rules as
select rule_id, title, severity, count(*) as occurrences,
       max(last_seen) as last_seen
from asz_findings where status='open'
group by 1,2,3 order by occurrences desc limit 25;

alter table asz_scans    enable row level security;
alter table asz_findings enable row level security;
-- الـ service-role key يتجاوز RLS؛ أضف سياسات anon-read للوحة العامة إن رغبت.
