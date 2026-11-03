#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agent-Mem-ZeroBaran — Layer 4: Delivery (Telegram memory status + API gateway)
===========================================================================
Project #34 — ZeroBaran Innovation Fleet | © Baran Avisat
Email: Baranavisat@gmail.com | WhatsApp: 00905313263722
"""
from __future__ import annotations
import json
import os
import urllib.request
from typing import Dict, Any

SIGN = ("\n\n🧠 <b>Agent-Mem-ZeroBaran</b> · مشروع #34 — ZeroBaran Studio\n"
        "✍️ Baran Avisat · 📧 Baranavisat@gmail.com · 📱 واتساب: 00905313263722")


class TelegramNotifier:
    def __init__(self):
        self.token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
        self.chat = os.environ.get("TELEGRAM_CHAT_ID", "")

    @property
    def enabled(self) -> bool:
        return bool(self.token and self.chat)

    def send(self, html: str) -> bool:
        if not self.enabled:
            return False
        req = urllib.request.Request(
            f"https://api.telegram.org/bot{self.token}/sendMessage",
            data=json.dumps({"chat_id": self.chat, "text": html,
                             "parse_mode": "HTML", "disable_web_page_preview": True}).encode(),
            headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=20) as r:
                return json.loads(r.read().decode()).get("ok", False)
        except Exception:
            return False

    def ingest_report(self, doc_id: str, n_chunks: int, card: Dict[str, Any],
                      store_stats: Dict[str, Any], provider: str) -> bool:
        facts = "، ".join((card.get("facts") or [])[:4]) or "—"
        ents = "، ".join((card.get("entities") or [])[:5]) or "—"
        msg = (f"🧠 <b>تقرير أرشفة ذاكرة:</b> تم حفظ المستند «{doc_id}».\n"
               f"📦 القطع المخزنة: <b>{n_chunks}</b> بطاقة ذاكرة دلالية.\n"
               f"🔎 أهم الحقائق: {facts}\n"
               f"🏷️ الكيانات: {ents}\n"
               f"🗄️ إجمالي الذاكرة: {store_stats.get('memories',0)} ذكر "
               f"| {store_stats.get('tokens_stored',0)} توكن تقديري\n"
               f"⚙️ مزوّد الذكاء: {provider}" + SIGN)
        return self.send(msg)

    def recall_report(self, question: str, ans: Dict[str, Any],
                      latency_ms: float) -> bool:
        cites = ", ".join(ans.get("cited_chunk_ids", [])[:3]) or "—"
        msg = (f"💭 <b>استرجاع من الذاكرة طويلة المدى:</b>\n"
               f"❓ السؤال: {question[:120]}\n"
               f"✅ الإجابة المدعومة: {ans.get('answer_summary','')[:400]}\n"
               f"🔗 المصادر: {cites}\n"
               f"📊 الثقة: {int(float(ans.get('confidence',0))*100)}% "
               f"| ⏱️ {latency_ms:.0f}ms" + SIGN)
        return self.send(msg)

    def weekly_digest(self, stats: Dict[str, Any], top_memories: list) -> bool:
        rows = "".join(
            f"\n• <code>{m['chunk_id']}</code> — دُخلت {m['accesses']} مرة "
            f"(قوة {(m['recency']*100):.0f}%)" for m in top_memories[:5])
        msg = (f"📅 <b>الملخص الأسبوعي لذاكرة الوكلاء:</b>\n"
               f"🗃️ إجمالي الذكريات: {stats.get('memories',0)}\n"
               f"📚 المستندات المؤرشفة: {stats.get('documents',0)}\n"
               f"🔥 الذكريات الساخنة: {stats.get('hot_memories',0)}" + rows + SIGN)
        return self.send(msg)


if __name__ == "__main__":
    n = TelegramNotifier()
    print("telegram_enabled=", n.enabled)
