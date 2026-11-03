# 📈 LLM-Router-ZeroBaran — Project #37
**المنظومة الذاتية المتقدمة للتوجيه الذكي، إدارة النماذج، والتحليل المالي الآلي**
*LLM-Router & Trading Agents — بديل Kronos/OpenRouter-Plus المجاني الصريح 100%*

> 👤 **المؤلف:** Baran Avisat · 📧 Baranavisat@gmail.com · 📱 واتساب: **00905313263722**
> 🛡️ ZeroBaran Studio · MIT License · لا يدفع دولاراً واحداً لأي منصة تحليل مالي أو توجيه ذكي مدفوعة.

## ما هو؟
نظام مستقل يراقب الأسواق، يحسب المؤشرات الفنية (RSI/MACD/Bollinger/ATR/OBV بمحرك Pandas)، يوجّه كل طلب تحليل لأرخص نموذج مجاني قادر (Ollama محلي ← Groq Free ← Gemini Free)، يخزّل التوصيات وسجل أدائها في Supabase، ويرسل تقارير فورية لتليجرام ولوحة Streamlit — بتكلفة صفر وسيادة كاملة على بياناتك.

## لماذا تتمناه كل شركة ومتداول؟
- 💰 **توفير فلكي:** فاتورة OpenRouter/LiteLLM-Cloud ومنصات التحليل المدفوعة → $0 عبر التوجيه للطبقات المجانية. الراوتر يسجّل لكل نداء «التكلفة الموفَّرة» مقابل السعر المدفوع المكافئ.
- ⚡ **Zero-Latency Routing:** مصنّف مهام (kind + complexity + tokens) يرسل المهام الصغيرة لنموذج خفيف سريع، والتحليلات الثقيلة لنموذج كبير — مع failover تلقائي وhealth score ذاتي Tuning لكل نموذج.
- 🔒 **سيادة مطلقة:** استراتيجياتك تبقى في بيئتك؛ يمكنك تشغيل كل شيء على Ollama المحلي دون إرسال أي بايت للخارج.

## 🛠️ Stack مجاني بحت
| المكون | التقنية المجانية |
|---|---|
| Cron/الخادم | GitHub Actions (`.github/workflows/llm-router-zerobaran.yml` — كل 6 ساعات + ملخص أسبوعي) |
| محرك المعالجة | Python + FastAPI-compatible modules + Pandas/NumPy TA |
| عقل التوجيه والتحليل | Ollama (Kronos-class open models) / Groq / Google Gemini Free Tiers |
| قاعدة البيانات | Supabase PostgreSQL Free (`supabase/schema.sql`) + fallback JSON محلي |
| التنبيه والواجهة | Telegram Bot API + Streamlit Dashboard |

## 📐 البنية (4 طبقات)
```
[طلب تحليل / قائمة مراقبة (config.yaml أو dispatch)]
        ▼
[market_data.py — Yahoo/Stooq/Binance شموع مجانية + كاش]
        ▼
[indicators.py — RSI·MACD·BB·ATR·OBV → trend_score ±100 + confidence + خطة دخول/وقف/هدف]
        ▼
[router.py — تصنيف المهمة → أرخص نموذج قادر (Ollama→Groq→Gemini→Mock) + failover + إحصاءات]
        ▼
[store.py — Supabase lrz_analysis_log/lrz_signal_events + تسوية outcomes]
        ▼
[notify.py — 📈 تقرير التحليل المالي والتداول بنسبة الثقة وخطة الدخول → تليجرام]
```

## 🚀 التشغيل السريع
```bash
pip install -r scripts/requirements.txt
python scripts/llm_router.py run          # دورة كاملة على قائمة المراقبة
python scripts/llm_router.py ask "لخص مخاطر BTC"   # سؤال موجَّه مباشرة
python scripts/llm_router.py weekly       # الملخص الأسبوعي
streamlit run dashboard.py                # لوحة التحكم
python tests/smoke_test.py                # 28 عقداً — يعمل بلا مفاتيح: 🏆
```
**مفاتيح اختيارية (Secrets):** `GROQ_API_KEY` · `GEMINI_API_KEY` · `SUPABASE_URL/SUPABASE_SERVICE_KEY` · `TELEGRAM_BOT_TOKEN/CHAT_ID`. بدونها يعمل النظام كاملاً بالبيانات الحية + Mock brain محلياً.

## 🧪 إثباتات حية من بيئة التطوير (2026-11-03)
- AAPL: 65 شمعة حقيقية من Yahoo (إغلاق 338.32) — BTCUSDT: 200 شمعة من Binance (77,170$).
- دورة كاملة: 3 رموز حُللت، إشارة ETHUSDT SELL/AVOID سجلت وتُساوى تلقائياً عند إغلاقها.
- تسوية إشارة تجريبية: tp1_hit بنسبة PnL +3.79% — win-rate يُحتسب في الملخص الأسبوعي.
- اختبارات العقود: **🏆 ALL LAYER CONTRACTS OK (28/28)** offline بالكامل.

## ⚖️ إخلاء مسؤولية إلزامي
النظام **أداة دعم قرار آلية وليست نصيحة مالية**. التداول ينطوي على مخاطر خسارة رأس المال. لا يتم تنفيذ أي أمر شراء/بيع فعلي — النظام يولّد خططاً ويوثّق أداءها فقط.

© 2026 Baran Avisat — ZeroBaran Studio. جميع الحقوق محفوظة. الدعم: Baranavisat@gmail.com · واتساب 00905313263722
