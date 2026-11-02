#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pulse-Zero :: Persistence Layer (طبقة الأرشيف والمتابعة التاريخية)
===================================================================
يعمل مع Supabase (PostgreSQL مجاني) عبر REST API المدمج — بلا أي SDK ثقيل.
إن غابت بيانات Supabase، يسقط تلقائياً إلى ملف JSON محلي حتى لا تتوقف أبداً.

المسؤوليات:
  • known_ids()      — بصمات السجلات المخزنة سابقاً ( لمنع التكرار النهائي بين التشغيلات )
  • upsert_many()    — إدراج/تحديث جماعي (onconflict=id)
  • weekly_stats()   — مؤشرات السمعة الأسبوعية للتقرير (Sentiment Score العام)
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

RECORD_FIELDS = [
    "id", "source", "source_name", "title", "body", "url", "author",
    "published", "lang_hint", "meta", "sentiment", "score", "category",
    "issue_root", "severity", "reply_draft", "engine",
]


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class SupabaseStore:
    """عميل REST خفيف لطاولة public.mentions في Supabase."""

    def __init__(self, url: str, key: str, table: str = "mentions"):
        self.base = url.rstrip("/")
        self.table = table
        # service_role key إن وُجد وإلا anon — الاثنان يعملان مع policy مناسبة
        self.key = key

    def _req(self, path: str, method: str = "GET", body: Optional[dict] = None,
             headers: Optional[dict] = None) -> bytes:
        data = json.dumps(body).encode("utf-8") if body is not None else None
        req = urllib.request.Request(f"{self.base}{path}", data=data, method=method)
        req.add_header("apikey", self.key)
        req.add_header("Authorization", f"Bearer {self.key}")
        req.add_header("Content-Type", "application/json")
        for k, v in (headers or {}).items():
            req.add_header(k, v)
        with urllib.request.urlopen(req, timeout=25) as resp:
            return resp.read()

    def known_ids(self) -> set[str]:
        try:
            raw = self._req(f"/rest/v1/{self.table}?select=id&limit=5000")
            return {str(r["id"]) for r in json.loads(raw)}
        except Exception as exc:
            print(f"  ⚠️ known_ids failed ({exc}) — سنعتبر كل شيء جديداً")
            return set()

    def upsert_many(self, records: list[dict]) -> int:
        if not records:
            return 0
        rows = [{k: rec.get(k) for k in RECORD_FIELDS} | {"analyzed_at": _now_iso()}
                for rec in records]
        # دفعات 500 صف لتفادي حدود حجم الطلب
        sent = 0
        for i in range(0, len(rows), 500):
            chunk = rows[i:i + 500]
            self._req(f"/rest/v1/{self.table}?on_conflict=id", method="POST",
                      body=chunk,
                      headers={"Prefer": "resolution=merge-duplicates,return=minimal"})
            sent += len(chunk)
        return sent

    def weekly_stats(self, days: int = 7) -> dict:
        since = datetime.now(timezone.utc).timestamp() - days * 86400
        since_iso = datetime.fromtimestamp(since, timezone.utc).isoformat()
        q = (f"/rest/v1/{self.table}?select=sentiment,score,severity,category"
             f"&analyzed_at=gte.{urllib.parse.quote(since_iso)}")
        try:
            rows = json.loads(self._req(q))
        except Exception:
            rows = []
        return _compute_stats(rows)


class JsonStore:
    """وضع محلي/اختباري: نفس الواجهة فوق ملف JSON واحد."""

    def __init__(self, path: str):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def _load(self) -> list[dict]:
        if self.path.exists():
            try:
                return json.loads(self.path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                return []
        return []

    def _save(self, rows: list[dict]) -> None:
        tmp = self.path.with_suffix(".tmp")
        tmp.write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")
        tmp.replace(self.path)

    def known_ids(self) -> set[str]:
        return {str(r.get("id")) for r in self._load()}

    def upsert_many(self, records: list[dict]) -> int:
        rows = self._load()
        index = {r.get("id"): i for i, r in enumerate(rows)}
        n = 0
        for rec in records:
            row = {k: rec.get(k) for k in RECORD_FIELDS} | {"analyzed_at": _now_iso()}
            rid = rec.get("id")
            if rid in index:
                rows[index[rid]] = row
            else:
                index[rid] = len(rows)
                rows.append(row)
            n += 1
        self._save(rows)
        return n

    def weekly_stats(self, days: int = 7) -> dict:
        cutoff = datetime.now(timezone.utc).timestamp() - days * 86400
        rows = []
        for r in self._load():
            ts = r.get("analyzed_at") or r.get("published") or ""
            try:
                dt = datetime.fromisoformat(ts)
                if dt.timestamp() >= cutoff:
                    rows.append(r)
            except ValueError:
                rows.append(r)  # سجل بلا وقت مفهوم ⇒ نحتفظ به محافظين
        return _compute_stats(rows)


def _compute_stats(rows: list[dict]) -> dict:
    total = len(rows)
    counts = {"positive": 0, "negative": 0, "neutral": 0}
    sev_counts = {"low": 0, "medium": 0, "high": 0, "crisis": 0}
    cat_counts: dict[str, int] = {}
    score_sum = 0.0
    negatives: list[dict] = []
    for r in rows:
        s = str(r.get("sentiment", "neutral"))
        counts[s if s in counts else "neutral"] += 1
        sev = str(r.get("severity", "low"))
        if sev in sev_counts:
            sev_counts[sev] += 1
        cat = str(r.get("category", "other"))
        cat_counts[cat] = cat_counts.get(cat, 0) + 1
        try:
            score_sum += float(r.get("score", 0.0))
        except (TypeError, ValueError):
            pass
        if s == "negative":
            negatives.append(r)
    avg = round(score_sum / total, 3) if total else 0.0
    # مؤشر سمعة من 0..100 (100 = ولاء تام)
    rep_index = round((avg + 1) / 2 * 100, 1)
    negatives.sort(key=lambda r: float(r.get("score", 0) or 0))
    top_issues = [{"body": str(r.get("body", ""))[:140], "severity": r.get("severity"),
                   "category": r.get("category")} for r in negatives[:5]]
    return {
        "total": total,
        "counts": counts,
        "severity": sev_counts,
        "categories": cat_counts,
        "avg_score": avg,
        "reputation_index": rep_index,
        "top_issues": top_issues,
    }


def get_store(cfg: dict):
    st = cfg.get("storage", {})
    backend = (st.get("backend") or "supabase").lower()
    url = os.environ.get("SUPABASE_URL", "").strip()
    key = (os.environ.get("SUPABASE_SERVICE_KEY")
           or os.environ.get("SUPABASE_ANON_KEY") or "").strip()

    if backend == "supabase" and url and key:
        print(f"  🗄️ التخزين: Supabase → {url[:40]}…/table:{st.get('table','mentions')}")
        return SupabaseStore(url, key, st.get("table", "mentions"))

    if backend == "supabase":
        print("  ⚠️ SUPABASE_URL/SUPABASE_SERVICE_KEY مفقودان — تحويل تلقائي إلى JSON المحلي")
    path = st.get("json_fallback_path", "state/mentions.json")
    return JsonStore(path)


if __name__ == "__main__":
    store = JsonStore("/tmp/pz_test.json")
    demo = [{"id": "abc", "sentiment": "negative", "score": -0.8, "severity": "crisis",
             "category": "complaint_delivery", "body": "لم يصلني المنتج", "analyzed_at": _now_iso()}]
    print(store.upsert_many(demo), store.known_ids(), store.weekly_stats())
