# -*- coding: utf-8 -*-
"""Voice-ZeroBaran — Project #36 | © 2026 Baran Avisat — Support: Baranavisat@gmail.com | WhatsApp 00905313263722

pytest suite — every test runs OFFLINE with ZERO keys (CI-safe).
"""
import json
import sys
import wave
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from vzb import audio_lab, stt_whisper, store, tts_engine, voice_brain  # noqa: E402
from vzb.config import CFG, OUTPUT_DIR  # noqa: E402


# ------------------------------------------------------------------ TTS -----
def test_tts_produces_real_audio():
    a = tts_engine.synthesize("hello world this is voice zerobaran studio")
    assert len(a) > 20000, "audio too short"
    assert 0.5 < float(np.max(np.abs(a))) <= 1.0


def test_tts_energy_in_speech_band():
    a = tts_engine.synthesize("professional free voiceover generation")
    S = np.abs(np.fft.rfft(a * np.hanning(len(a))))
    f = np.fft.rfftfreq(len(a), 1 / CFG.sample_rate)
    ratio = S[(f >= 80) & (f < 5000)].sum() / (S.sum() + 1e-12)
    assert ratio > 0.6, f"speech-band ratio {ratio:.2f} too low"


def test_tts_deterministic():
    t = "determinism check for ci"
    assert np.allclose(tts_engine.synthesize(t), tts_engine.synthesize(t))


def test_voices_are_distinct_profiles():
    m = tts_engine.synthesize("same text here", voice="vzb-morgan")
    v = tts_engine.synthesize("same text here", voice="vzb-violet")
    def dom(sig):
        S = np.abs(np.fft.rfft(sig * np.hanning(len(sig))))
        f = np.fft.rfftfreq(len(sig), 1 / CFG.sample_rate)
        lo = (f > 60) & (f < 400)
        return float(f[lo][np.argmax(S[lo])])
    assert abs(dom(m) - dom(v)) > 20


def test_tts_writes_valid_wav(tmp_path):
    p = tts_engine.tts("wave file integrity test", tmp_path / "x.wav")
    with wave.open(str(p), "rb") as wf:
        assert wf.getnchannels() == 1 and wf.getframerate() in (22050, 24000)
        assert wf.getnframes() > 1000


def test_phonemizer_handles_arabic():
    segs = tts_engine.text_to_segments("مرحبا بالعالم")
    assert len(segs) >= 2 and all(s.duration > 0 for s in segs)


# ----------------------------------------------------------------- LAB ------
def _band(sig, lo, hi):
    S = np.abs(np.fft.rfft(sig))
    f = np.fft.rfftfreq(len(sig), 1 / CFG.sample_rate)
    return float(S[(f >= lo) & (f <= hi)].sum())


def test_hum_notch_removes_50hz():
    t = np.linspace(0, 2, CFG.sample_rate * 2)
    x = (0.4 * np.sin(2 * np.pi * 200 * t) + 0.3 * np.sin(2 * np.pi * 50 * t)).astype(np.float32)
    y = audio_lab.hum_notch(x, base=50.0)
    assert _band(y, 48, 52) < _band(x, 48, 52) * 0.1


def test_denoise_reduces_noise_floor_keeps_signal():
    t = np.linspace(0, 2, CFG.sample_rate * 2)
    rng = np.random.default_rng(3)
    noisy = (0.4 * np.sin(2 * np.pi * 200 * t) + rng.standard_normal(len(t)) * 0.05).astype(np.float32)
    clean = audio_lab.denoise(noisy)
    assert _band(clean, 9000, 11999) < _band(noisy, 9000, 11999)
    assert _band(clean, 195, 205) > _band(noisy, 195, 205) * 0.5


def test_loudness_normalization_target():
    x = (0.02 * np.sin(2 * np.pi * 300 * np.linspace(0, 1, CFG.sample_rate))).astype(np.float32)
    y = audio_lab.normalize_loudness(x, target_db=-16.0)
    assert abs(audio_lab.rms_db(y) - (-16.0)) < 3.0


