# -*- coding: utf-8 -*-
"""
Design-Guard-ZeroBaran — الطبقة 3: الأرشيف والسجلات التاريخية
===============================================================
Persistence Layer: يخزن تقارير الفحص في Supabase (PostgreSQL مجاني)
عبر REST خام، مع سقوط تلقائي إلى JSON محلي. يبني مؤشرات إنتاجية:
نسبة القبول، متوسط المطابقة، وأكثر العيوب تكراراً عبر الزمن.

المؤلف: Baran Avisat | baranavisat@gmail.com | واتساب: 00905313263722
الحقوق محفوظة © ZeroBaran Studio — MIT License
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

import requests


def _env(name: str, default: str = "") -> str:
    return os.getenv(name, default)


class QaStore:
    """واجهة موحدة للتخزين: supabase أو json — لا يسقط الأنبوب أبداً."""

    def __init__(self, cfg: dict, base_dir: Path):
        st = cfg["storage"]
        self.backend_pref = st.get("backend", "json")
        self.table = st.get("table", "qa_reports")
        self.json_path = base_dir / st.get("json_fallback_path", "state/qa_reports.json")
        self.url = _env("SUPABASE_URL")
        self.key = _env("SUPABASE_SERVICE_KEY") or _env("SUPABASE_ANON_KEY")
        self.mode = "supabase" if (self.backend_pref == "supabase" and self.url and self.key) else "json"
        self.warnings: List[str] = []

    # ---------------- helpers
    def _headers(self):
        return {"apikey": self.key, "Authorization": f"Bearer {self.key}",
                "Content-Type": "application/json", "Prefer": "resolution=merge-duplicates"}

    def _load_local(self) -> dict:
        if self.json_path.exists():
            try:
                return json.loads(self.json_path.read_text(encoding="utf-8"))
            except Exception:
                self.warnings.append("محلي JSON تالف — أُعيد إنشاؤه.")
        return {}

    def _save_local(self, data: dict):
        self.json_path.parent.mkdir(parents=True, exist_ok=True)
        self.json_path.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")

    # ---------------- API
    def known_checksums(self) -> dict:
        """checksum -> filename لمنع إعادة فحص نفس الأصل مراراً."""
        if self.mode == "supabase":
            try:
                r = requests.get(f"{self.url}/rest/v1/{self.table}"
                                 f"?select=checksum,filename&order=created_at.desc&limit=2000",
                                 headers=self._headers(), timeout=30)
                r.raise_for_status()
                return {row["checksum"]: row["filename"] for row in r.json() if row.get("checksum")}
            except Exception as e:
                self.warnings.append(f"Supabase unavailable ({e.__class__.__name__}) — fallback محلي.")
                self.mode = "json"
        data = self._load_local()
        return {k: v.get("filename", k) for k, v in data.items()}

    def save_report(self, report: dict) -> bool:
        report.setdefault("created_at", datetime.now(timezone.utc).isoformat())
        if self.mode == "supabase":
            try:
                r = requests.post(f"{self.url}/rest/v1/{self.table}",
                                  headers={**self._headers(), "Prefer": "return=minimal"},
                                  json=[report], timeout=30)
                r.raise_for_status()
                return True
            except Exception as e:
                self.warnings.append(f"فشل حفظ Supabase ({e.__class__.__name__}) — حُفظ محلياً.")
                self.mode = "json"
        data = self._load_local()
        data[report.get("checksum") or report["asset_id"]] = report
        self._save_local(data)
        return True

    def recent(self, limit: int = 200) -> List[dict]:
        if self.mode == "supabase":
            try:
                r = requests.get(f"{self.url}/rest/v1/{self.table}"
                                 f"?select=*&order=created_at.desc&limit={limit}",
                                 headers=self._headers(), timeout=30)
                r.raise_for_status()
                return r.json()
            except Exception as e:
                self.warnings.append(f"قراءة Supabase فشلت ({e.__class__.__name__}).")
        rows = list(self._load_local().values())
        rows.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        return rows[:limit]

    # ---------------- مؤشرات الإنتاجية
    def productivity_metrics(self, days: int = 7) -> dict:
        cutoff = datetime.now(timezone.utc).timestamp() - days * 86400

        def _ts(r: dict) -> float:
            raw = (r.get("created_at") or "").replace("Z", "+00:00")
            try:
                dt = datetime.fromisoformat(raw)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                return dt.timestamp()
            except ValueError:
                return 0.0

        rows = [r for r in self.recent(1000) if _ts(r) >= cutoff]
        total = len(rows)
        if not total:
            return {"total": 0, "accept_rate": None, "avg_match": None, "top_defects": [], "by_verdict": {}}
        by = {}
        scores = []
        defect_counter: dict = {}
        for r in rows:
            v = r.get("verdict", "unknown")
            by[v] = by.get(v, 0) + 1
            if isinstance(r.get("match_score"), (int, float)):
                scores.append(r["match_score"])
            for d in (r.get("defects") or []):
                t = d.get("type", "?")
                defect_counter[t] = defect_counter.get(t, 0) + 1
        return {
            "total": total,
            "accept_rate": round(by.get("accepted", 0) / total * 100, 1),
            "reject_rate": round(by.get("rejected", 0) / total * 100, 1),
            "avg_match": round(sum(scores) / len(scores), 1) if scores else None,
            "by_verdict": by,
            "top_defects": sorted(defect_counter.items(), key=lambda x: -x[1])[:8],
        }


if __name__ == "__main__":
    import yaml
    cfg = yaml.safe_load(open(Path(__file__).parent / "config.yaml", encoding="utf-8"))
    store = QaStore(cfg, Path.cwd())
    print(json.dumps({"mode": store.mode, "metrics": store.productivity_metrics()},
                     ensure_ascii=False, indent=2))
