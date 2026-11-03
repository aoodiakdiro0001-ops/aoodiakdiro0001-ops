#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agent-Mem-ZeroBaran — Streamlit Command Center (free UI layer)
===========================================================
Project #34 — © Baran Avisat · Baranavisat@gmail.com · WhatsApp 00905313263722
Run: streamlit run dashboard.py
"""
import json
import os
import sys

import streamlit as st

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "scripts"))
from mem_engine import MemoryEngine  # noqa: E402

st.set_page_config(page_title="Agent-Mem-ZeroBaran", page_icon="🧠", layout="wide")
st.title("🧠 Agent-Mem-ZeroBaran — الذاكرة الاستراتيجية للوكلاء")
st.caption("مشروع #34 · ZeroBaran Studio · **Baran Avisat** · Baranavisat@gmail.com · واتساب 00905313263722")

@st.cache_resource
def get_eng():
    return MemoryEngine()

eng = get_eng()
stats = eng.stats()

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("🗃️ الذكريات", stats.get("memories", 0))
c2.metric("📚 المستندات", stats.get("documents", 0))
c3.metric("🔥 ذكريات ساخنة", stats.get("hot_memories", 0))
c4.metric("⚙️ المخزن", stats.get("store_mode", "-"))
c5.metric("🧠 العقل", stats.get("brain_provider", "-"))

tab_q, tab_add, tab_cards, tab_chat = st.tabs(["💭 استرجاع حي", "➕ أرشفة ذاكرة", "🏷️ بطاقات الذاكرة", "🔌 تكامل الوكلاء"])

with tab_q:
    q = st.text_input("اسأل ذاكرة الوكلاء (عربي/إنجليزي):",
                      "ما القرارات التي اتخذت بخصوص الميزانية؟")
    topk = st.slider("عدد البطاقات المسترجعة", 1, 10, 5)
    if st.button("🔎 استرجع الآن") and q:
        res = eng.recall(q, top_k=topk)
        st.success(f"✅ إجابة مدعومة بالذاكرة — ثقة {int(res['confidence']*100)}% "
                   f"| زمن {res['latency_ms']}ms | توكن محقون {res['injected_tokens']}")
        st.markdown(f"**{res['answer_summary']}**")
        with st.expander("🔗 بطاقات المصدر"):
            for r in res["retrieved"]:
                st.code(f"{r['chunk_id']}  cos={r['cosine']}  score={r['score']}")
        st.text_area("📋 context_block جاهز للحقن في prompt الوكيل:",
                     res.get("context_block", ""), height=180)

with tab_add:
    doc_id = st.text_input("معرّف المستند", "project-notes-001")
    txt = st.text_area("النص/المحضر/سجل المحادثة:", height=220)
    if st.button("🧠 احفظ في الذاكرة طويلة المدى") and doc_id and txt:
        r = eng.remember(doc_id, txt, source="streamlit")
        st.success(f"تم تخزين {r['stored']} بطاقة ذاكرة دلالية.")
        st.json(r["card"])

with tab_cards:
    p = os.path.join(os.path.dirname(__file__), "data", "memory_cards.json")
    if os.path.exists(p):
        cards = json.load(open(p, encoding="utf-8"))
        for did, card in cards.items():
            with st.expander(f"🏷️ {did}"):
                st.markdown(f"**الملخص:** {card.get('summary','')[:300]}")
                cols = st.columns(3)
                cols[0].write("**حقائق:**", "، ".join(card.get("facts", [])[:6]) or "—")
                cols[1].write("**قرارات:**", "؛ ".join(card.get("decisions", [])[:3]) or "—")
                cols[2].write("**وسوم:**", "، ".join(card.get("tags", [])[:6]) or "—")
    else:
        st.info("لا توجد بطاقات بعد — أرسل أول مستند من تبويب الأرشفة.")

with tab_chat:
    st.markdown("""**امنح أي وكيلاً ذاكرة فورية عبر HTTP (كل شيء مجاني وخاص):**
```bash
# أرشفة
curl -X POST http://localhost:8788/remember -H 'Content-Type: application/json' \\
  -d '{"doc_id":"sprint-notes","text":"قررنا..."}'
# استرجاع مع حقن سياق مضغوط
curl -X POST http://localhost:8788/recall -H 'Content-Type: application/json' \\
  -d '{"question":"ما قرار الميزانية؟","top_k":5}'
```
شغّل البوابة: `python scripts/gateway.py` — أو اربطه بـ LangChain/LlamaIndex
كأداة `recall(question)` تعيد `context_block` جاهزة للصق في الـ prompt.""")
    st.json(stats)
