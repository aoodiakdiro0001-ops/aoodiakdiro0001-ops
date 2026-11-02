#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pulse-Zero :: Delivery & Control Layer (طبقة التوصيل والتنبيه الفوري)
=====================================================================
  • تنبيه عاجل على تليجرام فور رصد تعليق سلبي/أزمة + الرد المقترح جاهزاً
  • تقرير سمعة أسبوعي (مؤشر Sentiment العام + أبرز الشكاوى والاتجاهات)
  • بلا مفتاح Telegram ⇒ يطبع الرسائل في اللوج (وضع مراقبة آمنة)

يستخدم Telegram Bot API المجاني بالكامل — لا اعتماديات خارجية.
"""

from __future__ import annotations

import json
import os
import urllib.parse
import urllib.request
from datetime import datetime, timezone

SEV_EMOJI = {"crisis": "🚨", "high": "⚠️", "medium": "🔶", "low": "ℹ️"}
SENTI_EMOJI = {"positive": "🟢", "negative": "🔴", "neutral": "⚪"}


def _env(name: str) -> str:
    return (os.environ.get(name) or "").strip()


class TelegramGateway:
    def __init__(self, token: str, chat_id: str):
        self.token, self.chat_id = token, chat_id
        self.enabled = bool(token and chat_id)

    @classmethod
    def from_env(cls) -> "TelegramGateway":
        return cls(_env("TELEGRAM_BOT_TOKEN"), _env("TELEGRAM_CHAT_ID"))

    def send(self, text: str, parse_mode: str = "HTML") -> bool:
        if not self.enabled:
            print("---- [TG DRY-RUN] ----\n" + _strip_html(text) + "\n----------------------")
            return False
        try:
            data = json.dumps({
                "chat_id": self.chat_id,
                "text": text[:4000],           # حد تليجرام 4096 حرفاً بأمان
                "parse_mode": parse_mode,
                "disable_web_page_preview": True,
            }).encode("utf-8")
            req = urllib.request.Request(
                f"https://api.telegram.org/bot{self.token}/sendMessage",
                data=data, method="POST",
                headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=15) as resp:
                ok = json.loads(resp.read()).get("ok", False)
            print(f"  ✉️ telegram sent ({'OK' if ok else 'NOT-OK'})")
            return bool(ok)
        except Exception as exc:
            print(f"  ⚠️ telegram failed: {type(exc).__name__}: {exc}")
            return False


def _esc(s: str) -> str:
    return (str(s) or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _strip_html(s: str) -> str:
    import re
    return re.sub(r"<[^>]+>", "", s)


# ------------------------------------------------------------------ Alerts
def format_negative_alert(rec: dict, brand_name: str) -> str:
    sev = rec.get("severity", "medium")
    emoji = SEV_EMOJI.get(sev, "⚠️")
    senti = SENTI_EMOJI.get(rec.get("sentiment", "negative"), "🔴")
    body = _esc((rec.get("body") or "")[:280])
    root = _esc(rec.get("issue_root") or "غير محدد")
    reply = _esc(rec.get("reply_draft") or "—")
    url = rec.get("url") or ""
    link = f'<a href="{_esc(url)}">🔗 فتح المصدر</a>' if url.startswith("http") else ""
    return (
        f"{emoji} <b>تنبيه سمعة عاجل — {brand_name}</b>\n\n"
        f"{senti} <b>تقييم سلبي</b> | الخطورة: <code>{sev.upper()}</code> | "
        f"النوع: <code>{_esc(rec.get('category','other'))}</code> | "
        f"الدرجة: <code>{rec.get('score', 0)}</code>\n"
        f"📍 المصدر: <b>{_esc(rec.get('source_name',''))}</b> — {_esc(rec.get('author',''))}\n\n"
        f"💬 <b>نص الشكوى:</b>\n<blockquote>{body}</blockquote>\n"
        f"🔎 <b>جذر المشكلة:</b> {root}\n\n"
        f"💡 <b>الرد المقترح للاستجابة:</b>\n<blockquote>{reply}</blockquote>\n"
        f"{link}"
    )


def format_weekly_report(stats: dict, brand_name: str, week_label: str) -> str:
    total = stats.get("total", 0)
    c = stats.get("counts", {})
    sev = stats.get("severity", {})
    rep = stats.get("reputation_index", 0)
    trend = "📈 تتحسن" if rep >= 65 else "➡️ مستقرة" if rep >= 45 else "📉 تحتاج تدخلاً"
    bar_len = 20
    pos_n = int(round(bar_len * c.get("positive", 0) / max(total, 1)))
    neu_n = int(round(bar_len * c.get("neutral", 0) / max(total, 1)))
    neg_n = max(0, bar_len - pos_n - neu_n)
    bar = "🟢" * pos_n + "⚪" * neu_n + "🔴" * neg_n

    issues = stats.get("top_issues", [])
    issues_txt = ""
    for i, it in enumerate(issues[:5], 1):
        issues_txt += (f"\n{i}. {SEV_EMOJI.get(it.get('severity'), '•')} "
                       f"<code>{_esc(it.get('category'))}</code> — {_esc(it.get('body'))[:120]}")
    if not issues_txt:
        issues_txt = "\n✅ لا شكاوى تستحق المتابعة هذا الأسبوع."

    cats = stats.get("categories", {})
    top_cat = max(cats.items(), key=lambda kv: kv[1])[0] if cats else "—"

    return (
        f"📊 <b>تقرير السمعة الأسبوعي — {_esc(brand_name)}</b>\n"
        f"🗓️ {week_label}\n\n"
        f"🏅 <b>مؤشر السمعة العام: {rep}/100</b> — {trend}\n"
        f"📈 حجم الرصد: <b>{total}</b> ذكر/تقييم\n\n"
        f"<b>توزيع المشاعر:</b>\n"
        f"🟢 إيجابي: {c.get('positive',0)}   ⚪ محايد: {c.get('neutral',0)}   "
        f"🔴 سلبي: {c.get('negative',0)}\n{bar}\n\n"
        f"🚨 أزمات: {sev.get('crisis',0)} | ⚠️ عالية: {sev.get('high',0)} | "
        f"🔶 متوسطة: {sev.get('medium',0)}\n"
        f"🧭 أكثر فئة نشاطاً: <code>{_esc(top_cat)}</code>\n\n"
        f"<b>أبرز المشاكل التي يجب حلها:</b>{issues_txt}\n\n"
        f"⚙️ Pulse-Zero — يعمل ذاتياً عبر GitHub Actions بتكلفة صفر."
    )


def push_run_summary(gw: TelegramGateway, new_count: int, neg_count: int,
                     crisis_count: int, errors: list[str], brand: str) -> None:
    """رسالة تشغيل مختصرة (تُرسل فقط عند وجود جديد أو أخطاء كثيرة)."""
    if new_count == 0 and not errors:
        return
    lines = [f"🔄 <b>Pulse-Zero run</b> — {_esc(brand)}",
             f"جديد: <b>{new_count}</b> | سلبي: <b>{neg_count}</b> | أزمات: <b>{crisis_count}</b>"]
    if errors:
        lines.append(f"⚠️ أخطاء المصادر ({len(errors)}):")
        for e in errors[:5]:
            lines.append(f"• <code>{_esc(e[:160])}</code>")
    gw.send("\n".join(lines))


if __name__ == "__main__":
    gw = TelegramGateway.from_env()
    demo_rec = {"severity": "crisis", "sentiment": "negative", "score": -0.9,
                "category": "complaint_delivery", "source_name": "Gumroad", "author": "user_05",
                "body": "عمليتي لم تصل ولا يوجد رد من الدعم!! هذا احتيال",
                "issue_root": "عملية دفع مكتملة بدون تسليم", "reply_draft": "نعتذر… سنعالج خلال ساعة.",
                "url": "https://example.com/r/1"}
    print(gw.send(format_negative_alert(demo_rec, "BaranAvi")))
    stats = {"total": 42, "counts": {"positive": 25, "neutral": 9, "negative": 8},
             "severity": {"crisis": 1, "high": 3, "medium": 4, "low": 34},
             "categories": {"praise": 25, "complaint_technical": 6, "question": 7},
             "avg_score": 0.31, "reputation_index": 65.5,
             "top_issues": [{"body": "لم يصلني المنتج", "severity": "crisis", "category": "complaint_delivery"}]}
    print(gw.send(format_weekly_report(stats, "BaranAvi",
                                       datetime.now(timezone.utc).strftime("%Y-%m-%d → أسبوع"))))
