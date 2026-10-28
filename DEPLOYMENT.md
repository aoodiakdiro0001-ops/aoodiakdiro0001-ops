# 🚀 دليل النشر - Data-Nexus ZeroBaran

## 📋 المتطلبات

- Node.js 18+
- npm أو yarn
- حساب GitHub
- حساب Vercel (اختياري للنشر)

---

## 🔧 التثبيت المحلي

```bash
# استنساخ المشروع
git clone https://github.com/YOUR_USERNAME/data-nexus-zerobaran.git
cd data-nexus-zerobaran

# تثبيت الحزم
npm install

# تشغيل خادم التطوير
npm run dev

# بناء للإنتاج
npm run build
```

---

## 🌐 النشر على Vercel

### الطريقة 1: عبر Vercel Dashboard

1. اذهب إلى [vercel.com](https://vercel.com)
2. سجل دخول بحساب GitHub
3. اضغط "Add New Project"
4. اختر مستودع `data-nexus-zerobaran`
5. اضغط "Deploy"

### الطريقة 2: عبر Vercel CLI

```bash
# تثبيت Vercel CLI
npm i -g vercel

# تسجيل الدخول
vercel login

# النشر
vercel

# النشر للإنتاج
vercel --prod
```

---

## 🤖 النشر على GitHub Pages

1. قم ببناء المشروع:
```bash
npm run build
```

2. انشر مجلد `dist` على فرع `gh-pages`:
```bash
git subtree push --prefix dist origin gh-pages
```

3. فعّل GitHub Pages من إعدادات المستودع

---

## 📦 النشر على Netlify

### الطريقة 1: عبر Netlify Dashboard

1. اذهب إلى [netlify.com](https://netlify.com)
2. اسحب مجلد `dist` وأفلته في Netlify
3. أو اربط مستودع GitHub للنشر التلقائي

### الطريقة 2: عبر Netlify CLI

```bash
# تثبيت Netlify CLI
npm i -g netlify-cli

# تسجيل الدخول
netlify login

# النشر
netlify deploy --prod --dir=dist
```

---

## 🔧 متغيرات البيئة

أنشئ ملف `.env` في الجذر:

```env
# Telegram Bot (اختياري)
VITE_TELEGRAM_BOT_TOKEN=your_bot_token

# Supabase (اختياري)
VITE_SUPABASE_URL=your_supabase_url
VITE_SUPABASE_ANON_KEY=your_anon_key

# Google Gemini API (اختياري)
VITE_GEMINI_API_KEY=your_gemini_api_key
```

---

## 📱 إعداد Telegram Bot

1. تحدث مع [@BotFather](https://t.me/botfather) على Telegram
2. أرسل `/newbot` واتبع التعليمات
3. انسخ التوكن وأضفه في `.env`

---

## 💾 إعداد Supabase

1. اذهب إلى [supabase.com](https://supabase.com)
2. أنشئ مشروع جديد
3. انسخ URL و Anon Key
4. أضفهما في `.env`

---

## 🧠 إعداد Google Gemini API

1. اذهب إلى [Google AI Studio](https://makersuite.google.com/app/apikey)
2. أنشئ مفتاح API
3. أضفه في `.env`

---

## 🎨 التخصيص

### تغيير الألوان

عدّل الألوان في `src/App.tsx`:

```typescript
// الألوان الأساسية
bg-gradient-to-br from-blue-500 via-purple-500 to-green-500
```

### تغيير المعلومات

عدّل معلومات التواصل في `src/App.tsx`:

```typescript
// معلومات التواصل
baranavisat@gmail.com
+90 531 326 3722
baranavi.gumroad.com
```

---

## 📊 التحليلات

### إضافة Google Analytics

أضف في `index.html`:

```html
<!-- Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'G-XXXXXXXXXX');
</script>
```

---

## 🔒 الأمان

### حماية المفاتيح

- لا ترفع `.env` إلى GitHub
- أضف `.env` في `.gitignore`
- استخدم متغيرات البيئة في Vercel/Netlify

### CORS

إذا استخدمت APIs خارجية، تأكد من إعداد CORS بشكل صحيح.

---

## 🐛 حل المشاكل

### مشكلة: البناء يفشل

```bash
# مسح node_modules
rm -rf node_modules package-lock.json
npm install
npm run build
```

### مشكلة: الصور لا تظهر

تأكد من أن المسارات صحيحة في `public/` و `src/assets/`.

### مشكلة: الأنماط لا تعمل

```bash
# إعادة تثبيت Tailwind
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
```

---

## 📞 الدعم

- 📧 Email: baranavisat@gmail.com
- 📱 WhatsApp: +90 531 326 3722
- 🛒 Store: baranavi.gumroad.com

---

<div align="center">

**صُنع بـ ❤️ بواسطة Baran Avisat**

© 2025 Data-Nexus ZeroBaran. جميع الحقوق محفوظة.

</div>
