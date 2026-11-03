#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LLM-Router-ZeroBaran — Project #37 | Streamlit Command Center (free)
Author : Baran Avisat  <Baranavisat@gmail.com>  WhatsApp: 00905313263722
Copyright (c) 2026 Baran Avisat — ZeroBaran Studio. MIT License.
Run: streamlit run dashboard.py
"""
import json, os, sys, time
from datetime import datetime

import pandas as pd
import streamlit as st

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "scripts"))
import store, router  # noqa: E402

st.set_page_config(page_title="LLM-Router-ZeroBaran", page_icon="📈", layout="wide")
st.markdown("## 📈 LLM-Router-ZeroBaran — مركز التحليل المالي والتوجيه الذكي")
st.caption("Project #37 · Baran Avisat · ZeroBaran Studio · دعم قرار آلي 100% مجاني — ليس نصيحة مالية")

tab1, tab2, tab3, tab4 = st.tabs(["📊 لوحة القيادة", "🧠 سجل التحليلات", "🎯 الإشارات والأداء", "🤖 الراوتر وحالة النظام"])

analyses = store.fetch_recent("analysis", 200)
signals = store.fetch_recent("signals", 200)
rs = router.stats_summary()
perf = store.performance_summary()

with tab1:
    c = st.columns(5)
    c[0].metric("تحليلات مسجلة", perf["analyses_logged"])
    c[1].metric("إشارات مفتوحة/إجمالي", f"{sum(1 for s in signals if s.get('outcome')=='open')}/{len(signals)}")
    c[2].metric("نسبة نجاح الإشارات المغلقة", f"{(perf['win_rate'] or 0)*100:.0f}%")
    c[3].metric("متوسط PnL%", f"{perf['avg_pnl_pct']}")
    c[4].metric("💰 التكلفة الموفَّرة (تقديري)", f"${rs['total_saved_usd']:.4f}")
    if analyses:
        df = pd.DataFrame(analyses)
        df["dt"] = pd.to_datetime(df["ts"], unit="s")
        df = df.sort_values("ts")
        st.subheader("مؤشر الاتجاه (Trend Score ±100) لكل رمز")
        for sym, g in df.groupby("symbol"):
            st.line_chart(g.set_index("dt")["trend_score"].astype(float), height=120)
            st.caption(sym)
        st.subheader("آخر الأسعار")
        st.dataframe(df[["dt", "symbol", "price", "trend_score", "confidence", "provider"]].tail(15),
                     use_container_width=True)
    else:
        st.info("لا توجد تحليلات بعد — نفّذ `python scripts/llm_router.py run` أو انتظر GitHub Actions.")

with tab2:
    if analyses:
        for a in analyses[:20]:
            with st.expander(f"🧠 {a['symbol']} @ {datetime.fromtimestamp(a['ts']).strftime('%Y-%m-%d %H:%M')} — "
                             f"trend {a.get('trend_score')} conf {a.get('confidence')}% "
                             f"[{a.get('provider')}/{a.get('model')}]"):
                st.write(a.get("narrative", ""))
                try:
                    st.json(json.loads(a.get("plan", "{}")))
                except Exception:
                    pass
                st.code(", ".join(json.loads(a.get("signals", "[]"))), language="text")
    else:
        st.info("السجل فارغ.")

with tab3:
    if signals:
        sdf = pd.DataFrame(signals)
        sdf["dt"] = pd.to_datetime(sdf["ts"], unit="s")
        st.dataframe(sdf[["dt", "symbol", "side", "entry", "stop_loss", "take_profit_1",
                          "outcome", "pnl_pct"]], use_container_width=True)
        closed = sdf[sdf["outcome"].isin(["tp1_hit", "sl_hit"])]
        if len(closed):
            st.bar_chart(closed["pnl_pct"].astype(float))
        st.download_button("⬇️ تصدير CSV", sdf.to_csv(index=False).encode(),
                           "lrz_signals.csv", "text/csv")
    else:
        st.info("لا إشارات بعد.")

with tab4:
    st.subheader("أداء النماذج الموجَّهة (Router Stats)")
    rows = [{"النموذج": k, **v} for k, v in rs["models"].items()]
    st.dataframe(pd.DataFrame(rows), use_container_width=True) if rows else st.write(rs)
    st.markdown("**مسار التوجيه:** Ollama محلي ($0، خصوصية كاملة) ← Groq Free ← Gemini Free ← Mock (CI)")
    st.divider()
    with st.form("ask_form"):
        q = st.text_area("اسأل الراوتر مباشرة (سيُصنَّف ويُوجَّه لأرخص نموذج قادر):",
                         value="لخص مخاطر محفظة AAPL/BTC بنسب مئوية")
        if st.form_submit_button("🚀 وجّه السؤال"):
            rr = router.route(q)
            st.success(f"وُجّه إلى {rr.provider}/{rr.model} · مهمة {rr.task.kind}/{rr.task.complexity} "
                       f"· {rr.latency_ms}ms · توفير تقديري ${rr.cost_saved_usd:.6f}")
            st.write(rr.text)
    st.caption("© 2026 Baran Avisat · Baranavisat@gmail.com · واتساب 00905313263722 · MIT")
