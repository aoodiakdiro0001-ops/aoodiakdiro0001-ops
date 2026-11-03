# -*- coding: utf-8 -*-
"""
Design-Guard-ZeroBaran — المنسّق الرئيسي (Orchestrator)
=========================================================
يشغّل الطبقات الأربع بتناغم:
  inbox ─► OpenCV/Pillow inspection ─► Gemini Vision/Groq verdict
       ─► Supabase archive ─► Telegram instant report
كل أصل يُفحص مرة واحدة فقط (checksum dedupe)، ثم يُؤرشف إلى
archive/accepted أو archive/rejected تلقائياً.

الاستخدام:
  python design_guard.py --scan                 # افحص كل جديد في inbox
  python design_guard.py --file x.png --file y.md
  python design_guard.py --demo                 # ولّد عينات معيبة وسليمة وأفحصها
  python design_guard.py --weekly               # ملخص إنتاجية أسبوعي لتليجرام

المؤلف: Baran Avisat | baranavisat@gmail.com | واتساب: 00905313263722
الحقوق محفوظة © ZeroBaran Studio — MIT License
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

BASE_DIR = Path(__file__).resolve().parent.parent   # design-guard-zerobaran/
sys.path.insert(0, str(Path(__file__).resolve().parent))

from vision_inspect import inspect_asset, sha1_of            # noqa: E402
from quality_brain import build_brain, MockBrain     # noqa: E402
from store import QaStore                            # noqa: E402
from guard_notify import TelegramGuard               # noqa: E402


def load_config() -> dict:
    cfg_path = Path(__file__).parent / "config.yaml"
    return yaml.safe_load(cfg_path.read_text(encoding="utf-8"))


def final_decision(structural: float, ai_verdict: str, ai_score: float, hard_fail: bool,
                   cfg: dict) -> tuple:
    """دمج الحكم الآلي + الذكي ⇒ قرار نهائي ونسبة مطابقة نهائية."""
    dec = cfg["decision"]
    if hard_fail and ai_verdict == "accepted":
        ai_verdict = "needs_review"          # الحاسوب يملك حق النقض على النموذج
    blended = round(0.5 * structural + 0.5 * ai_score, 1)
    if blended >= dec["accept_score"] and ai_verdict == "accepted":
        verdict = "accepted"
    elif blended < dec["review_score"] or ai_verdict == "rejected":
        verdict = "rejected"
    else:
        verdict = "needs_review"
    return verdict, blended


def process_one(path: Path, cfg: dict, brain, store: QaStore, seen: dict,
                dry_run_archive: bool = False) -> dict:
    rep = inspect_asset(path, cfg, seen)
    text_seed = rep.extracted_text or (path.read_text(encoding="utf-8", errors="replace")
                                       if rep.kind == "text" else "")
    img_arg = path if rep.kind == "image" else None

    # ---- استدعاء العقل الذكي مع حماية من الأعطال
    try:
        if isinstance(brain, MockBrain):
            v = brain.review(img_arg, text_seed, structural_findings=[f.to_dict() for f in rep.findings])
        else:
            v = brain.review(img_arg, text_seed)
    except Exception as e:
        v = MockBrain(cfg["owner"]["brand"]).review(
            img_arg, text_seed, structural_findings=[f.to_dict() for f in rep.findings])
        v.provider = f"fallback-heuristic (AI error: {str(e)[:80]})"

    verdict, match = final_decision(rep.structural_score, v.verdict, v.match_score,
                                    rep.hard_fail, cfg)

    record = {
        "asset_id": rep.asset_id, "filename": rep.filename, "kind": rep.kind,
        "width": rep.width, "height": rep.height, "file_size": rep.file_size,
        "format": rep.format, "checksum": rep.checksum,
        "structural_score": rep.structural_score,
        "match_score": match, "verdict": verdict,
        "brand_consistency": v.brand_consistency,
        "defects": v.defects[:12], "summary_ar": v.summary_ar,
        "fix_suggestion_ar": v.fix_suggestion_ar, "ai_provider": v.provider,
        "inspector_findings": [f.to_dict() for f in rep.findings],
        "checked_at": datetime.now(timezone.utc).isoformat(),
    }
    store.save_report(record)
    seen[rep.checksum] = rep.filename

    # ---- الأرشفة التلقائية حسب القرار
    if not dry_run_archive:
        arch_dir = BASE_DIR / cfg["pipeline"]["archive_dir"] / (
            "accepted" if verdict == "accepted" else
            "review" if verdict == "needs_review" else "rejected")
        arch_dir.mkdir(parents=True, exist_ok=True)
        dest = arch_dir / rep.filename
        i = 1
        while dest.exists():
            dest = arch_dir / f"{Path(rep.filename).stem}_{i}{Path(rep.filename).suffix}"; i += 1
        shutil.move(str(path), str(dest))
        record["archived_to"] = str(dest.relative_to(BASE_DIR))
    return record


def scan_inbox(cfg, brain, store, tg):
    inbox = BASE_DIR / cfg["pipeline"]["inbox_dir"]
    inbox.mkdir(parents=True, exist_ok=True)
    files = sorted([p for p in inbox.iterdir() if p.is_file()], key=lambda p: p.name)
    known = store.known_checksums()
    results, skipped = [], 0
    for p in files:
        if sha1_of(p) in known:
            skipped += 1
            continue
        results.append(process_one(p, cfg, brain, store, known))

    print(f"\n{'='*62}\n🛡️  Design-Guard-ZeroBaran — دورة فحص مكتملة")
    print(f"   مفحوص جديد: {len(results)} | متجاهل (مكرّر): {skipped}")
    for r in results:
        icon = {"accepted": "🟢", "rejected": "🔴", "needs_review": "🟡"}[r["verdict"]]
        print(f"   {icon} {r['filename']:<28} مطابقة {r['match_score']:>5}%  ({r['ai_provider']})")
    print("=" * 62)

    if results:
        report_on = cfg["alerts"]["telegram"].get("report_on", ["rejected"])
        for r in results:
            if r["verdict"] in report_on:
                tg.report_asset(r)          # تقرير فوري لكل مرفوض/معلّق
        tg.batch_summary(results, warnings=store.warnings)
    elif store.warnings:
        tg.batch_summary([], warnings=store.warnings)
    return results


# ------------------------------------------------------------------ Demo assets
def make_demo_assets(cfg) -> list:
    """عيّنات حقيقية: صورة سليمة، ضبابية، سوداء، صغيرة، نص جيد، نص مشوّه."""
    import numpy as np
    from PIL import Image, ImageDraw, ImageFilter
    demo = BASE_DIR / cfg["pipeline"]["inbox_dir"]
    demo.mkdir(parents=True, exist_ok=True)
    made = []

    # 1) سليمة: بوستر متدرج مع نصوص حادة
    arr = np.zeros((640, 960, 3), dtype=np.uint8)
    grad = np.linspace(20, 235, 640)[:, None, None] * np.ones((1, 960, 3))
    arr[:] = np.stack([grad[..., 0] * .4, grad[..., 1] * .6, 255 - grad[..., 2] * .3], -1).astype("uint8")
    img = Image.fromarray(arr).filter(ImageFilter.DETAIL)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([80, 80, 880, 240], 30, fill=(255, 255, 255))
    d.text((140, 140), "ZeroBaran Studio - Premium AI Assets", fill=(10, 10, 60))
    d.ellipse([420, 320, 620, 520], outline=(255, 210, 0), width=8)
    p = demo / "poster_clean.png"; img.save(p); made.append(p)

    # 2) ضبابية شديدة
    blur = img.filter(ImageFilter.GaussianBlur(18))
    p = demo / "poster_blurry.png"; blur.save(p); made.append(p)

    # 3) إطار أسود ميت
    black = Image.new("RGB", (600, 600), (2, 2, 2))
    p = demo / "frame_black.png"; black.save(p); made.append(p)

    # 4) أبعاد صغيرة جداً
    tiny = img.resize((120, 90))
    p = demo / "thumb_tiny.png"; tiny.save(p); made.append(p)

    # 5) نسخة مكررة حرفية من السليمة
    p = demo / "poster_clean_COPY.png"; shutil.copy(made[0], p); made.append(p)

    # 6) نص سليم تسويقي
    good = ("Discover ZeroBaran Studio premium digital assets crafted with obsessive attention "
            "to detail. Every texture is inspected, every color profile verified, and every "
            "delivery ships on time. Join thousands of creators who trust our pipeline today.")
    p = demo / "copy_good.md"; p.write_text(good, encoding="utf-8"); made.append(p)

    # 7) نص مشوّه كلاسيكي LLM: placeholder + تكرار + إملاء رديء
    bad = ("Lorem ipsum dolor sit amet, our prodect is the bestest choise for all ur needs. "
           "buy buy buy buy now and recieve a refund if you are not satisfide with the qualty "
           "of our assests, we promisse 24/7 suport and delivary of digitarl goods. TODO: add price here")
    p = demo / "copy_bad.md"; p.write_text(bad, encoding="utf-8"); made.append(p)
    return made


def main():
    ap = argparse.ArgumentParser(description="Design-Guard-ZeroBaran QA Pipeline")
    ap.add_argument("--scan", action="store_true", help="افحص كل جديد في inbox/")
    ap.add_argument("--file", action="append", default=[], help="ملف محدد للفحص")
    ap.add_argument("--demo", action="store_true", help="ولّد عيّنات اختبار ثم افحصها")
    ap.add_argument("--weekly", action="store_true", help="أرسل الملخص الأسبوعي")
    ap.add_argument("--no-archive", action="store_true", help="لا تنقل الملفات بعد الفحص")
    args = ap.parse_args()

    cfg = load_config()
    store = QaStore(cfg, BASE_DIR)
    brain = build_brain(cfg)
    tg = TelegramGuard()
    print(f"🧠 محرك الجودة: {getattr(brain,'provider','mock')} | تخزين: {store.mode} | "
          f"تليجرام: {'مفعّل' if tg.enabled else 'معطّل ('+tg.disabled_reason+')'}")

    if args.weekly:
        m = store.productivity_metrics(days=7)
        print(json.dumps(m, ensure_ascii=False, indent=2))
        tg.weekly_productivity(m)
        return

    known = store.known_checksums()          # بصمات كل ما فُحص سابقاً — dedupe مطلق
    explicit = [Path(f) for f in args.file]
    if args.demo:
        explicit += make_demo_assets(cfg)
    batch = []
    for p in explicit:
        if not p.exists():
            print(f"⚠️ ملف غير موجود: {p}"); continue
        r = process_one(p, cfg, brain, store, known, dry_run_archive=args.no_archive)
        icon = {"accepted": "🟢", "rejected": "🔴", "needs_review": "🟡"}[r["verdict"]]
        print(f"{icon} {r['filename']} → {r['verdict']} ({r['match_score']}%) [{r['ai_provider']}]")
        batch.append(r)
        tg.report_asset(r)                   # تقرير فوري لكل أصل دُفع يدوياً/demo

    if args.scan or args.demo:
        # ما لم يُفحص صراحةً (--file/--demo) أو تُرِك في inbox يُلتقط هنا؛
        # dedupe عبر known_checksums يضمن فحص كل أصل مرة واحدة فقط في التاريخ.
        scan_inbox(cfg, brain, store, tg)


if __name__ == "__main__":
    main()
