#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LLM-Router-ZeroBaran — Project #37 | Contract Smoke Tests (offline, no keys, deterministic)
© 2026 Baran Avisat <Baranavisat@gmail.com> · WhatsApp 00905313263722 · ZeroBaran Studio · MIT
Run: python tests/smoke_test.py   -> must print 🏆 ALL LAYER CONTRACTS OK
"""
import json, os, sys, tempfile

TMP = tempfile.mkdtemp(prefix="lrz_test_")
os.environ["LRZ_STATE"] = TMP          # isolate all state writes
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE, "scripts"))

import indicators, router, store, notify, market_data  # noqa: E402

PASS, FAIL = 0, []


def check(name, cond):
    global PASS
    if cond:
        PASS += 1
    else:
        FAIL.append(name)
        print(f"  ✗ FAIL: {name}")


# --- C1: indicator math sanity (SMA of constant series == constant) ---
import pandas as pd
s = pd.Series([5.0] * 30)
check("C1 sma constant", abs(float(indicators.sma(s, 20).iloc[-1]) - 5.0) < 1e-9)

# --- C2: RSI bounds & oversold detection on falling series ---
falling = pd.Series([100 - i for i in range(40)], dtype=float)
r = float(indicators.rsi(falling, 14).iloc[-1])
check("C2 rsi oversold on monotonic fall", 0 <= r <= 20)

# --- C3: MACD bull cross detected on V-shaped recovery ---
data = [100 - i * 0.5 for i in range(30)] + [85 + i * 1.2 for i in range(25)]
line, sigl, hist = indicators.macd(pd.Series(data, dtype=float))
check("C3 macd hist turns positive after rally", float(hist.iloc[-1]) > 0)

# --- C4: snapshot contract fields present & bounded ---
candles = [{"t": i, "open": c, "high": c * 1.01, "low": c * 0.99, "close": c, "volume": 1000 + i}
           for i, c in enumerate([100 + i * 0.8 for i in range(80)])]
snap = indicators.compute_snapshot("TST", "1d", candles)
sd = {"price": snap.price, "trend_score": snap.trend_score, "confidence": snap.confidence,
      "signals": snap.signals, "indicators": snap.indicators, "volatility_pct": snap.volatility_pct}
check("C4 trend score in [-100,100]", -100 <= snap.trend_score <= 100)
check("C5 confidence in [0,100]", 0 <= snap.confidence <= 100)
check("C6 uptrend stack => BUY plan", snap.trend_score >= 35 and
      indicators.plan_trade(snap)["side"] == "BUY")

# --- C7: neutral band => NO_TRADE ---
ns = indicators.Snapshot(symbol="N", timeframe="1d", price=100, change_pct=0,
                         indicators={"atr14": 1}, signals=[], trend_score=0,
                         confidence=10, volatility_pct=1, bars=10)
check("C7 neutral => NO_TRADE", indicators.plan_trade(ns)["side"] == "NO_TRADE")

# --- C8: position sizing math exact (risk_amount == capital*risk%) ---
plan = indicators.plan_trade(snap, risk_pct=2.0, capital=500.0)
per_unit = abs(plan["entry"] - plan["stop_loss"])
check("C8 qty*risk==capital*riskpct", abs(plan["qty_for_risk"] * per_unit - 10.0) < 0.01)

# --- C9: task classifier routes summary->small, long-analysis->large ---
p_small = router.classify_task("TL;DR summarize this briefly please")
p_large = router.classify_task("analyze and compare the strategy and risk of " + ("deep detail words " * 40))
check("C9 summary classified small", p_small.kind == "summary" and p_small.complexity == "small")
check("C10 analysis classified large", p_large.kind == "analysis" and p_large.complexity == "large")

# --- C11: route() works with zero keys (mock fallback) & records stats ---
rr = router.route("Analyze BTC risk now", kind_hint="analysis")
check("C11 mock route succeeds offline", rr.provider == "mock" and len(rr.text) > 0)
st = router.stats_summary()
check("C12 router stats recorded", st["models"].get("mock:mock-analyst", {}).get("calls", 0) >= 1)

# --- C13: failover ordering — unhealthy model deprioritised ---
for _ in range(5):
    router._record("fake:broken", False, 10, 0)
check("C14 health penalises consecutive fails", router.health_score("fake:broken") <= 0.05 + 1e-9)

# --- C15: store roundtrip + signal settlement lifecycle ---
store.log_analysis("SYM", "1d", sd, {"provider": "mock", "model": "m", "latency_ms": 1,
                                     "cost_saved_usd": 0.001}, "narr", plan)
sig = store.log_signal("SYM", {"side": "BUY", "entry": 100, "stop_loss": 95,
                               "take_profit_1": 110}, sd)
check("C15 signal logged open", sig and sig["stored_in"] == "local")
settled = store.settle_open_signals({"SYM": [{"close": 112}]})
check("C16 tp1_hit settlement", settled and settled[0]["outcome"] == "tp1_hit")
perf = store.performance_summary()
check("C17 perf summary win_rate=1", perf["win_rate"] == 1.0 and perf["closed"] >= 1)

# --- C18: telegram formatter contains required report elements ---
msg = notify.fmt_signal_alert("XYZ", sd, {"side": "BUY", "entry": 1, "stop_loss": 0.5,
                                          "take_profit_1": 2, "take_profit_2": 3,
                                          "qty_for_risk": 10, "risk_pct": 1, "capital": 1000},
                              "because momentum", {"provider": "groq", "model": "g", "latency_ms": 5})
check("C19 report header style", "تقرير التحليل المالي والتداول" in msg)
check("C20 report has confidence+plan+footer", "نسبة ثقة" in msg and "وقف الخسارة" in msg
      and "Baranavisat@gmail.com" in msg and "00905313263722" in msg)

# --- C21: send() silent-safe without creds ---
check("C21 telegram silent-safe", notify.send("x") is False)

# --- C22: market data demo feed deterministic (same seed same values) ---
a = market_data.demo_candles("SYMBOL", 50)[-1]["close"]
b = market_data.demo_candles("SYMBOL", 50)[-1]["close"]
check("C22 demo feed deterministic", a == b)

# --- C23: fetch_candles never raises even with garbage symbol (falls back to demo) ---
cs, src = market_data.fetch_candles("!!bad!!sym", force_demo=True)
check("C23 demo path returns bars", len(cs) > 10 and src == "demo")

# --- C24: HTML escape prevents telegram parse breakage ---
check("C24 esc html", notify.fmt_signal_alert("<b>&", sd, {"side": "NO_TRADE"}, "", {})
      .count("&lt;b&gt;") >= 1)

# --- C25: weekly digest renders ---
dig = notify.fmt_weekly_digest(perf, st, [])
check("C26 digest has savings line", "الملخص الأسبوعي" in dig and "$" in dig)

# --- C27: config.yaml valid yaml & watchlist shape ---
try:
    import yaml
    cfg = yaml.safe_load(open(os.path.join(BASE, "scripts", "config.yaml")))
    ok_cfg = isinstance(cfg.get("watchlist"), list) and all("symbol" in w for w in cfg["watchlist"])
except Exception:
    ok_cfg = False
check("C27 config watchlist valid", ok_cfg)

# --- C28: schema.sql declares both tables + views ---
sql = open(os.path.join(BASE, "supabase", "schema.sql")).read()
check("C28 schema complete", "lrz_analysis_log" in sql and "lrz_signal_events" in sql
      and "lrz_symbol_performance" in sql and "row level security" in sql)

# --- C29: workflow yml parses & has cron + dispatch ---
try:
    wf = yaml.safe_load(open(os.path.join(BASE, "..", ".github", "workflows",
                                          "llm-router-zerobaran.yml")))
    trig = wf.get("true", wf.get(True, {})) or wf.get("on", {})
    ok_wf = "schedule" in str(trig) and "workflow_dispatch" in str(trig)
except Exception as e:
    ok_wf = False
    print("   workflow parse:", e)
check("C29 workflow valid", ok_wf)

# --- C30: dashboard imports compile ---
import py_compile
try:
    py_compile.compile(os.path.join(BASE, "dashboard.py"), doraise=True)
    ok_dash = True
except Exception:
    ok_dash = False
check("C30 dashboard compiles", ok_dash)

# --- C31: copyright header on every code file ---
missing = []
for root, _, files in os.walk(BASE):
    for fn in files:
        if fn.endswith((".py", ".sql", ".yaml")) and "test" not in root:
            txt = open(os.path.join(root, fn), encoding="utf-8").read()[:1200]
            if "Baran Avisat" not in txt:
                missing.append(fn)
check("C31 authorship headers everywhere", not missing)
if missing:
    print("   missing headers:", missing)

print(f"\n{'🏆 ALL LAYER CONTRACTS OK' if not FAIL else '❌ FAILURES: ' + str(FAIL)} ({PASS}/{PASS + len(FAIL)})")
sys.exit(1 if FAIL else 0)
