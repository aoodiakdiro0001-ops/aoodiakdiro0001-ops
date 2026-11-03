# -*- coding: utf-8 -*-
"""Voice-ZeroBaran — Project #36 | © 2026 Baran Avisat — Support: Baranavisat@gmail.com | WhatsApp 00905313263722

Telegram Bot gateway (python-telegram-bot free). Send it text -> get voice note;
send it a voice/audio file -> get the enhanced studio master back.
Run: python scripts/telegram_bot.py   (requires TELEGRAM_BOT_TOKEN)
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

try:
    from telegram import Update
    from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
except ImportError:
    print("pip install python-telegram-bot  (free)")
    sys.exit(1)

from vzb.config import CFG, OUTPUT_DIR          # noqa: E402
from vzb import audio_lab, tts_engine           # noqa: E402
sys.path.insert(0, str(Path(__file__).resolve().parent))
from vzb_orch import job_tts, job_enhance       # noqa: E402

WELCOME = ("🎙️ *استوديو Voice-ZeroBaran*\n"
           "أرسل لي نصاً وسأرد عليك بتعليق صوتي احترافي خلال ثوانٍ.\n"
           "أرسل لي ملفاً صوتياً وسأعيد لك نسخة نقية بهندسة استوديوهات كاملة.\n\n"
           f"/voice [morgan|violet|merlin|damien] — اختيار الصوت\n"
           f"© {CFG.author} · دعم: {CFG.support_email} · واتساب {CFG.support_whatsapp}")

_state = {"voice": CFG.default_voice}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(WELCOME, parse_mode="Markdown")


async def voice_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    arg = (context.args or ["morgan"])[0].lower()
    _state["voice"] = f"vzb-{arg}" if not arg.startswith("vzb-") else arg
    await update.message.reply_text(f"🎛️ تم ضبط الصوت على: {_state['voice']}")


async def on_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    txt = update.message.text[:CFG.max_chars_per_job]
    await update.message.reply_chat_action("typing")
    res = job_tts(txt, voice=_state["voice"], deliver=False)
    ogg = OUTPUT_DIR / (Path(res["asset"]).stem + ".ogg")
    import subprocess
    subprocess.run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", res["asset"],
                    "-c:a", "libopus", "-b:a", "48k", "-ar", "48000", "-ac", "1", str(ogg)])
    send = ogg if ogg.exists() else Path(res["mp3"])
    with send.open("rb") as fh:
        await update.message.reply_voice(fh) if send.suffix == ".ogg" \
            else await update.message.reply_audio(fh)


async def on_audio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    await msg.reply_chat_action("upload_document")
    file = await (msg.voice or msg.audio or msg.document).get_file()
    src = OUTPUT_DIR / f"tg_in_{file.file_unique_id}.{'ogg' if msg.voice else 'wav'}"
    await file.download_to_drive(str(src))
    wav = src.with_suffix(".in.wav")
    import subprocess
    subprocess.run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
                    "-i", str(src), "-ar", str(CFG.sample_rate), "-ac", "1", str(wav)])
    res = job_enhance(wav, preset="broadcast", deliver=False)
    out = Path(res["asset"])
    ogg = out.with_suffix(".ogg")
    subprocess.run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", str(out),
                    "-c:a", "libopus", "-b:a", "48k", "-ar", "48000", "-ac", "1", str(ogg)])
    b, a = res["chain"]["before"], res["chain"]["after"]
    await msg.reply_text(f"🎛️ هندسة استوديو: درجة {b['quality_grade']} ← {a['quality_grade']} · "
                         f"ضجيج مكتشف قبل: {', '.join(b['issues']) or 'لا شيء'}")
    with ogg.open("rb") as fh:
        await msg.reply_voice(fh)


def main():
    if not CFG.telegram_token:
        print("Set TELEGRAM_BOT_TOKEN first (free via @BotFather).")
        sys.exit(1)
    app = Application.builder().token(CFG.telegram_token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("voice", voice_cmd))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, on_text))
    app.add_handler(MessageHandler(filters.VOICE | filters.AUDIO, on_audio))
    print("🎙️ Voice-ZeroBaran bot polling… (Ctrl+C to stop)")
    app.run_polling()


if __name__ == "__main__":
    main()