def test_process_file_end_to_end(tmp_path):
    t = np.linspace(0, 1.5, int(CFG.sample_rate * 1.5))
    rng = np.random.default_rng(1)
    raw = (0.5 * np.sin(2 * np.pi * 220 * t) + rng.standard_normal(len(t)) * 0.06).astype(np.float32)
    src = audio_lab.save_wav(tmp_path / "in.wav", raw)
    rep = audio_lab.process_file(src, tmp_path / "out.wav", preset="broadcast")
    assert Path(rep["dst"]).exists()
    assert rep["after"]["quality_grade"] in ("A", "B", "C", "D")
    assert rep["after"]["rms_db"] > -30  # audible master


def test_analyze_detects_clipping():
    sq = np.tile(np.array([0.999, -0.999], np.float32), CFG.sample_rate // 2)
    rep = audio_lab.analyze(sq)
    assert "CLIPPING" in rep.issues


# ------------------------------------------------------------------ STT -----
def test_wer_math():
    assert stt_whisper.wer("the cat sat", "the cat sat") == 0.0
    assert 0.2 < stt_whisper.wer("the cat sat mat", "the cat sit") < 0.8
    assert stt_whisper.wer("", "") == 0.0


def test_transcribe_graceful_without_model(tmp_path):
    p = audio_lab.save_wav(tmp_path / "a.wav", np.zeros(CFG.sample_rate, np.float32))
    out = stt_whisper.transcribe(p)
    assert "engine" in out and "text" in out  # never crashes


# ----------------------------------------------------------------- BRAIN ----
def test_mock_brain_contract():
    sc = voice_brain.MockBrain().generate("اكتب مقدمة عن الاستوديو الصوتي المجاني. مع خاتمة قوية.")
    assert set(["title", "script", "voice", "speed", "preset", "scenes"]) <= set(sc)
    assert sc["voice"] in tts_engine.VOICES
    assert 0.8 <= float(sc["speed"]) <= 1.3


def test_write_script_falls_back_offline(monkeypatch):
    from vzb.config import Config
    monkeypatch.setattr(voice_brain, "CFG", Config())  # no keys
    out = voice_brain.write_script("topic without any api key")
    assert out["_brain"] == "mock-local"
    assert out["script"]


# ----------------------------------------------------------------- STORE ----
def test_store_dedupe(tmp_path, monkeypatch):
    ls = store.LocalStore(tmp_path / "state.json")
    job = {"id": "j1", "type": "tts", "created_at": store._now()}
    assert ls.add_job(job) is True
    assert ls.add_job(dict(job)) is False
    assert ls.stats()["jobs_total"] == 1


def test_store_record_with_asset(tmp_path, monkeypatch):
    st = store.Store.__new__(store.Store)
    st.local = store.LocalStore(tmp_path / "s.json")
    st.sb = None
    wav = audio_lab.save_wav(tmp_path / "m.wav", np.zeros(2000, np.float32))
    r = st.record_job({"id": "k1", "type": "enhance"}, wav)
    assert r["backend"] == "local-json" and r["stored"] is True


# --------------------------------------------------------------- ORCHEST ---
def test_orchestrator_full_pipeline(tmp_path, monkeypatch):
    sys.path.insert(0, str(ROOT / "scripts"))
    import vzb_orch
    monkeypatch.setattr(vzb_orch, "OUTPUT_DIR", tmp_path)
    monkeypatch.setattr(vzb_orch, "STORE",
                        type("S", (), {"record_job": lambda self, j, a=None: {"stored": True},
                                       "stats": lambda self: {}})())
    res = vzb_orch.job_full_production("Welcome to the zero cost voice studio.", deliver=False)
    assert res["summary"]["final_grade"] in ("A", "B", "C", "D")
    assert Path(res["master"]["asset"]).exists()
    assert Path(res["master"]["asset"]).stat().st_size > 10000


def test_gateway_no_credentials_safe(tmp_path, monkeypatch):
    from vzb.config import Config
    monkeypatch.setattr(sys.modules["vzb.gateway"], "CFG", Config())
    from vzb import gateway
    assert gateway.send_text("hi")["ok"] is False
    assert gateway.send_asset(tmp_path / "nope.wav")["skipped"]
