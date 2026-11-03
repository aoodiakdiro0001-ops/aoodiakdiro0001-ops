#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LLM-Router-ZeroBaran — Project #37 | Orchestrator (CLI entry for GitHub Actions cron)
Author : Baran Avisat  <Baranavisat@gmail.com>  WhatsApp: 00905313263722
Copyright (c) 2026 Baran Avisat — ZeroBaran Studio. MIT License.

Commands:
  run    — full pipeline over watchlist (fetch -> indicators -> route -> store -> telegram)
  demo   — same but forced offline data (no network needed)
  ask    — one-off routed query through the smart router ("ask" "text")
  weekly — performance digest to telegram + stdout
Config: scripts/config.yaml (watchlist, risk params). All secrets via env only.
"""
from __future__ import annotations
import json, os, sys, time

sys.path.insert(0, os.path.dirname(__file__))
import market_data, indicators, router, store, notify

try:
    import yaml
except Exception:
    yaml = None

CFG_PATH = os.path.join(os.path.dirname(__file__), "config.yaml")


def load_cfg() -> dict:
    defaults = {"watchlist": [{"symbol": "AAPL", "tf": "1d"}, {"symbol": "BTCUSDT", "tf": "1d"}],
                "risk_pct": 1.0, "capital": 1000.0,
                "min_confidence_alert": 60.0}
    if yaml and os.path.exists(CFG_PATH):
        try:
            with open(CFG_PATH) as f:
                user = yaml.safe_load(f) or {}
            defaults.update(user)
        except Exception as e:
            print(f"[cfg] config.yaml parse error: {e}")
    return defaults


def analyze_symbol(sym: str, tf: str, cfg: dict, force_demo: bool = False) -> dict:
    candles, src = market_data.fetch_candles(sym, tf, force_demo=force_demo)
    snap = indicators.compute_snapshot(sym, tf, candles)
    sd = {"price": snap.price, "change_pct": snap.change_pct, "indicators": snap.indicators,
          "signals": snap.signals, "trend_score": snap.trend_score,
          "confidence": snap.confidence, "volatility_pct": snap.volatility_pct, "bars": snap.bars}
    plan = indicators.plan_trade(snap, cfg["risk_pct"], cfg["capital"])
    prompt = (f"Symbol {sym} ({tf}). Last price {snap.price:.4f}, day change {snap.change_pct:+.2f}%. "
              f"Trend score {snap.trend_score}/100 confidence {snap.confidence}%. "
              f"Indicators: {json.dumps({k: v for k, v in snap.indicators.items() if k != 'obv'})}. "
              f"Signals: {', '.join(snap.signals)}. Proposed plan: {json.dumps(plan)}. "
              f"Analyze risk, confirm or reject the setup briefly (max 120 words). Market sentiment context.")
    rr = router.route(prompt, kind_hint="analysis")
    logged = store.log_analysis(sym, tf, sd, {"provider": rr.provider, "model": rr.model,
                                              "latency_ms": rr.latency_ms,
                                              "cost_saved_usd": rr.cost_saved_usd}, rr.text, plan)
    sig = store.log_signal(sym, plan, sd)
    alert_sent = False
    if sig and snap.confidence >= cfg["min_confidence_alert"]:
        msg = notify.fmt_signal_alert(sym, sd, plan, rr.text,
                                      {"provider": rr.provider, "model": rr.model,
                                       "latency_ms": rr.latency_ms})
        alert_sent = notify.send(msg)
    return {"symbol": sym, "source": src, "snapshot": sd, "plan": plan,
            "route": {"provider": rr.provider, "model": rr.model, "latency_ms": rr.latency_ms,
                      "cost_saved_usd": rr.cost_saved_usd, "attempts": rr.attempts},
            "narrative": rr.text[:300], "stored": logged, "signal": sig, "alert_sent": alert_sent}


def cmd_run(force_demo: bool = False) -> int:
    cfg = load_cfg()
    results = []
    candles_map = {}
    for item in cfg["watchlist"]:
        sym, tf = item["symbol"], item.get("tf", "1d")
        try:
            r = analyze_symbol(sym, tf, cfg, force_demo)
            results.append(r)
            cs, _ = market_data.fetch_candles(sym, tf, force_demo=force_demo)
            candles_map[sym] = cs
        except Exception as e:
            print(f"[run] {sym} failed: {type(e).__name__}: {e}")
            results.append({"symbol": sym, "error": str(e)})
    settled = store.settle_open_signals(candles_map)
    summary = {"ts": time.time(), "mode": "demo" if force_demo else "live",
               "analyzed": len([r for r in results if "error" not in r]),
               "errors": len([r for r in results if "error" in r]),
               "settled_signals": settled,
               "router_stats": router.stats_summary(),
               "performance": store.performance_summary(),
               "results": [{k: v for k, v in r.items() if k != "narrative"} for r in results]}
    os.makedirs(store.STATE_DIR, exist_ok=True)
    with open(os.path.join(store.STATE_DIR, "last_run.json"), "w") as f:
        json.dump(summary, f, ensure_ascii=False, indent=1, default=str)
    print(json.dumps({k: summary[k] for k in ("mode", "analyzed", "errors", "settled_signals",
                                              "router_stats", "performance")},
                     ensure_ascii=False, indent=1))
    for r in results:
        if "error" in r:
            print(f"  ✗ {r['symbol']}: {r['error']}")
        else:
            p = r["plan"]
            print(f"  ✓ {r['symbol']} [{r['source']}] trend={r['snapshot']['trend_score']} "
                  f"conf={r['snapshot']['confidence']}% → {p.get('side')} "
                  f"(via {r['route']['provider']}/{r['route']['model']} {r['route']['latency_ms']}ms"
                  f", saved≈${r['route']['cost_saved_usd']:.6f})")
    return 0


def cmd_ask(text: str) -> int:
    rr = router.route(text)
    print(f"[{rr.provider}/{rr.model}] task={rr.task.kind}/{rr.task.complexity} "
          f"{rr.latency_ms}ms saved≈${rr.cost_saved_usd}")
    print(rr.text)
    return 0


def cmd_weekly() -> int:
    perf = store.performance_summary()
    rs = router.stats_summary()
    recent = store.fetch_recent("signals", 5)
    msg = notify.fmt_weekly_digest(perf, rs, recent)
    print(msg.replace("<b>", "").replace("</b>", "").replace("<code>", "").replace("</code>", "")
            .replace("<i>", "").replace("</i>", ""))
    notify.send(msg)
    return 0


if __name__ == "__main__":
    args = sys.argv[1:]
    cmd = args[0] if args else "run"
    if cmd == "run":
        sys.exit(cmd_run())
    elif cmd == "demo":
        sys.exit(cmd_run(force_demo=True))
    elif cmd == "ask" and len(args) > 1:
        sys.exit(cmd_ask(" ".join(args[1:])))
    elif cmd == "weekly":
        sys.exit(cmd_weekly())
    else:
        print("usage: llm_router.py [run|demo|ask <question>|weekly]")
        sys.exit(2)
