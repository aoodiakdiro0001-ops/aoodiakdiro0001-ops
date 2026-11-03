# -*- coding: utf-8 -*-
"""
Design-Guard-ZeroBaran — الطبقة 2: العقل الذكي لتدقيق الجودة
=============================================================
AI Quality Core: يمرر الصورة إلى Gemini Vision API (أو النص إلى
Groq) كخبير Hallmark/Impeccable، فيعيد تقييماً إنشائياً صارماً:
match_score, verdict, defects, brand_consistency, fix_suggestion.
مع محرك Mock محلي ذكي يعمل بلا أي مفتاح (للاختبار وCI).

المؤلف: Baran Avisat | baranavisat@gmail.com | واتساب: 00905313263722
الحقوق محفوظة © ZeroBaran Studio — MIT License
"""
from __future__ import annotations

import base64
import json
import os
import re
import time
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

import requests

GEMINI_ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
GROQ_ENDPOINT = "https://api.groq.com/openai/v1/chat/completions"

SYSTEM_PROMPT = """أنت {persona}. مهمتك تدقيق أصول رقمية مولّدة بالذكاء الاصطناعي قبل اعتمادها للنشر التجاري.
افحص: التشوهات التشريحية (أصابع/أسنان/عيون/أطراف)، التناسق البصري، النصوص المشوهة داخل الصورة،
الأخطاء الإملائية والنحوية والمنطقية، بقايا placeholders، ومطابقة الهوية التجارية «{brand}».
أجب حصراً بـ JSON صالح دون أي نص خارجه، بهذا الشكل بالضبط:
{{"match_score": 0-100, "verdict": "accepted|rejected|needs_review",
 "defects": [{{"type": "...", "location": "...", "severity": "critical|major|minor", "note_ar": "..."}}],
 "brand_consistency": 0-100, "summary_ar": "خلاصة عربية من سطرين",
 "fix_suggestion_ar": "إصلاح مقترح قابل للتنفيذ فوراً"}}"""


@dataclass
class AIVerdict:
    match_score: float
    verdict: str                  # accepted | rejected | needs_review | unavailable
    defects: list
    brand_consistency: float
    summary_ar: str
    fix_suggestion_ar: str
    provider: str

    def to_dict(self):
        return dict(match_score=self.match_score, verdict=self.verdict,
                    defects=self.defects, brand_consistency=self.brand_consistency,
                    summary_ar=self.summary_ar, fix_suggestion_ar=self.fix_suggestion_ar,
                    provider=self.provider)


def _extract_json(text: str) -> Optional[dict]:
    """انتشال أول كائن JSON متوازن من رد النموذج (يتسامح مع ```json fences)."""
    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text.strip())
    start = text.find("{")
    if start < 0:
        return None
    depth = 0
    for i in range(start, len(text)):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                try:
                    return json.loads(text[start:i+1])
                except json.JSONDecodeError:
                    return None
    return None


def _post_with_retry(url: str, headers: dict, payload: dict, timeout: int = 60) -> dict:
    last_err = "unknown"
    for attempt in range(3):
        try:
            r = requests.post(url, headers=headers, json=payload, timeout=timeout)
            if r.status_code == 429:                      # حصة مجانية نفدت
                time.sleep(2 ** attempt * 3)
                last_err = "rate_limited(429)"
                continue
            r.raise_for_status()
            return r.json()
        except requests.RequestException as e:
            last_err = f"{e.__class__.__name__}: {e}"[:200]
            time.sleep(2 ** attempt)
    raise RuntimeError(last_err)


