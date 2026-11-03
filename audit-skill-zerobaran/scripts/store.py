#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Audit-Skill-ZeroBaran — Layer 3: Persistence (Supabase + local fallback)
========================================================================
Project #35 | Baran Avisat | ZeroBaran Studio
Baranavisat@gmail.com | WhatsApp 00905313263722 | MIT (c) 2026

Stores audit reports + per-finding rows in Supabase (Postgres free tier) via
the PostgREST API, with a transparent JSON-file fallback so the system keeps
working with zero configuration. Tracks security posture over time so you can
answer: "هل مشاريعنا أصبحت أكثر أماناً من الشهر الماضي؟"
"""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

__author__ = "Baran Avisat"

STATE_DIR = Path(os.getenv("ASZ_STATE_DIR", Path(__file__).resolve().parent.parent / "data"))
LOCAL_DB = STATE_DIR / "audit_state.json"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


class Store:
    def __init__(self, url: Optional[str] = None, key: Optional[str] = None):
        self.url = (url or os.getenv("SUPABASE_URL", "")).rstrip("/")
        self.key = key or os.getenv("SUPABASE_SERVICE_KEY", "")
        self.remote_ok = bool(self.url and self.key)
        self.mode = "supabase" if self.remote_ok else "local-json"

    # ---------------- low-level PostgREST -----------------
    def _req(self, table: str, method: str, payload=None, query: str = "") -> Any:
        u = f"{self.url}/rest/v1/{table}{query}"
        data = json.dumps(payload).encode() if payload is not None else None
        req = urllib.request.Request(u, data=data, method=method, headers={
            "apikey": self.key, "Authorization": f"Bearer {self.key}",
            "Content-Type": "application/json",
            "Prefer": "resolution=merge-duplicates,return=minimal"})
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                body = r.read().decode()
                return json.loads(body) if body else []
        except urllib.error.HTTPError as e:
            raise RuntimeError(f"supabase {method} {table}: {e.code} {e.read().decode()[:200]}")
        except Exception as e:  # network down -> caller falls back
            raise RuntimeError(f"supabase unreachable: {e}")

    # ---------------- local json -----------------
    def _load_local(self) -> Dict[str, Any]:
        if LOCAL_DB.exists():
            try:
                return json.loads(LOCAL_DB.read_text(encoding="utf-8"))
            except Exception:
                pass
        return {"scans": [], "findings": {}, "history": []}

    def _save_local(self, db: Dict[str, Any]) -> None:
        STATE_DIR.mkdir(parents=True, exist_ok=True)
        LOCAL_DB.write_text(json.dumps(db, ensure_ascii=False, indent=1), encoding="utf-8")

    # ---------------- public API -----------------
    def save_report(self, report: Dict[str, Any], project_tag: str = "default") -> Dict[str, Any]:
        row = {
            "scan_id": report["scan_id"], "project_tag": project_tag,
            "target": report["target"], "ran_at": report.get("started_at", _now()),
            "files_scanned": report["files_scanned"],
            "findings_total": report["findings_total"],
            "counts_by_severity": report["counts_by_severity"],
            "security_score": report["security_score"],
            "verdict": report["verdict"],
            "engines": report["engines"], "ai_brains": report.get("ai_brains_used", []),
            "executive_summary_ar": report.get("executive_summary_ar", ""),
            "stored_at": _now(),
        }
        finding_rows = [{
            "scan_id": report["scan_id"], "fingerprint": f["fingerprint"],
            "rule_id": f["rule_id"], "title": f["title"], "severity": f["severity"],
            "category": f["category"], "file": f["file"], "line": f["line"],
            "cwe": f.get("cwe", ""), "owasp": f.get("owasp", ""),
            "engine": f.get("engine", "native"),
            "explanation_ar": (f.get("ai") or {}).get("explanation_ar", ""),
            "secure_fix_code": (f.get("ai") or {}).get("secure_fix_code", ""),
            "status": "open", "first_seen": _now(), "last_seen": _now(),
        } for f in report["findings"]]

        result = {"mode": self.mode, "saved_findings": len(finding_rows)}
        if self.remote_ok:
            try:
                self._req("asz_scans", "POST", [row])
                if finding_rows:
                    self._req("asz_findings", "POST", finding_rows)
                result["remote"] = True
                return result
            except RuntimeError as e:
                result["remote_error"] = str(e)
        db = self._load_local()
        db["scans"] = [s for s in db["scans"] if s["scan_id"] != row["scan_id"]] + [row]
        db["scans"] = db["scans"][-200:]
        for fr in finding_rows:
            prev = db["findings"].get(fr["fingerprint"])
            if prev:
                fr["first_seen"] = prev["first_seen"]
                fr["status"] = prev["status"]
            db["findings"][fr["fingerprint"]] = fr
        db["history"].append({"ts": _now(), "scan_id": row["scan_id"],
                              "score": row["security_score"], "verdict": row["verdict"]})
        db["history"] = db["history"][-500:]
        self._save_local(db)
        result["local"] = True
        return result

    def mark_fixed(self, fingerprint: str) -> bool:
        if self.remote_ok:
            try:
                self._req("asz_findings", "PATCH", {"status": "fixed", "fixed_at": _now()},
                          query=f"?fingerprint=eq.{fingerprint}")
                return True
            except RuntimeError:
                pass
        db = self._load_local()
        if fingerprint in db["findings"]:
            db["findings"][fingerprint]["status"] = "fixed"
            db["findings"][fingerprint]["fixed_at"] = _now()
            self._save_local(db)
            return True
        return False

    def open_findings(self, severities: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        db = self._load_local()
        rows = [f for f in db["findings"].values() if f["status"] == "open"]
        if severities:
            rows = [f for f in rows if f["severity"] in severities]
        order = {"CRITICAL": 4, "HIGH": 3, "MEDIUM": 2, "LOW": 1, "INFO": 0}
        return sorted(rows, key=lambda x: -order.get(x["severity"], 0))

    def trend(self, last_n: int = 30) -> List[Dict[str, Any]]:
        return self._load_local()["history"][-last_n:]

    def stats(self) -> Dict[str, Any]:
        db = self._load_local()
        open_f = [f for f in db["findings"].values() if f["status"] == "open"]
        fixed = [f for f in db["findings"].values() if f["status"] == "fixed"]
        by_sev: Dict[str, int] = {}
        by_rule: Dict[str, int] = {}
        for f in open_f:
            by_sev[f["severity"]] = by_sev.get(f["severity"], 0) + 1
            by_rule[f["rule_id"]] = by_rule.get(f["rule_id"], 0) + 1
        scores = [h["score"] for h in db["history"]]
        return {"mode": self.mode, "total_scans": len(db["scans"]),
                "open_findings": len(open_f), "fixed_findings": len(fixed),
                "open_by_severity": by_sev,
                "top_rules": dict(sorted(by_rule.items(), key=lambda kv: -kv[1])[:8]),
                "avg_score": round(sum(scores) / len(scores), 1) if scores else None,
                "latest_score": scores[-1] if scores else None}


if __name__ == "__main__":
    import sys
    sys.path.insert(0, str(Path(__file__).parent))
    from scanners import scan
    st = Store()
    rep = enrich = None
    from audit_brain import enrich_report
    rep = enrich_report(scan(sys.argv[1] if len(sys.argv) > 1 else "."))
    print(json.dumps(st.save_report(rep), ensure_ascii=False), json.dumps(st.stats(), ensure_ascii=False))
