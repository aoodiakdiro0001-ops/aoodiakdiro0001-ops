#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LLM-Router-ZeroBaran — Project #37 | Layer 1b: Quant Indicator Engine (Pandas/NumPy)
Author : Baran Avisat  <Baranavisat@gmail.com>  WhatsApp: 00905313263722
Copyright (c) 2026 Baran Avisat — ZeroBaran Studio. MIT License.
Pure-python/pandas TA: SMA/EMA/RSI/MACD/Bollinger/ATR/OBV + trend score. No paid libs.
NOT financial advice — decision-support only.
"""
from __future__ import annotations
import math
from dataclasses import dataclass, field
from typing import List, Dict

import numpy as np
import pandas as pd


def sma(s: pd.Series, n: int) -> pd.Series:
    return s.rolling(n, min_periods=1).mean()


def ema(s: pd.Series, n: int) -> pd.Series:
    return s.ewm(span=n, adjust=False, min_periods=1).mean()


def rsi(close: pd.Series, n: int = 14) -> pd.Series:
    delta = close.diff()
    up = delta.clip(lower=0.0)
    dn = (-delta).clip(lower=0.0)
    ru = up.ewm(alpha=1 / n, adjust=False, min_periods=1).mean()
    rd = dn.ewm(alpha=1 / n, adjust=False, min_periods=1).mean()
    rs = ru / rd.replace(0.0, np.nan)
    out = 100 - (100 / (1 + rs))
    return out.fillna(50.0)


def macd(close: pd.Series, fast: int = 12, slow: int = 26, sig: int = 9):
    line = ema(close, fast) - ema(close, slow)
    signal = ema(line, sig)
    hist = line - signal
    return line, signal, hist


def bollinger(close: pd.Series, n: int = 20, k: float = 2.0):
    mid = sma(close, n)
    sd = close.rolling(n, min_periods=1).std(ddof=0).fillna(0.0)
    return mid + k * sd, mid, mid - k * sd


def atr(df: pd.DataFrame, n: int = 14) -> pd.Series:
    hl = df["high"] - df["low"]
    hc = (df["high"] - df["close"].shift(1)).abs()
    lc = (df["low"] - df["close"].shift(1)).abs()
    tr = pd.concat([hl, hc, lc], axis=1).max(axis=1)
    return tr.ewm(alpha=1 / n, adjust=False, min_periods=1).mean()


def obv(close: pd.Series, volume: pd.Series) -> pd.Series:
    direction = np.sign(close.diff()).fillna(0.0)
    return (direction * volume.fillna(0.0)).cumsum()


@dataclass
class Snapshot:
    symbol: str
    timeframe: str
    price: float
    change_pct: float
    indicators: Dict[str, float] = field(default_factory=dict)
    signals: List[str] = field(default_factory=list)
    trend_score: float = 0.0          # -100..100
    confidence: float = 0.0           # 0..100
    volatility_pct: float = 0.0       # ATR as % of price
    bars: int = 0


def compute_snapshot(symbol: str, timeframe: str, candles: List[Dict]) -> Snapshot:
    """candles: list of {t, open, high, low, close, volume} oldest->newest."""
    df = pd.DataFrame(candles)
    for col, default in (("open", 0.0), ("high", 0.0), ("low", 0.0), ("close", 0.0), ("volume", 0.0)):
        if col not in df.columns:
            df[col] = default
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(default)
    close = df["close"]
    n = len(df)
    price = float(close.iloc[-1])
    prev = float(close.iloc[-2]) if n >= 2 else price
    change_pct = ((price - prev) / prev * 100.0) if prev else 0.0

    ind: Dict[str, float] = {}
    sigs: List[str] = []
    score = 0.0

    if n >= 3:
        s20, s50 = sma(close, 20), sma(close, 50)
        e12 = ema(close, 12)
        r14 = rsi(close, 14)
        m_line, m_sig, m_hist = macd(close)
        u_b, mid_b, l_b = bollinger(close, 20)
        a14 = atr(df, 14)
        o_bv = obv(close, df["volume"])

        last = lambda s: float(s.iloc[-1])
        ind.update({"sma20": round(last(s20), 6), "sma50": round(last(s50), 6),
                    "ema12": round(last(e12), 6), "rsi14": round(last(r14), 3),
                    "macd": round(last(m_line), 6), "macd_signal": round(last(m_sig), 6),
                    "macd_hist": round(last(m_hist), 6), "bb_upper": round(last(u_b), 6),
                    "bb_lower": round(last(l_b), 6), "atr14": round(last(a14), 6),
                    "obv": round(last(o_bv), 3)})
        ind["volatility_pct"] = round(last(a14) / price * 100.0, 3) if price else 0.0

        # --- rule stack with weights ---
        if price > last(s20) > last(s50):
            score += 25; sigs.append("TREND_UP_MA_STACK")
        elif price < last(s20) < last(s50):
            score -= 25; sigs.append("TREND_DOWN_MA_STACK")
        if last(m_hist) > 0 and float(m_hist.iloc[-2]) <= 0:
            score += 20; sigs.append("MACD_BULL_CROSS")
        elif last(m_hist) < 0 and float(m_hist.iloc[-2]) >= 0:
            score -= 20; sigs.append("MACD_BEAR_CROSS")
        elif last(m_hist) > 0:
            score += 8; sigs.append("MACD_ABOVE_SIGNAL")
        else:
            score -= 8; sigs.append("MACD_BELOW_SIGNAL")
        rv = last(r14)
        if rv < 30:
            score += 15; sigs.append("RSI_OVERSOLD")
        elif rv > 70:
            score -= 15; sigs.append("RSI_OVERBOUGHT")
        if price <= last(l_b):
            score += 10; sigs.append("BB_LOWER_TOUCH")
        elif price >= last(u_b):
            score -= 10; sigs.append("BB_UPPER_TOUCH")
        if float(o_bv.iloc[-1]) > float(o_bv.iloc[-5]) if n >= 5 else False:
            score += 10; sigs.append("OBV_RISING")
        elif n >= 5 and float(o_bv.iloc[-1]) < float(o_bv.iloc[-5]):
            score -= 10; sigs.append("OBV_FALLING")
        if change_pct > 1.5:
            sigs.append("MOMENTUM_STRONG_UP")
        elif change_pct < -1.5:
            sigs.append("MOMENTUM_STRONG_DOWN")

    score = max(-100.0, min(100.0, score))
    # confidence grows with sample size & signal agreement
    agree = sum(1 for s in sigs if ("UP" in s or "BULL" in s or "OVERSOLD" in s) == (score >= 0) for s in sigs) if sigs else 0
    confidence = min(99.0, (n / 60.0) * 40.0 + (agree / max(len(sigs), 1)) * 60.0) if sigs else (n / 60.0) * 40.0

    return Snapshot(symbol=symbol, timeframe=timeframe, price=price,
                    change_pct=round(change_pct, 4), indicators=ind, signals=sigs,
                    trend_score=round(score, 2), confidence=round(confidence, 2),
                    volatility_pct=ind.get("volatility_pct", 0.0), bars=n)


def plan_trade(snap: Snapshot, risk_pct: float = 1.0, capital: float = 1000.0) -> Dict:
    """Deterministic entry/exit plan from quant snapshot (decision support, NOT advice)."""
    atr_val = snap.indicators.get("atr14", 0.0) or (snap.price * 0.01)
    if snap.trend_score >= 35:
        side = "BUY"
        entry = snap.price
        stop = entry - 1.5 * atr_val
        tp1, tp2 = entry + 1.5 * atr_val, entry + 3.0 * atr_val
    elif snap.trend_score <= -35:
        side = "SELL/AVOID"
        entry = snap.price
        stop = entry + 1.5 * atr_val
        tp1, tp2 = entry - 1.5 * atr_val, entry - 3.0 * atr_val
    else:
        return {"side": "NO_TRADE", "reason": "trend_score_within_neutral_band",
                "trend_score": snap.trend_score}
    risk_amount = capital * (risk_pct / 100.0)
    per_unit_risk = abs(entry - stop) or 1e-9
    qty = round(risk_amount / per_unit_risk, 6)
    rr1 = round(abs(tp1 - entry) / per_unit_risk, 2)
    return {"side": side, "entry": round(entry, 6), "stop_loss": round(stop, 6),
            "take_profit_1": round(tp1, 6), "take_profit_2": round(tp2, 6),
            "qty_for_risk": qty, "risk_amount": round(risk_amount, 4),
            "capital": capital, "risk_pct": risk_pct, "rr_tp1": rr1,
            "confidence": snap.confidence, "trend_score": snap.trend_score}


if __name__ == "__main__":
    import json, random
    random.seed(7)
    px, cs = 100.0, []
    for i in range(80):
        px *= (1 + random.gauss(0.0015, 0.01))
        o = px * (1 + random.gauss(0, 0.003)); c = px
        h = max(o, c) * 1.006; l = min(o, c) * 0.994
        cs.append({"t": i, "open": o, "high": h, "low": l, "close": c, "volume": random.randint(1000, 9000)})
    snap = compute_snapshot("DEMO", "1d", cs)
    print(json.dumps({"trend": snap.trend_score, "conf": snap.confidence,
                      "signals": snap.signals, "plan": plan_trade(snap)}, ensure_ascii=False, indent=1))