# --------------------------------------------------------------- Gemini Vision
class GeminiBrain:
    provider = "gemini-vision"

    def __init__(self, api_key: str, model: str, temperature: float, brand: str, persona: str):
        self.key, self.model, self.temp = api_key, model, temperature
        self.prompt = SYSTEM_PROMPT.format(persona=persona, brand=brand)

    def review(self, image_path: Optional[Path], text_content: str) -> AIVerdict:
        parts = [{"text": self.prompt + ("\n\nالنص المراد تدقيقه:\n" + text_content[:3000]
                                         if text_content else "\n\nقيّم الصورة المرفقة.")}]
        if image_path is not None:
            b64 = base64.b64encode(image_path.read_bytes()).decode()
            mime = {"png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg",
                    "webp": "image/webp", "bmp": "image/bmp"}.get(
                        image_path.suffix.lower().lstrip("."), "image/png")
            parts.append({"inline_data": {"mime_type": mime, "data": b64}})

        data = _post_with_retry(
            GEMINI_ENDPOINT.format(model=self.model) + f"?key={self.key}",
            {"Content-Type": "application/json"},
            {"system_instruction": {"parts": [{"text": self.prompt}]},
             "contents": [{"role": "user", "parts": parts}],
             "generationConfig": {"temperature": self.temp, "responseMimeType": "application/json"}},
        )
        try:
            body = data["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError):
            raise RuntimeError("Gemini returned empty candidates (blocked/safety).")
        parsed = _extract_json(body)
        if parsed is None:
            raise RuntimeError("Gemini reply is not valid JSON.")
        return _to_verdict(parsed, self.provider)


# ---------------------------------------------------------------------- Groq
class GroqBrain:
    provider = "groq-text"

    def __init__(self, api_key: str, model: str, temperature: float, brand: str, persona: str):
        self.key, self.model, self.temp = api_key, model, temperature
        self.prompt = SYSTEM_PROMPT.format(persona=persona, brand=brand)

    def review(self, image_path: Optional[Path], text_content: str) -> AIVerdict:
        content = text_content
        if not content and image_path is not None:
            # لا vision في Groq — نغذّيه بوصف الفحص الآلي كسياق
            content = f"[صورة: {image_path.name} — لا OCR متاح، قيّم بناءً على الفحص المجترة]"
        data = _post_with_retry(
            GROQ_ENDPOINT,
            {"Authorization": f"Bearer {self.key}", "Content-Type": "application/json"},
            {"model": self.model, "temperature": self.temp,
             "response_format": {"type": "json_object"},
             "messages": [{"role": "system", "content": self.prompt},
                          {"role": "user", "content": content[:6000]}]},
        )
        body = data["choices"][0]["message"]["content"]
        parsed = _extract_json(body)
        if parsed is None:
            raise RuntimeError("Groq reply is not valid JSON.")
        return _to_verdict(parsed, self.provider)


# --------------------------------------------------- Mock Brain (بلا مفاتيح أبداً)
class MockBrain:
    """محرك حتمي يستند إلى نتائج الطبقة 1 — يسمح بتشغيل الأنبوب كاملاً في CI."""
    provider = "mock-heuristic"

    def __init__(self, brand: str = ""):
        self.brand = brand

    def review(self, image_path: Optional[Path], text_content: str,
               structural_findings: Optional[list] = None) -> AIVerdict:
        findings = structural_findings or []
        codes = {f["code"]: f for f in findings}
        defects, score = [], 100.0
        weights = {"critical": 30, "major": 12, "minor": 4, "info": 0}
        for f in findings:
            w = weights.get(f["severity"], 0)
            score -= w
            if w:
                defects.append({"type": f["code"], "location": "auto-inspection",
                                "severity": f["severity"], "note_ar": f["message_ar"]})
        score = max(0.0, min(100.0, score))
        verdict = "accepted" if score >= 75 else ("needs_review" if score >= 55 else "rejected")
        fix = ("الأصل سليم — انشره بثقة." if verdict == "accepted" else
               "أعد التوليد مع تصحيح العيوب المدرجة أعلاه، ثم أعد الدفع للفحص.")
        return AIVerdict(round(score, 1), verdict, defects, round(min(score + 5, 100), 1),
                         f"تقييم مبدئي آلي (Mock) للمخرج: {verdict}. عيوب مرصودة: {len(defects)}.",
                         fix, self.provider)


def _to_verdict(p: dict, provider: str) -> AIVerdict:
    return AIVerdict(
        match_score=float(p.get("match_score", 0)),
        verdict=str(p.get("verdict", "needs_review")).lower(),
        defects=list(p.get("defects", []) or []),
        brand_consistency=float(p.get("brand_consistency", 0)),
        summary_ar=str(p.get("summary_ar", ""))[:800],
        fix_suggestion_ar=str(p.get("fix_suggestion_ar", ""))[:800],
        provider=provider,
    )


def build_brain(cfg: dict):
    """auto: gemini ← groq ← mock حسب المفاتيح المتاحة."""
    ai = cfg["ai"]
    owner = cfg.get("owner", {})
    persona, brand = ai.get("persona", "خبير جودة"), owner.get("brand", "Unknown")
    want = ai.get("provider", "auto")
    gk, gm = os.getenv("GEMINI_API_KEY", ""), ai["model"]["gemini"]
    kr, km = os.getenv("GROQ_API_KEY", ""), ai["model"]["groq"]
    temp = ai.get("temperature", 0.15)

    if want in ("auto", "gemini") and gk:
        return GeminiBrain(gk, gm, temp, brand, persona)
    if want in ("auto", "groq") and kr:
        return GroqBrain(kr, km, temp, brand, persona)
    if want == "gemini" and not gk:
        raise RuntimeError("provider=gemini لكن GEMINI_API_KEY غير مضبوط.")
    if want == "groq" and not kr:
        raise RuntimeError("provider=groq لكن GROQ_API_KEY غير مضبوط.")
    return MockBrain(brand)


if __name__ == "__main__":
    import yaml
    from pathlib import Path as _P
    cfg = yaml.safe_load(open(_P(__file__).parent / "config.yaml", encoding="utf-8"))
    brain = build_brain(cfg)
    v = brain.review(None, "", structural_findings=[
        {"code": "BLURRY_IMAGE", "severity": "major", "message_ar": "صورة ضبابية"}])
    print(json.dumps(v.to_dict(), ensure_ascii=False, indent=2))
