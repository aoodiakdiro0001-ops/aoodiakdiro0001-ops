# -*- coding: utf-8 -*-
"""
Design-Guard-ZeroBaran — الطبقة 4: قناة التنبيهات والتحكم
==========================================================
Delivery Layer: Telegram Bot API يرسل تقرير الفحص الفوري بنمط:
🔍 تقرير مراقبة الجودة / 🟢 الحالة / 📊 نسبة المطابقة
بالإضافة إلى ملخص إنتاجية أسبوعي. يعمل بصمت تام إن لم تُضبط المفاتيح.

المؤلف: Baran Avisat | baranavisat@gmail.com | واتساب: 00905313263722
الحقوق محفوظة © ZeroBaran Studio — MIT License
"""
from __future__ import annotations

import html
import os
from typing import List, Optional

import requests

VERDICT_ICON = {"accepted": "🟢", "rejected": "🔴", "needs_review": "🟡"}
VERDICT_AR = {"accepted": "معتمد — اجتاز كافة اختبارات الجودة",
              "rejected": "مرفوض — أعد التوليد قبل النشر",
              "needs_review": "يحتاج مراجعة بشرية"}


class TelegramGuard:
    def __init__(self):
        self.token = os.getenv("TELEGRAM_BOT_TOKEN", "")
        self.chat_id = os.getenv("TELEGRAM_CHAT_ID", "")
        self.disabled_reason = ""
        if not (self.token and self.chat_id):
            self.disabled_reason = "TELEGRAM_BOT_TOKEN/TELEGRAM_CHAT_ID غير مضبوطين — التنبيهات معطلة."

    @property
    def enabled(self) -> bool:
        return bool(self.token and self.chat_id)

    def _send(self, text: str) -> bool:
        if not self.enabled:
            return False
        try:
            r = requests.post(f"https://api.telegram.org/bot{self.token}/sendMessage",
                              json={"chat_id": self.chat_id, "text": text,
                                    "parse_mode": "HTML", "disable_web_page_preview": True},
                              timeout=20)
            ok = r.status_code == 200
            if not ok:
                self.disabled_reason = f"Telegram HTTP {r.status_code}: {r.text[:120]}"
            return ok
        except requests.RequestException as e:
            self.disabled_reason = f"Telegram network error: {e.__class__.__name__}"
            return False

    # -------------------------------------------------- تقرير فحص مفرد
    def report_asset(self, rep: dict) -> bool:
        v = rep.get("verdict", "needs_review")
        icon = VERDICT_ICON.get(v, "⚪")
        defects = rep.get("defects") or []
        lines = [
            "🔍 <b>تقرير مراقبة الجودة — Design-Guard-ZeroBaran</b>",
            f"📦 الأصل: <code>{html.escape(rep.get('filename','?'))}</code> ({rep.get('kind','?')})",
            f"{icon} <b>الحالة:</b> {VERDICT_AR.get(v, v)}",
            f"📊 <b>نسبة المطابقة:</b> {rep.get('match_score', 0)}%",
        ]
        dims = rep.get("width") or 0
        if dims:
            lines.append(f"📐 الأبعاد: {dims}×{rep.get('height')}px | الحجم: {rep.get('file_size',0)//1024}KB")
        if defects:
            lines.append("🧾 <b>العيوب المرصودة:</b>")
            for d in defects[:5]:
                sev = {"critical": "🛑", "major": "⚠️", "minor": "ℹ️"}.get(d.get("severity"), "•")
                lines.append(f"  {sev} [{d.get('type')}] {html.escape(str(d.get('note_ar',''))[:160])}")
        if rep.get("summary_ar"):
            lines.append(f"🧠 <b>تلخيص الذكاء الاصطناعي:</b> {html.escape(rep['summary_ar'][:300])}")
        if v != "accepted" and rep.get("fix_suggestion_ar"):
            lines.append(f"💡 <b>الإصلاح المقترح:</b> {html.escape(rep['fix_suggestion_ar'][:300])}")
        lines.append("— ⚙️ صفر تكلفة • صفر أخطاء منشورة • ZeroBaran Studio")
        return self._send("\n".join(lines))

    # -------------------------------------------------- موجز دفعة
    def batch_summary(self, results: List[dict], warnings: Optional[List[str]] = None) -> bool:
        if not results:
            return True
        n = len(results)
        acc = sum(1 for r in results if r.get("verdict") == "accepted")
        rej = sum(1 for r in results if r.get("verdict") == "rejected")
        rev = n - acc - rej
        avg = round(sum(r.get("match_score", 0) for r in results) / n, 1)
        lines = [
            "✅ <b>انتهت دورة فحص Design-Guard-ZeroBaran</b>",
            f"📦 أصول مفحوصة: {n} | 🟢 معتمد: {acc} | 🔴 مرفوض: {rej} | 🟡 مراجعة: {rev}",
            f"📊 متوسط المطابقة: {avg}%",
        ]
        worst = sorted((r for r in results if r.get("verdict") != "accepted"),
                       key=lambda x: x.get("match_score", 100))[:3]
        for w in worst:
            lines.append(f"  🔻 <code>{html.escape(w['filename'])}</code> → {w.get('match_score')}%")
        if warnings:
            lines.append("⚠️ ملاحظات النظام: " + "; ".join(html.escape(x) for x in warnings[:3]))
        lines.append("👤 Baran Avisat • ZeroBaran Studio")
        return self._send("\n".join(lines))

    # -------------------------------------------------- ملخص أسبوعي
    def weekly_productivity(self, metrics: dict) -> bool:
        if not metrics or not metrics.get("total"):
            return self._send("📅 <b>الملخص الأسبوعي للجودة</b>\nلا توجد عمليات فحص هذا الأسبوع.")
        top = "\n".join(f"  • {t}: <b>{c}×</b>" for t, c in metrics.get("top_defects", [])[:5]) or "  — لا عيوب مسجّلة 🎉"
        lines = [
            "📅 <b>الملخص الأسبوعي لإنتاجية الجودة — Design-Guard-ZeroBaran</b>",
            f"📦 إجمالي الفحوصات: {metrics['total']}",
            f"🟢 نسبة القبول من أول محاولة: {metrics.get('accept_rate')}%",
            f"🔴 نسبة الرفض (إعادة توليد): {metrics.get('reject_rate')}%",
            f"📊 متوسط مطابقة الهوية: {metrics.get('avg_match')}%",
            "🧨 أكثر العيوب تكراراً:",
            top,
            "💰 كل هذا بتكلفة صفر — بديل Hallmark/Impeccable المجاني الكامل.",
        ]
        return self._send("\n".join(lines))


if __name__ == "__main__":
    tg = TelegramGuard()
    print("Telegram enabled:", tg.enabled, "| reason:", tg.disabled_reason or "-")
