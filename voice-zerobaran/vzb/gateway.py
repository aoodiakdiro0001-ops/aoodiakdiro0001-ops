# -*- coding: utf-8 -*-
"""
Voice-ZeroBaran — Project #36 | ZeroBaran Studio
Copyright (c) 2026 Baran Avisat. Support: Baranavisat@gmail.com | WhatsApp 00905313263722

Layer 4 — DELIVERY GATEWAY: Telegram Bot API (free).
Sends voice notes (OGG/Opus), audio files, videos and studio reports straight
to the owner's phone. Silent-safe when no token is configured.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Optional

from .config import CFG

API = "https://api.telegram.org/bot{token}/{method}"


def _post(method: str, payload: dict) -> dict:
    url = API.format(token=CFG.telegram_token, method=method)
    data = urllib.parse.urlencode(payload).encode()
    req = urllib.request.Request(url, data=data)
    with urllib.request.urlopen(req, timeout=40) as r:
        return json.loads(r.read().decode())


def _multipart(method: str, filepath: Path, payload: dict) -> dict:
    """Manual multipart for sendVoice/sendAudio/sendVideo (no requests dep)."""
    boundary = "vzb-boundary-zerobaran"
    parts = []
    for k, v in payload.items():
        parts.append(f"--{boundary}\r\nContent-Disposition: form-data; name=\"{k}\"\r\n\r\n{v}\r\n".encode())
    fname = filepath.name
    ctype = "audio/ogg" if filepath.suffix == ".ogg" else \
            "video/mp4" if filepath.suffix in (".mp4", ".mov") else \
            "audio/mpeg" if filepath.suffix == ".mp3" else "audio/wav"
    parts.append(
        f"--{boundary}\r\nContent-Disposition: form-data; name=\"document\"; filename=\"{fname}\"\r\n"
        f"Content-Type: {ctype}\r\n\r\n".encode()
        + filepath.read_bytes() + f"\r\n--{boundary}--\r\n".encode())
    body = b"".join(parts)
    url = API.format(token=CFG.telegram_token, method=method)
    req = urllib.request.Request(url, data=body,
                                 headers={"Content-Type": f"multipart/form-data; boundary={boundary}"})
    with urllib.request.urlopen(req, timeout=90) as r:
        return json.loads(r.read().decode())


def _wav_to_ogg(wav: Path) -> Optional[Path]:
    """Telegram voice notes must be Opus/OGG — FFmpeg converts for free."""
    if not shutil.which("ffmpeg"):
        return None
    ogg = wav.with_suffix(".ogg")
    r = subprocess.run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
                        "-i", str(wav), "-c:a", "libopus", "-b:a", "48k",
                        "-ar", "48000", "-ac", "1", str(ogg)],
                       capture_output=True, text=True)
    return ogg if r.returncode == 0 and ogg.exists() else None


def send_text(html: str) -> dict:
    if not CFG.has_telegram:
        return {"ok": False, "skipped": "no telegram credentials"}
    try:
        return _post("sendMessage", {"chat_id": CFG.telegram_chat_id, "text": html,
                                    "parse_mode": "HTML", "disable_web_page_preview": "true"})
    except (urllib.error.URLError, KeyError) as e:
        return {"ok": False, "error": str(e)[:160]}


def send_asset(path: Path, caption: str = "") -> dict:
    """Send a produced media file: voice-note first, fall back to document."""
    path = Path(path)
    if not CFG.has_telegram:
        return {"ok": False, "skipped": "no telegram credentials", "asset": str(path)}
    try:
        if path.suffix == ".wav":
            ogg = _wav_to_ogg(path)
            if ogg:
                return _multipart("sendVoice", ogg,
                                  {"chat_id": CFG.telegram_chat_id, "caption": caption[:900]})
        method = "sendVideo" if path.suffix in (".mp4", ".mov") else \
                 "sendAudio" if path.suffix in (".mp3", ".ogg") else "sendDocument"
        return _multipart(method, path, {"chat_id": CFG.telegram_chat_id,
                                         "caption": caption[:900]})
    except (urllib.error.URLError, KeyError) as e:
        # last resort: plain document
        try:
            return _multipart("sendDocument", path,
                              {"chat_id": CFG.telegram_chat_id, "caption": caption[:900]})
        except Exception as e2:
            return {"ok": False, "error": str(e2)[:160]}


FOOTER = (f'— <b>Voice-ZeroBaran</b> · {CFG.author} · '
          f'<a href="mailto:{CFG.support_email}">{CFG.support_email}</a> · '
          f'واتساب {CFG.support_whatsapp}')


def report_job(job_type: str, title: str, details: dict, asset: Optional[Path] = None) -> dict:
    lines = [f"🎙️ <b>تقرير استوديو Voice-ZeroBaran</b>",
             f"🧩 العملية: <b>{job_type}</b> — {title}"]
    for k, v in details.items():
        lines.append(f"• {k}: <b>{v}</b>")
    lines.append(FOOTER)
    msg = "\n".join(lines)
    out = send_text(msg)
    if asset:
        out["asset_delivery"] = send_asset(Path(asset), msg[:200])
    return out
