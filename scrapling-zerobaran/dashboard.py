#!/usr/bin/env python3
# =====================================================================
#  Scrapling-ZeroBaran — Streamlit Command Center (Layer 4 UI)
#  Project #38 | Author: Baran Avisat | WhatsApp: 00905313263722
#  Run: streamlit run dashboard.py
# =====================================================================
import json
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE / "scripts"))

import streamlit as st  # noqa: E402

st.set_page_config(page_title="Scrapling-ZeroBaran", page_icon="🕸️", layout="wide")
st.title("🕸️ Scrapling-ZeroBaran — مركز قيادة الزحف الذاتي")
st.caption("© Baran Avisat • Baranavisat@gmail.com • واتساب: 00905313263722 • ZeroBaran Studio")

STATE = BASE / "state"


def load(f):
    try:
        return json.loads((STATE / f).read_text(encoding="utf-8"))
    except Exception:
        return {}


records = load("records.json")
runs = load("runs.json")

tab1, tab2, tab3, tab4 = st.tabs(["📊 النظرة العامة", "🗃️ السجلات", "🔔 سجل الجلسات", "🧭 الحوكمة"])

with tab1:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("إجمالي السجلات", len(records))
    c2.metric("جلسات الزحف", len(runs))
    newest = max(runs.values(), key=lambda r: r.get("ts", 0), default={})
    c3.metric("أحدث جلسة — سجلات جديدة", newest.get("records_new", 0))
    c4.metric("حواجز رُصدت (آخر جلسة)", newest.get("blocks_detected", 0))
    if records:
        import pandas as pd
        df = pd.DataFrame(list(records.values()))
        st.subheader("التوزيع حسب الهدف")
        st.bar_chart(df.groupby("target").size())
        st.subheader("التوزيع حسب تصنيف الذكاء الاصطناعي")
        st.bar_chart(df.groupby("category").size())

with tab2:
    q = st.text_input("🔍 بحث في البيانات المستخرجة", "")
    rows = []
    for r in records.values():
        blob = json.dumps(r, ensure_ascii=False).lower()
        if q.lower() in blob:
            rows.append({"الهدف": r.get("target"), "التصنيف": r.get("category"),
                         "العنوان": str(r.get("fields", {}).get("text") or r.get("fields", {}).get("title") or "")[:90],
                         "السعر/التقييم": json.dumps(r.get("values", {}), ensure_ascii=False),
                         "الرابط": r.get("url", ""), "آخر رؤية": r.get("last_seen")})
    if rows:
        import pandas as pd
        st.dataframe(pd.DataFrame(rows), use_container_width=True, height=420)
        st.download_button("📥 تصدير CSV", pd.DataFrame(rows).to_csv(index=False).encode("utf-8-sig"),
                           file_name="scrapling_zerobaran.csv", mime="text/csv")
    else:
        st.info("لا سجلات بعد — شغّل: python scripts/scrape_run.py run")

with tab3:
    for run in sorted(runs.values(), key=lambda r: r.get("ts", 0), reverse=True)[:30]:
        with st.expander(f"🕒 {run.get('run_id')} — {run.get('status')} — "
                         f"{run.get('pages_fetched')} صفحة / +{run.get('records_new')} جديد / "
                         f"~{run.get('records_changed')} تغيّر"):
            st.json(run)

with tab4:
    st.markdown(
        "**مبادئ المنظومة (Ethical-by-Design):**\n"
        "1. ✅ احترام robots.txt دائماً — البوابة تُسقط أي مسار محظور قبل الطلب.\n"
        "2. 🐢 تخنيق مهذب عشوائي (1–3 ثوانٍ لكل مضيف) — لا إزعاج للسيرفرات.\n"
        "3. 🚨 قاطع دائرة (Circuit Breaker): عند 3 حواجز متتالية يتوقف النظام بأدب ولا يطرق الباب أكثر.\n"
        "4. 🚫 ممنوع تماماً: تجاوز جدران الدفع/تسجيل الدخول، جمع بيانات أشخاص خاصة بلا أساس قانوني، حصاد كلمات المرور.\n"
        "5. 🔐 السيادة: بياناتك تُخزَّن في بيئتك (Supabase مجانيتك أو JSON محلي) — صفر مشاركة خارجية.\n\n"
        "> أنت مسؤول قانونياً عن أهداف الزحف التي تختارها؛ استخدم مواقع تسمح بالزحف أو تملك حق جمعه."
    )
