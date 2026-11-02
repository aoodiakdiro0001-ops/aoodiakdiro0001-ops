#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pulse-Zero :: AI Sentiment Core (العقل الذكي لتحليل المشاعر)
=============================================================
يقرأ كل تعليق/تقييم ويستخرج JSON منظماً:
  sentiment   : positive | negative | neutral
  score       : -1.0 .. +1.0
  category    : praise | complaint_delivery | complaint_technical | question | spam | other
  issue_root  : جذر المشكلة بدقة (أو null)
  severity    : low | medium | high | crisis
  reply_draft : رد احترافي جاهز للإرسال للعميل الغاضب

المزوّدون المدعومون (كلها بخطط مجانية):
  • groq   — Groq Cloud API  (مجاني، سريع جداً)
  • gemini — Google Gemini API (خطة مجانية)
  • mock   — معجم عربي/إنجليزي قياسي بلا أي مفتاح (للتجربة المحلية و CI)

استراتيجيات توفير الحصص: batch calls + دقة منخفضة + retry/backoff على 429.
"""

from __future__ import annotations

import json
import os
import re
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field, asdict
from typing import Optional

# ------------------------------------------------------------- أنواع البيانات
@dataclass
class Analysis:
    mention_id: str
    sentiment: str = "neutral"        # positive | negative | neutral
    score: float = 0.0                # -1..1
    category: str = "other"
    issue_root: Optional[str] = None
    severity: str = "low"             # low | medium | high | crisis
    reply_draft: Optional[str] = None
    engine: str = "mock"
    error: Optional[str] = None


SYSTEM_PROMPT = """You are Pulse-Zero, an elite customer-sentiment and brand-reputation analyst.
For EACH item you receive a JSON object with fields id, title, body, lang_hint.
Return ONLY a JSON array (no markdown fences, no prose), one object per input item, in the same order:
[{"id":"...","sentiment":"positive|negative|neutral","score":-1.0 to 1.0,
  "category":"praise|complaint_delivery|complaint_technical|question|spam|other",
  "issue_root":"exact root cause of complaint or null",
  "severity":"low|medium|high|crisis",
  "reply_draft":"professional empathetic reply in the CUSTOMER's language for negative/crisis items, else null"}]
