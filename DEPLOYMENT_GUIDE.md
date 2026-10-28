# 🚀 دليل النشر الشامل — Studio-ZeroBaran

## 📋 محتويات هذا الدليل:
1. [النشر على GitHub](#1-النشر-على-github)
2. [النشر على Vercel (الموقع المباشر)](#2-النشر-على-vercel)
3. [النشر على Gumroad (المتجر)](#3-النشر-على-gumroad)
4. [إعداد البوت التليجرام](#4-إعداد-بوت-تليجرام)
5. [إعداد GitHub Actions](#5-إعداد-github-actions)

---

## 1. النشر على GitHub

### الخطوة 1: إنشاء Repository جديد على GitHub
1. اذهب إلى https://github.com/new
2. املأ البيانات:
   - **Repository name:** `studio-zerobaran`
   - **Description:** `استوديو الإنتاج المرئي والإعلاني الذاتي واللامركزي`
   - **Public** (عام)
   - ❌ لا تضع علامة على "Add a README" (لدينا واحد جاهز)
3. اضغط **Create repository**

### الخطوة 2: رفع المشروع من جهازك

```bash
# افتح Terminal/CMD في مجلد المشروع

# تهيئة Git
git init

# إضافة كل الملفات
git add .

# Commit أول
git commit -m "🚀 Initial commit: Studio-ZeroBaran"

# ربط بالـ Repository على GitHub (استبدل YOUR_USERNAME باسم حسابك)
git remote add origin https://github.com/YOUR_USERNAME/studio-zerobaran.git

# رفع الملفات
git branch -M main
git push -u origin main
```

### ✅ تم! المشروع الآن على GitHub!

---

## 2. النشر على Vercel (الموقع المباشر)

### الطريقة الأسهل — عبر Vercel Dashboard:
1. اذهب إلى https://vercel.com
2. سجل دخول بحساب GitHub
3. اضغط **Add New → Project**
4. اختر `studio-zerobaran`
5. Vercel سيكتشف أنه Vite project تلقائياً
6. اضغط **Deploy**
7. خلال 30 ثانية سيكون موقعك جاهزاً على رابط مثل: `studio-zerobaran.vercel.app`

### الطريقة البديلة — عبر CLI:
```bash
npm i -g vercel
vercel
# اتبع التعليمات
```

---

## 3. النشر على Gumroad (المتجر)

### إضافة المنتج على Gumroad:
1. اذهب إلى https://baranavi.gumroad.com/
2. سجل دخول
3. اضغط **Products → New Product**
4. املأ البيانات:
   - **Name:** Studio-ZeroBaran — استوديو الإنتاج المرئي الذكي
   - **Price:** حدد السعر (مثلاً: $49 أو مجاني)
   - **Description:** انسخ الوصف من README.md
5. ارفع صور المنتج (يمكن توليدها عبر النظام نفسه!)
6. اضغط **Publish**

### نصائح لوصف المنتج على Gumroad:
```
🚀 Studio-ZeroBaran — منظومة أتمتة الإنتاج المرئي والإعلاني

✅ توليد صور تسويقية احترافية بالذكاء الاصطناعي
✅ نصوص إعلانية ذكية وهاشتاغات
✅ نشر تلقائي مجدول على السوشيال ميديا
✅ مجاني بالكامل — بدون اشتراكات
✅ يعمل 24/7 بدون تدخل بشري

📧 للدعم: baranavisat@gmail.com
📱 واتساب: +90 531 326 3722
```

---

## 4. إعداد بوت تليجرام

### إنشاء البوت:
1. افتح تليجرام وابحث عن: `@BotFather`
2. أرسل `/newbot`
3. اتبع التعليمات واختر اسماً للبوت
4. ستحصل على **Bot Token** — احفظه

### ربط البوت بالنظام:
- ضع التوكن في ملف `.env` (لا ترفعه على GitHub!)
- استخدم `python-telegram-bot` library للتشغيل

---

## 5. إعداد GitHub Actions

### ملف Workflow جاهز (في `.github/workflows/deploy.yml`):

```yaml
name: Deploy to Vercel
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
      - run: npm ci
      - run: npm run build
      - uses: amondnet/vercel-action@v25
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.VERCEL_ORG_ID }}
          vercel-project-id: ${{ secrets.VERCEL_PROJECT_ID }}
          vercel-args: '--prod'
```

### إضافة Secrets في GitHub:
1. اذهب لـ Repository → Settings → Secrets and variables → Actions
2. أضف:
   - `VERCEL_TOKEN`
   - `VERCEL_ORG_ID`
   - `VERCEL_PROJECT_ID`

---

## 🔐 أمان المفاتيح

**⚠️ مهم جداً:**
- ❌ لا ترفع أي مفاتيح API خاصة على GitHub
- ✅ استخدم `.env` محلياً فقط
- ✅ استخدم GitHub Secrets للـ CI/CD
- ✅ أعد توليد أي مفتاح تم تسريبه

---

## 📞 للدعم والمساعدة

- 📧 Email: baranavisat@gmail.com
- 📱 Phone: +90 531 326 3722
- 🛒 Store: https://baranavi.gumroad.com/

---

<div align="center">

**جاهز للانطلاق! 🚀**

© 2025 Studio-ZeroBaran

</div>
