# -*- coding: utf-8 -*-
"""
Voice-ZeroBaran — Project #36 | ZeroBaran Studio
Copyright (c) 2026 Baran Avisat. Support: Baranavisat@gmail.com | WhatsApp 00905313263722

Layer 2 (part B) — AUDIO/FREQUENCY ENGINEERING (Hyperframes/VoiceStudio alternative)

Pure-numpy DSP + FFmpeg for container/format work:
  * denoise        : spectral-gate broadband noise removal (hum/hiss)
  * hum_notch      : 50/60Hz + harmonics comb notch
  * declick        : outlier spike repair
  * eq / lowpass / highpass / boost_freq : biquad & FFT filtering
  * compress       : soft-knee compressor + limiter
  * normalize      : peak + target loudness (RMS-based LUFS approximation)
  * silence_trim   : leading/trailing silence cut
  * speed/pitch    : resample tempo, formant-safe-ish pitch shift via SS simple
  * waveform/spectrogram PNG reports
  * ffmpeg wrappers: to_mp3/aac/ogg, extract audio from video, concat, fade,
    video+audio -> mp4 (Hyperframes-style slideshow/video builder)
"""
from __future__ import annotations

import json
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import numpy as np

from .config import CFG, OUTPUT_DIR

SR = CFG.sample_rate


# ------------------------------------------------------------------ io ------
def load_wav(path: Path | str) -> np.ndarray:
    import wave
    with wave.open(str(path), "rb") as wf:
        sr = wf.getframerate()
        n = wf.getnframes()
        raw = wf.readframes(n)
    data = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
    if sr != SR:  # crude linear resample to internal rate
        idx = np.linspace(0, len(data) - 1, int(len(data) * SR / sr))
        data = np.interp(idx, np.arange(len(data)), data).astype(np.float32)
    return data


def save_wav(path: Path | str, audio: np.ndarray) -> Path:
    import wave
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    pcm = (np.clip(audio, -1, 1) * 32767).astype(np.int16)
    with wave.open(str(path), "wb") as wf:
        wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(SR)
        wf.writeframes(pcm.tobytes())
    return path


# ------------------------------------------------------------- filters ------
def _rfft_signal(x): return np.fft.rfft(x)
def _irfft_signal(X, n): return np.fft.irfft(X, n)


def highpass(x: np.ndarray, freq: float = 80.0) -> np.ndarray:
    X = _rfft_signal(x); f = np.fft.rfftfreq(len(x), 1 / SR)
    X *= 1.0 / (1.0 + (freq / np.maximum(f, 1e-6)) ** 4)
    return _irfft_signal(X, len(x)).astype(np.float32)


def lowpass(x: np.ndarray, freq: float = 12000.0) -> np.ndarray:
    X = _rfft_signal(x); f = np.fft.rfftfreq(len(x), 1 / SR)
    X *= 1.0 / (1.0 + (f / max(freq, 1.0)) ** 4)
    return _irfft_signal(X, len(x)).astype(np.float32)


def boost_freq(x: np.ndarray, center: float, gain_db: float = 3.0, q: float = 6.0) -> np.ndarray:
    X = _rfft_signal(x); f = np.fft.rfftfreq(len(x), 1 / SR)
    bump = (gain_db / 20.0) * np.exp(-((f - center) ** 2) / (2 * (center / q) ** 2))
    X *= (1.0 + bump)
    return _irfft_signal(X, len(x)).astype(np.float32)


def eq(x: np.ndarray, bands=((120, 2.0), (2500, 1.5), (8000, 2.5))) -> np.ndarray:
    for c, g in bands:
        x = boost_freq(x, c, g)
    return x


def hum_notch(x: np.ndarray, base: float = 50.0, harmonics: int = 6) -> np.ndarray:
    X = _rfft_signal(x); f = np.fft.rfftfreq(len(x), 1 / SR)
    for h in range(1, harmonics + 1):
        fc = base * h
        if fc < f[-1]:
            X *= 1.0 - 0.97 * np.exp(-((f - fc) ** 2) / (2 * 3.0 ** 2))
    return _irfft_signal(X, len(x)).astype(np.float32)


def denoise(x: np.ndarray, strength: float = 2.0, win: int = 1024) -> np.ndarray:
    """Broadband noise reduction — per-frame percentile noise-floor estimate
    with an oversubtracted Wiener-style soft gain mask.

    For each STFT frame we take the k-th percentile of its magnitude spectrum
    as a local noise-floor proxy (speech/sinusoid energy lives in peaks, noise
    fills the floor), subtract strength x floor, and reshape into a smooth
    gain in [floor_min .. 1]. Signal peaks pass through (~gain 1); noise bins
    are attenuated toward the floor. Deterministic, pure numpy.
    """
    n = len(x)
    if n < win:
        return x.copy()
    hop = win // 2
    starts = list(range(0, n - win + 1, hop))
    w = np.hanning(win)
    specs = []
    for st in starts:
        F = np.fft.rfft(x[st:st + win] * w)
        specs.append(F)
    out = np.zeros(n, dtype=np.float32)
    norm = np.zeros(n, dtype=np.float32)
    floor_min = 10 ** (-70 / 20.0)  # never boost; min residual gain
    for F, st in zip(specs, starts):
        M = np.abs(F)
        floor = np.percentile(M, 35) * strength  # local noise floor proxy
        sig_est = np.maximum(M - floor, 0.0)
        gain = sig_est / (M + 1e-9)
        gain = np.clip(gain, floor_min, 1.0)
        seg_f = np.fft.irfft(F * gain, win).astype(np.float32) * w
        out[st:st + win] += seg_f
        norm[st:st + win] += w ** 2
    out /= np.maximum(norm, 1e-6)
    return out[:n].astype(np.float32)


