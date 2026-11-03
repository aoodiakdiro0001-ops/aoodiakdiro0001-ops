#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Audit-Skill-ZeroBaran — Layer 2: AI Audit Brain (Zero-Cost)
===========================================================
Project #35 | Author: Baran Avisat | ZeroBaran Studio
Email: Baranavisat@gmail.com | WhatsApp: 00905313263722
License: MIT (c) 2026 Baran Avisat

Turns raw scanner findings into *human-readable Arabic explanations* plus
ready-to-paste secure replacement code, using FREE-tier LLMs:
    Groq API  ->  Gemini API  ->  deterministic MockBrain (offline / CI).

The brain receives the report produced by scanners.scan() and returns an
enriched dict per finding: {explanation_ar, severity_assessed, exploit_scenario,
secure_fix_code, priority}. It also writes a top-level executive summary.

Design notes:
 * Strict JSON contract with repair pass (models love to wrap JSON in fences).
 * Batch mode: one call covers up to N findings to stay inside free quotas.
 * Failover ladder + rate-limit backoff; if every remote brain fails, the
   MockBrain guarantees the pipeline NEVER dies (CI always green).
 * Nothing is sent to the LLM except sanitized snippets (secrets redacted).
"""
from __future__ import annotations

import json
import os
import re
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

__author__ = "Baran Avisat"

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
GEMINI_URL = ("https://generativelanguage.googleapis.com/v1beta/models/"
              "{model}:generateContent?key={key}")

SYSTEM_PROMPT = """You are Audit-Skill, a senior application-security auditor (OWASP Top 10 + OWASP LLM Top 10) working for ZeroBaran Studio.
For each finding you MUST output STRICT JSON (no markdown fences) with keys:
{
 "id": "<fingerprint echoed>",
 "severity_assessed": "CRITICAL|HIGH|MEDIUM|LOW",
 "exploitable": true|false,
 "explanation_ar": "<شرح مختصر بالعربية الفصحى يوضح الثغرة وأثرها على المشروع أو الوكيل>",
 "exploit_scenario": "<سيناريو استغلال واقعي بسطر واحد>",
 "secure_fix_code": "<كود آمن جاهز للاستبدال، أو '' إذا الإصلاح تكويني>",
 "priority_rank": <1..10 حيث 1 أعلى أولوية>
}
Rules: never invent line numbers; keep fixes minimal and idiomatic; if the
finding is a false positive say so via exploitable=false and explain why."""


def _post_json(url: str, payload: dict, headers: dict, timeout: int = 60) -> dict:
    req = urllib.request.Request(url, data=json.dumps(payload).encode(),
                                 headers={"Content-Type": "application/json", **headers})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode())


def redact(text: str) -> str:
    """Never leak real secrets to any provider — mask before sending."""
    text = re.sub(r"(AKIA[0-9A-Z]{16})", r"AKIA_****", text)
    text = re.sub(r"(ghp_)[A-Za-z0-9]{36}", r"\1****", text)
    text = re.sub(r"(sk-)[A-Za-z0-9]{20,}", r"\1****", text)
    text = re.sub(r"(AIza)[0-9A-Za-z_\-]{30,}", r"\1****", text)
    text = re.sub(r"(['\"])([A-Za-z0-9+/=_\-]{16,})(['\"])",
                  lambda m: m.group(1) + "***REDACTED***" + m.group(3), text)
    return text[:400]


class AuditBrain:
    def analyze(self, findings: List[Dict[str, Any]], context: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        raise NotImplementedError

    def summarize(self, report: Dict[str, Any], enriched: Dict[str, Dict[str, Any]]) -> str:
        raise NotImplementedError


# ---------------------------------------------------------------- Groq
class GroqBrain(AuditBrain):
    name = "groq"

    def __init__(self, api_key: Optional[str] = None, model: str = "llama-3.3-70b-versatile"):
        self.key = api_key or os.getenv("GROQ_API_KEY", "")
        self.model = model

    def available(self) -> bool:
        return bool(self.key)

    def analyze(self, findings, context):
        user = {"context": {k: context[k] for k in ("target", "security_score", "verdict") if k in context},
                "findings": [{"fingerprint": f["fingerprint"], "rule_id": f["rule_id"],
                              "title": f["title"], "severity": f["severity"],
                              "file": f["file"], "line": f["line"],
                              "snippet": redact(f["snippet"]), "fix_hint": f.get("fix_hint", "")}
                             for f in findings]}
        payload = {"model": self.model,
                   "messages": [{"role": "system", "content": SYSTEM_PROMPT},
                                {"role": "user", "content": json.dumps(user, ensure_ascii=False)}],
                   "temperature": 0.2, "response_format": {"type": "json_object"}}
        data = _post_json(GROQ_URL, payload, {"Authorization": f"Bearer {self.key}"})
        txt = data["choices"][0]["message"]["content"]
        return _parse_batch(txt)

    def summarize(self, report, enriched):
        return _fallback_summary(report, enriched)


# ---------------------------------------------------------------- Gemini
class GeminiBrain(AuditBrain):
    name = "gemini"

    def __init__(self, api_key: Optional[str] = None, model: str = "gemini-1.5-flash"):
        self.key = api_key or os.getenv("GEMINI_API_KEY", "")
        self.model = model

    def available(self) -> bool:
        return bool(self.key)

    def analyze(self, findings, context):
        user = json.dumps({"context": {"target": context.get("target"),
                                       "score": context.get("security_score")},
                           "findings": [{"fingerprint": f["fingerprint"], "rule_id": f["rule_id"],
                                         "title": f["title"], "severity": f["severity"],
                                         "file": f["file"], "line": f["line"],
                                         "snippet": redact(f["snippet"])} for f in findings]},
                          ensure_ascii=False)
        url = GEMINI_URL.format(model=self.model, key=self.key)
        payload = {"systemInstruction": {"parts": [{"text": SYSTEM_PROMPT}]},
                   "contents": [{"role": "user", "parts": [{"text": user}]}],
                   "generationConfig": {"temperature": 0.2, "responseMimeType": "application/json"}}
        data = _post_json(url, payload, {})
        txt = data["candidates"][0]["content"]["parts"][0]["text"]
        return _parse_batch(txt)

    def summarize(self, report, enriched):
        return _fallback_summary(report, enriched)


# ---------------------------------------------------------------- Mock (offline)
CAT_AR = {
    "secret": "تسريب أسرار برمجية (مفاتيح API/كلمات مرور) داخل الكود المصدري",
    "injection": "حقن أكواد عبر إدخال غير مُدخَّل (SQL/OS/Template Injection)",
    "deserialization": "فك تسلسل غير آمن لبيانات خارجية قد يقود لتنفيذ كود عن بُعد",
    "crypto": "استخدام خوارزميات تشفير ضعيفة أو تعطيل التحقق من شهادات TLS",
    "ssrf": "طلب خادم موجّه ببيانات المستخدم (SSRF) قد يكشف الشبكة الداخلية",
    "agent": "ثغرة خاصة بوكلاء الذكاء الاصطناعي (Prompt Injection / صلاحيات مفرطة)",
    "iaco": "إعداد غير آمن للبنية التحتية/حاويات Docker يسمح بتصعيد الصلاحيات",
    "deps": "اعتماد على مكتبة معروفة بثغرات حرجة أو إصدار غير مثبت",
    "config": "إعداد تشغيلي غير آمن في وضع الإنتاج",
    "misc": "ممارسة برمجية غير آمنة تستوجب المراجعة",
}

FIX_TPL = {
    "ASZ-INJ-001": "cur.execute('SELECT * FROM users WHERE id = %s', (user_id,))",
    "ASZ-INJ-003": "subprocess.run(['ls', '-l', target_dir], shell=False, check=True)",
    "ASZ-DESER-001": "data = json.loads(raw)  # instead of pickle.loads on untrusted bytes",
    "ASZ-DESER-002": "cfg = yaml.safe_load(open(path, encoding='utf-8'))",
    "ASZ-CRY-002": "requests.get(url, verify=True)  # keep cert validation ON",
    "ASZ-SEC-001": 'API_KEY = os.environ["API_KEY"]  # value lives only in secret manager',
    "ASZ-AGT-004": "require_confirmation = True  # human-in-the-loop for irreversible actions",
    "ASZ-AGT-002": "system_prompt = FIXED_TEMPLATE  # never interpolate user content here",
}


class MockBrain(AuditBrain):
    """Deterministic offline auditor — keeps every layer contract-valid without keys."""
    name = "mock"

    def available(self) -> bool:
        return True

    def analyze(self, findings, context):
        out: Dict[str, Dict[str, Any]] = {}
        for i, f in enumerate(findings):
            cat = f.get("category", "misc")
            sev = f.get("severity", "MEDIUM")
            expl = (f"{CAT_AR.get(cat, CAT_AR['misc'])}. الرصد: «{f['title']}» "
                    f"في الملف {f['file']} السطر {f['line']}.")
            scenario = {
                "secret": "متسلل يطّلع على المستودع ويسرق المفتاح ويستهلك رصيدك أو بيانات عملائك.",
                "injection": "مستخدم يمرر نص SQL خبيث form field فيسحب كامل قاعدة البيانات.",
                "deserialization": "ملف خبيث يُرفع للنظام فيُنفَّذ كود بأي صلاحيات العملية.",
                "crypto": "وسيط في الشبكة يقوّض الاتصال ويقرأ البيانات الحساسة.",
                "ssrf": "مهاجم يستدعي رابط metadata السحابي ويسرّب credentials الدور.",
                "agent": "تعليق خبيث يتضمّن تعليمات مخفية يجعل الوكيل ينفّذ أوامر المهاجم.",
                "iaco": "حاوية متميزة تخرج من عزلتها وتسيطر على مضيف الاستضافة.",
                "deps": "الإصدار القديم معروف CVE يُستغل آلياً خلال ساعات من النشر.",
                "config": "صفحة debug تكشف stack trace وأسرار بيئة التشغيل لأي زائر.",
            }.get(cat, "قد يستغل مهاجم مدخل غير محصّن للوصول لبيانات أو تنفيذ أوامر.")
            fix = FIX_TPL.get(f.get("rule_id", ""), f.get("fix_hint", ""))
            out[f["fingerprint"]] = {
                "id": f["fingerprint"], "severity_assessed": sev,
                "exploitable": sev in ("CRITICAL", "HIGH"),
                "explanation_ar": expl, "exploit_scenario": scenario,
                "secure_fix_code": fix, "priority_rank": max(1, 10 - i),
                "brain": self.name,
            }
        return out

    def summarize(self, report, enriched):
        return _fallback_summary(report, enriched)


# ---------------------------------------------------------------- helpers
def _parse_batch(text: str) -> Dict[str, Dict[str, Any]]:
    """Extract JSON object/array even when models wrap it in ``` fences."""
    t = text.strip()
    fence = re.search(r"```(?:json)?\s*(.+?)```", t, re.S)
    if fence:
        t = fence.group(1).strip()
    try:
        obj = json.loads(t)
    except json.JSONDecodeError:
        m = re.search(r"(\{.*\}|\[.*\])", t, re.S)
        if not m:
            return {}
        obj = json.loads(m.group(1))
    items = obj if isinstance(obj, list) else obj.get("results", [obj] if "id" in obj else [])
    out = {}
    for it in items:
        if isinstance(it, dict) and it.get("id"):
            it.setdefault("brain", "remote")
            out[it["id"]] = it
    return out


def _fallback_summary(report, enriched) -> str:
    c = report["counts_by_severity"]
    verdict = report["verdict"]
    icon = {"BLOCKED": "🔴", "REJECTED": "🟠", "APPROVED_WITH_WARNINGS": "🟡",
            "APPROVED": "🟢"}[verdict]
    lines = [f"{icon} الحكم العام: {verdict} — درجة الأمان {report['security_score']}/100",
             f"الملفات المفحوصة: {report['files_scanned']} | الثغرات: {report['findings_total']} "
             f"(حرجة {c['CRITICAL']}، عالية {c['HIGH']}، متوسطة {c['MEDIUM']})"]
    top = sorted(enriched.values(), key=lambda x: x.get("priority_rank", 99))[:3]
    if top:
        lines.append("أخطر ما يجب إصلاحه فوراً:")
        for e in top:
            lines.append(f"  • {e['explanation_ar']}")
    return "\n".join(lines)


# ---------------------------------------------------------------- facade
def get_brains() -> List[AuditBrain]:
    brains: List[AuditBrain] = []
    g, gem = GroqBrain(), GeminiBrain()
    if g.available():
        brains.append(g)
    if gem.available():
        brains.append(gem)
    brains.append(MockBrain())
    return brains


BATCH_SIZE = 12  # stay inside free-tier request size limits


def enrich_report(report: Dict[str, Any], max_batch_calls: int = 4) -> Dict[str, Any]:
    """Attach AI analysis + executive summary to a scan report (never raises)."""
    findings = report["findings"]
    enriched: Dict[str, Dict[str, Any]] = {}
    used = []
    for brain in get_brains():
        try:
            chunks = [findings[i:i + BATCH_SIZE] for i in range(0, len(findings), BATCH_SIZE)][:max_batch_calls]
            partial: Dict[str, Dict[str, Any]] = {}
            for ch in chunks:
                partial.update(brain.analyze(ch, report))
            if partial:
                enriched.update(partial)
                used.append(brain.name)
            if len(enriched) >= len(findings):
                break
        except Exception:
            continue  # fail over to next brain
    # guarantee full coverage via mock for anything the remotes missed
    missing = [f for f in findings if f["fingerprint"] not in enriched]
    if missing:
        enriched.update(MockBrain().analyze(missing, report))
        if "mock" not in used:
            used.append("mock")
    for f in findings:
        f["ai"] = enriched.get(f["fingerprint"], {})
    report["ai_brains_used"] = used
    report["executive_summary_ar"] = _fallback_summary(report, enriched) \
        if used and used[0] == "mock" else \
        (MockBrain().summarize(report, enriched))
    return report


if __name__ == "__main__":
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent))
    from scanners import scan
    rep = scan(sys.argv[1] if len(sys.argv) > 1 else ".")
    print(json.dumps(enrich_report(rep), ensure_ascii=False, indent=2)[:3000])
