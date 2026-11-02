# ============================================================
#  Pulse-Zero — لوحة السمعة الحية (Streamlit · مجاني بالكامل)
#  التشغيل المحلي:   streamlit run dashboard.py
#  النشر المجاني:    https://share.streamlit.io  (مستودع هذا الملف)
#
#  تقرأ اللوحة بياناته من Supabase مباشرة؛ وإن لم يتوفر الاتصال
#  تعرض بيانات تجريبية حتى تعمل دائماً بلا انقطاع.
# ============================================================

import os
from datetime import datetime, timezone

import pandas as pd
import streamlit as st

st.set_page_config(page_title="Pulse-Zero · Reputation Radar",
                   page_icon="🫀", layout="wide", initial_sidebar_state="expanded")

# ---------------------------------------------------------------- Data access
@st.cache_data(ttl=300, show_spinner="🛰️ جارٍ جلب سجلات السمعة…")
def load_mentions() -> pd.DataFrame:
    url = os.environ.get("SUPABASE_URL", "").strip()
    key = (os.environ.get("SUPABASE_ANON_KEY") or
           os.environ.get("SUPABASE_SERVICE_KEY") or "").strip()
    if url and key:
        try:
            from supabase import create_client  # pip install supabase
            sb = create_client(url, key)
            rows = (sb.table("mentions").select("*")
                    .order("analyzed_at", desc=True).limit(2000).execute().data)
            if rows:
                return pd.DataFrame(rows)
        except Exception as exc:
            st.sidebar.warning(f"Supabase غير متاح ({exc}) — عرض بيانات تجريبية")
    # ---- Demo fallback حتى لا تسقط اللوحة أبداً ----
    now = datetime.now(timezone.utc)
    demo = [
        ("المنتج رائع وسهل الاستخدام!", "positive", 0.85, "praise", "low", "Gumroad"),
        ("المنتج وصل تالفاً ولم يعمل معي", "negative", -0.9, "complaint_technical", "crisis", "Gumroad"),
        ("Best free reputation tool this year", "positive", 0.75, "praise", "low", "Reddit"),
        ("عمليتي لم تصل ولا رد من الدعم!!", "negative", -0.95, "complaint_delivery", "crisis", "Email feed"),
        ("التصميم جميل لكن لوحة التحكم بطيئة", "neutral", -0.1, "other", "medium", "Twitter/X"),
        ("هل يدعم ربط Telegram Bot؟", "neutral", 0.0, "question", "low", "Reddit"),
    ]
    return pd.DataFrame([
        {"id": f"demo{i}", "body": b, "sentiment": s, "score": sc, "category": c,
         "severity": sv, "source_name": src, "author": f"user_{i}",
         "analyzed_at": now.isoformat(), "reply_draft": None, "url": "#"}
        for i, (b, s, sc, c, sv, src) in enumerate(demo)])


df = load_mentions()
df["score"] = pd.to_numeric(df["score"], errors="coerce").fillna(0.0)

# ---------------------------------------------------------------- Header
st.markdown("""
<style>
 .pz-title{font-size:2.2rem;font-weight:800;background:linear-gradient(90deg,#22c55e,#3b82f6,#ef4444);
 -webkit-background-clip:text;-webkit-text-fill-color:transparent;}
 .pz-sub{color:#94a3b8;margin-top:-8px}
 div[data-testid="stMetricValue"]{font-size:1.9rem}
</style>
""", unsafe_allow_html=True)
st.markdown('<div class="pz-title">🫀 Pulse-Zero — رصد مشاعر العملاء وإدارة السمعة</div>'
            '<div class="pz-sub">مجاني 100% · GitHub Actions + Gemini/Groq + Supabase + Telegram</div>',
            unsafe_allow_html=True)

# ---------------------------------------------------------------- KPI row
total = len(df)
pos = int((df.sentiment == "positive").sum())
neg = int((df.sentiment == "negative").sum())
neu = total - pos - neg
avg = float(df.score.mean()) if total else 0.0
rep_index = round((avg + 1) / 2 * 100, 1)
crisis_n = int(df.severity.isin(["high", "crisis"]).sum()) if total else 0

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("🏅 مؤشر السمعة", f"{rep_index}/100")
c2.metric("📡 إجمالي الرصد", total)
c3.metric("🟢 إيجابي", pos)
c4.metric("🔴 سلبي", neg)
c5.metric("🚨 أزمات نشطة", crisis_n, delta=None if crisis_n == 0 else "تحتاج تدخلاً", delta_color="inverse")