def declick(x: np.ndarray, spike_db: float = 24.0) -> np.ndarray:
    y = x.copy()
    d = np.abs(np.diff(y, prepend=y[0]))
    med = np.median(d[d > 0]) + 1e-9
    idx = np.where(d > med * (10 ** (spike_db / 20.0)))[0]
    for i in idx:
        lo, hi = max(i - 3, 0), min(i + 4, len(y))
        y[i] = np.median(y[lo:hi])
    return y.astype(np.float32)


# ------------------------------------------------------------ dynamics ------
def compress(x: np.ndarray, thresh_db: float = -20.0, ratio: float = 3.0,
             attack_ms: float = 5.0, release_ms: float = 80.0) -> np.ndarray:
    env_db = 20 * np.log10(np.abs(x) + 1e-9)
    a = np.exp(-1 / (SR * attack_ms / 1000)); r = np.exp(-1 / (SR * release_ms / 1000))
    e = np.zeros_like(env_db); prev = env_db[0]
    for i, v in enumerate(env_db):  # single pass envelope follower
        k = a if v < prev else r
        prev = k * prev + (1 - k) * v
        e[i] = prev
    gain_db = np.where(e > thresh_db, thresh_db + (e - thresh_db) / ratio, e)
    out = x * 10 ** ((gain_db - e) / 20.0)
    return out.astype(np.float32)


def limiter(x: np.ndarray, ceiling_db: float = -1.0) -> np.ndarray:
    ceil = 10 ** (ceiling_db / 20.0)
    return np.clip(x, -ceil, ceil).astype(np.float32)


def rms_db(x: np.ndarray) -> float:
    return float(20 * np.log10(np.sqrt(np.mean(x ** 2)) + 1e-12))


def normalize_loudness(x: np.ndarray, target_db: float = -16.0) -> np.ndarray:
    cur = rms_db(x)
    gain = 10 ** ((target_db - cur) / 20.0)
    return limiter(x * gain)


def silence_trim(x: np.ndarray, thresh_db: float = -45.0) -> np.ndarray:
    frames = len(x) // (SR // 50) or 1
    flen = SR // 50
    e = np.array([rms_db(x[i * flen:(i + 1) * flen]) for i in range(frames)])
    on = np.where(e > thresh_db)[0]
    if len(on) == 0:
        return x
    s, t = on[0] * flen, min((on[-1] + 1) * flen + flen, len(x))
    pad = int(0.05 * SR)
    return x[max(s - pad, 0):min(t + pad, len(x))]


def change_speed(x: np.ndarray, factor: float) -> np.ndarray:
    idx = np.linspace(0, len(x) - 1, int(len(x) / factor))
    return np.interp(idx, np.arange(len(x)), x).astype(np.float32)


def pitch_shift_simple(x: np.ndarray, semitones: float) -> np.ndarray:
    """Resample + tempo-compensate (naive but effective for short clips)."""
    r = 2 ** (semitones / 12.0)
    sped = change_speed(x, r)
    return change_speed(sped, 1 / r * r).astype(np.float32) if abs(semitones) < 0.01 \
        else change_speed(sped, 1.0 / r)


def crossfade_concat(parts: list[np.ndarray], fade_ms: int = 60) -> np.ndarray:
    if not parts:
        return np.zeros(0, dtype=np.float32)
    out = parts[0]
    fd = SR * fade_ms // 1000
    for p in parts[1:]:
        if len(out) >= fd and len(p) >= fd:
            mix = out[-fd:] * np.linspace(1, 0, fd) + p[:fd] * np.linspace(0, 1, fd)
            out = np.concatenate([out[:-fd], mix, p[fd:]])
        else:
            out = np.concatenate([out, p])
    return out.astype(np.float32)


# --------------------------------------------------------------- ffmpeg -----
HAS_FFMPEG = shutil.which("ffmpeg") is not None


def ff_run(args: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error"] + args,
                          capture_output=True, text=True)


def to_mp3(wav_path: Path, bitrate: str = "192k") -> Path:
    out = wav_path.with_suffix(".mp3")
    if HAS_FFMPEG:
        r = ff_run(["-i", str(wav_path), "-codec:a", "libmp3lame", "-b:a", bitrate, str(out)])
        if r.returncode == 0:
            return out
    # fallback: keep wav, note it
    return wav_path


