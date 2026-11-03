-- ============================================================
--  Design-Guard-ZeroBaran — مخطط قاعدة البيانات (Supabase / PostgreSQL)
--  المشروع #39: منظومة مراقبة جودة مخرجات الذكاء الاصطناعي
--  المؤلف: Baran Avisat | baranavisat@gmail.com | واتساب: 00905313263722
--  الصق هذا الملف في Supabase SQL Editor وانقر Run — مرة واحدة فقط.
-- ============================================================

create table if not exists qa_reports (
  id                uuid primary key default gen_random_uuid(),
  asset_id          text not null,
  checksum          text unique not null,              -- يمنع فحص نفس الأصل مرتين
  filename          text not null,
  kind              text not null check (kind in ('image','text','unknown')),
  width             integer default 0,
  height            integer default 0,
  file_size         bigint  default 0,
  format            text,
  structural_score  numeric(5,1) default 0,            -- نتيجة OpenCV/Pillow المجترة
  match_score       numeric(5,1) default 0,            -- النسبة النهائية المدمجة
  brand_consistency numeric(5,1) default 0,
  verdict           text not null check (verdict in ('accepted','rejected','needs_review')),
  defects           jsonb default '[]',                -- [{type,location,severity,note_ar}]
  inspector_findings jsonb default '[]',               -- نتائج الطبقة 1 الخام
  summary_ar        text,
  fix_suggestion_ar text,
  ai_provider       text,                              -- gemini-vision / groq-text / mock
  created_at        timestamptz default now()
);

create index if not exists idx_qa_verdict    on qa_reports (verdict);
create index if not exists idx_qa_created    on qa_reports (created_at desc);
create index if not exists idx_qa_kind       on qa_reports (kind);

-- ---------- عرض: إنتاجية كل يوم (قبول/رفض/متوسط المطابقة) ----------
create or replace view production_daily as
select
  date_trunc('day', created_at)::date                     as day,
  count(*)                                                as checked,
  count(*) filter (where verdict = 'accepted')            as accepted,
  count(*) filter (where verdict = 'rejected')            as rejected,
  count(*) filter (where verdict = 'needs_review')        as review,
  round(avg(match_score), 1)                              as avg_match,
  round(100.0 * count(*) filter (where verdict='accepted') / nullif(count(*),0), 1) as accept_rate
from qa_reports
group by 1 order by 1;

-- ---------- عرض: أكثر العيوب تكراراً (خريطة إعادة التوليد) ----------
create or replace view defect_leaderboard as
select d->>'type'     as defect_type,
       d->>'severity' as severity,
       count(*)       as occurrences
from qa_reports, jsonb_array_elements(defects) as d
group by 1, 2
order by occurrences desc;

-- ---------- عرض: طابور المراجعة البشرية ----------
create or replace view human_review_queue as
select filename, kind, match_score, summary_ar, fix_suggestion_ar, created_at
from qa_reports
where verdict = 'needs_review'
order by created_at desc;

-- Row Level Security: الجدول خلف service-role فقط (مفتاح الخادم).
alter table qa_reports enable row level security;
