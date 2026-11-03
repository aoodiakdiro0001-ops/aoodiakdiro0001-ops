#!/usr/bin/env python3
# =====================================================================
#  Scrapling-ZeroBaran — Layer 4: Telegram Delivery & Reports
#  Project #38 | ZeroBaran Studio — 100% Free Stack
#  Author : Baran Avisat | Baranavisat@gmail.com | WhatsApp: 00905313263722
#  Copyright (c) 2026 Baran Avisat. All rights reserved. (MIT licensed)
# =====================================================================
from __future__ import annotations

import logging
import os
import time
from typing import Any

log = logging.getLogger("sz.notify")

OWNER_FOOTER = ("\n<blockquote>🛡️ Scrapling-ZeroBaran — منظومة الزحف الذاتي\n"
                "المؤلف: Baran Avisat | الدعم: Baranavisat@gmail.com | واتساب: 00905313263722"
                "</blockquote>")


class Notifier:
    def __init__(self, cfg: dict):
        self.token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
        self.chat_id = os.environ.get("TELEGRAM_CHAT_ID", "")
        self.enabled = bool(self.token and self.chat_id)
        self.cfg = cfg

    def send(self, text_html: str) -> bool:
        if not self.enabled:
            log.info("[no-telegram] %s", text_html[:200])
            return False
        import requests
        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        for attempt in range(3):
            try:
                r = requests.post(url, json={"chat_id": self.chat_id, "text": text_html,
                                             "parse_mode": "HTML", "disable_web_page_preview": True},
                                  timeout=20)
                if r.status_code == 429:
                    ra = int(r.json().get("parameters", {}).get("retry_after", 2 ** attempt))
                    time.sleep(ra + 1); continue
                return r.ok
            except Exception as e:
                log.warning("telegram send failed: %s", e)
                time.sleep(2 ** attempt)
        return False

    # ---------- report builders ----------
    def crawl_report(self, run: dict) -> str:
        a = self.cfg.get("alerts", {})
        if not a.get("send_run_report", True):
            return ""
        pct = "100" if run.get("status") == "ok" else str(run.get("completion_pct", "?"))
        engines = ", ".join(f"{k}×{v}" for k, v in (run.get("engines_used") or {}).items()) or "requests"
        lines = [
            "🕸️ <b>تقرير زحف البيانات</b>",
            f"📦 تم استخراج <b>{run.get('records_new', 0)}</b> سجلاً جديداً و<b>{run.get('records_changed', 0)}</b> تغيّراً من {len(run.get('targets', []))} هدف.",
            f"📊 حالة الزحف: <b>{'اكتمل بنسبة ' + pct + '% دون أي حظر' if run.get('blocks_detected', 0) == 0 else 'رُصد ' + str(run.get('blocks_detected')) + ' حاجز حماية — التزمنا بالخروج الآمن'}</b>",
            f"🌐 الصفحات المفحوصة: {run.get('pages_fetched', 0)} | المحركات: {engines}",
            f"🧠 محرك التحليل: {run.get('brain', 'mock')}",
            "📥 البيانات جاهزة للتصدير من لوحة التحكم أو ملف JSONL.",
            OWNER_FOOTER,
        ]
        return "\n".join(lines)

    def change_alert(self, ev: dict[str, Any]) -> str:
        title = str(ev.get("title", ""))[:120]
        arrow = "🔻" if float(ev.get("new", 0)) < float(ev.get("old", 0) or 0) else "🔺"
        return "\n".join([
            f"{arrow} <b>تنبيه تغيّر بيانات فوري</b>",
            f"📄 السجل: <code>{title}</code>",
            f"🔖 الحقل: <b>{ev.get('field')}</b> | القديم: <code>{ev.get('old')}</code> ➜ الجديد: <b>{ev.get('new')}</b>",
            OWNER_FOOTER,
        ])

    def breaker_alert(self, target: str, detail: str) -> str:
        return "\n".join([
            "🚨 <b>قاطع الحماية تدخّل — لم نطرق الباب أكثر</b>",
            f"🎯 الهدف: <code>{target}</code>",
            f"ℹ️ {detail}",
            "✅ النظام توقف بأدب لحماية عنوان IP الخاص بك ولعدم إزعاج الموقع.",
            OWNER_FOOTER,
        ])
