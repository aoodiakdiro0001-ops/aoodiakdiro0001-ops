#!/usr/bin/env python3
# =====================================================================
#  Scrapling-ZeroBaran — Layer 3: Persistence + Change Detection
#  Project #38 | ZeroBaran Studio — 100% Free Stack
#  Author : Baran Avisat | Baranavisat@gmail.com | WhatsApp: 00905313263722
#  Copyright (c) 2026 Baran Avisat. All rights reserved. (MIT licensed)
#
#  Supabase (Postgres free tier) via raw REST, with automatic local JSON
#  fallback. Tracks value history per record key -> emits CHANGED events
#  (price drops, new stock, rating shifts) for instant alerts.
# =====================================================================
from __future__ import annotations

import json
import logging
import os
import time
from pathlib import Path
from typing import Any

log = logging.getLogger("sz.store")


class Store:
    def __init__(self, cfg: dict, base_dir: Path):
        st = cfg.get("storage", {})
        self.table_records = st.get("supabase_table_records", "scraped_records")
        self.table_runs = st.get("supabase_table_runs", "crawl_runs")
        self.keep_history = st.get("history_keep_per_key", 50)
        self.sb_url = os.environ.get("SUPABASE_URL", "").rstrip("/")
        self.sb_key = os.environ.get("SUPABASE_SERVICE_KEY", "") or os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
        self.local_dir = (base_dir / st.get("local_state_dir", "../state")).resolve()
        self.local_dir.mkdir(parents=True, exist_ok=True)
        self.records_file = self.local_dir / "records.json"
        self.runs_file = self.local_dir / "runs.json"
        self.mode = "supabase+json" if (self.sb_url and self.sb_key) else "json"

    # ---------- helpers ----------
    def _load(self, f: Path) -> dict:
        try:
            return json.loads(f.read_text(encoding="utf-8"))
        except Exception:
            return {}

    def _save(self, f: Path, data: Any) -> None:
        tmp = f.with_suffix(".tmp")
        tmp.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
        tmp.replace(f)

    def _sb_headers(self) -> dict:
        return {"apikey": self.sb_key, "Authorization": f"Bearer {self.sb_key}",
                "Content-Type": "application/json", "Prefer": "resolution=merge-duplicates,return=minimal"}

    def _sb_upsert(self, table: str, rows: list[dict]) -> bool:
        import requests
        url = f"{self.sb_url}/rest/v1/{table}"
        try:
            r = requests.post(url, json=rows, headers=self._sb_headers(), timeout=30)
            ok = r.status_code in (200, 201, 204)
            if not ok:
                log.warning("supabase upsert %s -> %s %s", table, r.status_code, r.text[:200])
            return ok
        except Exception as e:
            log.warning("supabase unreachable (%s) -> json only", e)
            return False

    # ---------- public API ----------
    def put_records(self, records: list[dict], target: str) -> dict[str, dict]:
        """Insert/update records; returns {id: change_event} where value changed."""
        now = int(time.time())
        db = self._load(self.records_file)
        changes: dict[str, dict] = {}
        rows = []
        for rec in records:
            rid = rec.get("id") or f"{target}-{now}"
            key_fields = {k: v for k, v in rec.items()
                          if k not in ("id", "_source_url", "ai_confidence") and not k.startswith("_")}
            tracked = self._tracked_values(rec)
            prev = db.get(rid)
            event = None
            if prev:
                old_vals = prev.get("values", {})
                title = (rec.get("ai_title") or rec.get("text") or rec.get("title")
                         or next((str(v) for k, v in key_fields.items()
                                  if isinstance(v, str) and len(str(v)) > 3), rid))[:120]
                for name, newv in tracked.items():
                    oldv = old_vals.get(name)
                    if oldv is not None and newv is not None and oldv != newv:
                        event = {"type": "CHANGED", "field": name, "old": oldv, "new": newv,
                                 "title": title}
                        break
                hist = prev.get("history", [])
            else:
                hist = []
                if self.mode == "json":
                    event = None  # brand-new record -> counted as NEW elsewhere
            hist.append({"ts": now, "values": tracked})
            db[rid] = {"id": rid, "target": target, "url": rec.get("_source_url", ""),
                       "fields": key_fields, "values": tracked,
                       "category": rec.get("ai_category", "general"),
                       "first_seen": (prev or {}).get("first_seen", now), "last_seen": now,
                       "history": hist[-self.keep_history:]}
            if event:
                changes[rid] = event
            rows.append({"id": rid, "target": target, "source_url": rec.get("_source_url", ""),
                         "data": key_fields, "values": tracked,
                         "category": rec.get("ai_category", "general"),
                         "first_seen": db[rid]["first_seen"], "last_seen": now})
        self._save(self.records_file, db)
        if rows and self.sb_url and self.sb_key:
            self._sb_upsert(self.table_records, rows)
        return changes

    @staticmethod
    def _tracked_values(rec: dict) -> dict:
        vals = {}
        av = rec.get("ai_values") or {}
        if isinstance(av, dict):
            for k in ("price", "rating"):
                if av.get(k) is not None:
                    vals[k] = float(av[k])
        for k, v in rec.items():
            if k in ("price", "cost", "amount") and isinstance(v, (int, float)):
                vals[k] = float(v)
        return vals

    def count_known(self, ids: list[str]) -> set[str]:
        db = self._load(self.records_file)
        return {i for i in ids if i in db}

    def log_run(self, run: dict) -> None:
        runs = self._load(self.runs_file)
        runs[run["run_id"]] = run
        # keep newest 500
        if len(runs) > 500:
            oldest = sorted(runs.items(), key=lambda kv: kv[1].get("ts", 0))[:len(runs) - 500]
            for k, _ in oldest:
                runs.pop(k, None)
        self._save(self.runs_file, runs)
        if self.sb_url and self.sb_key:
            self._sb_upsert(self.table_runs, [{
                "run_id": run["run_id"], "ts": run.get("ts", int(time.time())),
                "targets": run.get("targets", []), "pages_fetched": run.get("pages_fetched", 0),
                "records_new": run.get("records_new", 0), "records_changed": run.get("records_changed", 0),
                "blocks_detected": run.get("blocks_detected", 0), "engines_used": run.get("engines_used", {}),
                "status": run.get("status", "ok")}])

    def stats(self) -> dict:
        db = self._load(self.records_file)
        runs = self._load(self.runs_file)
        by_target: dict[str, int] = {}
        by_cat: dict[str, int] = {}
        for r in db.values():
            by_target[r.get("target", "?")] = by_target.get(r.get("target", "?"), 0) + 1
            by_cat[r.get("category", "general")] = by_cat.get(r.get("category", "general"), 0) + 1
        return {"total_records": len(db), "by_target": by_target, "by_category": by_cat,
                "total_runs": len(runs), "mode": self.mode}

    def export_jsonl(self, out_path: Path) -> Path:
        db = self._load(self.records_file)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with out_path.open("w", encoding="utf-8") as fh:
            for r in db.values():
                fh.write(json.dumps(r, ensure_ascii=False) + "\n")
        return out_path
