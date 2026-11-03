# -*- coding: utf-8 -*-
"""
Design-Guard-ZeroBaran — لوحة التحكم (Streamlit Dashboard)
===========================================================
Bديل مجاني لوحات Hallmark/Impeccable: مؤشرات الإنتاجية، اتجاهات
القبول عبر الزمن، طابور المراجعة البشرية، ومعرض الأصول المرفوضة
مع العيوب والاقتراحات.

التشغيل محلياً:   streamlit run dashboard.py
على Cloud:        Streamlit Community Cloud (مجاني) + نفس الـ Secrets
المؤلف: Baran Avisat | baranavisat@gmail.com | واتساب: 00905313263722
"""
from collections import Counter
from datetime import datetime
from pathlib import Path

import pandas as pd
import streamlit as st
import yaml

BASE = Path(__file__).resolve().parent
CFG = yaml.safe_load((BASE / "scripts" / "config.yaml").read_text(encoding="utf-8"))

st.set_page_config(page_title="Design-Guard-ZeroBaran | QA Command Center",
                   page_icon="🛡️", layout="wide", initial_sidebar_state="expanded")

# ------------------------------------------------------------------ Data layer
@st.cache_data(ttl=60)
def load_reports():
    import sys
    sys.path.insert(0, str(BASE / "scripts"))
    from store import QaStore
    store = QaStore(CFG, BASE)
    rows = store.recent(limit=1000)
    return rows, store.mode, store.warnings


rows, mode, warnings = load_reports()
df = pd.DataFrame(rows)

VERDICT_COLORS = {"accepted": "#2ecc71", "rejected": "#e74c3c", "needs_review": "#f1c40f"}
VERDICT_AR = {"accepted": "🟢 معتمد", "rejected": "🔴 مرفوض", "needs_review": "🟡 مراجعة"}

# ------------------------------------------------------------------ Sidebar
st.sidebar.title("🛡️ Design-Guard-ZeroBaran")
st.sidebar.caption(f"منظومة مراقبة جودة مخرجات الذكاء الاصطناعي\n\n"
                   f"⚙️ وضع التخزين: `{mode}`\n\n"
                   f"🗂️ آخر تحديث: {datetime.now():%Y-%m-%d %H:%M}")
st.sidebar.image("https://img.shields.io/badge/ZeroBaran_Studio-QA_Guard-111", use_container_width=True)
if st.sidebar.button("🔄 إعادة تحميل البيانات"):
    st.cache_data.clear()
    st.rerun()
for w in warnings[:3]:
    st.sidebar.warning(w)

# ------------------------------------------------------------------ KPIs
st.title("مركز قيادة الجودة — Quality Command Center")
if df.empty:
    st.info("لا توجد تقارير بعد. ضع ملفات في `inbox/` ثم شغّل "
            "`python scripts/design_guard.py --scan` أو جرّب `--demo`.")
    st.stop()

total = len(df)
acc = int((df.verdict == "accepted").sum())
rej = int((df.verdict == "rejected").sum())
rev = total - acc - rej
avg_match = float(df.match_score.mean())
first_pass = acc / total * 100

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("إجمالي الفحوصات", total)
c2.metric("🟢 معتمد", acc, f"{acc/total*100:.0f}%")
c3.metric("🔴 مرفوض", rej, f"-{rej/total*100:.0f}%", delta_color="inverse")
c4.metric("🟡 مراجعة بشرية", rev)
c5.metric("متوسط المطابقة", f"{avg_match:.1f}%")

st.progress(min(first_pass / 100, 1.0), text=f"نسبة القبول من أول محاولة: {first_pass:.1f}%")

tab1, tab2, tab3, tab4 = st.tabs(["📈 الاتجاهات", "🧨 خريطة العيوب", "🧾 سجل الفحوصات", "👤 طابور المراجعة"])

with tab1:
    d = df.copy()
    d["day"] = pd.to_datetime(d.created_at).dt.date
    daily = d.groupby("day").agg(checked=("verdict", "size"),
                                 avg_match=("match_score", "mean")).reset_index()
    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("متوسط مطابقة الهوية يومياً")
        st.line_chart(daily.set_index("day")["avg_match"])
    with col_b:
        st.subheader("أصول مفحوصة يومياً")
        st.bar_chart(daily.set_index("day")["checked"])
    pivot = d.pivot_table(index="day", columns="verdict", values="checksum",
                          aggfunc="count", fill_value=0)
    for v in ["accepted", "rejected", "needs_review"]:
        if v not in pivot.columns:
            pivot[v] = 0
    st.subheader("توزيع القرارات عبر الزمن")
    st.area_chart(pivot[["accepted", "needs_review", "rejected"]].rename(
        columns={"accepted": "🟢 معتمد", "needs_review": "🟡 مراجعة", "rejected": "🔴 مرفوض"}))

