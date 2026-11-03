# 🛡️ Design-Guard-ZeroBaran
### المشروع #39 — المنظومة الذاتية المتقدمة لمراقبة وفحص جودة مخرجات الذكاء الاصطناعي والتصاميم

> **البديل المجاني الصريح لأدوات Hallmark / Impeccable** — يفحص الصور والنصوص المولّدة آلياً، يكشف التشوهات الهندسية والإملائية والمنطقية، ويقرر: **معتمد / مرفوض / يحتاج مراجعة** — قبل النشر، بتكلفة **صفر دولار**.

---

## 👤 المالك والحقوق (Ownership & Credits)

| | |
|---|---|
| ✍️ **المؤلف والمالك** | **Baran Avisat** — المؤسس والمطور الرئيسي |
| 📧 **البريد والدعم** | Baranavisat@gmail.com |
| 📱 **واتساب مباشر** | `00905313263722` (+90 531 326 3722) |
| 🛒 **المتجر الرسمي** | [baranavi.gumroad.com](https://baranavi.gumroad.com/) |
| 🏛️ **الاستوديو** | ZeroBaran Studio — جميع الحقوق محفوظة © 2026 |

---

## ❓ ما هو Design-Guard-ZeroBaran؟

نظام ذكي متكامل ومستقل لفحص ومراقبة جودة **المخرجات البصرية والنصية للذكاء الاصطناعي**: يقوم بمراجعة الصور والتصاميم والنصوص المولدة آلياً، واكتشاف أي عيوب (تشوهات الأطراف في الصور، إطارات ميتة، ملفات محزوفة، أخطاء إملائية، حلقات تكرار LLM، نصوص placeholder منسية) **قبل اعتمادها للنشر** — دون دفع دولار واحد لأي منصة فحص جودة مدفوعة.

### لماذا تتمناه كل شركة وكل صانع محتوى؟
- 💰 **توفير مال فلكي:** أدوات تدقيق الجودة الآلية باهظة؛ هنا نفس الغرض باحترافية عسكرية وبتكلفة صفر.
- 🎯 **ريادة فئة شبه فارغة (Niche Dominance):** سوق يفتقر للحلول التنافسية — ميزة فريدة لك.
- ✅ **جودة معصومة من الخطأ (Zero Defect Outputs):** لا يُنشر أصل مشوّه أبداً — احترافية مطلقة لعلامتك.

---

## 🛠️ التقنيات المجانية 100% (Free Tech Stack)

| المكون | الخدمة المجانية | دوره |
|---|---|---|
| محرك التشغيل المجدول (Cron) | **GitHub Actions** | فحص دوري كل 3 ساعات + فوري عند push + ملخص أسبوعي |
| محرك الفحص البصري والنصي | **Python + OpenCV + Pillow + PyTesseract** | تحليل بكسلات، كشف تشوه/ضبابية/فساد، OCR، تدقيق نصي |
| العقل الذكي للمراجعة | **Gemini Vision API / Groq API (Free Tiers)** | تقييم إنشائي: تشريح، تناسق، أخطاء خفية، مطابقة الهوية |
| قاعدة سجلات الفحص | **Supabase (PostgreSQL Free Tier)** | أرشيف التقارير + مؤشرات الإنتاجية عبر الزمن |
| قناة التنبيه والتحكم | **Telegram Bot API / Streamlit** | تقرير فوري على هاتفك + مركز قيادة تفاعلي |

---

## 📐 البنية الهندسية — 4 طبقات تتناغم كمراقب لا يغفل

```
[رفع/توليد المخرج (صورة أو نص) → ضعه في inbox/]
                │
                ▼
[طبقة 1: Python + OpenCV/Pillow — أبعاد، ضبابية، CRC، إطارات ميتة،
 كثافة حواف مشبوهة (أصابع/أطراف AI)، تكرار بصري، إملاء/منطق النصوص]
                │
                ▼
[طبقة 2: Gemini Vision / Groq — خبير جودة صارم يعيد JSON:
 match_score, verdict, defects[], brand_consistency, fix_suggestion]
                │
                ▼
[طبقة 3: Supabase — أرشيف qa_reports + views إنتاجية (fallback JSON محلي)]
                │
                ▼
[طبقة 4: Telegram تقرير فوري 🔍🟢📊 + لوحة Streamlit + ملخص أسبوعي]
```

### حق النقض العسكري ⚖️
لو قال النموذج «accepted» لكن الفحص المجتري رصد عيباً **critical** (ملف محزوف، إطار أسود، مستحيل فك الترميز) — يُسحق قرار النموذج تلقائياً. الحاسوب لا يكذب.

---

## 📂 هيكل المشروع

```
design-guard-zerobaran/
├── dashboard.py                 # 🖥️ مركز قيادة Streamlit (KPIs، خريطة عيوب، طابور مراجعة)
├── scripts/
│   ├── design_guard.py          # 🎼 المنسّق: inbox → فحص → قرار → أرشفة → تنبيه
│   ├── vision_inspect.py        # 👁️ الطبقة 1: OpenCV/Pillow/CRC/NLP inspection
│   ├── quality_brain.py         # 🧠 الطبقة 2: Gemini Vision + Groq + MockBrain
│   ├── store.py                 # 🗄️ الطبقة 3: Supabase REST + JSON fallback
│   ├── guard_notify.py          # 📲 الطبقة 4: Telegram reports/summaries
│   ├── config.yaml              # ⚙️ كل العتبات والأسعار هنا — بلا كود صلب
│   └── requirements.txt         # 📦 كل الاعتماديات مجانية
├── supabase/schema.sql          # 🏛️ الجدول + 3 views جاهزة (الصق وانسخ Run)
├── tests/smoke_test.py          # 🧪 13 عقداً تعاقدياً — يعمل بلا مفاتيح
├── inbox/                       # 📥 ضع المخرجات الجديدة هنا
└── archive/{accepted,rejected,review}/  # 📤 تُؤرشف تلقائياً حسب القرار
+ .github/workflows/design-guard-zerobaran.yml   # ⏰ Cron المجاني
```

---

## 🚀 التشغيل — 3 دقائق

### وضع تجريبي فوري (صفر حسابات، صفر مفاتيح):
```bash
cd design-guard-zerobaran
pip install -r scripts/requirements.txt
python scripts/design_guard.py --demo      # يولّد 7 عيّنات (سليمة ومعطوبة) ويفحصها
python scripts/design_guard.py --weekly    # مؤشرات الإنتاجية
streamlit run dashboard.py                 # مركز القيادة
```

### الوضع الاحترافي الكامل (مجاني 100%):
1. **Gemini Vision** — مفتاح مجاني من [aistudio.google.com](https://aistudio.google.com/apikey) ⇒ Secret `GEMINI_API_KEY`.
2. **Groq** (بديل نصي سريع) ⇒ Secret `GROQ_API_KEY`.
3. **Supabase** — مشروع مجاني، الصق `supabase/schema.sql` في SQL Editor ⇒ Secrets `SUPABASE_URL` + `SUPABASE_SERVICE_KEY`.
4. **Telegram** — أنشئ بوتاً عبر @BotFather، خذ الـ chat id ⇒ Secrets `TELEGRAM_BOT_TOKEN` + `TELEGRAM_CHAT_ID`.
5. اربط المستودع بـ GitHub Actions — وسيرفع الأصول المولّدة إلى `inbox/` ليصلك القرار على هاتفك خلال دقائق:

> 🔍 **تقرير مراقبة الجودة — Design-Guard-ZeroBaran**
> 📦 الأصل: `poster_v3.png` (image)
> 🟢 **الحالة:** معتمد — اجتاز كافة اختبارات الجودة
> 📊 **نسبة المطابقة:** 98%

---

## 🧨 ماذا يكشف النظام؟ (21 كود عيّنة)

**صور:** `EMPTY_FILE` `BAD_MAGIC` `PNG_CRC_BROKEN` `JPEG_EOF_MISSING` `UNDECODABLE_IMAGE` `TINY_DIMENSIONS` `EXTREME_ASPECT` `BLACK_FRAME` `WHITE_FRAME` `FLAT_IMAGE` `BLURRY_IMAGE` `LOW_ENTROPY_PATTERN` `EDGE_ANOMALY` (بصمة تشوه الأصابع/الأطراف) `OBJECT_FRAGMENTATION` `EXACT_DUPLICATE` `NEAR_DUPLICATE`

**نصوص:** `STUB_TEXT` `MOJIBAKE_ENCODING` `LAZY_PLACEHOLDERS` `REPETITION_LOOP` `POOR_STRUCTURE` `SPELL_ERRORS`

---

## ✅ إثبات العمل (نتائج حقيقية من تشغيل فعلي)

دورة `--demo` على 7 عيّنات مولّدة:

| الأصل | القرار | المطابقة | السبب المرصود |
|---|---|---|---|
| poster_clean.png | 🟢 accepted | 100% | نظيف بالكامل |
| poster_blurry.png | 🟡 needs_review | 62.5% | BLURRY_IMAGE (Laplacian=12.4) |
| frame_black.png | 🔴 rejected | 14% | BLACK_FRAME — فشل توليد |
| thumb_tiny.png | 🔴 rejected | 47.5% | TINY_DIMENSIONS 120×90 |
| poster_clean_COPY.png | 🟡 needs_review | 70% | EXACT_DUPLICATE + NEAR_DUPLICATE |
| copy_good.md | 🟢 accepted | 100% | — |
| copy_bad.md | 🔴 rejected | 32.5% | LAZY_PLACEHOLDERS + REPETITION_LOOP + SPELL_ERRORS |

- **Dedupe:** إعادة المسح التالي = «0 مفحوص جديد، متجاهل (مكرّر)» — لا يُعاد فحص أي أصل أبداً.
- **الأرشفة التلقائية:** انتقلت الملفات فعلياً إلى `archive/accepted|rejected|review`.
- **الملخص الأسبوعي:** نسبة قبول 16.7%، رفض 50%، متوسط مطابقة 54.4%، وأكثر العيوب تكراراً مصنّفة.
- **الاختبار التعاقدي:** `🏆 ALL LAYER CONTRACTS OK` (13/13).

---

## 🔒 الأمان والخصوصية
- لا تُرفع أي صورة إلى أي مكان إلا Gemini/Groq (اختياري) — التخزين اختيارك.
- مفاتيح الخادم في GitHub Secrets فقط؛ `schema.sql` يفعّل RLS — الوصول عبر service-role حصراً.
- احترام كامل لحصص الخطط المجانية: batching + retry/backoff على 429.

---

## 🌐 ضمن أسطول ZeroBaran Studio
هذا المشروع **#39** في سلسلة مشاريع «صفر تكلفة» — بما فيها **Pulse-Zero (#33)** لرصد مشاعر العملاء. كل مشروع مستقل بذاته، وكلها تعمل على نفس البنية المجانية: GitHub Actions + Supabase + Telegram + طبقة AI مجانية.

**لأي استفسار تجاري أو تخصيص مؤسسي:** تواصل مباشرة مع المؤلف **Baran Avisat** — 📧 Baranavisat@gmail.com • 📱 واتساب `00905313263722` • 🛒 baranavi.gumroad.com

*© 2026 Baran Avisat — ZeroBaran Studio. جميع الحقوق محفوظة.*
