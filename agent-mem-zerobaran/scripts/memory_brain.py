#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agent-Mem-ZeroBaran — Layer 3: AI Memory Brain (Groq -> Gemini -> Mock)
====================================================================
Project #34 — ZeroBaran Innovation Fleet | © Baran Avisat
Email: Baranavisat@gmail.com | WhatsApp: 00905313263722

Two jobs:
 1. summarize(doc_text)  -> distilled long-term memory card (facts/preferences/
    decisions/todos) so agents store essence, not raw noise.
 2. answer(question, memories) -> grounded context block ready for injection
    into any agent's prompt window ("context budget" enforced).
All brains return strict JSON. MockBrain is deterministic and Arabic-aware so
CI never needs an API key.
"""
from __future__ import annotations
import json
import os
import re
import urllib.request
from typing import List, Dict, Any


def _extract_json(txt: str) -> Dict[str, Any]:
    m = re.search(r"\{.*\}", txt, re.S)
    if not m:
        raise ValueError("no json")
    return json.loads(m.group(0))


SYSTEM_SUMMARY = """أنت محرك ذاكرة استراتيجية لوكلاء الذكاء الاصطناعي.
من النص الخام استخرج بطاقة ذاكرة JSON صارمة بالأحقية التالية فقط:
{"summary": "ملخص كثيف <=80 كلمة",
 "facts": ["حقيقة/رقم/اسم مهم"],
 "preferences": ["تفضيلات المستخدم/المشروع"],
 "decisions": ["قرارات متخذة مع سبب مختصر"],
 "todos": ["مهام معلّقة"],
 "entities": ["أسماء مشاريع/أشخاص/منتجات"],
 "tags": ["وسوم بحث قصيرة"]}
لا تضيف أي نص خارج JSON."""

SYSTEM_ANSWER = """أنت طبقة استرجاع ذكي. Given the retrieved memory snippets,
produce STRICT JSON: {"answer_summary": "direct grounded answer <=60 words",
"cited_chunk_ids": ["ids used"], "confidence": 0..1,
"context_block": "the minimal fused text to inject into the agent prompt"}.
Never invent facts absent from snippets. English or Arabic per question."""


class GroqBrain:
    name = "groq-llama-3.3-70b"

    def __init__(self, api_key: str):
        self.key = api_key

    def _chat(self, system: str, user: str) -> str:
        req = urllib.request.Request(
            "https://api.groq.com/openai/v1/chat/completions",
            data=json.dumps({"model": os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile"),
                             "temperature": 0.2, "max_tokens": 900,
                             "messages": [{"role": "system", "content": system},
                                          {"role": "user", "content": user}]}).encode(),
            headers={"Authorization": f"Bearer {self.key}",
                     "Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=45) as r:
            return json.loads(r.read().decode())["choices"][0]["message"]["content"]

    def summarize(self, text: str) -> Dict[str, Any]:
        return _extract_json(self._chat(SYSTEM_SUMMARY, text[:6000]))

    def answer(self, q: str, mems: List[Dict[str, Any]]) -> Dict[str, Any]:
        ctx = "\n---\n".join(f"[{m['chunk_id']}] {m['text'][:500]}" for m in mems)
        return _extract_json(self._chat(SYSTEM_ANSWER, f"Q: {q}\n\nSNIPPETS:\n{ctx}"))


class GeminiBrain(GroqBrain):
    name = "gemini-1.5-flash"

    def __init__(self, api_key: str):
        self.key = api_key

    def _chat(self, system: str, user: str) -> str:
        model = os.environ.get("GEMINI_MODEL", "gemini-1.5-flash")
        url = (f"https://generativelanguage.googleapis.com/v1beta/models/"
               f"{model}:generate?key={self.key}")
        req = urllib.request.Request(url, data=json.dumps({
            "system_instruction": {"parts": [{"text": system}]},
            "contents": [{"parts": [{"text": user}]}],
            "generationConfig": {"temperature": 0.2}}).encode(),
            headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=45) as r:
            d = json.loads(r.read().decode())
        return d["candidates"][0]["content"]["parts"][0]["text"]


class MockBrain:
    """Deterministic offline brain: TF keyword extraction + naive sentence
    fusion. Good enough to prove every contract without any API key."""
    name = "mock-local-brain"
    STOP = set("the a an of and or to in is are was for on with by من إلى في على أن هذا هذه that this with".split())

    def _kw(self, text: str, k: int = 8) -> List[str]:
        words = re.findall(r"[\w\u0600-\u06FF]{3,}", text.lower())
        freq: Dict[str, int] = {}
        for w in words:
            if w not in self.STOP:
                freq[w] = freq.get(w, 0) + 1
        return [w for w, _ in sorted(freq.items(), key=lambda x: -x[1])[:k]]

    def summarize(self, text: str) -> Dict[str, Any]:
        sents = re.split(r"(?<=[.!?\n])\s+", text.strip())
        core = [s.strip() for s in sents if len(s) > 30][:5]
        nums = re.findall(r"\$?\d[\d.,]*%?", text)[:10]
        return {"summary": " ".join(core)[:400] or text[:200],
                "facts": [n for n in nums if n],
                "preferences": [], "decisions": core[:2], "todos": [],
                "entities": self._kw(text, 5), "tags": self._kw(text, 8)}

    def answer(self, q: str, mems: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not mems:
            return {"answer_summary": "لا توجد ذاكرة محفوظة بعد لهذه السؤال.",
                    "cited_chunk_ids": [], "confidence": 0.0, "context_block": ""}
        qkw = set(self._kw(q, 10))
        best = max(mems, key=lambda m: len(qkw & set(self._kw(m["text"], 20))))
        top3 = mems[:3]
        return {"answer_summary": best["text"][:300],
                "cited_chunk_ids": [m["chunk_id"] for m in top3],
                "confidence": round(min(0.95, 0.5 + 0.15 * len(top3)), 2),
                "context_block": "\n---\n".join(m["text"][:400] for m in top3)}


class MemoryBrainRouter:
    def __init__(self):
        self.brain = None
        if os.environ.get("GROQ_API_KEY"):
            try:
                b = GroqBrain(os.environ["GROQ_API_KEY"])
                b.summarize("ping test"); self.brain = b; return
            except Exception:
                pass
        if os.environ.get("GEMINI_API_KEY"):
            try:
                b = GeminiBrain(os.environ["GEMINI_API_KEY"])
                b.summarize("ping test"); self.brain = b; return
            except Exception:
                pass
        self.brain = MockBrain()

    @property
    def provider(self) -> str:
        return self.brain.name

    def summarize(self, text: str) -> Dict[str, Any]:
        try:
            return self.brain.summarize(text)
        except Exception:
            self.brain = MockBrain()
            return self.brain.summarize(text)

    def answer(self, q: str, mems: List[Dict[str, Any]]) -> Dict[str, Any]:
        try:
            return self.brain.answer(q, mems)
        except Exception:
            self.brain = MockBrain()
            return self.brain.answer(q, mems)


if __name__ == "__main__":
    br = MemoryBrainRouter()
    print(br.provider, "->", list(br.summarize("Budget is $0. Client wants free radar.")["facts"]))