with tab2:
    all_defects = [dd.get("type", "?") for lst in df.defects.fillna([]) for dd in lst]
    sev_counter = Counter(dd.get("severity", "minor")
                          for lst in df.defects.fillna([]) for dd in lst)
    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("أكثر العيوب تكراراً")
        top = Counter(all_defects).most_common(12)
        if top:
            s = pd.Series(dict(reversed(top)))
            st.bar_chart(s)
            st.caption("💡 عيب يتكرر؟ عدّل Prompt التوليد لديك بناءً عليه — هذه خريطة إعادة التوليد.")
        else:
            st.success("صفر عيوب مسجّلة 🎉")
    with col_b:
        st.subheader("توزيع الخطورة")
        st.bar_chart(pd.Series(sev_counter).rename_axis("severity").sort_values(ascending=False))

with tab3:
    st.subheader("سجل الفحوصات الكامل")
    filt = st.multiselect("تصفية بالقرار", list(VERDICT_AR.keys()),
                          default=list(VERDICT_AR.keys()),
                          format_func=lambda x: VERDICT_AR[x])
    view = df[df.verdict.isin(filt)]
    show = view[["filename", "kind", "width", "height", "structural_score",
                 "match_score", "verdict", "ai_provider", "created_at"]].copy()
    show["verdict"] = show["verdict"].map(VERDICT_AR)
    st.dataframe(show.style.map(
        lambda v: f"color:{VERDICT_COLORS.get(v,'#333')};font-weight:bold", subset=["verdict"]),
        use_container_width=True, height=420)

    st.download_button("⬇️ تصدير كل التقارير CSV",
                       df.to_csv(index=False).encode("utf-8-sig"),
                       file_name="design_guard_reports.csv", mime="text/csv")

    exps = st.expander("🔎 تفاصيل فحص ملف", expanded=False)
    if exps.selectbox("اختر أصلاً", view.checksum.tolist(),
                      format_func=lambda c: view[view.checksum == c].iloc[0].filename):
        rec = view[view.checksum == exps.session_state.get("selectbox", None)]
        if rec.empty:
            rec = view.iloc[[0]]
        r = rec.iloc[0]
        a, b = st.columns([1, 1])
        with a:
            st.markdown(f"**{r.filename}** — {r.kind} | هيكل {r.structural_score}% | نهائي {r.match_score}%")
            if isinstance(r.archived_to, str) and (BASE / r.archived_to).exists():
                st.image(str(BASE / r.archived_to), use_container_width=True)
            elif r.kind == "text":
                st.text((r.extracted_text or "")[:1200])
        with b:
            st.markdown("**العيوب:**")
            for dd in (r.defects or []):
                st.error(f"[{dd.get('type')}] {dd.get('note_ar','')}") if dd.get("severity") != "minor" \
                    else st.warning(f"[{dd.get('type')}] {dd.get('note_ar','')}")
            if not r.defects:
                st.success("لا عيوب — أصل نظيف.")
            st.markdown(f"**خلاصة الذكاء الاصطناعي:** {r.summary_ar}")
            st.markdown(f"**الإصلاح المقترح:** {r.fix_suggestion_ar}")

with tab4:
    queue = df[df.verdict == "needs_review"]
    st.subheader(f"طابور المراجعة البشرية ({len(queue)})")
    if queue.empty:
        st.success("الطابور فارغ — الحارس يعمل بلا كلل ✅")
    else:
        for _, q in queue.head(20).iterrows():
            with st.container(border=True):
                st.markdown(f"### 🟡 {q.filename} — مطابقة {q.match_score}%")
                st.caption(q.summary_ar or "")
                st.markdown(f"**الإصلاح المقترح:** {q.fix_suggestion_ar or '—'}")
                cols = st.columns(3)
                if cols[0].button("✅ اعتماد يدوي", key=f"a{q.asset_id}"):
                    st.toast(f"تم اعتماد {q.filename} — سجّله في أرشيفك الذهبي.")
                if cols[1].button("❌ رفض نهائي", key=f"r{q.asset_id}"):
                    st.toast(f"رُفض {q.filename} — أعد التوليد.")

st.sidebar.divider()
st.sidebar.markdown(
    "**👤 Baran Avisat** — المؤسس والمطور الرئيسي\n\n"
    "📧 Baranavisat@gmail.com\n\n📱 واتساب: 00905313263722\n\n"
    "🛒 [baranavi.gumroad.com](https://baranavi.gumroad.com/)\n\n"
    "© ZeroBaran Studio — جميع الحقوق محفوظة.")
