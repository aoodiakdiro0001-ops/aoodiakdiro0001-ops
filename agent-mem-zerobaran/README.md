# 🧠 Agent-Mem-ZeroBaran — الذاكرة الاستراتيجية المستقلة وعصارة السياق للوكلاء الذكيين

> **المشروع #34 في أسطول ZeroBaran للابتكار البرمجي** · مصمم بالكامل بموارد مجانية 100% — بلا دولار واحد لمنصات ذاكرة أو سياق مدفوعة.

| | |
|---|---|
| ✍️ **المؤلف** | **Baran Avisat** |
| 📧 **البريد** | Baranavisat@gmail.com |
| 📱 **واتساب** | 00905313263722 |
| 🛡️ **الملكية** | © 2026 Baran Avisat — ZeroBaran Studio. كل الحقوق محفوظة |

## ما هو Agent-Mem-ZeroBaran؟
نظام ذكي متكامل ومستقل لإدارة الذاكرة طويلة المدى، سياق المحادثات الضخم، واسترجاع المعلومات الدلالي للوكلاء والمساعدين الذكيين (بديل مجاني لـ Claude-Mem / Letta / Zep / LangMem). يخزّن، ينظّم، ويسترجع البيانات السياقية بدقة — في بيئة **خاصة وسيادية تماماً**: ذكريات وكلائك لا تغادر مشروعك.

## لماذا تتمنى كل شركة ومطوّر الحصول عليه؟
- 💰 **توفير فلكي:** اشتراكات منصات ذاكرة الوكلاء (mem0, Zep…) تكلف مئات الدولارات شهرياً — هنا: صفر، للأبد.
- ♾️ **سياق بلا حدود:** أرشفة + استرجاع انتقائي يحقن فقط البطاقات ذات الصلة ضمن «ميزانية سياق» مضبوطة — النوافذ المحدودة للنماذج لم تعد قيداً.
- 🔒 **سيادة مطلقة:** التخزين في Supabase خاصتك أو SQLite محلياً؛ لا طرف ثالث يقرأ شيئاً.
- 🧹 **ذاكرة تتنفس وحدها:** cron في GitHub Actions ينظّف ويضغط ويرسل ملخصاً أسبوعياً على تليجرام.
- ⚡ **من أجزاء الثانية للتوكن حتى الحقن:** بحث متجه هجين (دقة × حداثة) مع تتبع أي بطاقة «ساخنة» وأيها باردة.

## 🛠️ التقنيات المجانية البحتة
| المكوّن | التقنية المجانية | الدور |
|---|---|---|
| محرك المتابعة المجدولة | GitHub Actions | تنظيف الذاكرة، ضغط السياق، الملخص الأسبوعي |
| التقطيع والتنظيم | Python stdlib (خوارزمية مطابقة لـ LangChain RecursiveSplitter) | تقسيم السياق المترابط دون تثبيت أي مكتبة |
| التضمين | Gemini text-embedding-004 (مجاني) → متجه Hash-Ngram محلي حتمي | متجهات دلالية 512B تعمل أوفلاين دائماً |
| التخزين المتجه | Supabase PostgreSQL + pgvector (Free Tier) / SQLite محلي | تخزين واسترجاع طويل المدى بفهرس HNSW |
| العقل الدلالي | Groq llama-3.3-70b ثم Gemini Flash (طبقتان مجانيتان) → MockBrain | بطاقات ذاكرة وملخصات وإجابات مدعومة بالمصادر |
| البوابة والتوصيل | Telegram Bot + HTTP Gateway (stdlib) | أوامر الوكيل وتقارير الحالة على هاتفك |

## 📐 البنية — 4 طبقات
```
[سياق جديد من الوكيل/المستخدم] ──► L1 تقطيع دلالي متداخل (chunking.py)
        ──► L2 تضمين + تخزين متجه (embeddings.py → vector_store.py / supabase/schema.sql)
        ──► L3 استرجاع هجين + خلاصة وحقن ضمن ميزانية السياق (memory_brain.py)
        ──► L4 توصيل: Telegram + API Gateway (notify.py / gateway.py / dashboard.py)
```

## 🚀 التشغيل الفوري (بلا مفاتيح، بلا تثبيتات)
```bash
python3 scripts/mem_engine.py demo          # أرشفة → استرجاع عربي حي → تقرير صحة
python3 tests/smoke_test.py                 # 🏆 ALL LAYER CONTRACTS OK (42/42)
python3 scripts/gateway.py                  # بوابة HTTP لكل وكيل: /remember /recall /stats
streamlit run dashboard.py                  # مركز القيادة العربي
```
**CLI للوكلاء:**
```bash
python3 scripts/mem_engine.py remember --doc-id sprint-42 --file notes.md
python3 scripts/mem_engine.py recall "ما قرار الميزانية ولماذا أُجل تويتر؟" --notify
python3 scripts/mem_engine.py chat --transcript examples/session_transcript.json
```
**HTTP لأي وكيل (LangChain/LlamaIndex/custom):**
```bash
curl -X POST localhost:8788/remember -H 'Content-Type: application/json' \
  -d '{"doc_id":"sprint-42","text":"قررنا..."}'
curl -X POST localhost:8788/recall   -H 'Content-Type: application/json' \
  -d '{"question":"ما قرار الميزانية؟","top_k":5}'   # يعيد context_block جاهزاً للحقن
```

## ☁️ النشر الاحترافي المجاني (اختياري — كل شيء يعمل بدونه)
1. **Supabase:** أنشئ مشروعاً مجانياً ← SQL Editor ← الصق `supabase/schema.sql` ← فعّل pgvector.
2. **GitHub Actions:** انسخ الملف إلى `.github/workflows/` ← Secrets: `GROQ_API_KEY`, `GEMINI_API_KEY`, `SUPABASE_URL`, `SUPABASE_SERVICE_KEY`, `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`.
3. سيقوم النظام آلياً كل 6 ساعات بمرور النظافة، وكل أسبوع بملخص حالة الذاكرة على تليجرام. بدون مفاتيح يعمل المحرك محلياً بذكاء MockBrain الحتمي — لا تفشل CI أبداً.

## 🧪 إثبات العمل الحي (أُجري وقت البناء)
- Demo: حفظ محضر اجتماع عربي → **بطاقتا ذاكرة دلالية** → سؤال بالعربية أعاد القرار الصحيح بثقة 80% وزمن ~1ms وحقن 139 توكن فقط بدل النص الكامل.
- اختبارات العقود: **42/42** تغطي الطبقات الأربع + التغليف + الملكية.

## 📦 محتويات المشروع
```
agent-mem-zerobaran/
├── scripts/{chunking,embeddings,vector_store,memory_brain,mem_engine,notify,gateway}.py
├── supabase/schema.sql            ├── dashboard.py (Streamlit)
├── .github/workflows/agent-mem-zerobaran.yml   ├── tests/smoke_test.py
├── examples/session_transcript.json            ├── README/LICENSE/AUTHORS/SUPPORT…
```

## ⚖️ الترخيص وحقوق الملكية
MIT الاستخدام التجاري والشخصي مع الإبقاء على إشعار الملكية. **اسم وشعار Agent-Mem-ZeroBaran™ مملوكان لـ Baran Avisat.** للنسخ المعدّلة التجارية أو الدعم الخاص: تواصل قبل النشر.

💬 **الدعم على مدار الساعة للمالك:** واتساب **00905313263722** · 📧 Baranavisat@gmail.com — Baran Avisat، مصمم أسطول ZeroBaran (35+ مشروعاً مجانياً بالكامل).
