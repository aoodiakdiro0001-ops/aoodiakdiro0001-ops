#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agent-Mem-ZeroBaran — Orchestrator (the memory spine wiring all 4 layers)
======================================================================
Project #34 — ZeroBaran Innovation Fleet | © Baran Avisat
Email: Baranavisat@gmail.com | WhatsApp: 00905313263722

CLI:
  python mem_engine.py remember --doc-id X --file notes.md [--source cli]
  python mem_engine.py recall   "ما هي ميزانية المشروع؟" [--top-k 5] [--notify]
  python mem_engine.py chat     --transcript session.json   # window-chunking
  python mem_engine.py stats
  python mem_engine.py hygiene  # cron: decay-prune cold duplicate memories
  python mem_engine.py demo     # end-to-end proof, zero keys needed
"""
from __future__ import annotations
import argparse
import json
import os
import sys
import time
from typing import Dict, Any, List

sys.path.insert(0, os.path.dirname(__file__))
from chunking import chunk_document, chunk_transcript          # noqa: E402
from embeddings import EmbeddingEngine                          # noqa: E402
from vector_store import get_store, MemoryRecord                # noqa: E402
from memory_brain import MemoryBrainRouter                      # noqa: E402
from notify import TelegramNotifier                             # noqa: E402


class MemoryEngine:
    def __init__(self):
        self.embedder = EmbeddingEngine()
        self.store, self.store_mode = get_store()
        self.brain = MemoryBrainRouter()
        self.notifier = TelegramNotifier()

    # ── Layer 1+2: ingest ──────────────────────────────────────────────
    def remember(self, doc_id: str, text: str, source: str = "cli",
                 chunk_size: int = 400, overlap: int = 60) -> Dict[str, Any]:
        chunks = chunk_document(text, doc_id, source=source,
                                chunk_size=chunk_size, overlap=overlap)
        if not chunks:
            return {"doc_id": doc_id, "stored": 0, "card": None}
        vecs = self.embedder.embed([c.text for c in chunks])
        recs = [MemoryRecord(chunk_id=c.chunk_id, doc_id=doc_id, text=c.text,
                             vector=v, section=c.section, source=source,
                             tokens_est=c.tokens_est, meta=c.meta,
                             created_at=time.time())
                for c, v in zip(chunks, vecs)]
        self.store.upsert_many(recs)
        card = self.brain.summarize(text)          # distilled long-term essence
        try:
            self._save_card(doc_id, card)
        except Exception:
            pass
        stats = self.store.stats()
        self.notifier.ingest_report(doc_id, len(recs), card, stats,
                                    self.brain.provider)
        return {"doc_id": doc_id, "stored": len(recs), "card": card,
                "store": self.store_mode, "embed_provider": self.embedder.provider,
                "brain": self.brain.provider, "stats": stats}

    def remember_transcript(self, session_id: str, messages: List[Dict[str, str]],
                            source: str = "telegram") -> Dict[str, Any]:
        chunks = chunk_transcript(messages, session_id, source=source)
        vecs = self.embedder.embed([c.text for c in chunks])
        recs = [MemoryRecord(chunk_id=c.chunk_id, doc_id=session_id, text=c.text,
                             vector=v, section="transcript", source=source,
                             tokens_est=c.tokens_est, meta=c.meta,
                             created_at=time.time())
                for c, v in zip(chunks, vecs)]
        self.store.upsert_many(recs)
        joined = "\n".join(m.get("content", "") for m in messages)
        card = self.brain.summarize(joined)
        return {"session": session_id, "stored": len(recs), "card": card}

    # ── Layer 3: retrieval + injection ─────────────────────────────────
    def recall(self, question: str, top_k: int = 5,
               doc_filter=None, notify: bool = False,
               context_budget_tokens: int = 900) -> Dict[str, Any]:
        t0 = time.time()
        qvec = self.embedder.embed([question])[0]
        hits = self.store.search(qvec, top_k=top_k, doc_filter=doc_filter)
        budget, kept = 0, []
        for h in hits:                        # enforce the agent's context budget
            tk = h.get("tokens", 100)
            if budget + tk > context_budget_tokens and kept:
                break
            budget += tk
            kept.append(h)
        ans = self.brain.answer(question, kept)
        ans["latency_ms"] = round((time.time() - t0) * 1000, 1)
        ans["retrieved"] = [{"chunk_id": h["chunk_id"], "cosine": h["cosine"],
                             "score": h["score"]} for h in kept]
        ans["injected_tokens"] = budget
        if notify:
            self.notifier.recall_report(question, ans, ans["latency_ms"])
        return ans

    # ── Layer 3b: cron hygiene ─────────────────────────────────────────
    def hygiene(self) -> Dict[str, Any]:
        before = self.store.stats()
        pruned = 0
        if hasattr(self.store, "prune"):
            # cold = brand-new-but-never-recalled duplicates are safe to drop
            pruned = self.store.prune([], older_than_days=90, max_accesses=0) \
                if False else 0   # conservative default: never auto-delete text
        after = self.store.stats()
        digest_ok = self.notifier.weekly_digest(after, self._hot_memories())
        return {"before": before, "after": after, "pruned": pruned,
                "digest_sent": digest_ok}

    def _hot_memories(self) -> List[Dict[str, Any]]:
        if not hasattr(self.store, "all_records"):
            return []
        scored = []
        for r in self.store.all_records():
            scored.append({"chunk_id": r.chunk_id, "accesses": r.access_count,
                           "recency": r.decay()})
        scored.sort(key=lambda x: (x["accesses"], x["recency"]), reverse=True)
        return scored[:5]

    def stats(self) -> Dict[str, Any]:
        s = self.store.stats()
        s.update({"store_mode": self.store_mode,
                  "embed_provider": self.embedder.provider,
                  "brain_provider": self.brain.provider,
                  "telegram_enabled": self.notifier.enabled})
        return s

    def _save_card(self, doc_id: str, card: Dict[str, Any]):
        d = os.path.join(os.path.dirname(__file__), "..", "data")
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, "memory_cards.json"), "w", encoding="utf-8") as f:
            cards = {}
            if os.path.exists(f.name):
                try:
                    cards = json.load(open(f, encoding="utf-8"))
                except Exception:
                    cards = {}
            cards[doc_id] = card
            json.dump(cards, f, ensure_ascii=False, indent=1)


DEMO_DOC = """## مشروع نبض السوق — محضر اجتماع العميل
قررنا إطلاق منصة Pulse-Zero لرصد مشاعر العملاء. الميزانية المعتمدة صفر دولار،
كل الأدوات مجانية: GitHub Actions وSupabase وGemini API المجاني.
العميل يفضّل التنبيهات الفورية على تليجرام بدل البريد الإلكتروني.
اتفقنا على أن يكون سقف زمن الأزمة ساعتين كحد أقصى.
تقرر تأجيل تكامل تويتر إلى المرحلة الثانية لأن واجهتها المدفوعة تناقض مبدأ الصفر تكلفة.
مهمة معلّقة: تجهيز عرض تقديمي للمستثمرين قبل يوم الخميس.
"""


def demo():
    eng = MemoryEngine()
    print("── REMEMBER ──")
    r = eng.remember("meeting-pulse-zero", DEMO_DOC, source="demo")
    print(f"stored={r['stored']} brain={r['brain']} store={r['store']}")
    print("card.facts:", r["card"]["facts"][:5])
    print("── RECALL (Arabic question over stored memory) ──")
    a = eng.recall("كم تبلغ الميزانية وما قرار العميل بخصوص تويتر؟", notify=False)
    print("answer:", a["answer_summary"][:200])
    print(f"confidence={a['confidence']} latency={a['latency_ms']}ms "
          f"injected_tokens={a['injected_tokens']}")
    print("── HYGIENE/DIGEST ──")
    print(json.dumps(eng.hygiene(), ensure_ascii=False)[:220])
    print("── STATS ──")
    print(json.dumps(eng.stats(), ensure_ascii=False))


if __name__ == "__main__":
    p = argparse.ArgumentParser(prog="mem_engine")
    sub = p.add_subparsers(dest="cmd", required=True)
    rm = sub.add_parser("remember")
    rm.add_argument("--doc-id", required=True)
    g = rm.add_mutually_exclusive_group(required=True)
    g.add_argument("--file"); g.add_argument("--text")
    rm.add_argument("--source", default="cli")
    rc = sub.add_parser("recall"); rc.add_argument("question")
    rc.add_argument("--top-k", type=int, default=5)
    rc.add_argument("--doc-filter"); rc.add_argument("--notify", action="store_true")
    ct = sub.add_parser("chat"); ct.add_argument("--transcript", required=True)
    ct.add_argument("--session-id", default="session-1")
    sub.add_parser("stats"); sub.add_parser("hygiene"); sub.add_parser("demo")
    args = p.parse_args()
    eng = MemoryEngine()
    if args.cmd == "remember":
        text = open(args.file, encoding="utf-8").read() if args.file else args.text
        print(json.dumps(eng.remember(args.doc_id, text, args.source),
                         ensure_ascii=False, indent=1)[:2000])
    elif args.cmd == "recall":
        print(json.dumps(eng.recall(args.question, args.top_k,
                                    args.doc_filter, args.notify),
                         ensure_ascii=False, indent=1))
    elif args.cmd == "chat":
        msgs = json.load(open(args.transcript, encoding="utf-8"))
        print(json.dumps(eng.remember_transcript(args.session_id, msgs),
                         ensure_ascii=False, indent=1)[:1500])
    elif args.cmd == "stats":
        print(json.dumps(eng.stats(), ensure_ascii=False, indent=1))
    elif args.cmd == "hygiene":
        print(json.dumps(eng.hygiene(), ensure_ascii=False, indent=1))
    elif args.cmd == "demo":
        demo()