def extract_audio(video_path: Path, out_wav: Optional[Path] = None) -> Path:
    out_wav = out_wav or (OUTPUT_DIR / (video_path.stem + ".wav"))
    r = ff_run(["-i", str(video_path), "-vn", "-ac", "1", "-ar", str(SR), str(out_wav)])
    if r.returncode != 0:
        raise RuntimeError(f"ffmpeg extract failed: {r.stderr[:200]}")
    return out_wav


def build_video(images: list[Path], audio_wav: Path, out_mp4: Path,
                per_image_sec: float = 3.0, size: str = "1280x720") -> Path:
    """Hyperframes-style: slideshow of design frames synced to VO narration."""
    if not HAS_FFMPEG:
        raise RuntimeError("ffmpeg required for video build")
    listfile = OUTPUT_DIR / "_vzb_frames.txt"
    with listfile.open("w") as fh:
        for img in images:
            fh.write(f"file '{Path(img).resolve()}'\nduration {per_image_sec}\n")
        fh.write(f"file '{Path(images[-1]).resolve()}'\n")
    w_px, h_px = size.split("x")
    vf = (f"scale={w_px}:{h_px}:force_original_aspect_ratio=decrease,"
          f"pad={w_px}:{h_px}:(ow-iw)/2:(oh-ih)/2,format=yuv420p")
    r = ff_run(["-f", "concat", "-safe", "0", "-i", str(listfile), "-i", str(audio_wav),
                "-vf", vf, "-fps_mode", "cfr", "-r", "10",
                "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", "-shortest", str(out_mp4)])
    if r.returncode != 0:
        raise RuntimeError(f"ffmpeg video build failed: {r.stderr[:300]}")
    return out_mp4


# ------------------------------------------------------------- analysis -----
@dataclass
class AudioReport:
    duration_s: float
    sample_rate: int
    peak_db: float
    rms_db: float
    clip_ratio: float
    silence_ratio: float
    dominant_hz: float
    bandwidth_top_hz: float
    quality_grade: str
    issues: list

    def to_dict(self) -> dict:
        return self.__dict__.copy()


def analyze(x: np.ndarray) -> AudioReport:
    dur = len(x) / SR
    peak = float(np.max(np.abs(x)) + 1e-12)
    rms = 10 ** (rms_db(x) / 20.0)
    clipped = float(np.mean(np.abs(x) > 0.999))
    flen = SR // 50
    frames = max(len(x) // flen, 1)
    sil = float(np.mean([rms_db(x[i * flen:(i + 1) * flen]) < -45 for i in range(frames)]))
    S = np.abs(np.fft.rfft(x * np.hanning(len(x))))
    f = np.fft.rfftfreq(len(x), 1 / SR)
    dom = float(f[np.argmax(S)])
    cum = np.cumsum(S) / (np.sum(S) + 1e-9)
    bw = float(f[min(np.searchsorted(cum, 0.95), len(f) - 1)])
    issues = []
    if clipped > 0.002: issues.append("CLIPPING")
    if peak < 0.05: issues.append("TOO_QUIET")
    if sil > 0.6: issues.append("EXCESS_SILENCE")
    if dom in (50.0, 60.0) or any(abs(dom - b * 50) < 2 for b in (1, 2)): issues.append("HUM_DETECTED")
    if rms < 0.02 and peak > 0.05: issues.append("LOW_DYNAMIC_RANGE")
    grade = "A" if not issues else ("B" if len(issues) == 1 else "C" if len(issues) == 2 else "D")
    return AudioReport(round(dur, 3), SR, round(20 * np.log10(peak), 2),
                       rms_db(x), round(clipped, 5), round(sil, 3),
                       round(dom, 1), round(bw, 1), grade, issues)


def process_file(src: Path | str, dst: Optional[Path | str] = None,
                 preset: str = "broadcast") -> dict:
    """One-shot studio chain. Presets: broadcast|podcast|clean|voiceover."""
    src = Path(src)
    dst = Path(dst or src.with_name(src.stem + "_vzb.wav"))
    x = load_wav(src)
    before = analyze(x)
    chains = {
        "clean":     lambda a: denoise(declick(a)),
        "podcast":   lambda a: normalize_loudness(compress(eq(highpass(hum_notch(denoise(declick(a))), 70)))),
        "broadcast": lambda a: limiter(normalize_loudness(compress(eq(lowpass(highpass(hum_notch(denoise(declick(a))), 80), 14000))))),
        "voiceover": lambda a: normalize_loudness(compress(boost_freq(highpass(denoise(declick(a)), 90), 3200, 2.0), ratio=2.2)),
    }
    fn = chains.get(preset, chains["broadcast"])
    y = silence_trim(fn(x))
    save_wav(dst, y)
    after = analyze(y)
    return {"src": str(src), "dst": str(dst), "preset": preset,
            "before": before.to_dict(), "after": after.to_dict()}


if __name__ == "__main__":
    demo = np.sin(2 * np.pi * 220 * np.linspace(0, 1, SR)).astype(np.float32)
    print(json.dumps(analyze(demo).to_dict(), indent=1)[:300])
