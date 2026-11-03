#!/usr/bin/env python3
# =====================================================================
#  Scrapling-ZeroBaran — Layer 2: AI Parsing Brain (Gemini / Groq)
#  Project #38 | ZeroBaran Studio — 100% Free Stack
#  Author : Baran Avisat | Baranavisat@gmail.com | WhatsApp: 00905313263722
#  Copyright (c) 2026 Baran Avisat. All rights reserved. (MIT licensed)
#
#  Cleans messy extracted text into typed JSON records, classifies and
#  normalizes fields (prices -> numeric+currency), with a deterministic
#  offline MockBrain so CI works with zero keys.
# =====================================================================
from __future__ import annotations

import json
import logging
import os
import re
import time
from typing import Any

log = logging.getLogger("sz.brain")

SCHEMA_HINT = """You are a data-cleaning engine. Input is raw scraped web text or messy JSON records.
Return STRICT JSON only: {"records":[{"title":str,"value_fields":{"price":number|null,"currency":str|null,"rating":number|null},"category":str,"summary":str,"confidence":0..1}],"notes":str}
Rules: no invented data; drop ads/nav/cookie noise; normalize numbers; keep original language of content."""


def _extract_json(text: str) -> dict:
    m = re.search(r"\{.*\}", text, re.S)
    if not m:
        raise ValueError("no JSON object in model output")
    return json.loads(m.group(0))


class GroqBrain:
    name = "groq"

    def __init__(self, cfg: dict):
        self.key = os.environ.get("GROQ_API_KEY", "")
        self.model = cfg.get("ai", {}).get("groq_model", "llama-3.3-70b-versatile")
        self.url = "https://api.groq.com/openai/v1/chat/completions"

    @property
    def available(self) -> bool:
        return bool(self.key)

    def complete(self, prompt: str) -> str:
        import requests
        body = {"model": self.model, "temperature": 0.1,
                "messages": [{"role": "system", "content": SCHEMA_HINT},
                             {"role": "user", "content": prompt[:12000]}]}
        for attempt in range(3):
            r = requests.post(self.url, json=body, timeout=60,
                              headers={"Authorization": f"Bearer {self.key}"})
            if r.status_code == 429:
                time.sleep(2 ** (attempt + 1)); continue
            r.raise_for_status()
            return r.json()["choices"][0]["message"]["content"]
        r.raise_for_status()
        return ""


class GeminiBrain:
    name = "gemini"

    def __init__(self, cfg: dict):
        self.key = os.environ.get("GEMINI_API_KEY", "")
        self.model = cfg.get("ai", {}).get("gemini_model", "gemini-2.0-flash")

    @property
    def available(self) -> bool:
        return bool(self.key)

    def complete(self, prompt: str) -> str:
        import requests
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.key}"
        body = {"systemInstruction": {"parts": [{"text": SCHEMA_HINT}]},
                "contents": [{"parts": [{"text": prompt[:12000]}]}],
                "generationConfig": {"temperature": 0.1}}
        for attempt in range(3):
            r = requests.post(url, json=body, timeout=60)
            if r.status_code == 429:
                time.sleep(2 ** (attempt + 1)); continue
            r.raise_for_status()
            data = r.json()
            return data["candidates"][0]["content"]["parts"][0]["text"]
        r.raise_for_status()
        return ""


