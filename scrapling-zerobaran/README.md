# 🕸️ Scrapling-ZeroBaran — المنظومة الذاتية لزحف البيانات واستخراج المحتوى

> **المشروع الثامن والثلاثون (38)** من أسطول ZeroBaran — البديل المجاني الصريح لخدمات Zyte / ScraperAPI / Bright Data.
> **© المؤلف: Baran Avisat** | 📧 Baranavisat@gmail.com | 📱 واتساب: **00905313263722** | ZeroBaran Studio

---

## ما هو Scrapling-ZeroBaran؟

عنكبوت بيانات رقمي مستقل يعمل بالكامل على موارد مجانية 100%: يزحف للمواقع المستهدفة دورياً، يستخرج الحقول والجداول والأسعار بدقة، يعيد الذكاء الاصطناعي هيكلة النص العشوائي إلى سجلات JSON نظيفة مصنّفة، يقارنها بالنسخ القديمة فيرصد أي تغيّر سعر أو عنصر جديد فوراً، ثم يرسل تقرير «🕸️ حالة الزحف» إلى هاتفك عبر تليجرام — وكل ذلك مع حوكمة أخلاقية صارمة داخل الكود نفسه.

## 🛠️ التقنيات المجانية البحتة

| الطبقة | التقنية | الدور |
|---|---|---|
| Cron مجاني | GitHub Actions | زحف مجدول كل 6 ساعات + ملخص أسبوعي |
| محرك الزحف | Python + Scrapling OSS + Playwright + BeautifulSoup/lxml | تصفح ذكي بتدرّج محركات آمن |
| عقل الهيكلة | Gemini API / Groq API (Free Tiers) | تنظيف النصوص، تصنيفها، تطبيع الأسعار |
| الأرشيف | Supabase PostgreSQL (Free Tier) + JSON fallback | سجلات + تاريخ تغيّرات لكل قيمة |
| التوصيل | Telegram Bot + Streamlit | تقارير فورية ولوحة قيادة عربية |

## 🏗️ البنية (4 طبقات)

```
[config.yaml أهداف+وصفات] → crawler.py (RobotsGate + Throttle + AntiBlock + CircuitBreaker)
        → extractor.py (وصفات CSS + Self-Healing Selectors + جداول + ترقيم صفحات)
        → parsing_brain.py (Groq/Gemini/MockBrain → JSON منظّم ومصنّف)
        → store.py (Supabase/JSON + Change Detection بتاريخ قيم)
        → notify.py (تقرير 🕸️ + تنبيهات 🔻🔺 التغيّر) | dashboard.py (Streamlit)
```

## 🚀 التشغيل السريع

```bash
pip install -r scripts/requirements.txt          # الأساس فقط يكفي للعمل
python scripts/scrape_run.py demo                # تجربة offline بلا إنترنت
python scripts/scrape_run.py run                 # زحف حي لكل الأهداف
python scripts/scrape_run.py stats               # إحصاءات المخزن
python scripts/scrape_run.py export              # تصدير JSONL إلى exports/
streamlit run dashboard.py                       # مركز القيادة
python tests/smoke_test.py                       # 31 عقداً تعاقدياً — يجب 🏆
```

### إضافة موقعك المستهدف
عدّل `scripts/config.yaml`:
```yaml
targets:
  - name: "my-store"
    start_urls: ["https://example.com/products"]
    max_pages: 5
    follow_links_selector: "a.next"
    extractors:
      item_selector: "div.product-card"
      fields:
        title: { selector: "h3.name" }
        price: { selector: "span.price" }
```

### الأسرار الاختيارية (GitHub Secrets)
`GROQ_API_KEY` أو `GEMINI_API_KEY` — `SUPABASE_URL` + `SUPABASE_SERVICE_KEY` — `TELEGRAM_BOT_TOKEN` + `TELEGRAM_CHAT_ID`.
بدونها يعمل النظام بوضع آمن كامل (MockBrain + JSON محلي + سجلات في CI summary). نفّذ `supabase/schema.sql` مرة واحدة عند استخدام Supabase.

## ⚖️ الحوكمة الأخلاقية (Ethical-by-Design) — جزء من المحرك لا صفحة قانونية

1. **بوابة robots.txt** تُسقط أي مسار محظور قبل إرسال الطلب.
2. **تخنيق مهذب** عشوائي 1–3 ثوانٍ لكل مضيف — لا إزعاج للسيرفرات أبداً.
3. **قاطع الدائرة**: بعد 3 حواجز متتالية يتوقف النظام بأدب ويُرسل تنبيهاً بدل الإلحاح.
4. **ممنوع برمجياً**: تجاوز جدران الدفع/تسجيل الدخول، حصاد بيانات الاعتماد، جمع بيانات أشخاص خاصة بلا أساس قانوني.
5. **السيادة**: بياناتك تبقى في بيئتك؛ صفر مشاركة لطرف خارجي.
> أنت المسؤول القانوني عن اختيار الأهداف؛ استخدم مواقع تسمح بالزحف أو تملك حق جمع بياناتها.

## ✅ ما تم إثباته فعلياً (نتائج تشغيل حقيقية)
- زحف حي ناجح لموقعين تجريبيين: **30 سجلاً جديداً** من صفحتين، محرك `requests`، صفر حواجز، صفر أخطاء.
- **كشف التغيّر مُثبت**: تغيير سعر مسجّل (9.99→7.49) أطلق حدث `CHANGED` بتنبيه 🔻 صحيح العنوان.
- **Dedupe مُطلق**: إعادة التشغيل أعطت `records_new: 0` — لا تكرار نهائياً.
- **Self-healing selectors**: وصفة مكسورة أعادت الرسو بنيوياً وأخرجت السجلات.
- **Smoke test: 🏆 ALL LAYER CONTRACTS OK (31/31)** يعمل offline بالكامل.

## 📂 خريطة الملفات
```
scrapling-zerobaran/
├── scripts/ crawler.py · extractor.py · parsing_brain.py · store.py · notify.py
│            scrape_run.py (المنسّق) · config.yaml · requirements.txt
├── supabase/schema.sql
├── dashboard.py · tests/smoke_test.py
├── state/ (سجلات JSON) · exports/ (JSONL)
└── ../.github/workflows/scrapling-zerobaran.yml
```

## 📜 الرخصة والحقوق
MIT © **Baran Avisat** — ZeroBaran Studio. جميع الحقوق محفوظة للمؤلف. للدعم والتعاون التجاري: Baranavisat@gmail.com أو واتساب 00905313263722.
