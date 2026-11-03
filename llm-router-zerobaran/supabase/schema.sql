-- ============================================================
-- LLM-Router-ZeroBaran — Project #37 | Supabase schema (Free tier)
-- © 2026 Baran Avisat <Baranavisat@gmail.com> · WhatsApp 00905313263722
-- ZeroBaran Studio — MIT License. Run once in Supabase SQL editor.
-- ============================================================

create table if not exists lrz_analysis_log (
  id text primary key,
  ts double precision not null,
  symbol text not null,
  timeframe text not null,
  price double precision,
  trend_score double precision,          -- -100..100 quant stack score
  confidence double precision,           -- 0..100
  signals jsonb,                         -- ["MACD_BULL_CROSS", ...]
  provider text,                         -- ollama|groq|gemini|mock
  model text,
  latency_ms double precision,
  cost_saved_usd double precision,       -- what free-tier routing saved vs paid API
  narrative text,
  plan jsonb,                            -- entry/stop/tp/qty
  created_at timestamptz default now()
);

create table if not exists lrz_signal_events (
  id text primary key,
  ts double precision not null,
  symbol text not null,
  side text not null,                    -- BUY / SELL-AVOID
  entry double precision,
  stop_loss double precision,
  take_profit_1 double precision,
  trend_score double precision,
  confidence double precision,
  outcome text default 'open',           -- open|tp1_hit|sl_hit
  pnl_pct double precision,
  created_at timestamptz default now()
);

create index if not exists lrz_an_sym_ts on lrz_analysis_log (symbol, ts desc);
create index if not exists lrz_sig_outcome on lrz_signal_events (outcome);

-- Weekly performance view: win-rate & avg pnl per symbol
create or replace view lrz_symbol_performance as
select symbol,
       count(*)                                        as signals_total,
       count(*) filter (where outcome in ('tp1_hit','sl_hit')) as closed,
       round(avg(case when outcome='tp1_hit' then 1.0
                      when outcome='sl_hit' then 0.0 end)::numeric, 3) as win_rate,
       round(avg(pnl_pct)::numeric, 3)                 as avg_pnl_pct
from lrz_signal_events
group by symbol order by signals_total desc;

-- Router economics view: savings per model
create or replace view lrz_router_economics as
select provider, model,
       count(*)                        as calls,
       round(avg(latency_ms)::numeric, 1) as avg_latency_ms,
       round(sum(cost_saved_usd)::numeric, 6) as total_saved_usd
from lrz_analysis_log
group by provider, model
order by total_saved_usd desc;

-- Row Level Security: service-role only writes; reads blocked for anon keys
alter table lrz_analysis_log enable row level security;
alter table lrz_signal_events enable row level security;
