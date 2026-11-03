-- =============================================================
-- Agent-Mem-ZeroBaran — Project #34 | © Baran Avisat
-- Email: Baranavisat@gmail.com | WhatsApp: 00905313263722
-- Supabase free-tier schema: PostgreSQL + pgvector semantic memory
-- Run in Supabase SQL editor. Dimension must match AGENTMEM_DIM (512).
-- =============================================================
create extension if not exists vector;

create table if not exists memories (
  chunk_id   text primary key,
  doc_id     text not null,
  section    text default '',
  source     text default '',
  content    text not null,
  embedding  vector(512) not null,
  tokens_est integer default 0,
  meta       jsonb default '{}'::jsonb,
  accesses   integer default 0,
  last_seen  timestamptz,
  created_at timestamptz default now()
);
create index if not exists memories_doc_idx on memories(doc_id);
create index if not exists memories_hnsw_idx on memories
  using hnsw (embedding vector_cosine_ops);

create table if not exists memory_cards (
  doc_id     text primary key,
  summary    text,
  facts      jsonb default '[]'::jsonb,
  preferences jsonb default '[]'::jsonb,
  decisions  jsonb default '[]'::jsonb,
  todos      jsonb default '[]'::jsonb,
  entities   jsonb default '[]'::jsonb,
  tags       jsonb default '[]'::jsonb,
  updated_at timestamptz default now()
);

-- Batch upsert used by scripts/vector_store.py (SupabaseVectorStore)
create or replace function upsert_memories_batch(records jsonb)
returns integer language plpgsql as $$
declare n integer := 0; r jsonb;
begin
  for r in select * from jsonb_array_elements(records)
  loop
    insert into memories(chunk_id,doc_id,section,source,content,embedding,tokens_est,meta)
    values (r->>'p_chunk_id', r->>'p_doc_id', r->>'p_section', r->>'p_source',
            r->>'p_text', (r->>'p_vector')::vector,
            coalesce((r->>'p_tokens')::int,0), coalesce(r->'p_meta','{}'::jsonb))
    on conflict (chunk_id) do update
      set content=excluded.content, embedding=excluded.embedding,
          tokens_est=excluded.tokens_est, meta=excluded.meta,
          updated_at = now();
    n := n + 1;
  end loop;
  return n;
end $$;

-- Hybrid retrieval: cosine relevance + recency boost (mirrors local store)
create or replace function search_memory(qvec vector(512), k int, doc_id_f text default null)
returns table (chunk_id text, doc_id text, content text, section text,
               source text, tokens int, distance float8, score float8)
language sql as $$
  select m.chunk_id, m.doc_id, m.content, m.section, m.source, m.tokens_est,
         1 - (m.embedding <=> qvec) as distance,
         0.85*(1-(m.embedding <=> qvec)) +
         0.15*(0.5 ^ (extract(epoch from (now()-coalesce(m.last_seen,m.created_at)))
                      / (30*86400.0))) as score
  from memories m
  where (doc_id_f is null or m.doc_id = doc_id_f)
  order by score desc limit k;
$$;

create or replace function memory_stats() returns jsonb language sql as $$
  select jsonb_build_object(
    'memories', count(*),
    'documents', count(distinct doc_id),
    'tokens_stored', coalesce(sum(tokens_est),0),
    'hot_memories', count(*) filter (where accesses>=3))
  from memories;
$$;

-- Touch access counters when the agent recalls a memory
create or replace function touch_memories(ids text[]) returns void language sql as $$
  update memories set accesses = accesses+1, last_seen = now()
  where chunk_id = any(ids);
$$;

create or replace view memory_health as
select doc_id, count(*) chunks, sum(tokens_est) tokens,
       max(accesses) peak_access, max(coalesce(last_seen,created_at)) freshest
from memories group by doc_id order by freshest desc;

alter table memories     enable row level security;
alter table memory_cards enable row level security;
-- service-role only (writes come from GitHub Actions with the service key)
create policy "service owns memories" on memories for all using (true) with check (true);
create policy "service owns cards"    on memory_cards for all using (true) with check (true);
