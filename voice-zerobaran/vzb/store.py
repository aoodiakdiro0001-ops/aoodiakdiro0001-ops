# -*- coding: utf-8 -*-
"""
Voice-ZeroBaran — Project #36 | ZeroBaran Studio
Copyright (c) 2026 Baran Avisat. Support: Baranavisat@gmail.com | WhatsApp 00905313263722

Layer 3 — PERSISTENCE: Supabase (Postgres + Storage free tier) with automatic
local JSON fallback so the studio never stops when keys are absent.
Stores job records + uploads produced assets to a Supabase storage bucket and
returns public URLs for instant delivery.
"""
from __future__ import annotations

import hashlib
import json
import mimetypes
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from .config import CFG, DATA_DIR, STATE_FILE


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _sha(p: Path) -> str:
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()[:16]


class LocalStore:
    """JSON state mirror — always works."""

    def __init__(self, path: Path = STATE_FILE):
        self.path = path
        self.data = {"jobs": [], "assets": []}
        if path.exists():
            try:
                self.data = json.loads(path.read_text(encoding="utf-8"))
            except Exception:
                pass

    def save(self):
        self.path.write_text(json.dumps(self.data, ensure_ascii=False, indent=1),
                             encoding="utf-8")

    def add_job(self, job: dict) -> bool:
        if any(j.get("id") == job["id"] for j in self.data["jobs"]):
            return False  # dedupe contract
        self.data["jobs"].append(job)
        if "asset" in job:
            self.data["assets"].append(job["asset"])
        self.save()
        return True

    def stats(self) -> dict:
        jobs = self.data["jobs"]
        by_type = {}
        for j in jobs:
            by_type[j.get("type", "?")] = by_type.get(j.get("type", "?"), 0) + 1
        return {"jobs_total": len(jobs), "by_type": by_type,
                "assets": len(self.data["assets"]),
                "last": jobs[-1]["created_at"] if jobs else None}


class SupabaseClient:
    def __init__(self):
        self.base = CFG.supabase_url.rstrip("/")
        self.key = CFG.supabase_service_key

    def _req(self, url: str, method: str, payload=None, extra_headers=None,
             data_bytes: Optional[bytes] = None, content_type: str = "application/json"):
        headers = {"apikey": self.key, "Authorization": f"Bearer {self.key}"}
        if extra_headers:
            headers.update(extra_headers)
        body = None
        if data_bytes is not None:
            body = data_bytes
            headers["Content-Type"] = content_type
        elif payload is not None:
            body = json.dumps(payload).encode()
            headers["Content-Type"] = content_type
        req = urllib.request.Request(url, data=body, method=method, headers=headers)
        with urllib.request.urlopen(req, timeout=40) as r:
            raw = r.read().decode()
        return json.loads(raw) if raw else {}

    def upsert_job(self, job: dict) -> bool:
        url = f"{self.base}/rest/v1/vzb_jobs"
        self._req(url, "POST", [job], {"Prefer": "resolution=merge-duplicates,return=minimal"})
        return True

    def upload_asset(self, local: Path, bucket: str = "vzb-assets") -> Optional[str]:
        """Upload to Supabase Storage; return public URL."""
        dest = f"{local.stem}_{_sha(local)}{local.suffix}"
        url = f"{self.base}/storage/v1/object/{bucket}/{dest}"
        ctype = mimetypes.guess_type(str(local))[0] or "application/octet-stream"
        try:
            self._req(url, "POST", data_bytes=local.read_bytes(),
                      extra_headers={"x-upsert": "true"}, content_type=ctype)
            return f"{self.base}/storage/v1/object/public/{bucket}/{dest}"
        except (urllib.error.URLError, KeyError) as e:
            print(f"[supabase] upload skipped: {str(e)[:120]}")
            return None


class Store:
    def __init__(self):
        self.local = LocalStore()
        self.sb = SupabaseClient() if CFG.has_supabase else None

    def record_job(self, job: dict, asset_path: Optional[Path] = None) -> dict:
        job.setdefault("created_at", _now())
        new = self.local.add_job(job)
        result = {"stored": new, "backend": "local-json"}
        if asset_path and Path(asset_path).exists():
            asset = {"path": str(asset_path), "sha": _sha(asset_path),
                     "size_kb": round(Path(asset_path).stat().st_size / 1024, 1),
                     "created_at": _now()}
            if self.sb:
                pub = self.sb.upload_asset(Path(asset_path))
                if pub:
                    asset["public_url"] = pub
                    result["backend"] = "supabase+local"
                    try:
                        self.sb.upsert_job({**job, "asset_url": pub})
                    except Exception as e:
                        result["supabase_note"] = str(e)[:120]
            job["asset"] = asset
            self.local.save()
        result["deduped"] = not new
        return result

    def stats(self) -> dict:
        return self.local.stats()


STORE = Store()
