# -*- coding: utf-8 -*-
"""
Voice-ZeroBaran — Project #36 | ZeroBaran Studio
Copyright (c) 2026 Baran Avisat. Support: Baranavisat@gmail.com | WhatsApp 00905313263722

Central configuration loader (env vars + optional config.yaml).
Everything is OPTIONAL: with zero keys the system still runs fully on the
local DSP voice engine + FFmpeg media pipeline (100% free, offline-capable).
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
OUTPUT_DIR = ROOT / "output"
STATE_FILE = DATA_DIR / "state.json"

for _d in (DATA_DIR, OUTPUT_DIR):
    _d.mkdir(parents=True, exist_ok=True)


def _env(key: str, default: str = "") -> str:
    return os.environ.get(key, default).strip()


@dataclass
class Config:
    brand: str = "Voice-ZeroBaran"
    author: str = "Baran Avisat"
    support_email: str = "Baranavisat@gmail.com"
    support_whatsapp: str = "00905313263722"

    # Free-tier AI keys (optional — scripts/ layer)
    groq_api_key: str = field(default_factory=lambda: _env("GROQ_API_KEY"))
    gemini_api_key: str = field(default_factory=lambda: _env("GEMINI_API_KEY"))

    # Supabase storage/DB (optional)
    supabase_url: str = field(default_factory=lambda: _env("SUPABASE_URL"))
    supabase_service_key: str = field(default_factory=lambda: _env("SUPABASE_SERVICE_KEY"))

    # Telegram gateway (optional)
    telegram_token: str = field(default_factory=lambda: _env("TELEGRAM_BOT_TOKEN"))
    telegram_chat_id: str = field(default_factory=lambda: _env("TELEGRAM_CHAT_ID"))

    # Audio engine parameters
    sample_rate: int = 24000
    default_voice: str = "vzb-morgan"      # built-in DSP voice
    default_speed: float = 1.0
    loudness_target_db: float = -16.0      # broadcast-style target level
    max_chars_per_job: int = 6000

    @property
    def has_groq(self) -> bool:
        return bool(self.groq_api_key)

    @property
    def has_gemini(self) -> bool:
        return bool(self.gemini_api_key)

    @property
    def has_supabase(self) -> bool:
        return bool(self.supabase_url and self.supabase_service_key)

    @property
    def has_telegram(self) -> bool:
        return bool(self.telegram_token and self.telegram_chat_id)

    @classmethod
    def load(cls) -> "Config":
        cfg = cls()
        try:
            import yaml  # optional dependency
            f = ROOT / "config.yaml"
            if f.exists():
                raw = yaml.safe_load(f.read_text(encoding="utf-8")) or {}
                for k, v in raw.items():
                    if hasattr(cfg, k) and v is not None:
                        setattr(cfg, k, v)
        except Exception:
            pass
        return cfg


CFG = Config.load()
