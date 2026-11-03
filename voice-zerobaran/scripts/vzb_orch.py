# -*- coding: utf-8 -*-
"""
Voice-ZeroBaran — Project #36 | ZeroBaran Studio
Copyright (c) 2026 Baran Avisat. Support: Baranavisat@gmail.com | WhatsApp 00905313263722

ORCHESTRATOR — the self-driving studio pipeline wiring all 4 layers:

  vzb make-script   "brief"            AI writes narration script (Gemini/Groq/Mock)
  vzb tts           --voice --speed    text -> speech (Bark/Piper/DSP cascade) + QA grade
  vzb enhance       file.wav           studio chain (denoise/EQ/compress/loudness)
  vzb transcribe    file.wav           Whisper STT + WER intelligibility score
  vzb video         --images dir       Hyperframes-style slideshow synced to VO
  vzb deliver       file               push asset to Telegram
  vzb run           brief              FULL end-to-end: script->tts->enhance->QA->store->deliver
  vzb demo          offline deterministic showcase
  vzb stats         archive statistics
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from vzb.config import CFG, OUTPUT_DIR                      # noqa: E402
from vzb import tts_engine, audio_lab, stt_whisper, voice_brain, store, gateway  # noqa: E402

STORE = store.STORE


def _jid(payload: str, kind: str) -> str:
    return f"{kind}-{hashlib.sha1(payload.encode()).hexdigest()[:12]}"


def job_tts(text: str, voice: str = "", speed: float = 1.0,
            deliver: bool = True, preset: str = "voiceover") -> dict:
    jid = _jid(text + voice + str(speed), "tts")
    wav = OUTPUT_DIR / f"{jid}.wav"
    path = tts_engine.tts(text, wav, voice=voice or CFG.default_voice, speed=speed)
    x = audio_lab.load_wav(path)
    polished = audio_lab.normalize_loudness(audio_lab.compress(x), CFG.loudness_target_db)
    audio_lab.save_wav(path, polished)
    rep = audio_lab.analyze(audio_lab.load_wav(path))
    mp3 = audio_lab.to_mp3(path)
    job = {"id": jid, "type": "tts", "title": text[:60], "voice": voice or CFG.default_voice,
           "speed": speed, "preset": preset, "quality_grade": rep.quality_grade,
           "duration_s": rep.duration_s, "issues": rep.issues,
           "engine": "bark/piper" if path.stat().st_size else "vzb-dsp"}
    res = STORE.record_job(job, path)
    if deliver and CFG.has_telegram:
        gateway.report_job("توليد صوتي (TTS)", text[:50],
                           {"الجودة": rep.quality_grade, "المدة": f"{rep.duration_s}s",
                            "الصوت": job["voice"], "الملف": mp3.name}, path)
    return {"job": job, "storage": res, "asset": str(path), "mp3": str(mp3)}


def job_enhance(src: Path, preset: str = "broadcast", deliver: bool = True) -> dict:
    src = Path(src)
    jid = _jid(str(src.resolve()) + str(src.stat().st_mtime) + preset, "enh")
    out = OUTPUT_DIR / f"{src.stem}_{preset}_{jid[-6:]}.wav"
    chain = audio_lab.process_file(src, out, preset)
    job = {"id": jid, "type": "enhance", "title": src.name, "preset": preset,
           "grade_before": chain["before"]["quality_grade"],
           "grade_after": chain["after"]["quality_grade"],
           "rms_before": chain["before"]["rms_db"], "rms_after": chain["after"]["rms_db"]}
    res = STORE.record_job(job, out)
    if deliver and CFG.has_telegram:
        gateway.report_job("هندسة صوتية", src.name,
                           {"قبل": f'درجة {job["grade_before"]}',
                            "بعد": f'درجة {job["grade_after"]}',
                            "مستوى الضجيج قبل": chain["before"]["issues"] or "لا شيء"}, out)
    return {"job": job, "chain": chain, "storage": res, "asset": str(out)}


def job_script(brief: str, deliver: bool = False) -> dict:
    sc = voice_brain.write_script(brief)
    jid = _jid(brief, "script")
    job = {"id": jid, "type": "script", "title": sc.get("title", "")[:60],
           "brain": sc.get("_brain"), "words": len(stt_whisper.words(sc["script"]))}
    res = STORE.record_job(job)
    (OUTPUT_DIR / f"{jid}_script.json").write_text(
        json.dumps(sc, ensure_ascii=False, indent=1), encoding="utf-8")
    if deliver and CFG.has_telegram:
        gateway.report_job("صياغة سيناريو", job["title"], {"المحرك": job["brain"],
                                                           "الكلمات": job["words"]})
    return {"job": job, "script": sc, "storage": res}


def job_transcribe(wav: Path) -> dict:
    wav = Path(wav)
    jid = _jid(wav.name + str(wav.stat().st_size), "stt")
    t = stt_whisper.transcribe(wav)
    job = {"id": jid, "type": "transcribe", "title": wav.name,
           "engine": t["engine"], "chars": len(t.get("text", ""))}
    res = STORE.record_job(job)
    return {"job": job, "transcript": t, "storage": res}


def job_full_production(brief: str, voice: str = "", deliver: bool = True) -> dict:
    """End-to-end: brain writes -> DSP/Bark speaks -> lab polishes -> store -> telegram."""
    sc = job_script(brief)
    script = sc["script"]["script"]
    tts = job_tts(script, voice=voice or sc["script"].get("voice", ""),
                  speed=sc["script"].get("speed", 1.0), deliver=False)
    enh = job_enhance(Path(tts["asset"]), preset=sc["script"].get("preset", "voiceover"),
                      deliver=False)
    # QA loop: analyze final master
    final = Path(enh["asset"])
    rep = audio_lab.analyze(audio_lab.load_wav(final))
    summary = {"brief": brief[:80], "brain": sc["job"]["brain"],
               "tts_grade": tts["job"]["quality_grade"],
               "final_grade": rep.quality_grade, "duration_s": rep.duration_s,
               "issues": rep.issues}
    if deliver and CFG.has_telegram:
        gateway.report_job("إنتاج كامل (Auto-Pipeline)", brief[:50],
                           {"السيناريو بواسطة": summary["brain"],
                            "الدرجة النهائية": summary["final_grade"],
                            "المدة": f'{summary["duration_s"]}s',
                            "ملاحظات": ", ".join(rep.issues) or "نقي ✅"}, final)
    return {"summary": summary, "script": sc, "tts": tts, "master": enh}


def job_video(images_dir: Path, audio_wav: Path, per_img: float = 3.0) -> dict:
    images = sorted([p for p in Path(images_dir).iterdir()
                     if p.suffix.lower() in (".png", ".jpg", ".jpeg")])
    if not images:
        return {"error": f"no images in {images_dir}"}
    jid = _jid(str(images_dir) + str(audio_wav), "video")
    mp4 = OUTPUT_DIR / f"{jid}.mp4"
    try:
        audio_lab.build_video(images, Path(audio_wav), mp4, per_image_sec=per_img)
    except RuntimeError as e:
        return {"error": str(e)}
    job = {"id": jid, "type": "video", "title": mp4.name, "frames": len(images),
           "seconds_per_frame": per_img}
    res = STORE.record_job(job, mp4)
    if CFG.has_telegram:
        gateway.report_job("بناء فيديو (Hyperframes)", mp4.name,
                           {"الإطارات": len(images)}, mp4)
    return {"job": job, "storage": res, "asset": str(mp4)}


def demo() -> dict:
    """Fully offline deterministic showcase — runs anywhere, costs nothing."""
    print("🎙️ Voice-ZeroBaran DEMO — zero keys, zero cost, full pipeline\n")
    r1 = job_full_production("Welcome to Voice-ZeroBaran. Free studio voice, "
                             "professional quality. No subscriptions.", deliver=False)
    print("[1] auto-production EN:", json.dumps(r1["summary"], ensure_ascii=False))
    r2 = job_full_production("مرحباً بكم في فويس زيرو باران. استوديو صوتي مجاني بالكامل، "
                             "بدون اشتراكات وبدون حدود.", deliver=False)
    print("[2] auto-production AR:", json.dumps(r2["summary"], ensure_ascii=False))
    # synthesize a noisy clip then enhance it to prove the lab works
    import numpy as np
    rng = np.random.default_rng(7)
    t = np.linspace(0, 2, CFG.sample_rate * 2)
    clean = 0.5 * np.sin(2 * np.pi * 180 * t)
    noisy = (clean + 0.25 * np.sin(2 * np.pi * 50 * t) +
             rng.standard_normal(len(t)).astype(np.float32) * 0.08).astype(np.float32)
    raw = OUTPUT_DIR / "demo_noisy_input.wav"
    audio_lab.save_wav(raw, noisy)
    before = audio_lab.analyze(noisy)
    r3 = job_enhance(raw, preset="broadcast", deliver=False)
    after = r3["chain"]["after"]
    print(f"[3] enhancement: hum+noise input grade {before.quality_grade} "
          f"(dom {before.dominant_hz}Hz) -> output grade {after['quality_grade']} "
          f"rms {after['rms_db']}dB issues={after['issues']}")
    r4 = job_transcribe(Path(r1["master"]["asset"]))
    print("[4] STT status:", r4["transcript"]["engine"])
    print("\n✅ DEMO COMPLETE — outputs in ./output/ , archive in ./data/state.json")
    return {"en": r1, "ar": r2, "enh": r3, "stt": r4}


def main():
    ap = argparse.ArgumentParser(prog="vzb_orch", description="Voice-ZeroBaran studio CLI")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("make-script"); p.add_argument("brief"); p.add_argument("--deliver", action="store_true")
    p = sub.add_parser("tts"); p.add_argument("text"); p.add_argument("--voice", default="")
    p.add_argument("--speed", type=float, default=1.0); p.add_argument("--no-deliver", action="store_true")
    p = sub.add_parser("enhance"); p.add_argument("file"); p.add_argument("--preset", default="broadcast")
    p.add_argument("--no-deliver", action="store_true")
    p = sub.add_parser("transcribe"); p.add_argument("file")
    p = sub.add_parser("video"); p.add_argument("images_dir"); p.add_argument("audio")
    p.add_argument("--per-image", type=float, default=3.0)
    p = sub.add_parser("run"); p.add_argument("brief"); p.add_argument("--voice", default="")
    p.add_argument("--no-deliver", action="store_true")
    sub.add_parser("demo")
    sub.add_parser("stats")

    a = ap.parse_args()
    if a.cmd == "make-script":
        out = job_script(a.brief, deliver=a.deliver)
    elif a.cmd == "tts":
        out = job_tts(a.text, a.voice, a.speed, deliver=not a.no_deliver)
    elif a.cmd == "enhance":
        out = job_enhance(Path(a.file), a.preset, deliver=not a.no_deliver)
    elif a.cmd == "transcribe":
        out = job_transcribe(Path(a.file))
    elif a.cmd == "video":
        out = job_video(Path(a.images_dir), Path(a.audio), a.per_image)
    elif a.cmd == "run":
        out = job_full_production(a.brief, a.voice, deliver=not a.no_deliver)
    elif a.cmd == "demo":
        demo(); return
    elif a.cmd == "stats":
        out = STORE.stats()
    print(json.dumps(out, ensure_ascii=False, indent=1, default=str)[:3000])


if __name__ == "__main__":
    main()
