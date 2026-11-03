# 🛡️ Audit-Skill-ZeroBaran — المنظومة الذاتية لفحص أمان الوكلاء وتدقيق الشفرات

> **بديل مجاني صريح لمنصات التدقيق الأمنية المدفوعة (Cloudflare-style audits + Ghidra workflows + SaaS code-scanners).**
> مشروع رقم **#35** في سلسلة **ZeroBaran** — تكلفة تشغيل: **0$ شهرياً، إلى الأبد**.

نظام ذكي متكامل ومستقل يفحص الأكواد البرمجية ومهارات/أدوات وكلاء الذكاء الاصطناعي، يكتشف الثغرات الخفية (حقن، تسريب مفاتيح، فك تسلسل قاتل، ثغرات Prompt Injection الخاصة بالوكلاء)، يحللها بلغة عربية واضحة مع **كود آمن جاهز للإصلاح**، ويؤرشف كل تقرير ويقفز إنذاراً عاجلاً على هاتفك قبل أي نشر — دون دولار واحد لأي منصة فحص مدفوعة.

```
[رفع أو دفع كود جديد إلى المستودع]
                │
                ▼
[GitHub Actions + Semgrep/Bandit + محرك ASZ الأصلي (40+ قاعدة)]   ← الطبقة 1: الفحص الساكن
                │
                ▼
[Groq / Gemini API — شرح عربي + سيناريو استغلال + الكود الآمن المصحح] ← الطبقة 2: العقل الذكي
                │
                ▼
[تخزين التقرير في Supabase ──► إنذار أمني عاجل + ملخص أسبوعي على تليجرام] ← الطبقتان 3 و4
```

## ✨ لماذا تتمنى كل شركة الحصول عليه؟
- 💸 **توفير فلكي:** أدوات التدقيق الأمني الآلي اشتراكاتها باهظة؛ هنا نفس الغرض ببنية مجانية بالكامل.
- 🧬 **فئة نادرة حقيقية:** قليل من يدقق **وكلاء LLM تحديداً** (Prompt injection في system prompts، أدوات مدمّرة بلا تأكيد بشري، تفويضات مفرطة في skill manifests) — النظام يغطي OWASP LLM Top 10 إضافة إلى OWASP Top 10 التقليدي.
- 🔒 **سيادة مطلقة:** الكود لا يغادر بيئتك إلا مختفياً — جميع الأسرار تُستّر (`redact`) قبل أي إرسال للنموذج، وهناك محرك محلي حتمي يعمل بلا إنترنت أصلاً.
- 🚦 **بوابة نشر فعلية:** أكواد خروج تعني CI يتوقف عند ثغرة CRITICAL (exit 3) ولا يُنشر الكود المعطوب.

## 🛠️ التقنيات المجانية البحتة
| المكون | التقنية المجانية |
|---|---|
| الجدولة وبوابة CI | GitHub Actions (runs مجانية) |
| محركات الفحص | Semgrep OSS + Bandit (اختياريان، يُكتشفان تلقائياً) + **محرك Python أصلي بـ 40+ قاعدة** يعمل دائماً |
| عقل التدقيق | Groq API / Gemini API (Free Tiers) + MockBrain محلي للحتمية والـ CI |
| الأرشيف | Supabase Postgres Free Tier + fallback JSON محلي |
| التنبيه والتحكم | Telegram Bot + Streamlit Dashboard |

## 📁 هيكل المشروع
```
scripts/scanners.py     ← الطبقة 1: محركات الفحص المتدرجة (native/semgrep/bandit)
scripts/audit_brain.py  ← الطبقة 2: عقل التدقيق الذكي (Groq→Gemini→Mock) + إخفاء الأسرار
scripts/store.py        ← الطبقة 3: أرشيف Supabase/محلي + اتجاهات الوضع الأمني
scripts/notify.py       ← الطبقة 4: الإنذارات العاجلة والتقارير الأسبوعية لتليجرام
scripts/audit.py        ← المنسّق CLI: scan / demo / stats / fix / weekly
dashboard.py            ← مركز القيادة Streamlit (5 تبويبات، عربي RTL-friendly)
supabase/schema.sql     ← جدولان + 3 عروض SQL جاهزة + RLS
rules/semgrep/          ← قواعد Semgrep مخصصة للوكاء
examples/vulnerable_repo← مستودع مُثقب مقصود للاختبار (31 ثغرة مكتشفة)
examples/clean_skill    ← مهارة نظيفة مُحصّنة (100/100 APPROVED)
tests/smoke_test.py     ← 33 عقداً تعاقدياً بين الطبقات (يعمل offline)
.github/workflows/…yml  ← بوابة CI + مسح مجدول كل 6 ساعات + ملخص أسبوعي
```

## 🚀 التشغيل خلال دقيقتين
```bash
pip install -r requirements.txt          # النواة تعمل بدون أي اعتماديات أيضاً!
python scripts/audit.py demo             # تدقيق كامل على المستودع المُثقب التجريبي
python scripts/audit.py scan ./your-repo --fail-on critical   # بوابة نشر حقيقية
streamlit run dashboard.py               # مركز القيادة
```
**الإعدادات الاختيارية (env):** `GROQ_API_KEY` · `GEMINI_API_KEY` · `SUPABASE_URL` + `SUPABASE_SERVICE_KEY` · `TELEGRAM_BOT_TOKEN` + `TELEGRAM_CHAT_ID`. بدونها يعمل النظام كاملاً بالمحرك المحلي والتخزين المحلي وتقارير dry-run.

## 🧪 إثباتات حية من بيئة التطوير
- `examples/vulnerable_repo`: **BLOCKED — 0/100**، 31 رصداً (10 CRITICAL / 14 HIGH): AWS key، مفتاح Stripe في `.env`، SQLi بـ f-string، `pickle.loads`، `verify=False`، SSTI، حاوية `--privileged`/root، pyjwt CVE-2022-29217، وأربع ثغرات وكيل (system prompt ملوث، أداة حذف بلا تأكيد، auto_approve=True، webhook مفتوح).
- `examples/clean_skill`: **APPROVED — 100/100** بصفر إنذارات كاذبة.
- اختبار العقود: **🏆 ALL LAYER CONTRACTS OK (33/33)** دون أي مفتاح أو اتصال.
- عينة الإنذار الفعلي بالصيغة المطلوبة: «🛡️ تنبيه أمني عاجل… 💻 السبب… 🛠️ الإصلاح المقترح» + توقيع الملكية.

## ⚖️ الحوكمة والأخلاقيات
افحص فقط أكواداً تملكها أو لديك إذن صريح بفحصها. النظام دفاعي بحت: لا يستغل، لا يخترق، لا يرسل أسراراً خاماً للمزودات. عثرات الأنماط تُعرض بثقة confidence قابلة للفلترة، وثغرة الوكيل الحرجة تُراجَع بشرياً عبر طابور dashboard.

## 👤 المؤلف وحقوق الملكية
**Baran Avisat** — ZeroBaran Studio
📧 Baranavisat@gmail.com · 📱 واتساب: **00905313263722**
الترخيص: MIT © 2026 Baran Avisat — استخدام تجاري حر مع حفظ الاسم.
موقع الأعمال: baranavi.gumroad.com

*جزء من أسطول ZeroBaran — مشاريع ذاتية التسيير بتكلفة صفر.* 🚀