class MockBrain:
    """Deterministic offline cleaner — always available, zero cost."""
    name = "mock"
    available = True

    PRICE_RE = re.compile(r"(?:[$€£¥﷼د\.إ]\s*?)(\d+(?:[.,]\d+)?)|(\d+(?:[.,]\d+)?)\s*(?:USD|EUR|GBP|SAR|AED|EGP|\$)", re.I)
    RATING_RE = re.compile(r"(\d(?:[.,]\d)?)\s*(?:/5|stars?|نجوم?|تقييم)", re.I)

    def complete(self, prompt: str) -> str:
        recs = []
        # structured pass-through if the input already is our record JSON
        try:
            payload = json.loads(prompt)
            if isinstance(payload, list):
                for item in payload:
                    if isinstance(item, dict):
                        recs.append(self._normalize_dict(item))
        except Exception:
            pass
        if not recs:
            for line in prompt.splitlines():
                line = line.strip(" •-\t")
                if len(line) < 12 or re.match(r"(?i)^(cookie|menu|nav|ad|subscribe|follow)", line):
                    continue
                recs.append({"title": line[:120],
                             "value_fields": self._values(line),
                             "category": self._category(line),
                             "summary": line[:200], "confidence": 0.55})
        return json.dumps({"records": recs[:40], "notes": "offline deterministic clean"}, ensure_ascii=False)

    def _normalize_dict(self, item: dict) -> dict:
        title = item.get("text") or item.get("title") or item.get("name") or str(list(item.values())[0])[:120]
        blob = " ".join(str(v) for v in item.values())
        return {"title": str(title)[:200], "value_fields": self._values(blob),
                "category": item.get("category") or self._category(blob),
                "summary": str(title)[:200], "confidence": 0.9, "_passthrough": True,
                "_keep": {k: v for k, v in item.items() if not k.startswith("_")}}

    def _values(self, s: str) -> dict:
        out: dict[str, Any] = {"price": None, "currency": None, "rating": None}
        m = self.PRICE_RE.search(s)
        if m:
            num = (m.group(1) or m.group(2)).replace(",", ".")
            out["price"] = float(num)
            cu = re.search(r"(USD|EUR|GBP|SAR|AED|EGP|\$|€|£)", s, re.I)
            out["currency"] = cu.group(1) if cu else "USD"
        mr = self.RATING_RE.search(s)
        if mr:
            out["rating"] = float(mr.group(1).replace(",", "."))
        return out

    @staticmethod
    def _category(s: str) -> str:
        low = s.lower()
        for cat, words in {
            "price_offer": ["price", "$", "€", "discount", "sale", "سعر", "خصم"],
            "review": ["review", "rating", "stars", "تقييم", "مراجعة"],
            "product": ["product", "buy", "add to cart", "منتج", "شراء"],
            "article": ["news", "article", "blog", "خبر", "مقال"],
        }.items():
            if any(w in low for w in words):
                return cat
        return "general"


def get_brain(cfg: dict):
    prov = cfg.get("ai", {}).get("provider", "auto")
    if prov == "groq":
        b = GroqBrain(cfg); return b if b.available else MockBrain()
    if prov == "gemini":
        b = GeminiBrain(cfg); return b if b.available else MockBrain()
    # auto: prefer groq (fast free tier), then gemini, then mock
    for cls in (GroqBrain, GeminiBrain):
        b = cls(cfg)
        if b.available:
            return b
    return MockBrain()


def structure_records(brain, raw_records: list[dict], max_items: int = 20) -> tuple[list[dict], str]:
    """Send recipe-extracted records through the brain for normalization/classification."""
    if not raw_records:
        return [], "no-input"
    batch = raw_records[:max_items]
    try:
        out = brain.complete(json.dumps(batch, ensure_ascii=False))
        parsed = _extract_json(out)
        recs = parsed.get("records", [])
        # merge AI enrichment back onto originals by order/id when passthrough
        merged = []
        for i, r in enumerate(recs):
            base = dict(batch[i]) if i < len(batch) and r.get("_passthrough") else {}
            keep = r.pop("_keep", None)
            if keep:
                base.update({k: v for k, v in keep.items()})
            base.update({"ai_title": r.get("title"), "ai_category": r.get("category", "general"),
                         "ai_values": r.get("value_fields", {}), "ai_summary": r.get("summary", ""),
                         "ai_confidence": float(r.get("confidence", 0.5)),
                         "id": base.get("id") or r.get("title", str(i))[:64]})
            base.setdefault("id", base.get("_source_url", "") + f"#{i}")
            merged.append(base)
        return merged, brain.name
    except Exception as e:
        log.warning("brain failed (%s) -> raw passthrough", e)
        return [dict(r, ai_category="general", ai_confidence=0.3) for r in raw_records], f"{brain.name}-fallback"


def structure_page_text(brain, page_text: str, url: str, max_items: int = 20) -> tuple[list[dict], str]:
    """Full-text mode: turn messy page text into typed records."""
    if not page_text or len(page_text.strip()) < 40:
        return [], "empty"
    try:
        out = brain.complete(page_text[:12000])
        parsed = _extract_json(out)
        recs = []
        for i, r in enumerate(parsed.get("records", [])[:max_items]):
            rid = hashlib_sha(f"{url}::txt::{r.get('title','')[:80]}::{i}")
            recs.append({"id": rid, "_source_url": url, "ai_title": r.get("title"),
                         "ai_category": r.get("category", "general"),
                         "ai_values": r.get("value_fields", {}),
                         "ai_summary": r.get("summary", ""),
                         "ai_confidence": float(r.get("confidence", 0.5))})
        return recs, brain.name
    except Exception as e:
        log.warning("page-text structuring failed: %s", e)
        return [], f"{brain.name}-fallback"


def hashlib_sha(s: str) -> str:
    import hashlib
    return hashlib.sha1(s.encode("utf-8", "ignore")).hexdigest()
