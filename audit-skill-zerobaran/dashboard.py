#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Audit-Skill-ZeroBaran — Command Center (Streamlit, free tier)
=============================================================
Project #35 | Baran Avisat | ZeroBaran Studio
Baranavisat@gmail.com | WhatsApp 00905313263722 | MIT (c) 2026

Run:  streamlit run dashboard.py
Tabs: 📊 الوضع الأمني | 🚨 الثغرات المفتوحة | 🧬 سجل الفحوصات | 🔍 فحص جديد | ⚖️ الحوكمة
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "scripts"))

from scanners import scan                    # noqa: E402
from audit_brain import enrich_report        # noqa: E402
from store import Store                      # noqa: E402

st.set_page_config(page_title="Audit-Skill-ZeroBaran", page_icon="🛡️", layout="wide")
st.sidebar.title("🛡️ Audit-Skill-ZeroBaran")
st.sidebar.caption("الحارس الأمني الذاتي للأكواد ووكلاء الذكاء الاصطناعي\n\n"
                   "© **Baran Avisat** — ZeroBaran Studio\n"
                   "📧 Baranavisat@gmail.com\n📱 واتساب: 00905313263722")

store = Store()
stats = store.stats()
open_f = store.open_findings()
trend = store.trend()

tab_posture, tab_open, tab_history, tab_new, tab_gov = st.tabs(
    ["📊 الوضع الأمني", "🚨 الثغرات المفتوحة", "🧬 سجل الفحوصات", "🔍 فحص جديد", "⚖️ الحوكمة"])

with tab_posture:
    c = st.columns(4)
    c[0].metric("درجة الأمان", f"{stats.get('latest_score') or 0}/100")
    c[1].metric("ثغرات مفتوحة", stats["open_findings"])
    c[2].metric("تم إصلاحها", stats["fixed_findings"])
    c[3].metric("عمليات التدقيق", stats["total_scans"])
    if trend:
        df = pd.DataFrame(trend)
        df["ts"] = pd.to_datetime(df["ts"])
        st.line_chart(df.set_index("ts")["score"], use_container_width=True)
    sev = stats.get("open_by_severity", {})
    if sev:
        st.bar_chart(pd.DataFrame({"عددها": [sev.get(k, 0) for k in ("CRITICAL", "HIGH", "MEDIUM", "LOW")]},
                                  index=["CRITICAL", "HIGH", "MEDIUM", "LOW"]))
    top_rules = stats.get("top_rules", {})
    if top_rules:
        st.markdown("**أكثر قواعد الرصد تكراراً**")
        st.dataframe(pd.DataFrame({"rule": list(top_rules), "count": list(top_rules.values())}),
                     hide_index=True, use_container_width=True)

with tab_open:
    if not open_f:
        st.success("✅ لا ثغرات مفتوحة — أسطولك نظيف.")
    else:
        df = pd.DataFrame(open_f)
        show = df[["severity", "rule_id", "title", "file", "line", "cwe",
                   "explanation_ar", "fingerprint"]]
        order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3, "INFO": 4}
        show = show.assign(_o=show.severity.map(order)).sort_values("_o").drop(columns="_o")
        filt = st.multiselect("تصفية حسب الخطورة", ["CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"],
                              default=["CRITICAL", "HIGH"])
        view = show[show.severity.isin(filt)] if filt else show
        st.dataframe(view, hide_index=True, use_container_width=True)
        st.download_button("⬇️ تصدير CSV", view.to_csv(index=False).encode("utf-8-sig"),
                           "audit-open-findings.csv", "text/csv")
        sel = st.selectbox("عرض تفاصيل ثغرة (الكود الآمن للإصلاح)",
                           list(view["fingerprint"]), index=None) if len(view) else None
        if sel:
            row = df[df.fingerprint == sel].iloc[0]
            st.markdown(f"### {row['severity']} — {row['title']}")
            st.text(f"{row['file']}:{row['line']}\n{row.get('snippet','')}")
            if row.get("explanation_ar"):
                st.info(row["explanation_ar"])
            st.code(row.get("secure_fix_code") or "(إصلاح تكويني — راجع fix_hint)", language="python")
            if st.button("✔ة تم الإصلاح — أغلق هذه الثغرة"):
                st.success(store.mark_fixed(sel))
                st.rerun()

with tab_history:
    scans = store._load_local()["scans"]
    if scans:
        sdf = pd.DataFrame(scans)[["ran_at", "project_tag", "security_score",
                                   "verdict", "findings_total", "files_scanned",
                                   "engines", "ai_brains"]]
        st.dataframe(sdf.sort_values("ran_at", ascending=False),
                     hide_index=True, use_container_width=True)
    else:
        st.info("لا سجلات بعد — نفّذ `python scripts/audit.py demo`.")

with tab_new:
    target = st.text_input("المسار أو المستودع المراد تدقيقه", value=str(HERE / "examples/vulnerable_repo"))
    tag = st.text_input("وسم المشروع", value="manual")
    if st.button("🛡️ ابدأ التدقيق الآن", type="primary"):
        with st.spinner("فحص + تحليل ذكي + أرشفة..."):
            rep = enrich_report(scan(target))
            store.save_report(rep, project_tag=tag)
        icon = {"BLOCKED": "🔴", "REJECTED": "🟠", "APPROVED_WITH_WARNINGS": "🟡", "APPROVED": "🟢"}
        st.markdown(f"## {icon[rep['verdict']]} الحكم: **{rep['verdict']}** — {rep['security_score']}/100")
        st.write(rep.get("executive_summary_ar", ""))
        st.json(rep["counts_by_category"])

with tab_gov:
    st.markdown("""
**نطاق مسموح به فقط:** فحص أكواد تملكها أو لديك إذن بفحصها. النظام يعمل محلياً/في سحابتك؛
الأسرار تُخفى (redaction) قبل أي إرسال لمزوّد الذكاء الاصطناعي، ويمكن تشغيل الطبقة الذكية
بالمحرك المحلي دون أي اتصال خارجي. هذا المنتج أداة وقاية (Defensive Security) وليس سلاح هجوم.

**الإصدار:** 1.0.0 · **الترخيص:** MIT © 2026 Baran Avisat — ZeroBaran Studio
""")
