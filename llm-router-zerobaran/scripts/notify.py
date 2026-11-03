#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LLM-Router-ZeroBaran — Project #37 | Layer 4: Telegram Alerts (free Bot API)
Author : Baran Avisat  <Baranavisat@gmail.com>  WhatsApp: 00905313263722
Copyright (c) 2026 Baran Avisat — ZeroBaran Studio. MIT License.
Formats the exact report style requested + weekly performance digest. Silent-safe offline.
"""
from __future__ import annotations
import json, os, time
from typing import Dict, List

import requests

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")
FOOTER = ("\n\n———\n🛡️ <b>LLM-Router-ZeroBaran</b> · Project #37 · ZeroBaran Studio\n"
          "👤 Baran Avisat · 📧 Baranavisat@gmail.com · 📱 واتساب: <code>00905313263722</code>\n"
          "⚠️ قرار آلي لدعم القرار فقط — ليس نصيحة مالية.")


def esc(s: str) -> str:
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def send(text: str) -> bool:
    if not BOT_TOKEN or not CHAT_ID:
        print("[notify] telegram not configured — message logged only")
        return False
    try:
        r = requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                          data={"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"},
                          timeout=15)
        ok = r.ok
        if not ok:
            print(f"[notify] telegram {r.status_code}: {r.text[:150]}")
        return ok
    except Exception as e:
        print(f"[notify] telegram error: {e}")
        return False


def fmt_signal_alert(symbol: str, snap: Dict, plan: Dict, narrative: str, route_info: Dict) -> str:
    side = plan.get("side", "NO_TRADE")
    icon = {"BUY": "🟢", "SELL/AVOID": "🔴"}.get(side, "⚪")
    conf = snap.get("confidence", 0)
    lines = [
        f"📈 <b>تقرير التحليل المالي والتداول</b>",
        f"{icon} تم رصد {'فرصة محتملة' if side == 'BUY' else 'تحذير اتجاه هابط'} للأصل <b>{esc(symbol)}</b>.",
        f"📊 مؤشرات الأداء: اتجاه {'صعودي' if snap.get('trend_score', 0) >= 0 else 'هابطي'} "
        f"بنسبة ثقة <b>{conf:.0f}%</b> (trend score {snap.get('trend_score')} / ±100)",
        f"💰 السعر الحالي: {snap.get('price')} | تذبذب ATR%: {snap.get('volatility_pct')}",
        f"🧭 إشارات المحرك الكمي: {esc(', '.join(snap.get('signals', []))[:220])}",
    ]
    if side != "NO_TRADE":
        lines += [
            f"💡 <b>التوصية الآلية (خطة دخول/خروج):</b>",
            f"   • الدخول: <code>{plan.get('entry')}</code>",
            f"   • وقف الخسارة: <code>{plan.get('stop_loss')}</code>",
            f"   • الهدف 1: <code>{plan.get('take_profit_1')}</code> | الهدف 2: <code>{plan.get('take_profit_2')}</code>",
            f"   • حجم المركز لمخاطرة {plan.get('risk_pct')}% من رأس مال {plan.get('capital')}: <code>{plan.get('qty_for_risk')}</code>",
        ]
    else:
        lines.append("💡 التوصية الآلية: لا صفقة — النطاق محايد، انتظر تأكيداً أوضح.")
    if narrative:
        lines.append(f"🧠 تحليل النموذج ({esc(route_info.get('provider', '?'))}/{esc(route_info.get('model', '?'))}, "
                     f"{route_info.get('latency_ms')}ms):\n<i>{esc(narrative[:700])}</i>")
    lines.append(FOOTER)
    return "\n".join(lines)


def fmt_weekly_digest(perf: Dict, router_stats: Dict, top_signals: List[Dict]) -> str:
    lines = ["📊 <b>الملخص الأسبوعي — LLM-Router-ZeroBaran</b>",
             f"✅ تحليلات مسجلة: <b>{perf.get('analyses_logged', 0)}</b>",
             f"🎯 إشارات مغلقة: {perf.get('closed', 0)} | نسبة نجاح: <b>{(perf.get('win_rate', 0) or 0) * 100:.1f}%</b>"
             f" | متوسط PnL%: {perf.get('avg_pnl_pct', 0)}",
             f"💸 التكلفة الموفَّرة التقديرية مقابل مزود مدفوع: <b>${perf.get('est_cost_saved_usd', 0):.4f}</b>"
             f" (إجمالي الراوتر: ${router_stats.get('total_saved_usd', 0):.4f})",
             "🤖 أداء النماذج الموجَّهة:"]
    for m, v in list(router_stats.get("models", {}).items())[:6]:
        lines.append(f"   • {esc(m)}: {v['calls']} نداء، نجاح {v['success_rate'] * 100:.0f}%، "
                     f"زمن {v['avg_latency_ms']}ms")
    if top_signals:
        lines.append("🧾 أحدث الإشارات:")
        for s in top_signals[:5]:
            lines.append(f"   • {esc(s.get('symbol'))} {esc(s.get('side'))} @ {s.get('entry')} → {esc(s.get('outcome'))}")
    lines.append(FOOTER)
    return "\n".join(lines)


if __name__ == "__main__":
    msg = fmt_signal_alert("BTCUSDT",
                           {"price": 77170.0, "confidence": 85.0, "trend_score": 43.0,
                            "volatility_pct": 2.1, "signals": ["TREND_UP_MA_STACK", "MACD_ABOVE_SIGNAL"]},
                           {"side": "BUY", "entry": 77170, "stop_loss": 75000, "take_profit_1": 79500,
                            "take_profit_2": 82000, "qty_for_risk": 0.04, "risk_pct": 1.0, "capital": 1000},
                           "Momentum confirmed by OBV accumulation; risk/reward 1:1 to TP1.",
                           {"provider": "groq", "model": "gemma-3-27b", "latency_ms": 640})
    print(msg[:400], "…")
    print(send(msg))
