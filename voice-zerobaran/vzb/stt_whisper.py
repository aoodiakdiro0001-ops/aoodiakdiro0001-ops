# -*- coding: utf-8 -*-
"""
Voice-ZeroBaran — Project #36 | ZeroBaran Studio
Copyright (c) 2026 Baran Avisat. Support: Baranavisat@gmail.com | WhatsApp 00905313263722

Layer 2 (part C) — WHISPER STT (free, local when installed; graceful stub otherwise).
Transcription feeds the QA loop: we re-transcribe generated speech and diff it
against the source script to compute a WER-style intelligibility score.
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
from pathlib import Path
from typing import Optional


def whisper_available() -> bool:
    return shutil.which("whisper") is not None or _faster_whisper()


def _faster_whisper():
    try:
        import faster_whisper  # type: ignore  # noqa
        return True
    except Exception:
        return False


def transcribe(audio_path: Path | str, model: str = "base",
               language: Optional[str] = None) -> dict:
    """Return {'text': str, 'engine': str, 'duration_s': float|None}."""
    audio_path = Path(audio_path)
    # engine 1: faster-whisper (python, CPU-friendly)
    if _faster_whisper():
        try:
            from faster_whisper import WhisperModel  # type: ignore
            m = WhisperModel(model, device="cpu", compute_type="int8")
            segs, info = m.transcribe(str(audio_path), language=language)
            text = " ".join(s.text.strip() for s in segs)
            return {"text": text, "engine": "faster-whisper",
                    "duration_s": round(float(info.duration), 2)}
        except Exception as e:
            err = str(e)[:120]
    # engine 2: openai-whisper CLI
    if shutil.which("whisper"):
        outdir = audio_path.parent / "_stt"
        outdir.mkdir(exist_ok=True)
        r = subprocess.run(["whisper", str(audio_path), "--model", model,
                            "--output_format", "json", "--output_dir", str(outdir)],
                           capture_output=True, text=True)
        if r.returncode == 0:
            jf = outdir / (audio_path.stem + ".json")
            if jf.exists():
                d = json.loads(jf.read_text(encoding="utf-8"))
                return {"text": d.get("text", "").strip(), "engine": "whisper-cli",
                        "duration_s": d.get("duration")}
    # engine 3: ffmpeg-based energy profile fallback (no neural model installed)
    return {"text": "", "engine": "unavailable",
            "note": "Install `pip install faster-whisper` for full STT. "
                    "System continues in TTS-only mode.",
            "duration_s": _ffprobe_duration(audio_path)}


def _ffprobe_duration(p: Path) -> Optional[float]:
    if not shutil.which("ffprobe"):
        return None
    try:
        r = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                            "format=duration", "-of", "csv=p=0", str(p)],
                           capture_output=True, text=True)
        return float(r.stdout.strip())
    except Exception:
        return None


def words(text: str) -> list[str]:
    return re.findall(r"[\w\u0600-\u06FF']+", (text or "").lower())


def wer(reference: str, hypothesis: str) -> float:
    """Word error rate with classic DP edit distance (0.0 = perfect)."""
    R, H = words(reference), words(hypothesis)
    if not R:
        return 0.0 if not H else 1.0
    prev = list(range(len(H) + 1))
    for i, rw in enumerate(R, 1):
        cur = [i] + [0] * len(H)
        for j, hw in enumerate(H, 1):
            cur[j] = min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (rw != hw))
        prev = cur
    return round(prev[-1] / max(len(R), 1), 4)


if __name__ == "__main__":
    print(json.dumps({"wer_demo": wer("the cat sat", "the cat sit down")}))
