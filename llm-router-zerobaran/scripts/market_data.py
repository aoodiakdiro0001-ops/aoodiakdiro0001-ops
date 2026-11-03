#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LLM-Router-ZeroBaran — Project #37 | Layer 1a: Free Market Data Feeds
Author : Baran Avisat  <Baranavisat@gmail.com>  WhatsApp: 00905313263722
Copyright (c) 2026 Baran Avisat — ZeroBaran Studio. MIT License.
Sources (all free): Yahoo Finance chart API -> Stooq CSV -> Binance klines -> deterministic demo.
Never raises: returns (candles, source_used). Cached per symbol in state/cache.
"""
from __future__ import annotations
import json, os, time, random, hashlib
from typing import List, Dict, Tuple

import requests

STATE_DIR = os.environ.get("LRZ_STATE", os.path.join(os.path.dirname(__file__), "..", "state"))
UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 LLM-Router-ZeroBaran/1.0"}


def _cache_path(symbol: str, tf: str) -> str:
    safe = hashlib.sha1(f"{symbol}|{tf}".encode()).hexdigest()[:16]
    return os.path.join(STATE_DIR, "cache", f"{safe}.json")


def _load_cache(symbol: str, tf: str, ttl: int = 900) -> List[Dict]:
    p = _cache_path(symbol, tf)
    try:
        with open(p) as f:
            obj = json.load(f)
        if time.time() - obj.get("ts", 0) < ttl:
            return obj.get("candles", [])
    except Exception:
        pass
    return []


def _save_cache(symbol: str, tf: str, candles: List[Dict]) -> None:
    p = _cache_path(symbol, tf)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    try:
        with open(p, "w") as f:
            json.dump({"ts": time.time(), "candles": candles}, f)
    except Exception:
        pass


def yahoo_chart(symbol: str, interval: str = "1d", range_: str = "3mo") -> List[Dict]:
    url = (f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
           f"?interval={interval}&range={range_}")
    r = requests.get(url, headers=UA, timeout=15)
    r.raise_for_status()
    j = r.json()
    res = j["chart"]["result"][0]
    ts = res.get("timestamp", [])
    q = res["indicators"]["quote"][0]
    out = []
    for i, t in enumerate(ts):
        c = q["close"][i]
        if c is None:
            continue
        out.append({"t": t, "open": q["open"][i] or c, "high": q["high"][i] or c,
                    "low": q["low"][i] or c, "close": c,
                    "volume": q["volume"][i] or 0})
    if len(out) < 5:
        raise ValueError("yahoo: too few bars")
    return out


def stooq_csv(symbol: str, tf: str = "d") -> List[Dict]:
    sym = symbol.lower().replace("-", ".")
    if "." not in sym:
        sym += ".us"
    url = f"https://stooq.com/q/d/l/?s={sym}&i={tf}"
    r = requests.get(url, headers=UA, timeout=15)
    r.raise_for_status()
    lines = r.text.strip().splitlines()
    if len(lines) < 6 or "Date" not in lines[0]:
        raise ValueError("stooq: no data")
    out = []
    for ln in lines[1:]:
        parts = ln.split(",")
        if len(parts) < 5:
            continue
        try:
            d = int(time.mktime(time.strptime(parts[0], "%Y-%m-%d")))
            out.append({"t": d, "open": float(parts[1]), "high": float(parts[3]),
                        "low": float(parts[4]), "close": float(parts[2]),
                        "volume": float(parts[5]) if len(parts) > 5 else 0})
        except Exception:
            continue
    if len(out) < 5:
        raise ValueError("stooq: parse failed")
    return out


def binance_klines(symbol: str, interval: str = "1d", limit: int = 200) -> List[Dict]:
    pair = symbol.upper().replace("/", "").replace("-USDT", "USDT")
    if not any(pair.endswith(s) for s in ("USDT", "BUSD", "USDC", "BTC", "ETH")):
        pair += "USDT"
    url = f"https://api.binance.com/api/v3/klines?symbol={pair}&interval={interval}&limit={limit}"
    r = requests.get(url, headers=UA, timeout=15)
    r.raise_for_status()
    rows = r.json()
    out = [{"t": x[0] // 1000, "open": float(x[1]), "high": float(x[2]),
            "low": float(x[3]), "close": float(x[4]), "volume": float(x[5])} for x in rows]
    if len(out) < 5:
        raise ValueError("binance: too few bars")
    return out


def demo_candles(symbol: str, n: int = 120) -> List[Dict]:
    """Deterministic seeded walk — CI/dev fallback so the pipeline always runs."""
    seed = int(hashlib.sha1(symbol.encode()).hexdigest(), 16) % (2 ** 31)
    rnd = random.Random(seed)
    px = 50 + (seed % 400)
    now = int(time.time())
    out = []
    drift = rnd.uniform(-0.001, 0.002)
    for i in range(n):
        px *= (1 + rnd.gauss(drift, 0.018))
        o = px * (1 + rnd.gauss(0, 0.004)); c = px
        h = max(o, c) * (1 + abs(rnd.gauss(0, 0.005))); l = min(o, c) * (1 - abs(rnd.gauss(0, 0.005)))
        out.append({"t": now - (n - i) * 86400, "open": round(o, 4), "high": round(h, 4),
                    "low": round(l, 4), "close": round(c, 4), "volume": rnd.randint(int(1e5), int(9e5))})
    return out


def fetch_candles(symbol: str, timeframe: str = "1d", force_demo: bool = False) -> Tuple[List[Dict], str]:
    cached = _load_cache(symbol, timeframe)
    if cached and not force_demo:
        return cached, "cache"
    if force_demo:
        cs = demo_candles(symbol)
        return cs, "demo"
    if ":" in symbol or symbol.upper().endswith(("USDT", "BUSD")):
        attempts = [("binance", lambda: binance_klines(symbol)), ("yahoo", lambda: yahoo_chart(symbol))]
    else:
        attempts = [("yahoo", lambda: yahoo_chart(symbol)), ("stooq", lambda: stooq_csv(symbol))]
    for name, fn in attempts:
        try:
            cs = fn()
            _save_cache(symbol, timeframe, cs)
            return cs, name
        except Exception as e:
            print(f"[market_data] {name} failed for {symbol}: {type(e).__name__}: {e}")
    return demo_candles(symbol), "demo_fallback"


if __name__ == "__main__":
    for s in ["AAPL", "BTCUSDT"]:
        cs, src = fetch_candles(s)
        print(s, "->", src, len(cs), "bars, last close:", cs[-1]["close"])
