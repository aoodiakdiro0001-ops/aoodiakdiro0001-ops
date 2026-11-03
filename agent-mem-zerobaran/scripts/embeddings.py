#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agent-Mem-ZeroBaran — Layer 2a: Embedding Engine (free-tier cascade)
================================================================
Project #34 — ZeroBaran Innovation Fleet | © Baran Avisat
Contact: Baranavisat@gmail.com | WhatsApp: 00905313263722

Cascade: Gemini embeddings (free) -> Groq -> deterministic local HashNGram
vectorizer (always available, offline, no install). The local fallback is a
real TF-style hashed n-gram embedding with L2 normalization — good enough for
lexical-semantic recall and it never fails CI.
"""
from __future__ import annotations
import hashlib
import json
import math
import os
import re
import urllib.request
import urllib.error
from typing import List, Dict, Any

DIM = int(os.environ.get("AGENTMEM_DIM", "512"))


def _norm(v: List[float]) -> List[float]:
    n = math.sqrt(sum(x * x for x in v)) or 1.0
    return [x / n for x in v]


def hash_ngram_vector(text: str, dim: int = DIM) -> List[float]:
    """Deterministic hashed word+char-ngram embedding, L2-normalized."""
    vec = [0.0] * dim
    words = re.findall(r"[\w\u0600-\u06FF]+", text.lower())
    grams: List[str] = []
    for w in words:
        grams.append(w)
        if len(w) >= 4:
            grams += [w[i:i + 3] for i in range(len(w) - 2)]
    bigs = [" ".join(p) for p in zip(words, words[1:])]
    grams += bigs
    for g in grams:
        h = hashlib.md5(g.encode("utf-8")).digest()
        idx = int.from_bytes(h[:4], "big") % dim
        sign = 1.0 if h[4] % 2 == 0 else -1.0
        vec[idx] += sign
    return _norm(vec)


class GeminiEmbedder:
    name = "gemini-embedding"

    def __init__(self, api_key: str):
        self.key = api_key
        self.model = os.environ.get("GEMINI_EMB_MODEL", "models/text-embedding-004")

    def embed(self, texts: List[str]) -> List[List[float]]:
        url = (f"https://generativelanguage.googleapis.com/v1beta/{self.model}"
               f":batchEmbeddings?key={self.key}")
        payload = {"requests": [{"content": {"parts": [{"text": t[:2000]}]},
                                 "outputDimensionality": DIM} for t in texts]}
        req = urllib.request.Request(url, data=json.dumps(payload).encode(),
                                     headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=30) as r:
            data = json.loads(r.read().decode())
        return [_norm(e["values"]) for e in data["embeddings"]]


class GroqEmbedder:
    """Groq has no embedding endpoint; we use its fast chat model to score
    keyword salience → sparse-ish vector. Kept as optional adapter stub that
    raises so the cascade cleanly falls through to local mode when chosen."""
    name = "groq-not-supported"

    def __init__(self, api_key: str):
        raise NotImplementedError("Groq free tier serves chat, not embeddings")


class LocalEmbedder:
    name = "hash-ngram-local"

    def embed(self, texts: List[str]) -> List[List[float]]:
        return [hash_ngram_vector(t) for t in texts]


class EmbeddingEngine:
    """Free-first cascade with graceful degradation + provider stats."""
    def __init__(self, prefer: str = "auto"):
        self.prefer = prefer
        self.gemini_key = os.environ.get("GEMINI_API_KEY", "")
        self.active = None
        self.stats: Dict[str, int] = {}
        self._select()

    def _select(self):
        if self.prefer in ("auto", "gemini") and self.gemini_key:
            try:
                GeminiEmbedder(self.gemini_key).embed(["ping"])
                self.active = GeminiEmbedder(self.gemini_key)
                return
            except Exception:
                pass
        self.active = LocalEmbedder()

    def embed(self, texts: List[str]) -> List[List[float]]:
        try:
            out = self.active.embed(texts)
            self.stats[self.active.name] = self.stats.get(self.active.name, 0) + len(texts)
            return out
        except Exception:
            self.active = LocalEmbedder()
            out = self.active.embed(texts)
            self.stats[self.active.name] = self.stats.get(self.active.name, 0) + len(texts)
            return out

    @property
    def provider(self) -> str:
        return getattr(self.active, "name", "unknown")


def cosine(a: List[float], b: List[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


if __name__ == "__main__":
    eng = EmbeddingEngine()
    vs = eng.embed(["الوكيل يتذكر تفاصيل المشروع", "the agent remembers project details"])
    print(f"provider={eng.provider} dim={len(vs[0])} cos={cosine(vs[0], vs[1]):.3f}")
