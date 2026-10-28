# 🌍 PolyGlot-StreamBaran

<div align="center">

### 🎙️ منظومة الترجمة الذاتية والدبلجة الصوتية اللامركزية

**نظام ذكي متكامل لترجمة، تفريغ، ودبلجة مقاطع الفيديو والصوتيات إلى أي لغة في العالم**

![Languages](https://img.shields.io/badge/Languages-50+-blue?style=for-the-badge)
![Accuracy](https://img.shields.io/badge/Accuracy-99%25-cyan?style=for-the-badge)
![Cost](https://img.shields.io/badge/Cost-FREE-green?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Active-brightgreen?style=for-the-badge)

[🌐 الموقع](#) | [📦 المتجر](https://baranavi.gumroad.com/) | [📧 تواصل](mailto:baranavisat@gmail.com)

</div>

---

## 📖 ما هو PolyGlot-StreamBaran؟

نظام ذكي متكامل يأخذ رابط فيديو أو ملف صوتي، ويقوم آلياً بـ:

- ✅ **تفريغ الصوت** بدقة مذهلة (Whisper)
- ✅ **ترجمة احترافية** بسياق قانوني/تسويقي (Gemini API)
- ✅ **توليد تعليق صوتي** بشري طبيعي (Edge-TTS)
- ✅ **دمج الترجمة** على الفيديو (FFmpeg)
- ✅ **إخراج فيديو نهائي** جاهز للنشر

**كل هذا — بدون دفع دولار واحد لأي منصة مدفوعة!**

---

## 🛠️ التقنيات المستخدمة (Free Tech Stack)

| المكون | التقنية | الدور |
|--------|---------|-------|
| 🔄 الأتمتة | GitHub Actions | خادم مجاني للمعالجة |
| 🎤 التفريغ | Whisper (OpenAI) | تحويل صوت لنص بدقة |
| 🧠 الترجمة | Google Gemini API | ترجمة سياقية احترافية |
| 🔊 الدبلجة | Edge-TTS | أصوات Microsoft العصبية |
| 🎬 الدمج | FFmpeg | تركيب الصوت والترجمة |
| 💾 التخزين | Supabase | إدارة الملفات |
| 📱 التسليم | Telegram Bot | واجهة التحكم |
| 🌐 الواجهة | React + Vite | واجهة المستخدم |

---

## 🏗️ البنية المعمارية

```
[إرسال رابط/ملف] → [FFmpeg: استخراج الصوت]
         ↓
[Whisper: تفريغ النص + توقيت] → [Gemini: ترجمة سياقية]
         ↓
[Edge-TTS: توليد صوت بشري] → [FFmpeg: دمج + تصدير]
         ↓
[Supabase: تخزين] → [Telegram: تسليم الفيديو النهائي]
```

### الطبقات الأربع:
1. **طبقة الالتقاط** — FFmpeg لاستخراج الصوت من الفيديو
2. **طبقة التفريغ والترجمة** — Whisper + Gemini API
3. **طبقة التعليق الصوتي** — Edge-TTS (أصوات Microsoft)
4. **طبقة الدمج والتسليم** — FFmpeg + Supabase + Telegram

---

## 🌐 اللغات المدعومة

50+ لغة تشمل:
- 🇬🇧 English | 🇹🇷 Türkçe | 🇸🇦 العربية | 🇫🇷 Français
- 🇩🇪 Deutsch | 🇪🇸 Español | 🇨🇳 中文 | 🇯🇵 日本語
- 🇰🇷 한국어 | 🇮🇳 हिन्दी | 🇷🇺 Русский | 🇧🇷 Português
- والمزيد...

---

## 🚀 التشغيل المحلي

```bash
# Clone
git clone https://github.com/YOUR_USERNAME/polyglot-streambaran.git
cd polyglot-streambaran

# Install
npm install

# Dev
npm run dev

# Build
npm run build
```

---

## 📞 التواصل والدعم

- 📧 **Email:** baranavisat@gmail.com
- 📱 **Phone/WhatsApp:** +90 531 326 3722
- 🛒 **Store:** [baranavi.gumroad.com](https://baranavi.gumroad.com/)

---

## 💳 طرق الدفع

| الطريقة | التفاصيل |
|---------|----------|
| 🏦 تحويل بنكي | ليرة تركية / دولار أمريكي |
| ₿ بيتكوين | دفع آمن ومباشر |
| 💎 USDT | عملات رقمية متنوعة |

---

## 📦 مشاريع أخرى من Studio-ZeroBaran

- **Studio-ZeroBaran** — استوديو الإنتاج المرئي والإعلاني
- **CryptoVault Pro** — محفظة رقمية متعددة السلاسل
- **AI Copywriter** — مولّد نصوص تسويقية ذكي
- **DesignForge** — مصمم جرافيك آلي
- **SocialPilot** — مدير سوشيال ميديا آلي
- **CodeMentor AI** — مساعد برمجة ذكي

---

<div align="center">

**صُنع بـ ❤️ وذكاء اصطناعي مجاني**

© 2025 PolyGlot-StreamBaran — Baran Avisat. جميع الحقوق محفوظة.

</div>
