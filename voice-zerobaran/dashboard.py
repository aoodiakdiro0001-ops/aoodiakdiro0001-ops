# -*- coding: utf-8 -*-
"""
Voice-ZeroBaran — Project #36 | ZeroBaran Studio
Copyright (c) 2026 Baran Avisat. Support: Baranavisat@gmail.com | WhatsApp 00905313263722

Streamlit Dashboard (free tier) — Arabic RTL studio control panel:
overview KPIs, voice lab (TTS + enhance with inline players), media/video builder,
archive & governance. Runs with zero keys; enriches automatically when configured.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import streamlit as st  # noqa: E402

from vzb import audio_lab, gateway, store, tts_engine, voice_brain  # noqa: E402
from vzb.config import CFG, OUTPUT_DIR  # noqa: E402

st.set_page_config(page_title="Voice-ZeroBaran Studio", page_icon="🎙️", layout="wide")

STORE = store.STORE


def header():
    st.markdown(
        f"""<div style='background:linear-gradient(90deg,#102a43,#880e4f);color:white;
        padding:14px 20px;border-radius:12px;margin-bottom:14px'>
        <h2 style='margin:0'>🎙️ استوديو Voice-ZeroBaran — الصوتيات والوسائط المجانية الذاتية</h2>
        <p style='margin:4px 0 0'>توليد صوتي بشري، هندسة ترددات، تنقية، وبناء فيديو — بتكلفة صفر ·
        © {CFG.author} · {CFG.support_email} · واتساب {CFG.support_whatsapp}</p></div>""",
        unsafe_allow_html=True)


header()

tab_ov, tab_voice, tab_lab, tab_video, tab_arch = st.tabs(
    ["📊 نظرة عامة", "🗣️ مختبر الصوت TTS", "🎛️ هندسة وتنقية", "🎬 بناء فيديو", "🗄️ الأرشيف"])

with tab_ov:
    s = STORE.stats()
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("إجمالي العمليات", s["jobs_total"])
    c2.metric("أصول وسائط", s["assets"])
    c3.metric("محرك السيناريو", "Groq/Gemini" if (CFG.has_groq or CFG.has_gemini) else "Mock محلي (مجاني)")
    c4.metric("قناة تليجرام", "مفعّلة ✅" if CFG.has_telegram else "غير مفعّلة")
    st.progress(min(1.0, s["jobs_total"] / 25), text=f"نسبة امتلاء الحصة المجانية (~25 عملية/يوم CI)")
    st.caption("💡 كل الطبقات تعمل بدون أي مفاتيح. إضافة المفاتيح ترفع الجودة فقط.")

with tab_voice:
    st.subheader("تحويل نص إلى تعليق صوتي احترافي")
    txt = st.text_area("النص (عربي/إنجليزي)", height=140,
                       value="مرحباً بكم في استوديو فويس زيرو باران. صوت مجاني بلا حدود.")
    colA, colB = st.columns([2, 1])
    with colB:
        voice = st.selectbox("الصوت", list(tts_engine.VOICES.keys()))
        speed = st.slider("السرعة", 0.7, 1.4, 1.0, 0.05)
        auto_polish = st.checkbox("تحسين تلقائي (مستوى بث)", True)
        send_tg = st.checkbox("إرسال للموبايل عبر تليجرام", CFG.has_telegram)
    with colA:
        if st.button("🎙️ توليد الصوت", type="primary"):
            with st.spinner("المحرك الصوتي يعمل..."):
                res = json.loads(json.dumps({"ok": True}))
                out = OUTPUT_DIR / f"ui_{abs(hash(txt + voice)) % 10**8}.wav"
                p = tts_engine.tts(txt[:CFG.max_chars_per_job], out, voice=voice, speed=speed)
                if auto_polish:
                    a = audio_lab.load_wav(p)
                    audio_lab.save_wav(p, audio_lab.normalize_loudness(audio_lab.compress(a)))
                rep = audio_lab.analyze(audio_lab.load_wav(p))
                mp3 = audio_lab.to_mp3(p)
                job = {"id": f"tts-{p.stem}", "type": "tts", "title": txt[:60],
                       "voice": voice, "quality_grade": rep.quality_grade,
                       "duration_s": rep.duration_s, "issues": rep.issues}
                STORE.record_job(job, p)
                st.success(f"✅ درجة الجودة: {rep.quality_grade} · المدة: {rep.duration_s}s")
                st.audio(str(mp3), format="audio/mp3")
                st.download_button("📥 تحميل MP3", mp3.read_bytes(), mp3.name, "audio/mpeg")
                if send_tg and CFG.has_telegram:
                    gateway.report_job("توليد صوتي (واجهة)", txt[:40],
                                       {"الجودة": rep.quality_grade}, p)

with tab_lab:
    st.subheader("هندسة الترددات وتنقية الملفات")
    up = st.file_uploader("ارفع ملف WAV/Podcast/تسجيل خام", type=["wav"])
    preset = st.selectbox("القالب الاستوديوهاتي",
                          ["broadcast", "podcast", "voiceover", "clean"], index=0)
    if up is not None:
        raw = OUTPUT_DIR / f"ui_raw_{up.name}"
        raw.write_bytes(up.getvalue())
        if st.button("🎛️ معالجة"):
            r = audio_lab.process_file(raw, OUTPUT_DIR / f"ui_{preset}_{up.name}", preset)
            b, a = r["before"], r["after"]
            m1, m2, m3 = st.columns(3)
            m1.metric("الدرجة قبل", b["quality_grade"], f'RMS {b["rms_db"]:.1f}dB')
            m2.metric("الدرجة بعد", a["quality_grade"], f'RMS {a["rms_db"]:.1f}dB')
            m3.metric("الضجيج المكتشف", ", ".join(b["issues"]) or "لا شيء")
            st.audio(str(r["dst"]), format="audio/wav")
            st.download_button("📥 تحميل النسخة النقية", Path(r["dst"]).read_bytes(),
                               Path(r["dst"]).name, "audio/wav")
            STORE.record_job({"id": f"enh-{raw.stem}-{preset}", "type": "enhance",
                              "title": up.name, "preset": preset,
                              "grade_before": b["quality_grade"],
                              "grade_after": a["quality_grade"]}, Path(r["dst"]))

with tab_video:
    st.subheader("Hyperframes-style: slideshow متزامن مع التعليق الصوتي")
    imgs = st.file_uploader("صور الإطارات (PNG/JPG)", type=["png", "jpg", "jpeg"], accept_multiple_files=True)
    aud = st.file_uploader("ملف الصوت الخلفي (WAV)", type=["wav"])
    per = st.slider("مدة كل إطار (ثانية)", 1.0, 6.0, 2.5, 0.5)
    if imgs and aud and st.button("🎬 بناء الفيديو"):
        fr_dir = OUTPUT_DIR / "_ui_frames"
        fr_dir.mkdir(exist_ok=True)
        for im in imgs:
            (fr_dir / im.name).write_bytes(im.getvalue())
        wav_p = OUTPUT_DIR / f"ui_{aud.name}"
        wav_p.write_bytes(aud.getvalue())
        r = job_v = None
        sys.path.insert(0, str(Path(__file__).resolve().parent / "scripts")); from vzb_orch import job_video
        r = job_video(fr_dir, wav_p, per)
        if "asset" in r:
            st.video(str(r["asset"]))
            st.success(f"تم بناء {Path(r['asset']).name}")
        else:
            st.error(r.get("error", "فشل البناء"))

with tab_arch:
    st.subheader("الأرشيف والسجلات")
    data = STORE.local.data
    if data["jobs"]:
        st.json(data["jobs"][-15:], expanded=False)
        st.caption(f"الخلفية: {'Supabase + Local' if CFG.has_supabase else 'Local JSON (مجاني بالكامل)'}")
    else:
        st.info("لا توجد عمليات بعد — استخدم المختبر أعلاه.")
    st.divider()
    st.markdown(f"""
    **⚖️ السيادة والملكية:** كل المعالجة محلية/سحابيتك الخاصة. لا تُرسل نصوصك لأي وسيط تجاري.  
    © 2026 **{CFG.author}** — ZeroBaran Studio · [بريد الدعم]({CFG.support_email}) · واتساب {CFG.support_whatsapp}
    """)


if __name__ == "__main__":
    pass
