#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LLM-Router-ZeroBaran — Project #37 | Layer 2: Intelligent Model Router (LiteLLM-style, zero-cost)
Author : Baran Avisat  <Baranavisat@gmail.com>  WhatsApp: 00905313263722
Copyright (c) 2026 Baran Avisat — ZeroBaran Studio. MIT License.
Classifies every task (complexity/cost/tokens) -> routes to cheapest capable FREE provider:
Ollama(local, $0) -> Groq (fast free tier) -> Gemini (free tier).
Tracks per-model stats (latency/success/cost-saved) in state/router_stats.json — self-tuning health score.
Failover built-in; MockBrain keeps the whole pipeline runnable with ZERO keys (CI/dev).
"""
from __future__ import annotations
import json, os, re, time, urllib.request
from dataclasses import dataclass, field
from typing import Dict, List, Optional

STATE_DIR = os.environ.get("LRZ_STATE", os.path.join(os.path.dirname(__file__), "..", "state"))
STATS_FILE = os.path.join(STATE_DIR, "router_stats.json")

# USD per 1M tokens of comparable PAID providers => what routing to free tiers SAVES you.
PAID_EQUIV = {"small": 0.30, "medium": 1.25, "large": 3.00}


@dataclass
class TaskProfile:
    kind: str            # qa | summary | analysis | synthesis
    complexity: str      # small | medium | large
    est_tokens: int
    needs_reasoning: bool

    @property
    def weight(self) -> float:
        return PAID_EQUIV[self.complexity] * (self.est_tokens / 1_000_000)


def classify_task(prompt: str, kind_hint: Optional[str] = None) -> TaskProfile:
    words = len(re.findall(r"\w+", prompt))
    est_tokens = max(64, int(words * 1.4))
    reasoning_words = ("why", "compare", "strategy", "risk", "analyz", "تحليل", "لماذا",
                       "قارن", "استراتيجية", "مخاطر", "تقييم", "خطة")
    needs = any(w in prompt.lower() for w in reasoning_words)
    if kind_hint:
        kind = kind_hint
    elif any(w in prompt.lower() for w in ("tl;dr", "summar", "ملخص", "لخص", "ترجم", "translate")):
        kind = "summary"
    elif needs:
        kind = "analysis"
    elif words > 400:
        kind = "synthesis"
    else:
        kind = "qa"
    if kind in ("analysis", "synthesis") or words > 300:
        # long reasoning-heavy prompts => big model; short ones stay on cheap tiers
        complexity = "large" if (needs and words > 40) else "medium"
    elif kind == "summary":
        complexity = "small"
    else:
        complexity = "small" if words < 60 else "medium"
    return TaskProfile(kind, complexity, est_tokens, needs)


def _load_stats() -> Dict:
    try:
        with open(STATS_FILE) as f:
            return json.load(f)
    except Exception:
        return {}


def _save_stats(s: Dict) -> None:
    os.makedirs(STATE_DIR, exist_ok=True)
    try:
        with open(STATS_FILE, "w") as f:
            json.dump(s, f, indent=1)
    except Exception:
        pass


def _record(model: str, ok: bool, latency_ms: float, cost_saved_usd: float) -> None:
    s = _load_stats()
    m = s.setdefault(model, {"calls": 0, "ok": 0, "total_latency_ms": 0.0,
                             "cost_saved_usd": 0.0, "consec_fail": 0})
    m["calls"] += 1
    m["ok"] += 1 if ok else 0
    m["total_latency_ms"] += latency_ms
    m["cost_saved_usd"] += cost_saved_usd if ok else 0.0
    m["consec_fail"] = 0 if ok else m["consec_fail"] + 1
    s["_saved_total_usd"] = s.get("_saved_total_usd", 0.0) + (cost_saved_usd if ok else 0.0)
    _save_stats(s)


def health_score(model: str) -> float:
    """0..1 — penalise recent consecutive failures & slow avg latency (self-tuning router)."""
    m = _load_stats().get(model)
    if not m or m["calls"] == 0:
        return 1.0
    sr = m["ok"] / m["calls"]
    lat = m["total_latency_ms"] / m["calls"]
    lat_pen = max(0.0, min(0.4, (lat - 2000) / 20000))
    cb = 0.0 if m["consec_fail"] < 3 else 0.5
    return max(0.05, sr * (1 - lat_pen) - cb)


def _token_ledger(provider: str, model: str, ptok: int, ctok: int) -> None:
    os.makedirs(STATE_DIR, exist_ok=True)
    p = os.path.join(STATE_DIR, "token_ledger.jsonl")
    try:
        with open(p, "a") as f:
            f.write(json.dumps({"ts": time.time(), "provider": provider, "model": model,
                                "prompt_tokens": ptok, "completion_tokens": ctok}) + "\n")
    except Exception:
        pass


class Provider:
    name = ""
    models_capable: Dict[str, List[str]] = {}  # complexity -> model ids

    def can(self, prof: TaskProfile) -> bool:
        return prof.complexity in self.models_capable

    def available(self) -> bool:
        return False

    def generate(self, model: str, prompt: str, system: str) -> str:
        raise NotImplementedError


class OllamaProvider(Provider):
    """Local free & private: runs Kronos-class open models on your own hardware."""
    name = "ollama"
    models_capable = {"small": ["qwen2.5:1.5b"], "medium": ["qwen2.5:3b"]}

    def available(self) -> bool:
        try:
            urllib.request.urlopen("http://localhost:11434/api/tags", timeout=1.5)
            return True
        except Exception:
            return False

    def generate(self, model: str, prompt: str, system: str) -> str:
        body = json.dumps({"model": model, "prompt": prompt, "system": system,
                           "stream": False}).encode()
        req = urllib.request.Request("http://localhost:11434/api/generate", data=body,
                                     headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=120) as r:
            return json.loads(r.read().decode())["response"].strip()


class GroqProvider(Provider):
    name = "groq"
    models_capable = {"small": ["openai/gemma-3-27b-it"], "medium": ["openai/gemma-3-27b-it"],
                      "large": ["llama-3.3-70b-versatile"]}
    BASE = "https://api.groq.com/openai/v1/chat/completions"

    def available(self) -> bool:
        return bool(os.environ.get("GROQ_API_KEY"))

    def generate(self, model: str, prompt: str, system: str) -> str:
        body = json.dumps({"model": model, "temperature": 0.2, "max_tokens": 1024,
                           "messages": [{"role": "system", "content": system},
                                        {"role": "user", "content": prompt}]}).encode()
        req = urllib.request.Request(self.BASE, data=body, headers={
            "Authorization": f"Bearer {os.environ['GROQ_API_KEY']}",
            "Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=60) as r:
            j = json.loads(r.read().decode())
        txt = j["choices"][0]["message"]["content"].strip()
        u = j.get("usage", {})
        if u:
            _token_ledger(self.name, model, u.get("prompt_tokens", 0), u.get("completion_tokens", 0))
        return txt


class GeminiProvider(Provider):
    name = "gemini"
    models_capable = {"small": ["gemini-2.0-flash"], "medium": ["gemini-2.0-flash"],
                      "large": ["gemini-2.5-pro"]}
    BASE = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"

    def available(self) -> bool:
        return bool(os.environ.get("GEMINI_API_KEY"))

    def generate(self, model: str, prompt: str, system: str) -> str:
        url = self.BASE.format(model=model) + f"?key={os.environ['GEMINI_API_KEY']}"
        body = json.dumps({"system_instruction": {"parts": [{"text": system}]},
                           "contents": [{"parts": [{"text": prompt}]}],
                           "generationConfig": {"temperature": 0.2}}).encode()
        req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=60) as r:
            j = json.loads(r.read().decode())
        txt = j["candidates"][0]["content"]["parts"][0]["text"].strip()
        u = j.get("usageMetadata", {})
        if u:
            _token_ledger(self.name, model, u.get("promptTokenCount", 0),
                          u.get("candidatesTokenCount", 0))
        return txt


class MockBrain(Provider):
    """Deterministic offline brain so CI/dev works with ZERO keys (honest about being mock)."""
    name = "mock"
    models_capable = {"small": ["mock-analyst"], "medium": ["mock-analyst"], "large": ["mock-analyst"]}

    def available(self) -> bool:
        return True

    def generate(self, model: str, prompt: str, system: str) -> str:
        low = prompt.lower()
        if "sentiment" in low or "مشاعر" in prompt:
            neg = sum(low.count(w) for w in ("crash", "loss", "drop", "fell", "انخفض", "خسائر"))
            pos = sum(low.count(w) for w in ("rally", "gain", "surge", "rose", "ارتفاع", "مكاسب"))
            tone = "bullish" if pos > neg else ("bearish" if neg > pos else "neutral")
            return json.dumps({"tone": tone, "confidence": 60 + min(abs(pos - neg) * 5, 30),
                               "drivers": ["momentum", "volume"], "note": "mock-analysis"},
                              ensure_ascii=False)
        return ("[MOCK-ROUTED] ملخص تحليلي تجريبي (يعمل دون مفاتيح API): "
                + prompt[:180].replace("\n", " ") + " …")


PROVIDERS: List[Provider] = [OllamaProvider(), GroqProvider(), GeminiProvider(), MockBrain()]


@dataclass
class RouteResult:
    text: str
    provider: str
    model: str
    latency_ms: float
    cost_saved_usd: float
    task: TaskProfile
    attempts: List[str] = field(default_factory=list)


def route(prompt: str, system: str = "You are a concise quantitative financial analyst.",
          kind_hint: Optional[str] = None) -> RouteResult:
    prof = classify_task(prompt, kind_hint)
    saved = round(prof.weight, 6)
    cands = []
    for pv in PROVIDERS:
        if pv.can(prof) and pv.available():
            model = pv.models_capable[prof.complexity][0]
            cands.append((health_score(f"{pv.name}:{model}"), PROVIDERS.index(pv), pv, model))
    # healthy first; among equals keep cheapest-first provider order
    cands.sort(key=lambda x: (-x[0], x[1]))
    tried = []
    for _, _, pv, model in cands:
        key = f"{pv.name}:{model}"
        tried.append(key)
        t0 = time.time()
        try:
            txt = pv.generate(model, prompt, system)
            dt = (time.time() - t0) * 1000
            _record(key, True, dt, saved)
            return RouteResult(txt, pv.name, model, round(dt, 1), saved, prof, tried)
        except Exception as e:
            dt = (time.time() - t0) * 1000
            _record(key, False, dt, 0.0)
            print(f"[router] {key} failed ({type(e).__name__}); failover…")
    raise RuntimeError("router: no provider succeeded")


def stats_summary() -> Dict:
    s = _load_stats()
    models = {k: {"calls": v["calls"], "success_rate": round(v["ok"] / max(v["calls"], 1), 3),
                  "avg_latency_ms": round(v["total_latency_ms"] / max(v["calls"], 1), 1),
                  "cost_saved_usd": round(v["cost_saved_usd"], 6)}
              for k, v in s.items() if isinstance(v, dict)}
    return {"models": models, "total_saved_usd": round(s.get("_saved_total_usd", 0.0), 6)}


if __name__ == "__main__":
    r = route("Analyze BTC: price rallied 5% with rising OBV and MACD bull cross. Why? Give risk view.")
    print(json.dumps({"provider": r.provider, "model": r.model, "task": r.task.kind,
                      "complexity": r.task.complexity, "latency_ms": r.latency_ms,
                      "cost_saved_usd": r.cost_saved_usd, "attempts": r.attempts,
                      "text_head": r.text[:120]}, ensure_ascii=False, indent=1))
    print(json.dumps(stats_summary(), ensure_ascii=False))
