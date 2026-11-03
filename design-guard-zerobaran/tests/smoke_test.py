# -*- coding: utf-8 -*-
"""
Design-Guard-ZeroBaran — اختبار تعاقدي نهائي (Smoke Test)
===========================================================
يتحقق من أن الطبقات الأربع موصولة بعقود صحيحة، وأن كاشفات العيوب
تعمل على عيّنات معيبة حقيقية. بلا أي مفتاح API — يعمل في CI دائماً.

المؤلف: Baran Avisat | baranavisat@gmail.com | واتساب: 00905313263722
"""
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import yaml                                            # noqa: E402
from PIL import Image                                  # noqa: E402
from vision_inspect import inspect_asset, sha1_of      # noqa: E402
from quality_brain import build_brain, MockBrain, _extract_json  # noqa: E402
from store import QaStore                              # noqa: E402
from guard_notify import TelegramGuard                 # noqa: E402
from design_guard import process_one, final_decision   # noqa: E402

CFG = yaml.safe_load((Path(__file__).parent.parent / "scripts" / "config.yaml")
                     .read_text(encoding="utf-8"))
failures = []


def check(name, cond):
    print(("✅" if cond else "❌"), name)
    if not cond:
        failures.append(name)


with tempfile.TemporaryDirectory() as td:
    tdp = Path(td)

    # ---- 1) كاشف الإطار الأسود الميت
    p = tdp / "black.png"; Image.new("RGB", (500, 500), (1, 1, 1)).save(p)
    r = inspect_asset(p, CFG, {})
    check("BLACK_FRAME detected on dead frame", any(f.code == "BLACK_FRAME" for f in r.findings))
    check("hard_fail flag set for critical defect", r.hard_fail)

    # ---- 2) كاشف الأبعاد الصغيرة
    p = tdp / "tiny.png"; Image.new("RGB", (50, 40), (200, 30, 30)).save(p)
    r = inspect_asset(p, CFG, {})
    check("TINY_DIMENSIONS detected", any(f.code == "TINY_DIMENSIONS" for f in r.findings))

    # ---- 3) نص LLM مشوّه كلاسيكي (placeholder + تكرار)
    p = tdp / "bad.md"
    p.write_text("Lorem ipsum buy buy buy buy product qualty is bestest with many mistaks here", encoding="utf-8")
    r = inspect_asset(p, CFG, {})
    codes = {f.code for f in r.findings}
    check("LAZY_PLACEHOLDERS detected", "LAZY_PLACEHOLDERS" in codes)
    check("REPETITION_LOOP detected", "REPETITION_LOOP" in codes)

    # ---- 4) سلامة PNG CRC (ملف سليم لا يُرفع عنه علم كاذب) + صورة غنية تُعتمد فعلاً
    p = tdp / "good.png"; Image.new("RGB", (600, 600), (10, 200, 30)).save(p)
    r = inspect_asset(p, CFG, {})
    check("clean png passes CRC integrity",
          not any(f.code in ("PNG_CRC_BROKEN", "BAD_MAGIC", "EMPTY_FILE") for f in r.findings))

    import numpy as np
    from PIL import ImageDraw, ImageFilter
    arr = (np.random.default_rng(7).integers(0, 256, (720, 720, 3))).astype("uint8")
    img = Image.fromarray(arr).filter(ImageFilter.DETAIL)
    d = ImageDraw.Draw(img)
    d.rectangle([100, 100, 620, 300], outline=(255, 255, 255), width=6)
    d.ellipse([250, 350, 470, 570], outline=(0, 0, 0), width=8)
    rich = tdp / "rich.png"; img.save(rich)
    rr = inspect_asset(rich, CFG, {})
    v_rich, _ = final_decision(rr.structural_score, "accepted", 92.0, rr.hard_fail, CFG)
    check("genuinely-rich asset is accepted end-to-end", v_rich == "accepted" and not rr.hard_fail)

    # ---- 5) حق النقض: hard_fail يمنع الاعتماد حتى لو قال النموذج accepted
    v, score = final_decision(10.0, "accepted", 99.0, True, CFG)
    check("veto power: structural hard-fail blocks AI accept", v != "accepted")

    # ---- 6) انتشال JSON من رد فوضوي للنموذج
    parsed = _extract_json('نص قبل ```json\n{"match_score": 91, "verdict": "accepted"}\n``` بعد')
    check("JSON extractor survives fenced replies", parsed and parsed["match_score"] == 91)

    # ---- 7) بناء العقل حسب المفاتيح (بدون مفاتيح ⇒ mock حتمي)
    brain = build_brain(CFG)
    check("no keys ⇒ deterministic MockBrain", isinstance(brain, MockBrain))

    # ---- 8) التخزين المحلي + مؤشرات الإنتاجية
    store = QaStore(CFG, tdp)
    store.save_report({"asset_id": "x1", "checksum": sha1_of(p), "filename": "good.png",
                       "verdict": "accepted", "match_score": 95.0,
                       "defects": [], "created_at": "2026-11-03T00:00:00+00:00"})
    m = store.productivity_metrics(days=30)
    check("metrics computed from archive", m["total"] >= 1 and m["accept_rate"] is not None)

    # ---- 9) تليجرام معطل بأمان عند غياب الأسرار (لا استثناء إطلاقاً)
    tg = TelegramGuard()
    check("telegram degrades silently without secrets",
          (not tg.enabled) and tg.report_asset({"filename": "x", "verdict": "rejected"}) is False)

    # ---- 10) الأنبوب الكامل: ملف → قرار → أرشفة
    known = {}
    rec = process_one(tdp / "black.png", CFG, brain, store, known, dry_run_archive=True)
    check("pipeline produces decision record with provider", rec["verdict"] in
          ("accepted", "rejected", "needs_review") and bool(rec["ai_provider"]))

print("\n" + ("🏆 ALL LAYER CONTRACTS OK — Design-Guard-ZeroBaran جاهز للنشر"
              if not failures else f"💥 {len(failures)} فشل: {failures}"))
sys.exit(1 if failures else 0)
