# -*- coding: utf-8 -*-
"""
Voice-ZeroBaran — Project #36 | ZeroBaran Studio
Copyright (c) 2026 Baran Avisat. Support: Baranavisat@gmail.com | WhatsApp 00905313263722

Layer 2 (part D) — AI VOICE BRAIN (Gemini / Groq free tiers)
Writes & polishes narration scripts for voiceover: SSML-ish pacing marks,
tone directives, per-scene breakdowns. Deterministic MockBrain keeps CI green
with zero keys.
"""
from __future__ import annotations

import json
import re
import urllib.error
import urllib.request
from typing import Optional

from .config import CFG

SYSTEM_PROMPT = """You are the Voice Director of Voice-ZeroBaran studio.
Given a topic/brief, produce a JSON object with EXACTLY these keys:
{
 "title": short Arabic/English title matching brief language,
 "script": narration text optimized for TTS (short sentences, no emoji, spelled-out numbers),
 "voice": one of ["vzb-morgan","vzb-violet","vzb-merlin","vzb-damien"],
 "speed": float 0.8..1.3,
 "preset": one of ["broadcast","podcast","clean","voiceover"],
 "scenes": [{"i":int,"text":str}],
 "tags": [str]
}
Return ONLY valid JSON."""


def _http_json(url: str, payload: dict, headers: dict, timeout: int = 45) -> dict:
    req = urllib.request.Request(url, data=json.dumps(payload).encode(),
                                headers={**headers, "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode())


class GroqBrain:
    name = "groq"

    def generate(self, brief: str) -> dict:
        d = _http_json(
            "https://api.groq.com/openai/v1/chat/completions",
            {"model": "llama-3.3-70b-versatile", "temperature": 0.4,
             "response_format": {"type": "json_object"},
             "messages": [{"role": "system", "content": SYSTEM_PROMPT},
                          {"role": "user", "content": brief}]},
            {"Authorization": f"Bearer {CFG.groq_api_key}"})
        return json.loads(d["choices"][0]["message"]["content"])


class GeminiBrain:
    name = "gemini"

    def generate(self, brief: str) -> dict:
        d = _http_json(
            f"https://generativelanguage.googleapis.com/v1beta/models/"
            f"gemini-2.0-flash:generateContent?key={CFG.gemini_api_key}",
            {"systemInstruction": {"parts": [{"text": SYSTEM_PROMPT}]},
             "contents": [{"parts": [{"text": brief}]}],
             "generationConfig": {"temperature": 0.4, "responseMimeType": "application/json"}},
            {})
        txt = d["candidates"][0]["content"]["parts"][0]["text"]
        m = re.search(r"\{.*\}", txt, re.S)
        return json.loads(m.group(0)) if m else {"raw": txt}


class MockBrain:
    """Offline deterministic scriptwriter — keeps the pipeline 100% free/CI-safe."""
    name = "mock-local"

    def generate(self, brief: str) -> dict:
        b = brief.strip()
        lang = "ar" if re.search(r"[\u0600-\u06FF]", b) else "en"
        sents = [s.strip() for s in re.split(r"[.!?؟\n]+", b) if s.strip()] or [b or "Welcome."]
        if lang == "ar":
            script = " ".join(f"{s}." for s in sents[:6])
            title = (sents[0][:48] + ("…" if len(sents[0]) > 48 else "")) if sents else "نص آلي"
        else:
            script = " ".join(f"{s}." for s in sents[:6])
            title = (sents[0][:48]) if sents else "Auto Script"
        scenes = [{"i": i + 1, "text": t} for i, t in enumerate(sents[:6])]
        return {"title": title, "script": script, "voice": "vzb-morgan",
                "speed": 1.0, "preset": "voiceover", "scenes": scenes,
                "tags": ["auto", lang, "zerobaran"]}


def get_brain(prefer: Optional[str] = None):
    order = [prefer] if prefer else ["groq", "gemini"]
    for p in order:
        if p == "groq" and CFG.has_groq:
            return GroqBrain()
        if p == "gemini" and CFG.has_gemini:
            return GeminiBrain()
    return MockBrain()


def write_script(brief: str, prefer: Optional[str] = None) -> dict:
    brain = get_brain(prefer)
    try:
        out = brain.generate(brief)
        out["_brain"] = brain.name
    except (urllib.error.URLError, KeyError, json.JSONDecodeError, TimeoutError) as e:
        out = MockBrain().generate(brief)
        out["_brain"] = "mock-local"
        out["_fallback_reason"] = str(e)[:160]
    # contract guard
    out.setdefault("script", brief)
    out.setdefault("voice", CFG.default_voice)
    out.setdefault("speed", CFG.default_speed)
    out.setdefault("preset", "voiceover")
    return out


if __name__ == "__main__":
    print(json.dumps(write_script("قدم لمحة عن استوديو صوتي مجاني"), ensure_ascii=False)[:200])
