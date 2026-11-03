# -*- coding: utf-8 -*-
"""
Design-Guard-ZeroBaran — الطبقة 1: محرك الفحص البصري والنصي
============================================================
Inspection & Vision Layer: يفحص هيكل الملف، الأبعاد، الضبابية،
الإطارات التالفة، التشوهات الهندسية (OpenCV)، ويقرأ النص المستخرج
ويدقق الإملاء/المنطق/الهيكلة. يعمل بالكامل دون أي API.

المؤلف: Baran Avisat | baranavisat@gmail.com | واتساب: 00905313263722
الحقوق محفوظة © ZeroBaran Studio — MIT License
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import re
import zlib
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import List, Optional

from PIL import Image, ImageFile

ImageFile.LOAD_TRUNCATED_IMAGES = True  # لا نسقط عند ملف تالف — بل نرفضه بتقرير

try:
    import cv2
    import numpy as np
    HAS_CV2 = True
except Exception:  # pragma: no cover
    HAS_CV2 = False


# ------------------------------------------------------------------ Helpers
def sha1_of(path: Path) -> str:
    h = hashlib.sha1()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


@dataclass
class Finding:
    """ملاحظة فحص واحدة — درجة خطورتها تحسم القرار النهائي."""
    code: str          # معرّف الآلة: BLURRY_IMAGE / SPELL_ERRORS ...
    severity: str      # critical | major | minor | info
    message_ar: str    # شرح عربي للمهندس/المصمم
    metric: dict = field(default_factory=dict)

    def to_dict(self):
        return asdict(self)


@dataclass
class InspectionReport:
    asset_id: str
    filename: str
    kind: str                       # image | text
    width: int = 0
    height: int = 0
    file_size: int = 0
    format: str = ""
    structural_score: float = 0.0   # 0..100 نتيجة الفحص الآلي المجترة
    findings: List[Finding] = field(default_factory=list)
    extracted_text: str = ""
    duplicate_of: Optional[str] = None
    checksum: str = ""

    @property
    def hard_fail(self) -> bool:
        return any(f.severity == "critical" for f in self.findings)

    def add(self, code, severity, message_ar, **metric):
        self.findings.append(Finding(code, severity, message_ar, metric))

    def to_dict(self):
        d = asdict(self)
        d["findings"] = [f.to_dict() for f in self.findings]
        d["hard_fail"] = self.hard_fail
        return d


# ----------------------------------------------------- بنية الملف (بدون فك ترميز كامل)
def _check_file_integrity(path: Path) -> List[Finding]:
    """فحص الترويسات السحرية + سلامة CRC داخل PNG/JPEG — يكشف الملفات المحزوفة/التالفة."""
    findings: List[Finding] = []
    raw = path.read_bytes()
    if len(raw) == 0:
        return [Finding("EMPTY_FILE", "critical", "الملف فارغ تماماً — أعد التوليد.")]

    sigs = {
        b"\x89PNG\r\n\x1a\n": "png",
        b"\xff\xd8\xff": "jpeg",
        b"BM": "bmp",
        b"RIFF": "webp/tiff-container",
        b"GIF8": "gif",
        b"II*\x00": "tiff-le", b"MM\x00*": "tiff-be",
    }
    fmt = next((v for k, v in sigs.items() if raw.startswith(k)), None)
    if fmt is None:
        # قد يكون نصاً عادياً — يُقبل إن كان قابلاً للترميز كنص
        try:
            raw.decode("utf-8")
            return findings
        except UnicodeDecodeError:
            findings.append(Finding("BAD_MAGIC", "critical",
                                    "ترويسة الملف غير معروفة أو تالفة — ملف ثنائي مكسور."))
        return findings

    if fmt == "png":
        # التحقق من كتل CRC: كل كتلة IDAT/IHDR... تسبقها crc32 صحيحة
        i, blocks_bad = 8, 0
        while i + 8 <= len(raw):
            length = int.from_bytes(raw[i:i+4], "big")
            btype = raw[i+4:i+8]
            if i + 12 + length > len(raw):
                blocks_bad += 1
                break
            stored_crc = int.from_bytes(raw[i+8+length:i+12+length], "big")
            calc_crc = zlib.crc32(raw[i+4:i+8+length]) & 0xFFFFFFFF
            if stored_crc != calc_crc:
                blocks_bad += 1
            i += 12 + length
            if btype == b"IEND":
                break
        if blocks_bad:
            findings.append(Finding("PNG_CRC_BROKEN", "critical",
                                    f"كتل CRC تالفة في PNG ({blocks_bad}) — الصورة مقطوعة/غير كاملة.",
                                    bad_blocks=blocks_bad))
    if fmt == "jpeg" and not raw.rstrip(b"\x00").endswith(b"\xff\xd9"):
        findings.append(Finding("JPEG_EOF_MISSING", "critical",
                                "JPEG تنتهي قبل علامة النهاية FFD9 — ملف محزوف أثناء التنزيل/التوليد."))
    return findings


# ------------------------------------------------------------- الفحص البصري (OpenCV)
def _pixel_entropy(gray_hist) -> float:
    p = gray_hist / max(gray_hist.sum(), 1)
    p = p[p > 0]
    return float(-(p * np.log2(p)).sum()) if HAS_CV2 else 0.0


def inspect_image(path: Path, cfg: dict, seen_hashes: dict) -> InspectionReport:
    insp = cfg["inspection"]
    rep = InspectionReport(
        asset_id=sha1_of(path)[:16], filename=path.name, kind="image",
        file_size=path.stat().st_size, checksum=sha1_of(path),
    )

    # 1) سلامة الهيكل أولاً
    rep.findings.extend(_check_file_integrity(path))

    try:
        img = Image.open(path)
        img.load()
        rep.width, rep.height = img.size
        rep.format = (img.format or "").lower()
    except Exception as e:
        rep.add("UNDECODABLE_IMAGE", "critical",
                f"تعذّر فك ترميز الصورة نهائياً: {e.__class__.__name__}")
        rep.structural_score = 0.0
        return rep

    if rep.checksum in seen_hashes:
        rep.duplicate_of = seen_hashes[rep.checksum]
        rep.add("EXACT_DUPLICATE", "major",
                f"نسخة مطابقة حرفياً للأصل المفحوص سابقاً «{rep.duplicate_of}» — مضيعة لدفعة توليد.")

    # 2) الأبعاد والنسب
    if rep.width < insp["min_width"] or rep.height < insp["min_height"]:
        rep.add("TINY_DIMENSIONS", "critical",
                f"الأبعاد ({rep.width}×{rep.height}) أصغر من الحد الأدنى "
                f"({insp['min_width']}×{insp['min_height']}) — غير صالحة للنشر التجاري.",
                width=rep.width, height=rep.height)
    ratio = max(rep.width, rep.height) / max(min(rep.width, rep.height), 1)
    if ratio > insp["max_aspect_ratio"]:
        rep.add("EXTREME_ASPECT", "major",
                f"نسبة الأبعاد شاذة ({ratio:.2f}:1) — غالباً قصّ خاطئ أو تمدد AI.",
                ratio=round(ratio, 2))

    if not HAS_CV2:
        # Pillow-only fallback: تقييم أساسي
        gray = img.convert("L")
        stat = list(gray.getextrema())
        rep.structural_score = 70.0
        rep.add("NO_OPENCV", "info", "OpenCV غير مثبت — تم فحص أعمق بإعدادات مبسطة.")
        if stat[1] - stat[0] < 10:
            rep.add("FLAT_IMAGE", "critical", "الصورة مسطحة (بلا تباين تقريباً) — إطار شبه أحادي اللون.")
        return rep

    arr = np.asarray(img.convert("RGB"))
    gray = cv2.cvtColor(arr, cv2.COLOR_RGB2GRAY)

    # 3) الإطارات الميتة (أسود/أبيض كامل)
    std = float(gray.std())
    mean = float(gray.mean())
    if std < insp["black_frame_std"]:
        rep.add("BLACK_FRAME", "critical", "الإطار شبه أسود بالكامل — فشل واضح في التوليد.", std=round(std, 2))
    elif std < insp["white_frame_std"] and mean > 240:
        rep.add("WHITE_FRAME", "critical", "الإطار شبه أبيض بالكامل — فشل واضح في التوليد.", std=round(std, 2))

    # 4) الضبابية (Laplacian variance)
    lap_var = float(cv2.Laplacian(gray, cv2.CV_64F).var())
    if lap_var < insp["blur_threshold"]:
        sev = "critical" if lap_var < insp["blur_threshold"] * 0.4 else "major"
        rep.add("BLURRY_IMAGE", sev,
                f"الصورة ضبابية (تباين Laplacian={lap_var:.1f} < {insp['blur_threshold']}).",
                laplacian=round(lap_var, 1))

    # 5) إنتروبيا البكسل — الأنماط الرديئة/المكررة جداً
    hist, _ = np.histogram(gray, bins=256, range=(0, 256))
    ent = _pixel_entropy(hist.astype(float))
    if ent < insp["corruption_entropy_min"]:
        rep.add("LOW_ENTROPY_PATTERN", "major",
                f"إنتروبيا منخفضة ({ent:.2f}) — نمط رديء/بلوكات متكررة توحي بفساد.", entropy=round(ent, 2))

    # 6) كشف التشوهات الهندسية الشائعة في صور AI
    edges = cv2.Canny(gray, 80, 180)
    edge_density = float(edges.sum()) / (255.0 * edges.size)
    if edge_density > insp["anomaly_edge_density_max"]:
        rep.add("EDGE_ANOMALY", "major",
                f"كثافة حواف استثنائية ({edge_density:.2f}) — مؤشر كلاسيكي على تشوه أطراف/أصابع زائدة.",
                edge_density=round(edge_density, 3))

    cnt_gray = cv2.GaussianBlur(gray, (5, 5), 0)
    contours, _ = cv2.findContours(
        (cnt_gray > 0).astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    big = [c for c in contours if cv2.contourArea(c) > gray.size * 0.002]
    if len(big) > insp["anomaly_contours_max"]:
        rep.add("OBJECT_FRAGMENTATION", "minor",
                f"عدد الكائنات الكبيرة غير معتاد ({len(big)}) — مشهد مجزّأ/عناصر ذائبة.",
                contours=len(big))

    # 7) تكرار شبه-مطابق (Perceptual-ish عبر هيستوجرام متشابه)
    hsv = cv2.calcHist([arr], [0, 1], None, [32, 32], [0, 256, 0, 256])
    cv2.normalize(hsv, hsv)
    for other_fp, other_hist in seen_hashes.get("_histograms", {}).items():
        if other_fp == rep.checksum:
            continue
        sim = cv2.compareHist(other_hist, hsv, cv2.HISTCMP_CORREL)
        if sim >= insp["duplicate_similarity"]:
            rep.add("NEAR_DUPLICATE", "major",
                    f"تشابه بصري {sim*100:.1f}% مع أصل مفحوص سابقاً — نسخة شبه مكررة.",
                    similarity=round(sim, 3))
            break
    seen_hashes.setdefault("_histograms", {})[rep.checksum] = hsv

    # ---- احتساب النتيجة المجترة (خصم حسب الخطورة)
    score = 100.0
    weights = {"critical": 45, "major": 18, "minor": 6, "info": 0}
    for f in rep.findings:
        score -= weights.get(f.severity, 0)
    rep.structural_score = max(0.0, round(score, 1))
    return rep


# ------------------------------------------------------------ OCR اختياري داخل الصورة
def ocr_if_available(path: Path) -> str:
    if not HAS_CV2:
        return ""
    try:
        import pytesseract
        img = cv2.imread(str(path))
        if img is None:
            return ""
        txt = pytesseract.image_to_string(img, lang="eng+ara")
        return txt.strip()
    except Exception:
        return ""  # tesseract binary غير مثبت — نتجاهل بأمان


# --------------------------------------------------------------- الفحص النصي
_MOJIBAKE_MARKS = ["ã€", "â€", "å¥", "ï¿½", "Ã©", "â€™", "\ufffd"]

def _words(text: str) -> List[str]:
    return re.findall(r"[A-Za-z\u0600-\u06FF']+", text)


def inspect_text(path: Path, cfg: dict, seen_hashes: dict) -> InspectionReport:
    tc = cfg["text_checks"]
    rep = InspectionReport(
        asset_id=sha1_of(path)[:16], filename=path.name, kind="text",
        file_size=path.stat().st_size, checksum=sha1_of(path), format="text",
    )
    rep.findings.extend(_check_file_integrity(path))

    raw = path.read_bytes()
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        try:
            text = raw.decode("cp1256", errors="replace")
        except Exception:
            text = raw.decode("latin-1", errors="replace")
    rep.extracted_text = text[:4000]

    if rep.checksum in seen_hashes and seen_hashes[rep.checksum] is not True:
        rep.duplicate_of = seen_hashes[rep.checksum]
        rep.add("EXACT_DUPLICATE", "major",
                f"نص مطابق حرفياً لنص مفحوص سابقاً «{rep.duplicate_of}». ")

    words = _words(text)
    if len(text.strip()) < tc["min_length"]:
        rep.add("STUB_TEXT", "critical",
                f"النص أقصر من {tc['min_length']} حرفاً — مقطع مبتور أو فشل توليد.")
    if not words:
        rep.add("NO_WORDS", "critical", "لا توجد كلمات قابلة للقراءة في الملف.")

    # ترميز مكسور (mojibake)
    if tc["mojibake_detect"]:
        marks = [m for m in _MOJIBAKE_MARKS if m in text]
        if marks:
            rep.add("MOJIBAKE_ENCODING", "critical",
                    f"ترميز مكسور مكتشَف ({', '.join(marks[:3])}) — انقل النص إلى UTF-8 وأعد التوليد.",
                    markers=marks[:5])

    # placeholders كسولة نموذجية في مخرجات LLM
    low = text.lower()
    hits = [ph for ph in tc["forbidden_placeholders"] if ph in low]
    if hits:
        rep.add("LAZY_PLACEHOLDERS", "major",
                f"عناصر نابضة بالتخمين لم تُستبدل: {', '.join(hits)} — المحتوى غير جاهز للنشر.",
                placeholders=hits)

    # تكرار متتالي (حلقة توليد)
    max_run, run, prev = 1, 1, None
    for w in words:
        lw = w.lower()
        if lw == prev:
            run += 1
            max_run = max(max_run, run)
        else:
            run = 1
        prev = lw
    if max_run > tc["max_repeated_word"]:
        rep.add("REPETITION_LOOP", "critical",
                f"كلمة تكررت {max_run} مرات متتالية — حلقة تكرار كلاسيكية في مخرجات الذكاء الاصطناعي.",
                longest_run=max_run)

    # جمل بلا علامات ترقيم بشكل مفرط (منطق/هيكل)
    sentences = [s for s in re.split(r"[.!?\n\u061F]", text) if len(s.strip()) > 25]
    if sentences:
        punct_ok = sum(1 for s in sentences if re.search(r"[,;:\u060C]", s))
        if punct_ok / len(sentences) < 0.15 and len(sentences) > 4:
            rep.add("POOR_STRUCTURE", "minor",
                    "جمل طويلة متتالية بلا فواصل — تدفق نصي رديء يستحسن إعادة صياغة.",
                    sentences=len(sentences))

    # إملاء إنجليزي (اختياري — pyspellchecker)
    if tc.get("spellcheck"):
        try:
            from spellchecker import SpellChecker
            sp = SpellChecker()
            en_words = [w for w in set(w.lower() for w in words) if re.fullmatch(r"[a-z']+", w)]
            unknown = sp.unknown(en_words) if en_words else set()
            # عتبة ذكية: نسبة الأخطاء المجهولة
            if en_words and len(unknown) / len(en_words) > 0.18 and len(unknown) >= 4:
                rep.add("SPELL_ERRORS", "major",
                        f"{len(unknown)} كلمات إنجليزية مشكوكة من أصل {len(en_words)} — راجع الإملاء قبل النشر.",
                        samples=sorted(unknown)[:8])
        except ImportError:
            rep.add("NO_SPELLCHECKER", "info", "pyspellchecker غير مثبت — تم تجاوز التدقيق الإملائي.")

    score = 100.0
    weights = {"critical": 45, "major": 18, "minor": 6, "info": 0}
    for f in rep.findings:
        score -= weights.get(f.severity, 0)
    rep.structural_score = max(0.0, round(score, 1))
    return rep


# ------------------------------------------------------------------ Dispatcher
def inspect_asset(path: Path, cfg: dict, seen_hashes: dict) -> InspectionReport:
    ext = path.suffix.lower()
    if ext in cfg["pipeline"]["extensions_image"]:
        rep = inspect_image(path, cfg, seen_hashes)
        ocr = ocr_if_available(path)
        if ocr:
            rep.extracted_text = ocr[:4000]
        return rep
    if ext in cfg["pipeline"]["extensions_text"]:
        return inspect_text(path, cfg, seen_hashes)
    rep = InspectionReport(asset_id=sha1_of(path)[:16], filename=path.name,
                           kind="unknown", file_size=path.stat().st_size,
                           checksum=sha1_of(path))
    rep.add("UNSUPPORTED_TYPE", "major", f"امتداد غير مدعوم للفحص: {ext}")
    rep.structural_score = 40.0
    return rep


if __name__ == "__main__":
    import sys, yaml
    cfg = yaml.safe_load(open(Path(__file__).parent / "config.yaml", encoding="utf-8"))
    for p in sys.argv[1:]:
        r = inspect_asset(Path(p), cfg, {})
        print(json.dumps(r.to_dict(), ensure_ascii=False, indent=2))
