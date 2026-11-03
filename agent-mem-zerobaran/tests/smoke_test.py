#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Agent-Mem-ZeroBaran — contract tests (offline, deterministic). © Baran Avisat"""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
PASS = FAIL = 0


def ck(name, cond):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  ✅ {name}")
    else:
        FAIL += 1
        print(f"  ❌ {name}")


print("── LAYER 1: chunking ──")
from chunking import chunk_document, chunk_transcript, recursive_split, est_tokens
long_doc = ("## A\n" + "sentence one here. " * 60) + "\n## B\n" + "x" * 900
cs = chunk_document(long_doc, "d1", source="t")
ck("splits long doc into multiple chunks", len(cs) >= 2)
ck("chunk ids unique & prefixed", len({c.chunk_id for c in cs}) == len(cs))
ck("all start with doc id", all(c.chunk_id.startswith("d1:") for c in cs))
ck("token estimate positive", all(c.tokens_est > 0 for c in cs))
ck("dedupe identical repeats", len(chunk_document("ab cd ef. " * 50, "d2"))
   <= len(chunk_document("ab cd ef. " * 50, "d3", dedupe=False)))
msgs = [{"role": "user", "content": f"msg{i} عندي سؤال رقم {i}"} for i in range(10)]
tc = chunk_transcript(msgs, "sess", per_window=4, overlap=1)
ck("transcript windowing produces overlapping chunks", len(tc) >= 3)
ck("window keeps role tags", "[user]:" in tc[0].text)
ck("no recursion blowup on pathological text", len(recursive_split("a"*5000, 100, 20)) > 10)
ck("est_tokens works arabic", est_tokens("مرحبا بالعالم") > 1)

print("── LAYER 2a: embeddings ──")
from embeddings import EmbeddingEngine, cosine, hash_ngram_vector
eng = EmbeddingEngine()
vs = eng.embed(["الوكيل يخزن الذاكرة الدلالية في قاعدة متجهات",
                "الوكيل يخزن الذاكرة الدلالية في قاعدة المتجهات",
                "today is sunny and markets are closed"])
ck("dim matches config", len(vs[0]) == 512)
ck("vectors normalized", abs(sum(x*x for x in vs[0]) - 1.0) < 1e-6)
ck("similar AR texts score higher than unrelated",
   cosine(vs[0], vs[1]) > cosine(vs[0], vs[2]))
ck("deterministic (reproducible CI)", hash_ngram_vector("abc def") == hash_ngram_vector("abc def"))
ck("provider reported", eng.provider in ("hash-ngram-local", "gemini-embedding"))

print("── LAYER 2b: vector store ──")
from vector_store import LocalVectorStore, MemoryRecord
st_ = LocalVectorStore(path="/tmp/amtest.db")
if os.path.exists("/tmp/amtest.db"):
    os.remove("/tmp/amtest.db")
st_ = LocalVectorStore(path="/tmp/amtest.db")
recs = [MemoryRecord(f"d:{i}", "d", t, v, tokens_est=10, created_at=1e9 + i)
        for i, (t, v) in enumerate([("نظام الذكريات مجاني", vs[0]),
                                    ("طقس مشمس", vs[2])])]
st_.upsert_many(recs)
hits = st_.search(vs[0], top_k=2)
ck("exact-cosine retrieves correct top hit", hits[0]["chunk_id"] == "d:0")
ck("hybrid score includes recency", "recency" in hits[0] and hits[0]["score"] > 0)
st_.search(vs[0], top_k=1)
hits2 = st_.search(vs[0], top_k=1)
ck("access counter increments on recall", hits2[0]["accesses"] >= 1)
ck("stats counts memories", st_.stats()["memories"] == 2)
ck("delete_doc removes lineage", st_.delete_doc("d") == 2)
ck("decay bounded (0,1]", 0 < recs[0].decay() <= 1)

print("── LAYER 3: memory brain ──")
from memory_brain import MemoryBrainRouter, MockBrain
br = MemoryBrainRouter()
card = br.summarize("قررنا الميزانية $0. العميل يفضل تليجرام. تسلم التقرير الخميس.")
ck("card has summary key", isinstance(card.get("summary"), str) and card["summary"])
ck("card extracts numeric facts", "$0." in card["facts"] or any("$0" in f for f in card["facts"]))
ck("mock fallback always present", br.provider)
ans = br.answer("ما الميزانية؟", [{"chunk_id": "x:0", "text": "الميزانية صفر دولار $0 معتمدة رسمياً", "tokens": 8}])
ck("answer grounded w/ citations", ans["cited_chunk_ids"] == ["x:0"])
ck("confidence in [0,1]", 0 <= ans["confidence"] <= 1)
ck("context_block non-empty", len(ans["context_block"]) > 5)
empty = MockBrain().answer("q", [])
ck("graceful no-memory answer", empty["confidence"] == 0.0)

print("── LAYER 4: notify + gateway contract ──")
from notify import TelegramNotifier
n = TelegramNotifier()
ck("disabled gracefully without keys", not n.enabled)
ok = n.ingest_report("d1", 3, card, st_.stats(), "mock-local-brain")
ck("send returns False offline (no crash)", ok is False)
src = open(os.path.join(os.path.dirname(__file__), "..", "scripts", "gateway.py"), encoding="utf-8").read()
ck("gateway exposes /remember /recall /stats /health",
   all(p in src for p in ('"/remember"', '"/recall"', "/stats", "/health")))
ck("gateway auth token supported", "X-Auth-Token" in src)

print("── WIRING: orchestrator + cron + schema ──")
me_src = open(os.path.join(os.path.dirname(__file__), "..", "scripts", "mem_engine.py"), encoding="utf-8").read()
ck("engine wires all 4 layers", all(m in me_src for m in
   ["chunk_document", "EmbeddingEngine", "get_store", "MemoryBrainRouter", "TelegramNotifier"]))
ck("context budget enforced", "context_budget_tokens" in me_src)
wf = open(os.path.join(os.path.dirname(__file__), "..", ".github", "workflows",
                       "agent-mem-zerobaran.yml"), encoding="utf-8").read()
ck("cron hygiene scheduled", "*/6 * * *" in wf)
ck("weekly digest scheduled", "7 3 * * 1" in wf)
ck("secrets wired", all(s in wf for s in ["GROQ_API_KEY", "SUPABASE_URL", "TELEGRAM_BOT_TOKEN"]))
sql = open(os.path.join(os.path.dirname(__file__), "..", "supabase", "schema.sql"), encoding="utf-8").read()
ck("pgvector extension", "create extension if not exists vector" in sql)
ck("hnsw index for fast ANN", "using hnsw" in sql)
ck("hybrid search fn mirrors local scoring", "0.85*(1-(m.embedding <=> qvec))" in sql)
ck("RLS enabled", sql.count("enable row level security") == 2)
db = open(os.path.join(os.path.dirname(__file__), "..", "dashboard.py"), encoding="utf-8").read()
ck("dashboard streams recall", "eng.recall" in db)

print("── BRAND & RIGHTS ──")
for f in ["scripts/mem_engine.py", "README.md"]:
    p = os.path.join(os.path.dirname(__file__), "..", f)
    if os.path.exists(p):
        t = open(p, encoding="utf-8").read()
        ck(f"author info in {f}", "Baran Avisat" in t and "00905313263722" in t)

print(f"\n🏆 {'ALL LAYER CONTRACTS OK' if FAIL==0 else 'FAILURES PRESENT'} ({PASS}/{PASS+FAIL})")
sys.exit(1 if FAIL else 0)