Rules: Arabic and English must be handled natively. A one-star angry review mentioning broken/undelivered/refund/scam
must be severity high or crisis. Never invent facts. Score calibration: praise ~ +0.6..+1, neutral ~ -0.2..+0.2,
complaints ~ -0.4..-1."""


def _json_block(payload: dict, url: str, headers: dict, timeout: int = 60, retries: int = 3) -> dict:
    """POST عام مع backoff لائق على Rate-Limit (429) وأخطاء الشبكة العابرة."""
    data = json.dumps(payload).encode("utf-8")
    last_err: Exception | None = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, data=data, method="POST")
            req.add_header("Content-Type", "application/json")
            for k, v in headers.items():
                req.add_header(k, v)
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:  # type: ignore[attr-defined]
            body = ""
            try:
                body = e.read().decode("utf-8", "ignore")[:300]
            except Exception:
                pass
            if e.code == 429 or e.code >= 500:
                wait = 5 * (2 ** attempt)          # 5s → 10s → 20s
                print(f"    ⏳ rate-limited/server ({e.code}) — retry in {wait}s")
                time.sleep(wait)
                last_err = e
                continue
            raise RuntimeError(f"HTTP {e.code}: {body}") from e
        except (urllib.error.URLError, TimeoutError) as e:  # type: ignore[attr-defined]
            last_err = e
            time.sleep(3 * (attempt + 1))
    raise RuntimeError(f"API unreachable after {retries} tries: {last_err}")


# ------------------------------------------------------------------ Providers
class GroqBrain:
    name = "groq"

    def __init__(self, api_key: str, model: str, temperature: float = 0.2):
        self.key, self.model, self.temp = api_key, model, temperature

    def analyze_batch(self, items: list[dict]) -> list[dict]:
        user_msg = json.dumps(items, ensure_ascii=False)
        payload = {
            "model": self.model,
            "temperature": self.temp,
            "response_format": {"type": "json_object"},
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f'Analyze these mentions and return {{"results":[...]}}:\n{user_msg}'},
            ],
        }
        resp = _json_block(payload, "https://api.groq.com/openai/v1/chat/completions",
                           {"Authorization": f"Bearer {self.key}"})
        text = resp["choices"][0]["message"]["content"]
        return _extract_array(text, key="results")


class GeminiBrain:
    name = "gemini"

    def __init__(self, api_key: str, model: str, temperature: float = 0.2):
        self.key, self.model, self.temp = api_key, model, temperature

    def analyze_batch(self, items: list[dict]) -> list[dict]:
        user_msg = ("Analyze these customer mentions. Return a JSON array only.\n"
                    + json.dumps(items, ensure_ascii=False))
        payload = {
            "systemInstruction": {"parts": [{"text": SYSTEM_PROMPT}]},
            "contents": [{"role": "user", "parts": [{"text": user_msg}]}],
            "generationConfig": {"temperature": self.temp, "responseMimeType": "application/json"},
        }
        url = (f"https://generativelanguage.googleapis.com/v1beta/models/"
               f"{self.model}:generateContent?key={self.key}")
        resp = _json_block(payload, url, {})
        try:
            text = resp["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError) as e:
            raise RuntimeError(f"Gemini unexpected shape: {str(resp)[:200]}") from e
        return _extract_array(text)


def _extract_array(text: str, key: Optional[str] = None) -> list[dict]:
    """ينتزع مصفوفة JSON من مخرجات النموذج مهما التف حولها نص أو أكواد."""
    text = re.sub(r"^```(?:json)?|```$", "", text.strip(), flags=re.M).strip()
    if key:
        try:
            obj = json.loads(text)
            if isinstance(obj, dict) and key in obj:
                return obj[key]
        except json.JSONDecodeError:
            pass
    m = re.search(r"\[.*\]", text, re.S)
    if m:
        try:
            arr = json.loads(m.group(0))
            if isinstance(arr, list):
                return arr
        except json.JSONDecodeError:
            pass
    try:
        obj = json.loads(text)
        return obj if isinstance(obj, list) else [obj]
    except json.JSONDecodeError:
        return []


# -------------------------------------------------------------------- Mock AI
_POS_AR = ["رائع", "ممتاز", "أفضل", "سريع", "سهل", "وفّر", "وفرت", "جميل", "شكرا", "شكراً", "أنصح", "عظيم", "محترف"]
_NEG_AR = ["سيئ", "تالف", "لم يعمل", "لم يصل", "احتيال", "نصب", "بطيء", "غالي", "استرجاع", "استرداد",
           "لم يرد", "لا يرد", "معيوب", "خراب", "فضيحة", "غضب", "أسوأ"]
_POS_EN = ["great", "excellent", "best", "love", "awesome", "saved", "fast", "easy", "recommend", "nice", "amazing"]
_NEG_EN = ["broken", "scam", "terrible", "worst", "refund", "never arrived", "slow", "crash", "bug",
           "useless", "angry", "awful", "didn't work", "did not work", "no response"]
_CRISIS = ["احتيال", "نصب", "scam", "fraud", "lawyer", "محامي", "report", "إبلاغ", "chargeback"]

# ── فلتر الضوضاء: منشورات لا تتحدث فعلاً عن العلامة تُصنَّف spam/low فوراً ──
_NOISE_MARKERS = ["submitted by", "[link] [comments]", "preview.redd.it", "r/politics",
                  "meme", "shitpost"]


def _is_noise(text: str, keywords: list[str]) -> bool:
    low = text.lower()
    if any(n in low for n in _NOISE_MARKERS):
        return True
    if keywords and not any(k.lower() in low for k in keywords):
        return True   # لا ذكر للعلامة ولا تقييم نجوم ⇒ خارج النطاق
    return False

_QUESTION = ["؟", "?", "هل", "how ", "what ", "does it", "أريد أن أعرف", "كيف"]


@dataclass
class MockBrain:
    name: str = "mock"
    brand_keywords: list[str] = None  # نوعاً ما: كلمات العلامة لفلتر الضوضاء

    def __post_init__(self):
        if self.brand_keywords is None:
            self.brand_keywords = []

    def analyze_batch(self, items: list[dict]) -> list[dict]:
        out = []
        for it in items:
            text = f"{it.get('title','')} {it.get('body','')}".lower()
            if _is_noise(text, self.brand_keywords) and not (it.get("meta") or {}).get("stars"):
                out.append({"id": it["id"], "sentiment": "neutral", "score": 0.0,
                            "category": "spam", "issue_root": None,
                            "severity": "low", "reply_draft": None})
                continue
            pos = sum(w in text for w in _POS_AR + _POS_EN)
            neg = sum(w in text for w in _NEG_AR + _NEG_EN)
            crisis = any(w in text for w in _CRISIS)
            stars = (it.get("meta") or {}).get("stars")
            star_penalty = 0.0
            if stars:
                n = stars.count("★")
                if n <= 2:
                    neg += 2
                    star_penalty = -0.3
                elif n >= 4:
                    pos += 1

            total = pos + neg
            if total == 0:
                score, senti = 0.0, "neutral"
            else:
                score = max(-1.0, min(1.0, (pos - neg) / max(total, 2) + star_penalty))
                senti = "positive" if score > 0.25 else "negative" if score < -0.25 else "neutral"

            is_q = any(q in text for q in _QUESTION) and senti != "negative"
            if is_q:
                category, severity = "question", "low"
            elif senti == "positive":
                category, severity = "praise", "low"
            elif senti == "negative":
                delivery = any(w in text for w in ["لم يصل", "never arrived", "توصيل", "shipping", "delivery", "وصل"])
                tech = any(w in text for w in ["لم يعمل", "لا يعمل", "تالف", "broken", "crash", "bug", "didn't work"])
                category = "complaint_delivery" if delivery else "complaint_technical" if tech else "other"
                severity = "crisis" if crisis else "high" if score <= -0.6 else "medium"
            else:
                category, severity = "other", "low"

            reply = None
            if senti == "negative":
                reply = ("مرحباً، نشعر بالأسف الشديد تجاه ما مررت به 🙏\n"
                        "فريقنا اطلع على مشكلتك الآن وسيتواصل معك خلال ساعات لحلها بالكامل "
                        "(تعويض/استبدال/استرجاع حسب رغبتك).\n— إدارة السمعة في BaranAvi")
            out.append({
                "id": it["id"], "sentiment": senti, "score": round(score, 3),
                "category": category, "issue_root": (it.get("body", "")[:120] or None) if senti == "negative" else None,
                "severity": severity, "reply_draft": reply,
            })
        return out


# ------------------------------------------------------------------ Factory
def get_brain(cfg: dict):
    ai = cfg.get("ai", {})
    provider = (ai.get("provider") or "mock").lower()
    model_map = ai.get("model", {}) or {}
    temp = float(ai.get("temperature", 0.2))

    if provider == "groq":
        key = _env_or_none("GROQ_API_KEY")
        if key:
            return GroqBrain(key, model_map.get("groq", "llama-3.3-70b-versatile"), temp)
        print("  ⚠️ GROQ_API_KEY مفقود — تحويل تلقائي إلى محرك Mock المحلي")
    elif provider == "gemini":
        key = _env_or_none("GEMINI_API_KEY") or _env_or_none("GOOGLE_API_KEY")
        if key:
            return GeminiBrain(key, model_map.get("gemini", "gemini-2.0-flash"), temp)
        print("  ⚠️ GEMINI_API_KEY مفقود — تحويل تلقائي إلى محرك Mock المحلي")

    keywords = list(cfg.get("brand", {}).get("keywords", []) or [])
    name = cfg.get("brand", {}).get("name")
    if name:
        keywords.append(name)
    return MockBrain(brand_keywords=keywords)


def _env_or_none(name: str) -> Optional[str]:
    v = os.environ.get(name)
    return (v or "").strip() or None


# ------------------------------------------------------------------ Pipeline
VALID_SENTI = {"positive", "negative", "neutral"}
VALID_SEV = {"low", "medium", "high", "crisis"}


def _normalize(raw: dict, mid: str) -> Analysis:
    a = Analysis(mention_id=mid)
    s = str(raw.get("sentiment", "neutral")).lower().strip()
    a.sentiment = s if s in VALID_SENTI else "neutral"
    try:
        a.score = max(-1.0, min(1.0, float(raw.get("score", 0.0))))
    except (TypeError, ValueError):
        a.score = 0.0
    a.category = str(raw.get("category", "other")).lower().strip() or "other"
    ir = raw.get("issue_root")
    a.issue_root = ir if isinstance(ir, str) and ir.strip() else None
    sev = str(raw.get("severity", "low")).lower().strip()
    a.severity = sev if sev in VALID_SEV else "low"
    rd = raw.get("reply_draft")
    a.reply_draft = rd if isinstance(rd, str) and rd.strip() else None
    return a


def analyze_mentions(mentions: list, brain, batch_size: int = 12) -> tuple[list[dict], list[str]]:
    """تحليل دفعي كامل: يعيد سجلات جاهزة للتخزين + قائمة أخطاء."""
    records: list[dict] = []
    errors: list[str] = []
    by_id = {m.id: m for m in mentions}

    for i in range(0, len(mentions), batch_size):
        batch = mentions[i:i + batch_size]
        payload_items = [{"id": m.id, "title": m.title, "body": m.body,
                          "lang_hint": m.lang_hint, "meta": m.meta} for m in batch]
        try:
            results = brain.analyze_batch(payload_items)
            rmap = {str(r.get("id", "")): r for r in results if isinstance(r, dict)}
            for m in batch:
                raw = rmap.get(m.id, {})
                ana = _normalize(raw, m.id)
                ana.engine = getattr(brain, "name", "mock")
                merged = asdict(m)
                merged.update({"sentiment": ana.sentiment, "score": ana.score,
                               "category": ana.category, "issue_root": ana.issue_root,
                               "severity": ana.severity, "reply_draft": ana.reply_draft,
                               "engine": ana.engine})
                records.append(merged)
        except Exception as exc:
            errors.append(f"[ai-batch {i//batch_size}] {type(exc).__name__}: {exc}")
            # لا نفقد البيانات: نمررها للمعجم المحلي كضمان احتياطي
            try:
                fallback = MockBrain().analyze_batch(payload_items)
                for m, raw in zip(batch, fallback):
                    ana = _normalize(raw, m.id)
                    ana.engine = "mock-fallback"
                    merged = asdict(m)
                    merged.update({"sentiment": ana.sentiment, "score": ana.score,
                                   "category": ana.category, "issue_root": ana.issue_root,
                                   "severity": ana.severity, "reply_draft": ana.reply_draft,
                                   "engine": ana.engine})
                    records.append(merged)
            except Exception as exc2:
                errors.append(f"[ai-fallback] {exc2}")

    return records, errors


if __name__ == "__main__":
    from ingest import demo_mentions
    brain = MockBrain()
    recs, errs = analyze_mentions(demo_mentions(), brain, batch_size=12)
    print(json.dumps(recs, ensure_ascii=False, indent=2))
    for e in errs:
        print("ERR:", e)