if total == 0:
    st.info("لا توجد سجلات بعد — شغّل `python pulse_zero.py` أو انتظر دورة GitHub Actions.")
    st.stop()

tab_live, tab_trend, tab_crisis, tab_all = st.tabs(
    ["📈 الاتجاه العام", "🗓️ عبر الزمن", "🚨 غرفة الأزمات", "🗄️ كل السجلات"])

with tab_live:
    left, right = st.columns([2, 1])
    with left:
        st.subheader("توزيع المشاعر حسب الفئة")
        cat_pivot = (df.pivot_table(index="category", columns="sentiment",
                                    values="id", aggfunc="count", fill_value=0))
        st.bar_chart(cat_pivot)
    with right:
        st.subheader("مزاج آخر ٢٤ ساعة")
        recent = df.sort_values("analyzed_at", ascending=False).head(20)
        score_recent = float(recent.score.mean())
        mood = "😍 سمعة ممتازة" if score_recent > 0.4 else \
               "🙂 جيدة" if score_recent > 0.1 else \
               "😐 مستقرة" if score_recent > -0.15 else "😰 تحت الضغط"
        st.metric("متوسط الدرجات الحديثة", round(score_recent, 2), mood)
        st.progress(max(0.0, min(1.0, (score_recent + 1) / 2)))

with tab_trend:
    st.subheader("مؤشر السمعة اليومي (Sentiment Score عبر الزمن)")
    dft = df.copy()
    dft["day"] = pd.to_datetime(dft.analyzed_at, errors="coerce", utc=True).dt.date
    daily = (dft.dropna(subset=["day"]).groupby("day")
             .agg(avg_score=("score", "mean"), n=("id", "count"))
             .sort_index(ascending=False).head(30).sort_index())
    daily["reputation_index"] = ((daily.avg_score + 1) / 2 * 100).round(1)
    st.line_chart(daily[["reputation_index"]])
    st.caption(f"أحدث يوم: {daily.index[-1] if len(daily) else '—'} — "
               f"النقاط: {int(daily.reputation_index.iloc[-1]) if len(daily) else 0}/100")

with tab_crisis:
    st.subheader("🚨 كل تعليق سلبي يحتاج رداً بشرياً الآن")
    bad = df[(df.sentiment == "negative")].sort_values("score").head(25)
    if bad.empty:
        st.success("✅ صفر شكاوى مفتوحة — سمعتك ناصعة!")
    for _, r in bad.iterrows():
        emoji = {"crisis": "🚨", "high": "⚠️", "medium": "🔶"}.get(r.get("severity"), "ℹ️")
        with st.expander(f'{emoji} [{r.category}] {str(r.body)[:70]}… — {r.source_name}'):
            st.markdown(f"**النص:** {r.body}")
            st.markdown(f"**جذر المشكلة:** {r.get('issue_root') or 'غير محدد'} | "
                        f"**الدرجة:** {r.score} | **المصدر:** {r.author}")
            reply = r.get("reply_draft")
            if reply and str(reply) != "None":
                st.info(f"💡 **الرد المقترح من الذكاء الاصطناعي:**\n\n{reply}")
            if r.get("url") and str(r.url).startswith("http"):
                st.markdown(f"[🔗 فتح المصدر]({r.url})")

with tab_all:
    q = st.text_input("🔍 ابحث في كل الآراء…", "")
    filt = st.multiselect("المشاعر", ["positive", "neutral", "negative"],
                          default=["positive", "neutral", "negative"])
    view = df[df.sentiment.isin(filt)]
    if q:
        mask = view.body.astype(str).str.contains(q, case=False, na=False) | \
               view.title.astype(str).str.contains(q, case=False, na=False)
        view = view[mask]
    st.dataframe(view[["analyzed_at", "source_name", "sentiment", "score",
                       "category", "severity", "body"]].head(500),
                 use_container_width=True, hide_index=True)
    st.download_button("⬇️ تصدير CSV للتقارير",
                       view.to_csv(index=False).encode("utf-8-sig"),
                       file_name=f"pulse-zero-{datetime.now():%Y%m%d}.csv",
                       mime="text/csv")

st.sidebar.markdown("---")
st.sidebar.caption("Pulse-Zero · المشروع #33 — صفر تكلفة، صفر تأخر في الأزمات.")
st.sidebar.caption(f"آخر تحديث للوحة: {datetime.now(timezone.utc):%H:%M UTC}")
