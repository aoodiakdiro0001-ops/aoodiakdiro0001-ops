#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
 ╔═══════════════════════════════════════════════════════════════╗
 ║  PULSE-ZERO — المنظومة الذاتية لرصد مشاعر العملاء وإدارة السمعة ║
 ║  Orchestrator: Ingestion → AI Sentiment → Supabase → Telegram  ║
 ╚═══════════════════════════════════════════════════════════════╝

الاستخدام:
    python3 pulse_zero.py                # دورة رصد وتحليل وتنبيه كاملة
    python3 pulse_zero.py --report       # تقرير السمعة الأسبوعي فقط
    python3 pulse_zero.py --dry-run      # لا تخزين ولا إرسال (معاينة)
    python3 pulse_zero.py --limit 20     # سقف عدد التعليقات المعالجة

يعمل محلياً أو داخل GitHub Actions — بنفس الكود تماماً.
"""

from __future__ import annotations

import argparse
import os
import sys
from dataclasses import asdict
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ingest import collect_all                      # noqa: E402
from sentiment import get_brain, analyze_mentions   # noqa: E402
from storage import get_store                       # noqa: E402
from alerts import (TelegramGateway, format_negative_alert,   # noqa: E402
                    format_weekly_report, push_run_summary)

BANNER = r"""
┌──────────────────────────────────────────────┐
│   ⚡ PULSE-ZERO · Zero-Cost Reputation Radar │
└──────────────────────────────────────────────┘"""


def load_config() -> dict:
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.yaml")
    try:
        import yaml
        with open(path, encoding="utf-8") as fh:
            return yaml.safe_load(fh) or {}
    except ImportError:
        print("  ⚠️ PyYAML غير مثبتة — استخدام إعدادات افتراضية (demo+mock)")
        return {"brand": {"name": "BaranAvi"}, "sources": {"demo": True},
                "ai": {"provider": "mock"},
                "alerts": {"telegram": {"enabled": True, "negative_threshold": -0.45}},
                "storage": {"backend": "json", "json_fallback_path": "state/mentions.json"}}
    except FileNotFoundError:
        print(f"  ❌ config.yaml غير موجود في {os.path.dirname(path)}")
        sys.exit(1)


def run_cycle(cfg: dict, args) -> int:
    brand = cfg.get("brand", {}).get("name", "MyBrand")
    al_cfg = cfg.get("alerts", {}).get("telegram", {})
    threshold = float(al_cfg.get("negative_threshold", -0.45))
    critical_kw = [k.lower() for k in al_cfg.get("critical_keywords", [])]

    # ── الطبقة 1: الجلب ──────────────────────────────────────────────
    print("\n📡 [1/4] طبقة الجلب والمسح الرقمي…")
    mentions, src_errors = collect_all(cfg)
    print(f"   ✔ تم جمع {len(mentions)} إشارة خام من المصادر المفعّلة")
    for e in src_errors:
        print(f"   ⚠️ {e}")

    store = get_store(cfg)
    known = set() if args.no_dedupe else store.known_ids()
    fresh = [m for m in mentions if m.id not in known]
    print(f"   ♻️ المرشحون الجدد (بعد إزالة المخزّن سابقاً): {len(fresh)}")
    if args.limit:
        fresh = fresh[:args.limit]

    # ── الطبقة 2: العقل الذكي ───────────────────────────────────────
    print("\n🧠 [2/4] تحليل المشاعر بالذكاء الاصطناعي…")
    brain = get_brain(cfg)
    print(f"   ⚙️ المحرك: {getattr(brain,'name','?')}")
    records, ai_errors = analyze_mentions(fresh, brain,
                                         int(cfg.get("ai", {}).get("max_items_per_call", 12)))
    for e in ai_errors:
        print(f"   ⚠️ {e}")

    counts = {"positive": 0, "negative": 0, "neutral": 0}
    for r in records:
        counts[r["sentiment"]] = counts.get(r["sentiment"], 0) + 1
    print(f"   ✔ نتائج التحليل → 🟢 {counts['positive']} | ⚪ {counts['neutral']} | 🔴 {counts['negative']}")

    # ── الطبقة 3: الأرشيف ───────────────────────────────────────────
    print("\n🗄️ [3/4] التخزين والأرشفة التاريخية…")
    if args.dry_run:
        print("   ⏭ dry-run: تم تخطي الكتابة")
        saved = len(records)
    else:
        saved = store.upsert_many(records)
        print(f"   ✔ محفوظة {saved} سجلات ({type(store).__name__})")

    # ── الطبقة 4: الإنذار الفوري ────────────────────────────────────
    print("\n🚨 [4/4] التنبيهات الفورية…")
    gw = TelegramGateway.from_env()
    if not gw.enabled and al_cfg.get("enabled", True):
        print("   ℹ️ TELEGRAM_BOT_TOKEN/CHAT_ID غير مضبوطين — عرض تجفيف في اللوج")

    alerted = crisis = 0
    for r in records:
        if r.get("category") == "spam":      # لا تُزعج أحداً بمنشور خارج النطاق
            continue
        is_bad = (r["sentiment"] == "negative" and
                  (r["score"] <= threshold or r["severity"] in ("high", "crisis")))
        has_kw = any(k in (r.get("body", "") or "").lower() for k in critical_kw)
        if is_bad or (r["sentiment"] == "negative" and has_kw):
            crisis += r["severity"] == "crisis"
            if not args.dry_run:
                gw.send(format_negative_alert(r, brand))
            else:
                print("---- [DRY-RUN ALERT] ----\n" +
                      format_negative_alert(r, brand).replace("<br>", "\n")[:600])
            alerted += 1
    print(f"   ✔ تنبيهات سلبية مرسلة: {alerted} (منها أزمات حرجة: {crisis})")

    push_run_summary(gw if not args.dry_run else TelegramGateway("", ""),
                     len(records), counts["negative"], crisis,
                     src_errors + ai_errors, brand)

    print(f"\n✅ اكتملت الدورة — {len(records)} سجلات جديدة معالجة لعلامة «{brand}»")
    return 0


def run_report(cfg: dict, args) -> int:
    brand = cfg.get("brand", {}).get("name", "MyBrand")
    store = get_store(cfg)
    stats = store.weekly_stats(days=int(args.days))
    week_label = datetime.now(timezone.utc).strftime("%Y-%m-%d") + " ↻ آخر 7 أيام"
    msg = format_weekly_report(stats, brand, week_label)
    if args.dry_run:
        print(msg)
    else:
        TelegramGateway.from_env().send(msg)
    print("📊 التقرير الأسبوعي جاهز.")
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description="Pulse-Zero — Free Sentiment & Reputation Radar")
    p.add_argument("--report", action="store_true", help="إرسال تقرير السمعة الأسبوعي فقط")
    p.add_argument("--days", default=7, help="نافذة التقرير بالأيام (مع --report)")
    p.add_argument("--dry-run", action="store_true", help="لا تخزين ولا إرسال — معاينة كاملة")
    p.add_argument("--no-dedupe", action="store_true", help="عطّل فلترة المكرر (للتجربة)")
    p.add_argument("--limit", type=int, default=0, help="سقف عدد السجلات الجديدة في الدورة")
    args = p.parse_args()

    print(BANNER)
    cfg = load_config()
    return run_report(cfg, args) if args.report else run_cycle(cfg, args)


if __name__ == "__main__":
    sys.exit(main())
