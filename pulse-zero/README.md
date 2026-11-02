🫀 **Pulse-Zero** — المنظومة الذاتية الذكية لرصد مشاعر العملاء وتحليل السمعة وتتبع الأزمات الرقمية
### المشروع #33 · تكلفة تشغيل صفر · موارد مجانية 100%

<div align="center">

**بدلاً من Brand24 (‏$149+/شهر) · Mention (‏$29+/شهر) · Meltwater (‏$1000+/شهر)**
**يدفع لك هذا النظام $0 شهرياً ويؤدي نفس المهمة: رصد → تحليل AI → تخزين → إنذار فوري**

</div>

---

## 📖 ما هو Pulse-Zero؟

نظام مستقل يعمل على **GitHub Actions** كخادم مجاني لا ينام: يمسح التقييمات والمنشورات التي تذكر علامتك التجارية كل 3 ساعات، يمررها على **عقل ذكاء اصطناعي** (Gemini أو Groq بخططهما المجانية) لتصنيف المشاعر واستخراج جذر المشكلة وتوليد رد احترافي جاهز، يخزنها في **Supabase PostgreSQL** لحساب مؤشر سمعة تاريخي، ثم **ينذرّك على تليجرام في نفس اللحظة** عند أي شكوى حرجة. لوحة **Streamlit** حية تعرض النبض كله.

```
[GitHub Actions Cron — مجاني]
        │
        ▼
┌───────────────────────┐   ┌──────────────────────────┐   ┌─────────────────────┐   ┌──────────────────────┐
│ 1️⃣ Ingestion Layer    │──▶│ 2️⃣ AI Sentiment Core     │──▶│ 3️⃣ Persistence      │──▶│ 4️⃣ Delivery & UI     │
│ RSS · Google News ·   │   │ Gemini / Groq / Mock     │   │ Supabase Postgres  │   │ Telegram Alerts +    │
│ BeautifulSoup scrape  │   │ senti·score·root·reply   │   │ + JSON fallback    │   │ Streamlit Dashboard  │
└───────────────────────┘   └──────────────────────────┘   └─────────────────────┘   └──────────────────────┘
```

## 🧰 البنية داخل المستودع

```
pulse-zero/
├── scripts/
│   ├── pulse_zero.py       ← المنسّق الرئيسي (CLI كامل بالأعلام)
│   ├── ingest.py           ← الطبقة 1: RSS/Atom + Google News + HTML scraping + Demo
│   ├── sentiment.py        ← الطبقة 2: GroqBrain / GeminiBrain / MockBrain (عربي+إنجليزي)
│   ├── storage.py          ← الطبقة 3: SupabaseStore (REST خام) / JsonStore
│   ├── alerts.py           ← الطبقة 4: تنبيهات تليجرام + التقرير الأسبوعي
│   ├── config.yaml         ← كل الإعدادات في مكان واحد
│   └── requirements.txt
├── supabase/schema.sql     ← الطاولة + الفهارس + views للمؤشر اليومي وغرفة الأزمات
├── dashboard.py            ← لوحة Streamlit (KPIs، اتجاهات، غرفة أزمات، بحث وتصدير CSV)
└── README.md
.github/workflows/pulse-zero.yml   ← Cron مجاني: دورة كل 3 ساعات + تقرير أسبوعي الأحد
```

## ⚡ تجربة فورية (بدون أي مفاتيح!)

```bash
cd pulse-zero/scripts
pip install -r requirements.txt
python3 pulse_zero.py --dry-run --no-dedupe
```

يعمل النظام تلقائياً بمحرك **Mock** المعجمي العربي/الإنجليزي وبيانات تجريبية — سترى التنبيهات والتقرير كاملاً في الطرفية. **لا يوجد أي مسار ينهار عند غياب مفتاح**: كل طبقة تسقط لوضع آمن.

## 🔑 التفعيل الكامل (5 مفاتيح مجانية)

أنشئ مشروع GitHub ثم في **Settings → Secrets and variables → Actions** أضف:

| Secret | من أين (مجاني) | إلزامي؟ |
|---|---|---|
| `GROQ_API_KEY` أو `GEMINI_API_KEY` | console.groq.com / aistudio.google.com | لا — دونه يعمل Mock |
| `SUPABASE_URL` + `SUPABASE_SERVICE_KEY` | supabase.com → Project → API Settings | لا — دونه يعمل JSON محلياً |
| `TELEGRAM_BOT_TOKEN` | @BotFather → `/newbot` | لا — بدونه طبع في اللوج |
| `TELEGRAM_CHAT_ID` | أرسل رسالة لبوتك ثم افتح `getUpdates` | لا |

ثم:
1. الصق `supabase/schema.sql` في SQL Editor وشغّله.
2. عدّل `config.yaml`: ضع اسم علامتك وكلمات البحث، وألغِ `demo: true` وأضف روابط تقييماتك الحقيقية (RSS أو صفحات عامة).
3. ارفع الكود إلى فرع `main` — سيبدأ Radar تلقائياً كل 3 ساعات (أو Run workflow يدوياً).

## 🧠 ماذا ينتج المحلل لكل تعليق؟

```json
{
  "sentiment": "negative",
  "score": -0.9,
  "category": "complaint_delivery",
  "issue_root": "عملية دفع مكتملة بدون تسليم المنتج",
  "severity": "crisis",
  "reply_draft": "مرحباً، نشعر بالأسف الشديد تجاه ما مررت به 🙏 سيتواصل فريقنا معك خلال ساعات لحلها بالكامل…"
}
```

مثال تنبيه تليجرام الحقيقي الذي يرسله النظام:

> 🚨 **تنبيه سمعة عاجل — BaranAvi**
> 🔴 **تقييم سلبي** | الخطورة: `CRISIS` | النوع: `complaint_delivery` | الدرجة: `-0.9`
> 💬 النص: «المنتج وصل تالفاً ولم يعمل معي، أريد استرجاع المبلغ فوراً.»
> 🔎 جذر المشكلة: تلف أثناء الشحن + طلب استرجاع
> 💡 الرد المقترح: رسالة اعتذار احترافية مع آلية تعويض فورية — جاهزة للنسخ

## 🛡️ هندسة الاعتمادية (لماذا لا يموت النظام أبداً؟)

- **Dedupe بصماتي مزدوج**: SHA1 لكل ذكر + مقارنة بالمخزن قبل التحليل ⇒ صفر تكرار عبر آلاف التشغيلات (وفّر حصص الـ API).
- **Batching ذكي**: حتى 12 تعليقاً في استدعاء AI واحد، و`retry/backoff` محترم على `429`.
- **Fallback لكل طبقة**: Supabase→JSON · Groq/Gemini→Mock · Telegram→Log · feedparser→محلل XML قياسي.
- **فلتر ضوضاء**: منشورات Reddit العامة التي لا تذكر العلامة تُصنَّف `spam` ولا تصل للتنبيهات أبداً.
- **concurrency group** في Actions يمنع تداخل الدورات؛ `timeout-minutes: 15` يمنع الاستنزاف.
- مصدر واحد يفشل ⇒ يسجَّل الخطأ في ملخص التشغيل ويستمر الباقي.

## 📊 مؤشرات تحصل عليها مجاناً

- **Reputation Index** ‏(0–100) يومي عبر view `reputation_daily` في SQL أو رسم Line في اللوحة.
- **Crisis Feed**: كل تعليق severity ≥ high مع الرد المقترح في مكان واحد.
- **توزيع الفئات**: شكاوى شحن / تقنية / أسئلة / مديح — لتعرف أين تُصلح المنتج فعلاً.
- تصدير CSV بضغطة زر لعرضه للإدارة.

## ⚖️ استخدام مسؤول

المصادر المفعّلة افتراضياً كلها رسمية ومسموحة (RSS عام، Google News RSS). طبقة HTML معطّلة افتراضياً — فعّلها فقط لصفحات تسمح robots.txt بمسحها، والتزم دائماً بشروط استخدام كل منصة. الغرض مراقبة سمعتك أنت، ليس جمع بيانات خاصة.

---

**Pulse-Zero · المشروع #33** — صفر تكلفة، صفر تأخر في الأزمات، سمعة تحت السيطرة الكاملة. 🫀
