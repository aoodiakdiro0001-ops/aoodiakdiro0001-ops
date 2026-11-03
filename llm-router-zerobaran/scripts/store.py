#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LLM-Router-ZeroBaran — Project #37 | Layer 3: Persistence (Supabase free tier + local JSON fallback)
Author : Baran Avisat  <Baranavisat@gmail.com>  WhatsApp: 00905313263722
Copyright (c) 2026 Baran Avisat — ZeroBaran Studio. MIT License.
Tables: analysis_log (per run), signal_events (BUY/SELL/NO_TRADE w/ outcome tracking),
        router_stats_mirror (model performance history). Falls back to state/*.json offline.
"""
from __future__ import annotations
import json, os, time
from typing import Dict, List, Optional

STATE_DIR = os.environ.get("LRZ_STATE", os.path.join(os.path.dirname(__file__), "..", "state"))
SUPA_URL = os.environ.get("SUPABASE_URL", "")
SUPA_KEY = os.environ.get("SUPABASE_SERVICE_KEY", "")

TABLES = {"analysis": "lrz_analysis_log", "signals": "lrz_signal_events"}


def _local_file(table: str) -> str:
    os.makedirs(STATE_DIR, exist_ok=True)
    return os.path.join(STATE_DIR, f"{table}.json")


def _load_local(table: str) -> List[Dict]:
    try:
        with open(_local_file(table)) as f:
            return json.load(f)
    except Exception:
        return []


def _save_local(table: str, rows: List[Dict]) -> None:
    try:
        with open(_local_file(table), "w") as f:
            json.dump(rows[-2000:], f, ensure_ascii=False, indent=1)
    except Exception:
        pass


def upsert(table_key: str, row: Dict) -> str:
    """Write one row. Returns 'supabase' or 'local'. Never raises."""
    table = TABLES[table_key]
    rows = _load_local(table_key)
    rows = [r for r in rows if r.get("id") != row.get("id")]
    rows.append(row)
    _save_local(table_key, rows)
    if SUPA_URL and SUPA_KEY:
        try:
            import requests
            r = requests.post(f"{SUPA_URL.rstrip('/')}/rest/v1/{table}",
                              json=row, headers={"apikey": SUPA_KEY,
                                                 "Authorization": f"Bearer {SUPA_KEY}",
                                                 "Content-Type": "application/json",
                                                 "Prefer": "resolution=merge-duplicates"},
                              timeout=15)
            if r.ok:
                return "supabase"
            print(f"[store] supabase {r.status_code}: {r.text[:120]}")
        except Exception as e:
            print(f"[store] supabase unavailable ({type(e).__name__}); using local mirror")
    return "local"


def fetch_recent(table_key: str, limit: int = 50) -> List[Dict]:
    if SUPA_URL and SUPA_KEY:
        try:
            import requests
            table = TABLES[table_key]
            r = requests.get(f"{SUPA_URL.rstrip('/')}/rest/v1/{table}"
                             f"?select=*&order=ts.desc&limit={limit}",
                             headers={"apikey": SUPA_KEY,
                                      "Authorization": f"Bearer {SUPA_KEY}"}, timeout=15)
            if r.ok:
                return r.json()
        except Exception:
            pass
    rows = _load_local(table_key)
    return sorted(rows, key=lambda x: x.get("ts", 0), reverse=True)[:limit]


def log_analysis(symbol: str, tf: str, snap_dict: Dict, route_info: Dict,
                 narrative: str, plan: Dict) -> Dict:
    rid = f"{symbol}-{int(time.time())}"
    row = {"id": rid, "ts": time.time(), "symbol": symbol, "timeframe": tf,
           "price": snap_dict.get("price"), "trend_score": snap_dict.get("trend_score"),
           "confidence": snap_dict.get("confidence"),
           "signals": json.dumps(snap_dict.get("signals", []), ensure_ascii=False),
           "provider": route_info.get("provider"), "model": route_info.get("model"),
           "latency_ms": route_info.get("latency_ms"),
           "cost_saved_usd": route_info.get("cost_saved_usd"),
           "narrative": narrative[:4000], "plan": json.dumps(plan, ensure_ascii=False)}
    dest = upsert("analysis", row)
    return {"row_id": rid, "stored_in": dest}


def log_signal(symbol: str, plan: Dict, snap_dict: Dict) -> Optional[Dict]:
    if plan.get("side") in (None, "NO_TRADE"):
        return None
    sid = f"sig-{symbol}-{int(time.time())}"
    row = {"id": sid, "ts": time.time(), "symbol": symbol, "side": plan["side"],
           "entry": plan.get("entry"), "stop_loss": plan.get("stop_loss"),
           "take_profit_1": plan.get("take_profit_1"),
           "trend_score": snap_dict.get("trend_score"),
           "confidence": snap_dict.get("confidence"),
           "outcome": "open", "pnl_pct": None}
    dest = upsert("signals", row)
    return {"signal_id": sid, "stored_in": dest}


def settle_open_signals(candles_by_symbol: Dict[str, List[Dict]]) -> List[Dict]:
    """Mark-to-last-price for open signals; flips outcome to tp1_hit/sl_hit after 2 bars rule-of-thumb."""
    settled = []
    rows = _load_local("signals")
    by_id = {r["id"]: r for r in rows}
    changed = False
    for r in rows:
        if r.get("outcome") != "open":
            continue
        cs = candles_by_symbol.get(r["symbol"])
        if not cs:
            continue
        last = cs[-1]["close"]
        entry = r.get("entry") or last
        r["pnl_pct"] = round((last - entry) / entry * 100.0, 4) if entry else 0.0
        if r["side"].startswith("BUY"):
            if last >= (r.get("take_profit_1") or float("inf")):
                r["outcome"] = "tp1_hit"; changed = True
            elif last <= (r.get("stop_loss") or -float("inf")):
                r["outcome"] = "sl_hit"; changed = True
        else:  # SELL/AVOID
            if last <= (r.get("take_profit_1") or -float("inf")):
                r["outcome"] = "tp1_hit"; changed = True
            elif last >= (r.get("stop_loss") or float("inf")):
                r["outcome"] = "sl_hit"; changed = True
        if changed:
            upsert("signals", r)
            settled.append({"id": r["id"], "outcome": r["outcome"], "pnl_pct": r["pnl_pct"]})
        changed = False
    return settled


def performance_summary() -> Dict:
    rows = _load_local("signals")
    closed = [r for r in rows if r.get("outcome") in ("tp1_hit", "sl_hit")]
    wins = sum(1 for r in closed if r["outcome"] == "tp1_hit")
    pnls = [r.get("pnl_pct") or 0.0 for r in closed]
    an_rows = _load_local("analysis")
    saved = sum(a.get("cost_saved_usd") or 0.0 for a in an_rows)
    return {"signals_total": len(rows), "closed": len(closed), "win_rate": round(wins / max(len(closed), 1), 3),
            "avg_pnl_pct": round(sum(pnls) / max(len(pnls), 1), 4),
            "analyses_logged": len(an_rows), "est_cost_saved_usd": round(saved, 6)}


if __name__ == "__main__":
    demo_snap = {"price": 100.2, "trend_score": 44.0, "confidence": 88.0, "signals": ["MACD_BULL_CROSS"]}
    print(log_analysis("DEMO", "1d", demo_snap, {"provider": "mock", "model": "m", "latency_ms": 1,
                                                 "cost_saved_usd": 0.0001}, "test narrative",
                       {"side": "BUY", "entry": 100.2, "stop_loss": 98, "take_profit_1": 103}))
    print(log_signal("DEMO", {"side": "BUY", "entry": 100.2, "stop_loss": 98, "take_profit_1": 103}, demo_snap))
    print(settle_open_signals({"DEMO": [{"close": 104.0}]}))
    print(performance_summary())
