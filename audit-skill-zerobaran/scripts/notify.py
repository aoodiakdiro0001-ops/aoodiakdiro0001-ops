#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Audit-Skill-ZeroBaran — Layer 4: Telegram Delivery & Alerts
===========================================================
Project #35 | Baran Avisat | ZeroBaran Studio
Baranavisat@gmail.com | WhatsApp 00905313263722 | MIT (c) 2026

Sends the exact alert format promised in the design:

   🛡️ تنبيه أمني عاجل: تم رصد ثغرة (High Risk) في ملف المعالجة.
   💻 السبب: استخدام دالة غير آمنة لإدخال البيانات.
   🛠️ الإصلاح المقترح: <الكود الآمن الجاهز للاستبدال>

Plus weekly posture digests and clean-scan confirmations. Degrades to a
dry-run log when no bot token is configured (CI-safe, zero cost).
"""
from __future__ import annotations

import json
import os
import urllib.parse
import urllib.request
from typing import Any, Dict, List, Optional

__author__ = "Baran Avisat"

API = "https://api.telegram.org/bot{token}/{method}"
FOOTER = ("\n\n———\n🛡️ <i>Audit-Skill-ZeroBaran — الحارس الأمني الذاتي</i>\n"
          "© <b>Baran Avisat</b> · ZeroBaran Studio\n"
          "📧 Baranavisat@gmail.com · 📱 واتساب: <code>00905313263722</code>")

SEV_ICON = {"CRITICAL": "🔥", "HIGH": "🟠", "MEDIUM": "🟡", "LOW": "🔵", "INFO": "ℹ️"}


class Notifier:
    def __init__(self, token: Optional[str] = None, chat_id: Optional[str] = None):
        self.token = token or os.getenv("TELEGRAM_BOT_TOKEN", "")
        self.chat_id = chat_id or os.getenv("TELEGRAM_CHAT_ID", "")
        self.enabled = bool(self.token and self.chat_id)

    def _send(self, text: str) -> Dict[str, Any]:
        if not self.enabled:
            return {"ok": True, "dry_run": True, "chars": len(text)}
        url = API.format(token=self.token, method="sendMessage")
        payload = {"chat_id": self.chat_id, "text": text, "parse_mode": "HTML",
                   "disable_web_page_preview": True}
        req = urllib.request.Request(url, data=json.dumps(payload).encode(),
                                     headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=20) as r:
                return json.loads(r.read().decode())
        except Exception as e:  # never crash the pipeline over a notification
            return {"ok": False, "error": str(e)[:200]}

    # ------------------------------------------------------------------
    def alert_critical(self, finding: Dict[str, Any], report_meta: Dict[str, Any]) -> Dict[str, Any]:
        sev = finding["severity"]
        ai = finding.get("ai") or {}
        fix = ai.get("secure_fix_code") or finding.get("fix_hint") or "راجع التوثيق في README"
        msg = (
            f"🛡️ <b>تنبيه أمني عاجل:</b> تم رصد ثغرة ({sev}) في {finding['file']}\n"
            f"⚡ الخطورة: {SEV_ICON.get(sev,'⚪')} {sev} — CWE: {finding.get('cwe','-')}\n"
            f"💻 السبب: {html_escape(finding['title'])}\n"
            f"📍 السطر: {finding['line']} — <code>{html_escape(finding['snippet'][:120])}</code>\n"
            f"🧠 الشرح: {html_escape(ai.get('explanation_ar',''))}\n"
            f"🎯 سيناريو الاستغلال: {html_escape(ai.get('exploit_scenario',''))}\n"
            f"🛠️ الإصلاح المقترح:\n<pre>{html_escape(fix[:900])}</pre>"
            + FOOTER)
        return self._send(msg)

    def scan_report(self, report: Dict[str, Any]) -> List[Dict[str, Any]]:
        out = []
        verdict = report["verdict"]
        icon = {"BLOCKED": "🔴", "REJECTED": "🟠",
                "APPROVED_WITH_WARNINGS": "🟡", "APPROVED": "🟢"}[verdict]
        head = (f"{icon} <b>تقرير التدقيق الأمني — Audit-Skill</b>\n"
                f"🎯 الهدف: <code>{html_escape(str(report['target'])[:120])}</code>\n"
                f"📁 الملفات المفحوصة: {report['files_scanned']} | "
                f"الثغرات: {report['findings_total']}\n"
                f"📊 درجة الأمان: <b>{report['security_score']}/100</b> | الحكم: <b>{verdict}</b>\n"
                f"🔌 المحركات: {', '.join(report['engines'])} | عقل الذكاء: {', '.join(report.get('ai_brains_used', ['mock']))}\n")
        crit = [f for f in report["findings"] if f["severity"] == "CRITICAL"]
        high = [f for f in report["findings"] if f["severity"] == "HIGH"]
        if crit or high:
            top = (crit + high)[:3]
            body = "\n".join(f"  {SEV_ICON[f['severity']]} <b>{f['rule_id']}</b> — "
                             f"{html_escape(f['title'])} <i>({f['file']}:{f['line']})</i>"
                             for f in top)
            head += f"\n🚨 أبرز الثغرات:\n{body}\n"
        else:
            head += "\n✅ لا ثغرات حرجة أو عالية — الكود نظيف.\n"
        head += f"\n📋 الملخص التنفيذي:\n{html_escape(report.get('executive_summary_ar',''))}"
        out.append(self._send(head + FOOTER))
        # individual urgent alerts (rate-limit friendly: max 5)
        for f in crit[:5]:
            out.append(self.alert_critical(f, report))
        return out

    def weekly_digest(self, stats: Dict[str, Any], trend: List[Dict[str, Any]]) -> Dict[str, Any]:
        spark = " ".join({"BLOCKED": "🔴", "REJECTED": "🟠",
                          "APPROVED_WITH_WARNINGS": "🟡", "APPROVED": "🟢"}.get(h["verdict"], "⚪")
                          for h in trend[-14:]) or "—"
        msg = (f"🗓️ <b>الملخص الأسبوعي للوضع الأمني</b>\n"
               f"📈 متوسط درجة الأمان: <b>{stats.get('avg_score','-')}</b>/100 "
               f"(آخر فحص: {stats.get('latest_score','-')})\n"
               f"🧾 إجمالي عمليات التدقيق: {stats.get('total_scans',0)}\n"
               f"🩺 ثغرات مفتوحة: {stats.get('open_findings',0)} | "
               f"مثبت عليها: {stats.get('fixed_findings',0)}\n"
               f"📉 الاتجاه الأخير: {spark}\n")
        tops = list(stats.get("top_rules", {}).items())[:5]
        if tops:
            msg += "🏆 أكثر الأنماط تكراراً:\n" + "\n".join(
                f"  • <code>{rid}</code> ×{n}" for rid, n in tops) + "\n"
        return self._send(msg + FOOTER)


def html_escape(s: str) -> str:
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


if __name__ == "__main__":
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent))
    from scanners import scan
    from audit_brain import enrich_report
    n = Notifier()
    rep = enrich_report(scan(sys.argv[1] if len(sys.argv) > 1 else "."))
    print(json.dumps(n.scan_report(rep), ensure_ascii=False))
