#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agent-Mem-ZeroBaran — Layer 2b: Vector Store (Supabase pgvector + local SQLite)
============================================================================
Project #34 — ZeroBaran Innovation Fleet | © Baran Avisat
Email: Baranavisat@gmail.com | WhatsApp: 00905313263722

Production path : Supabase (PostgreSQL + pgvector) via PostgREST RPC.
Offline/CI path : local SQLite vector store with exact cosine search
                  (vectors stored as compact JSON, brute-force is fine
                  for free-tier scale of ~100k memories).
Every memory row carries: text, embedding, doc lineage, section, tokens,
access_count, last_accessed and a decay score so "cleaning" jobs can prune.
"""
from __future__ import annotations
import json
import os
import sqlite3
import time
import urllib.request
from dataclasses import dataclass
from typing import List, Dict, Any, Optional

DATA_DIR = os.environ.get("AGENTMEM_DATA", os.path.join(os.path.dirname(__file__), "..", "data"))
DB_PATH = os.path.join(DATA_DIR, "memories.db")


@dataclass
class MemoryRecord:
    chunk_id: str
    doc_id: str
    text: str
    vector: List[float]
    section: str = ""
    source: str = ""
    tokens_est: int = 0
    meta: Optional[Dict[str, Any]] = None
    created_at: float = 0.0
    access_count: int = 0
    last_accessed: float = 0.0

    def decay(self, half_life_days: float = 30.0) -> float:
        """Recency weight in (0,1]; untouched old memories fade but never die."""
        ref = self.last_accessed or self.created_at
        if not ref:
            return 1.0
        age_days = max(0.0, (time.time() - ref) / 86400.0)
        return 0.5 ** (age_days / half_life_days)


class LocalVectorStore:
    """SQLite-backed exact-cosine vector store (zero external services)."""

    def __init__(self, path: str = DB_PATH):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        self.conn = sqlite3.connect(path)
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS memories(
              chunk_id TEXT PRIMARY KEY,
              doc_id TEXT, section TEXT, source TEXT,
              text TEXT, vec TEXT, tokens INTEGER, meta TEXT,
              created REAL, accesses INTEGER DEFAULT 0, last_seen REAL DEFAULT 0)
        """)
        self.conn.commit()

    def upsert_many(self, recs: List[MemoryRecord]) -> int:
        n = 0
        for r in recs:
            cur = self.conn.execute("""
                INSERT INTO memories(chunk_id,doc_id,section,source,text,vec,tokens,meta,created,accesses,last_seen)
                VALUES(?,?,?,?,?,?,?,?,?,?,?)
                ON CONFLICT(chunk_id) DO UPDATE SET
                  text=excluded.text, vec=excluded.vec, tokens=excluded.tokens,
                  meta=excluded.meta""",
                (r.chunk_id, r.doc_id, r.section, r.source, r.text,
                 json.dumps(r.vector), r.tokens_est, json.dumps(r.meta or {}),
                 r.created_at or time.time(), r.access_count, r.last_accessed))
            n += cur.rowcount
        self.conn.commit()
        return len(recs)

    def search(self, qvec: List[float], top_k: int = 5,
               doc_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        rows = self.conn.execute(
            "SELECT chunk_id,doc_id,section,source,text,vec,tokens,meta,"
            "created,accesses,last_seen FROM memories"
            + (" WHERE doc_id=?" if doc_filter else ""),
            ((doc_filter,) if doc_filter else ())).fetchall()
        scored = []
        for row in rows:
            vec = json.loads(row[5])
            cos = sum(a * b for a, b in zip(qvec, vec))
            rec = MemoryRecord(chunk_id=row[0], doc_id=row[1], text=row[4],
                               vector=vec, section=row[2], source=row[3],
                               tokens_est=row[6], meta=json.loads(row[7]),
                               created_at=row[8], access_count=row[9],
                               last_accessed=row[10])
            final = 0.85 * cos + 0.15 * rec.decay()   # hybrid relevance/recency
            scored.append({"chunk_id": row[0], "doc_id": row[1], "text": row[4],
                           "section": row[2], "source": row[3], "tokens": row[6],
                           "cosine": round(cos, 4), "score": round(final, 4),
                           "accesses": row[9], "recency": round(rec.decay(), 3)})
        scored.sort(key=lambda x: x["score"], reverse=True)
        hits = scored[:top_k]
        now = time.time()
        for h in hits:
            self.conn.execute(
                "UPDATE memories SET accesses=accesses+1, last_seen=? WHERE chunk_id=?",
                (now, h["chunk_id"]))
        self.conn.commit()
        return hits

    def stats(self) -> Dict[str, Any]:
        total, toks = self.conn.execute(
            "SELECT COUNT(*), COALESCE(SUM(tokens),0) FROM memories").fetchone()
        docs = self.conn.execute("SELECT COUNT(DISTINCT doc_id) FROM memories").fetchone()[0]
        hot = self.conn.execute(
            "SELECT COUNT(*) FROM memories WHERE accesses>=3").fetchone()[0]
        return {"memories": total, "documents": docs, "tokens_stored": toks,
                "hot_memories": hot}

    def prune(self, min_cos_keep_docs: List[str], older_than_days: float = 60,
              max_accesses: int = 0) -> int:
        """Cron-friendly hygiene: drop cold duplicates of refreshed docs."""
        cur = self.conn.execute(
            "DELETE FROM memories WHERE created < ? AND accesses <= ? "
            "AND doc_id IN (%s)" % ",".join("?" * len(min_cos_keep_docs)),
            (time.time() - older_than_days * 86400, max_accesses, *min_cos_keep_docs))
        self.conn.commit()
        return cur.rowcount

    def all_records(self) -> List[MemoryRecord]:
        rows = self.conn.execute(
            "SELECT chunk_id,doc_id,section,source,text,vec,tokens,meta,"
            "created,accesses,last_seen FROM memories").fetchall()
        return [MemoryRecord(chunk_id=r[0], doc_id=r[1], text=r[4],
                             vector=json.loads(r[5]), section=r[2], source=r[3],
                             tokens_est=r[6], meta=json.loads(r[7]),
                             created_at=r[8], access_count=r[9], last_accessed=r[10])
                for r in rows]

    def delete_doc(self, doc_id: str) -> int:
        cur = self.conn.execute("DELETE FROM memories WHERE doc_id=?", (doc_id,))
        self.conn.commit()
        return cur.rowcount


class SupabaseVectorStore:
    """pgvector via PostgREST RPC (upsert_memory / search_memory SQL funcs)."""

    def __init__(self, url: str, key: str):
        self.url = url.rstrip("/")
        self.key = key

    def _rpc(self, fn: str, params: Dict[str, Any]) -> Any:
        req = urllib.request.Request(
            f"{self.url}/rest/v1/rpc/{fn}",
            data=json.dumps(params).encode(),
            headers={"apikey": self.key, "Authorization": f"Bearer {self.key}",
                     "Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read().decode())

    def upsert_many(self, recs: List[MemoryRecord]) -> int:
        payload = [{"p_chunk_id": r.chunk_id, "p_doc_id": r.doc_id,
                    "p_text": r.text, "p_vector": r.vector,
                    "p_section": r.section, "p_source": r.source,
                    "p_tokens": r.tokens_est, "p_meta": r.meta or {}}
                   for r in recs]
        self._rpc("upsert_memories_batch", {"records": payload})
        return len(recs)

    def search(self, qvec: List[float], top_k: int = 5,
               doc_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        out = self._rpc("search_memory", {"qvec": qvec, "k": top_k,
                                          "doc_id_f": doc_filter})
        return [{**row, "cosine": round(1 - row.get("distance", 1), 4)} for row in out]

    def stats(self) -> Dict[str, Any]:
        out = self._rpc("memory_stats", {})
        return out[0] if isinstance(out, list) and out else {}


def get_store():
    url = os.environ.get("SUPABASE_URL", "")
    key = os.environ.get("SUPABASE_SERVICE_KEY", "") or os.environ.get("SUPABASE_KEY", "")
    if url and key:
        try:
            s = SupabaseVectorStore(url, key)
            s.search([0.0] * 8, top_k=1)   # health ping
            return s, "supabase-pgvector"
        except Exception:
            pass
    return LocalVectorStore(), "sqlite-local"


if __name__ == "__main__":
    st, mode = get_store()
    print(f"store={mode} stats={st.stats()}")
