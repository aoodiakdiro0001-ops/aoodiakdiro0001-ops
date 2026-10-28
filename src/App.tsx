import { useState, useEffect } from 'react';
import {
  Zap, Eye, Palette, Send, Bot, Cpu, Layers, Rocket,
  Mail, Phone, Globe, Shield, Clock, Sparkles,
  ArrowRight, CheckCircle, Star, Code, Image, Type,
  Share2, BarChart3, Workflow, Database, Cloud,
  Github, ExternalLink, Menu, X, ChevronDown
} from 'lucide-react';

// ============ HERO SECTION ============
function HeroSection() {
  const [currentWord, setCurrentWord] = useState(0);
  const words = ['إعلانات', 'تصاميم', 'شعارات', 'بوسترات', 'حملات'];

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentWord((prev) => (prev + 1) % words.length);
    }, 2000);
    return () => clearInterval(interval);
  }, []);

  return (
    <section className="relative min-h-screen flex items-center justify-center overflow-hidden">
      {/* Animated Background */}
      <div className="absolute inset-0 bg-gradient-to-br from-gray-950 via-purple-950/30 to-gray-950">
        <div className="absolute inset-0 opacity-20">
          <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-purple-500 rounded-full filter blur-[128px] animate-pulse"></div>
          <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-cyan-500 rounded-full filter blur-[128px] animate-pulse" style={{ animationDelay: '1s' }}></div>
          <div className="absolute top-1/2 left-1/2 w-64 h-64 bg-pink-500 rounded-full filter blur-[100px] animate-pulse" style={{ animationDelay: '2s' }}></div>
        </div>
        {/* Grid Pattern */}
        <div className="absolute inset-0 opacity-10" style={{
          backgroundImage: 'linear-gradient(rgba(139,92,246,0.3) 1px, transparent 1px), linear-gradient(90deg, rgba(139,92,246,0.3) 1px, transparent 1px)',
          backgroundSize: '60px 60px'
        }}></div>
      </div>

      <div className="relative z-10 text-center px-4 max-w-6xl mx-auto">
        {/* Badge */}
        <div className="inline-flex items-center gap-2 bg-purple-500/10 border border-purple-500/30 rounded-full px-4 py-2 mb-8">
          <Sparkles className="w-4 h-4 text-purple-400" />
          <span className="text-purple-300 text-sm font-medium">منظومة أتمتة متكاملة بالذكاء الاصطناعي</span>
        </div>

        {/* Main Title */}
        <h1 className="text-5xl md:text-7xl lg:text-8xl font-black text-white mb-4 tracking-tight">
          Studio-
          <span className="bg-gradient-to-r from-purple-400 via-pink-400 to-cyan-400 bg-clip-text text-transparent">
            ZeroBaran
          </span>
        </h1>

        {/* Subtitle */}
        <p className="text-xl md:text-2xl text-gray-300 mb-6 font-light">
          استوديو الإنتاج المرئي والإعلاني الذاتي واللامركزي
        </p>

        {/* Animated Words */}
        <div className="h-12 flex items-center justify-center mb-8">
          <span className="text-lg md:text-xl text-gray-400">نولّد لك </span>
          <span
            key={currentWord}
            className="text-xl md:text-xl font-bold text-cyan-400 mx-2 animate-fade-in"
          >
            {words[currentWord]}
          </span>
          <span className="text-lg md:text-xl text-gray-400"> احترافية مجاناً</span>
        </div>

        {/* CTA Buttons */}
        <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
          <a
            href="#services"
            className="group bg-gradient-to-r from-purple-600 to-pink-600 text-white px-8 py-4 rounded-xl font-bold text-lg hover:shadow-2xl hover:shadow-purple-500/30 transition-all duration-300 flex items-center gap-2"
          >
            <Rocket className="w-5 h-5" />
            ابدأ الآن
            <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
          </a>
          <a
            href="#how-it-works"
            className="border border-gray-600 text-gray-300 px-8 py-4 rounded-xl font-bold text-lg hover:border-purple-500 hover:text-purple-300 transition-all duration-300"
          >
            كيف يعمل؟
          </a>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mt-16 max-w-3xl mx-auto">
          {[
            { num: '100%', label: 'مجاني بالكامل' },
            { num: '<5s', label: 'زمن التوليد' },
            { num: '∞', label: 'بدون حدود' },
            { num: '24/7', label: 'تشغيل آلي' },
          ].map((stat, i) => (
            <div key={i} className="text-center">
              <div className="text-2xl md:text-3xl font-black text-white">{stat.num}</div>
              <div className="text-sm text-gray-400">{stat.label}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Scroll Indicator */}
      <div className="absolute bottom-8 left-1/2 -translate-x-1/2 animate-bounce">
        <ChevronDown className="w-6 h-6 text-gray-500" />
      </div>
    </section>
  );
}

// ============ SERVICES SECTION ============
function ServicesSection() {
  const services = [
    {
      icon: <Image className="w-8 h-8" />,
      title: 'صور تسويقية احترافية',
      desc: 'Product Mockups بخلفيات إبداعية مولّدة بالذكاء الاصطناعي',
      color: 'from-purple-500 to-pink-500',
    },
    {
      icon: <Palette className="w-8 h-8" />,
      title: 'شعارات وهويات بصرية',
      desc: 'تصميم شعارات فريدة وهويات بصرية كاملة بضغطة واحدة',
      color: 'from-cyan-500 to-blue-500',
    },
    {
      icon: <Share2 className="w-8 h-8" />,
      title: 'منشورات السوشيال ميديا',
      desc: 'Carousels & Banners جاهزة للنشر على جميع المنصات',
      color: 'from-pink-500 to-red-500',
    },
    {
      icon: <Type className="w-8 h-8" />,
      title: 'نصوص إعلانية ذكية',
      desc: 'Copywriting احترافي مع هاشتاغات وعناوين جذابة',
      color: 'from-green-500 to-emerald-500',
    },
    {
      icon: <BarChart3 className="w-8 h-8" />,
      title: 'حملات تسويقية متكاملة',
      desc: 'حملة كاملة (صور + نصوص + جدولة) خلال ثوانٍ معدودة',
      color: 'from-orange-500 to-yellow-500',
    },
    {
      icon: <Send className="w-8 h-8" />,
      title: 'نشر تلقائي مجدول',
      desc: 'نشر المحتوى آلياً في الأوقات المثلى على حساباتك',
      color: 'from-indigo-500 to-purple-500',
    },
  ];

  return (
    <section id="services" className="py-24 px-4 relative">
      <div className="absolute inset-0 bg-gradient-to-b from-gray-950 to-gray-900"></div>
      <div className="relative z-10 max-w-6xl mx-auto">
        {/* Section Header */}
        <div className="text-center mb-16">
          <div className="inline-flex items-center gap-2 bg-cyan-500/10 border border-cyan-500/30 rounded-full px-4 py-2 mb-4">
            <Zap className="w-4 h-4 text-cyan-400" />
            <span className="text-cyan-300 text-sm">الخدمات</span>
          </div>
          <h2 className="text-4xl md:text-5xl font-black text-white mb-4">
            ماذا ننتج <span className="text-purple-400">لك؟</span>
          </h2>
          <p className="text-gray-400 text-lg max-w-2xl mx-auto">
            منظومة متكاملة تأخذ فكرتك وتحوّلها لمحتوى بصري وإعلاني احترافي
          </p>
        </div>

        {/* Services Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {services.map((service, i) => (
            <div
              key={i}
              className="group bg-gray-900/50 border border-gray-800 rounded-2xl p-6 hover:border-purple-500/50 transition-all duration-300 hover:shadow-xl hover:shadow-purple-500/10 hover:-translate-y-1"
            >
              <div className={`w-14 h-14 rounded-xl bg-gradient-to-br ${service.color} flex items-center justify-center text-white mb-4 group-hover:scale-110 transition-transform`}>
                {service.icon}
              </div>
              <h3 className="text-xl font-bold text-white mb-2">{service.title}</h3>
              <p className="text-gray-400">{service.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

// ============ HOW IT WORKS SECTION ============
function HowItWorksSection() {
  const steps = [
    {
      num: '01',
      icon: <Bot className="w-6 h-6" />,
      title: 'إرسال الفكرة',
      desc: 'ترسل فكرة بسيطة أو اسم منتج عبر تليجرام أو واجهة الويب',
      color: 'border-purple-500',
    },
    {
      num: '02',
      icon: <Cpu className="w-6 h-6" />,
      title: 'المعالجة الذكية',
      desc: 'Gemini API يولّد زوايا التسويق والنصوص الإعلانية والوصف البصري',
      color: 'border-cyan-500',
    },
    {
      num: '03',
      icon: <Image className="w-6 h-6" />,
      title: 'توليد الصور',
      desc: 'Hugging Face يولّد الصور والخلفيات الاحترافية بالذكاء الاصطناعي',
      color: 'border-pink-500',
    },
    {
      num: '04',
      icon: <Layers className="w-6 h-6" />,
      title: 'الدمج والتجميع',
      desc: 'Pillow يدمج النصوص على الصور ويخرج التصميم النهائي الاحترافي',
      color: 'border-green-500',
    },
    {
      num: '05',
      icon: <Send className="w-6 h-6" />,
      title: 'التسليم والنشر',
      desc: 'التصميم جاهز على تليجرام مع النصوص، جاهز للنشر فوراً',
      color: 'border-orange-500',
    },
  ];

  return (
    <section id="how-it-works" className="py-24 px-4 relative">
      <div className="absolute inset-0 bg-gradient-to-b from-gray-900 to-gray-950"></div>
      <div className="relative z-10 max-w-6xl mx-auto">
        {/* Section Header */}
        <div className="text-center mb-16">
          <div className="inline-flex items-center gap-2 bg-pink-500/10 border border-pink-500/30 rounded-full px-4 py-2 mb-4">
            <Workflow className="w-4 h-4 text-pink-400" />
            <span className="text-pink-300 text-sm">آلية العمل</span>
          </div>
          <h2 className="text-4xl md:text-5xl font-black text-white mb-4">
            كيف يعمل <span className="text-cyan-400">النظام؟</span>
          </h2>
          <p className="text-gray-400 text-lg max-w-2xl mx-auto">
            5 خطوات فقط من الفكرة إلى التصميم النهائي الاحترافي
          </p>
        </div>

        {/* Steps */}
        <div className="relative">
          {/* Connection Line */}
          <div className="absolute left-1/2 top-0 bottom-0 w-px bg-gradient-to-b from-purple-500 via-cyan-500 to-green-500 hidden lg:block"></div>

          <div className="space-y-8 lg:space-y-12">
            {steps.map((step, i) => (
              <div key={i} className={`flex flex-col lg:flex-row items-center gap-6 ${i % 2 === 1 ? 'lg:flex-row-reverse' : ''}`}>
                <div className={`flex-1 ${i % 2 === 1 ? 'lg:text-left' : 'lg:text-right'}`}>
                  <div className="bg-gray-900/80 border border-gray-800 rounded-2xl p-6 hover:border-purple-500/30 transition-all">
                    <div className="flex items-center gap-3 mb-3">
                      <span className="text-3xl font-black text-gray-700">{step.num}</span>
                      <div className={`w-10 h-10 rounded-lg border-2 ${step.color} flex items-center justify-center text-white`}>
                        {step.icon}
                      </div>
                    </div>
                    <h3 className="text-xl font-bold text-white mb-2">{step.title}</h3>
                    <p className="text-gray-400">{step.desc}</p>
                  </div>
                </div>
                <div className="hidden lg:flex w-4 h-4 rounded-full bg-purple-500 border-4 border-gray-950 z-10"></div>
                <div className="flex-1 hidden lg:block"></div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}

// ============ TECH STACK SECTION ============
function TechStackSection() {
  const techs = [
    {
      icon: <Github className="w-6 h-6" />,
      name: 'GitHub Actions',
      role: 'محرك التشغيل والأتمتة',
      desc: 'مجدع التشغيل الآلي للمهام المجدولة',
      color: 'bg-gray-700',
    },
    {
      icon: <Cpu className="w-6 h-6" />,
      name: 'Google Gemini API',
      role: 'محرك النصوص التسويقية',
      desc: 'صياغة النصوص الإعلانية والعناوين الجذابة',
      color: 'bg-blue-600',
    },
    {
      icon: <Image className="w-6 h-6" />,
      name: 'Hugging Face',
      role: 'محرك توليد الصور',
      desc: 'Flux / Stable Diffusion لتوليد صور احترافية',
      color: 'bg-yellow-600',
    },
    {
      icon: <Palette className="w-6 h-6" />,
      name: 'Python + Pillow',
      role: 'محرك دمج التصاميم',
      desc: 'تركيب الصور والنصوص والشعارات',
      color: 'bg-green-600',
    },
    {
      icon: <Database className="w-6 h-6" />,
      name: 'Supabase',
      role: 'قاعدة البيانات والتخزين',
      desc: 'تخزين التصاميم وإدارة البيانات',
      color: 'bg-emerald-600',
    },
    {
      icon: <Send className="w-6 h-6" />,
      name: 'Telegram Bot',
      role: 'واجهة التحكم والنشر',
      desc: 'استقبال الطلبات وتسليم التصاميم',
      color: 'bg-sky-600',
    },
    {
      icon: <Cloud className="w-6 h-6" />,
      name: 'Vercel + Next.js',
      role: 'الاستضافة والواجهة',
      desc: 'نشر التطبيق بواجهة مستخدم عصرية',
      color: 'bg-gray-800',
    },
    {
      icon: <Code className="w-6 h-6" />,
      name: 'Groq API',
      role: 'بديل معالجة النصوص',
      desc: 'سرعة فائقة في توليد المحتوى النصي',
      color: 'bg-orange-600',
    },
  ];

  return (
    <section id="tech" className="py-24 px-4 relative">
      <div className="absolute inset-0 bg-gradient-to-b from-gray-950 to-gray-900"></div>
      <div className="relative z-10 max-w-6xl mx-auto">
        {/* Section Header */}
        <div className="text-center mb-16">
          <div className="inline-flex items-center gap-2 bg-green-500/10 border border-green-500/30 rounded-full px-4 py-2 mb-4">
            <Code className="w-4 h-4 text-green-400" />
            <span className="text-green-300 text-sm">التقنيات</span>
          </div>
          <h2 className="text-4xl md:text-5xl font-black text-white mb-4">
            الموارد <span className="text-green-400">المجانية</span> المستخدمة
          </h2>
          <p className="text-gray-400 text-lg max-w-2xl mx-auto">
            The Free Tech Stack — كل الأدوات المستخدمة مجانية بالكامل
          </p>
        </div>

        {/* Tech Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {techs.map((tech, i) => (
            <div
              key={i}
              className="bg-gray-900/60 border border-gray-800 rounded-xl p-5 hover:border-green-500/30 transition-all group hover:-translate-y-1"
            >
              <div className={`w-12 h-12 ${tech.color} rounded-lg flex items-center justify-center text-white mb-3 group-hover:scale-110 transition-transform`}>
                {tech.icon}
              </div>
              <h4 className="font-bold text-white text-sm mb-1">{tech.name}</h4>
              <p className="text-purple-400 text-xs font-medium mb-1">{tech.role}</p>
              <p className="text-gray-500 text-xs">{tech.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

// ============ ARCHITECTURE SECTION ============
function ArchitectureSection() {
  return (
    <section className="py-24 px-4 relative">
      <div className="absolute inset-0 bg-gradient-to-b from-gray-900 to-gray-950"></div>
      <div className="relative z-10 max-w-5xl mx-auto">
        <div className="text-center mb-16">
          <div className="inline-flex items-center gap-2 bg-orange-500/10 border border-orange-500/30 rounded-full px-4 py-2 mb-4">
            <Layers className="w-4 h-4 text-orange-400" />
            <span className="text-orange-300 text-sm">البنية المعمارية</span>
          </div>
          <h2 className="text-4xl md:text-5xl font-black text-white mb-4">
            البنية <span className="text-orange-400">الهندسية</span>
          </h2>
          <p className="text-gray-400 text-lg">4 طبقات ذكية تتناغم لإنتاج المحتوى الفني</p>
        </div>

        {/* Architecture Diagram */}
        <div className="bg-gray-900/80 border border-gray-800 rounded-2xl p-8 overflow-x-auto">
          <div className="min-w-[600px] space-y-4">
            {/* Layer 1 */}
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 rounded-xl bg-purple-600 flex items-center justify-center text-white font-bold shrink-0">1</div>
              <div className="flex-1 bg-purple-500/10 border border-purple-500/30 rounded-xl p-4">
                <h4 className="font-bold text-purple-300">طبقة استقبال الطلب (Input Layer)</h4>
                <p className="text-gray-400 text-sm mt-1">بوت تليجرام + واجهة ويب — تستقبل أفكارك وطلباتك</p>
              </div>
            </div>
            <div className="flex justify-center"><div className="w-px h-6 bg-gray-700"></div></div>

            {/* Layer 2 */}
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 rounded-xl bg-cyan-600 flex items-center justify-center text-white font-bold shrink-0">2</div>
              <div className="flex-1 bg-cyan-500/10 border border-cyan-500/30 rounded-xl p-4">
                <h4 className="font-bold text-cyan-300">العقل التسويقي (Copywriting Core)</h4>
                <p className="text-gray-400 text-sm mt-1">Gemini API — صياغة النصوص + وصف بصري دقيق للصور</p>
              </div>
            </div>
            <div className="flex justify-center"><div className="w-px h-6 bg-gray-700"></div></div>

            {/* Layer 3 */}
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 rounded-xl bg-pink-600 flex items-center justify-center text-white font-bold shrink-0">3</div>
              <div className="flex-1 bg-pink-500/10 border border-pink-500/30 rounded-xl p-4">
                <h4 className="font-bold text-pink-300">محرك التوليد والدمج (Visual Rendering Core)</h4>
                <p className="text-gray-400 text-sm mt-1">Hugging Face + Pillow — توليد الصور ودمج النصوص عليها</p>
              </div>
            </div>
            <div className="flex justify-center"><div className="w-px h-6 bg-gray-700"></div></div>

            {/* Layer 4 */}
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 rounded-xl bg-green-600 flex items-center justify-center text-white font-bold shrink-0">4</div>
              <div className="flex-1 bg-green-500/10 border border-green-500/30 rounded-xl p-4">
                <h4 className="font-bold text-green-300">طبقة التسليم والعرض (Delivery & Storage)</h4>
                <p className="text-gray-400 text-sm mt-1">Supabase + Telegram — تخزين التصاميم وإرسالها جاهزة</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

// ============ WHY SECTION ============
function WhySection() {
  const reasons = [
    {
      icon: <Shield className="w-8 h-8" />,
      title: 'توفير مالي هائل',
      desc: 'لا حاجة لاشتراكات شهرية باهظة أو توظيف مصممين — كل شيء مجاني',
    },
    {
      icon: <Clock className="w-8 h-8" />,
      title: 'السرعة المطلقة',
      desc: 'حملة تسويقية كاملة خلال ثوانٍ — صور، نصوص، وجدولة تلقائية',
    },
    {
      icon: <Star className="w-8 h-8" />,
      title: 'السيادة الإبداعية',
      desc: 'تصاميمك ملكك — بلا حقوق ملكية معقدة أو حدود استهلاك',
    },
    {
      icon: <Rocket className="w-8 h-8" />,
      title: 'إنتاج بالجملة',
      desc: 'بضغطة زر واحدة تنتج عشرات التصاميم المتنوعة لمنتجاتك',
    },
  ];

  return (
    <section className="py-24 px-4 relative">
      <div className="absolute inset-0 bg-gradient-to-b from-gray-950 via-purple-950/10 to-gray-950"></div>
      <div className="relative z-10 max-w-6xl mx-auto">
        <div className="text-center mb-16">
          <div className="inline-flex items-center gap-2 bg-yellow-500/10 border border-yellow-500/30 rounded-full px-4 py-2 mb-4">
            <Star className="w-4 h-4 text-yellow-400" />
            <span className="text-yellow-300 text-sm">لماذا نحن؟</span>
          </div>
          <h2 className="text-4xl md:text-5xl font-black text-white mb-4">
            لماذا <span className="text-yellow-400">Studio-ZeroBaran</span>؟
          </h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {reasons.map((reason, i) => (
            <div key={i} className="flex gap-4 bg-gray-900/50 border border-gray-800 rounded-2xl p-6 hover:border-yellow-500/30 transition-all">
              <div className="w-14 h-14 rounded-xl bg-yellow-500/10 flex items-center justify-center text-yellow-400 shrink-0">
                {reason.icon}
              </div>
              <div>
                <h3 className="text-xl font-bold text-white mb-2">{reason.title}</h3>
                <p className="text-gray-400">{reason.desc}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

// ============ CONTACT SECTION ============
function ContactSection() {
  return (
    <section id="contact" className="py-24 px-4 relative">
      <div className="absolute inset-0 bg-gradient-to-b from-gray-950 to-gray-900"></div>
      <div className="relative z-10 max-w-4xl mx-auto">
        <div className="text-center mb-16">
          <div className="inline-flex items-center gap-2 bg-purple-500/10 border border-purple-500/30 rounded-full px-4 py-2 mb-4">
            <Mail className="w-4 h-4 text-purple-400" />
            <span className="text-purple-300 text-sm">تواصل معنا</span>
          </div>
          <h2 className="text-4xl md:text-5xl font-black text-white mb-4">
            جاهز <span className="text-purple-400">للانطلاق؟</span>
          </h2>
          <p className="text-gray-400 text-lg">تواصل معنا الآن وابدأ رحلة الإنتاج المرئي المجاني</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Email */}
          <a
            href="mailto:baranavisat@gmail.com"
            className="bg-gray-900/80 border border-gray-800 rounded-2xl p-6 text-center hover:border-purple-500/50 transition-all group"
          >
            <div className="w-14 h-14 rounded-xl bg-purple-500/10 flex items-center justify-center text-purple-400 mx-auto mb-4 group-hover:scale-110 transition-transform">
              <Mail className="w-7 h-7" />
            </div>
            <h4 className="font-bold text-white mb-1">البريد الإلكتروني</h4>
            <p className="text-gray-400 text-sm break-all">baranavisat@gmail.com</p>
          </a>

          {/* Phone */}
          <a
            href="tel:+905313263722"
            className="bg-gray-900/80 border border-gray-800 rounded-2xl p-6 text-center hover:border-cyan-500/50 transition-all group"
          >
            <div className="w-14 h-14 rounded-xl bg-cyan-500/10 flex items-center justify-center text-cyan-400 mx-auto mb-4 group-hover:scale-110 transition-transform">
              <Phone className="w-7 h-7" />
            </div>
            <h4 className="font-bold text-white mb-1">الهاتف</h4>
            <p className="text-gray-400 text-sm" dir="ltr">+90 531 326 3722</p>
          </a>

          {/* Gumroad Store */}
          <a
            href="https://baranavi.gumroad.com/"
            target="_blank"
            rel="noopener noreferrer"
            className="bg-gray-900/80 border border-gray-800 rounded-2xl p-6 text-center hover:border-pink-500/50 transition-all group"
          >
            <div className="w-14 h-14 rounded-xl bg-pink-500/10 flex items-center justify-center text-pink-400 mx-auto mb-4 group-hover:scale-110 transition-transform">
              <Globe className="w-7 h-7" />
            </div>
            <h4 className="font-bold text-white mb-1">المتجر</h4>
            <p className="text-gray-400 text-sm">baranavi.gumroad.com</p>
          </a>
        </div>

        {/* Payment Methods */}
        <div className="mt-12 bg-gray-900/80 border border-gray-800 rounded-2xl p-8">
          <h3 className="text-2xl font-bold text-white text-center mb-6">طرق الدفع المتاحة</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-gray-800/50 rounded-xl p-4 text-center border border-gray-700">
              <div className="text-3xl mb-2">🏦</div>
              <h4 className="font-bold text-white text-sm">تحويل بنكي</h4>
              <p className="text-gray-500 text-xs mt-1">ليرة تركية / دولار</p>
            </div>
            <div className="bg-gray-800/50 rounded-xl p-4 text-center border border-gray-700">
              <div className="text-3xl mb-2">₿</div>
              <h4 className="font-bold text-white text-sm">بيتكوين</h4>
              <p className="text-gray-500 text-xs mt-1">دفع آمن ومباشر</p>
            </div>
            <div className="bg-gray-800/50 rounded-xl p-4 text-center border border-gray-700">
              <div className="text-3xl mb-2">💎</div>
              <h4 className="font-bold text-white text-sm">USDT / Crypto</h4>
              <p className="text-gray-500 text-xs mt-1">عملات رقمية متنوعة</p>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

// ============ NAVBAR ============
function Navbar() {
  const [isOpen, setIsOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const handleScroll = () => setScrolled(window.scrollY > 50);
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const links = [
    { href: '#services', label: 'الخدمات' },
    { href: '#how-it-works', label: 'آلية العمل' },
    { href: '#tech', label: 'التقنيات' },
    { href: '#contact', label: 'تواصل' },
  ];

  return (
    <nav className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${scrolled ? 'bg-gray-950/90 backdrop-blur-xl border-b border-gray-800/50' : ''}`}>
      <div className="max-w-6xl mx-auto px-4 py-4 flex items-center justify-between">
        {/* Logo */}
        <a href="#" className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center">
            <Zap className="w-4 h-4 text-white" />
          </div>
          <span className="font-black text-white text-lg">SZ<span className="text-purple-400">B</span></span>
        </a>

        {/* Desktop Links */}
        <div className="hidden md:flex items-center gap-6">
          {links.map((link) => (
            <a key={link.href} href={link.href} className="text-gray-400 hover:text-white transition-colors text-sm font-medium">
              {link.label}
            </a>
          ))}
          <a
            href="https://baranavi.gumroad.com/"
            target="_blank"
            rel="noopener noreferrer"
            className="bg-purple-600 hover:bg-purple-500 text-white px-4 py-2 rounded-lg text-sm font-bold transition-colors flex items-center gap-1"
          >
            المتجر <ExternalLink className="w-3 h-3" />
          </a>
        </div>

        {/* Mobile Menu Button */}
        <button onClick={() => setIsOpen(!isOpen)} className="md:hidden text-white">
          {isOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
        </button>
      </div>

      {/* Mobile Menu */}
      {isOpen && (
        <div className="md:hidden bg-gray-950/95 backdrop-blur-xl border-b border-gray-800 px-4 py-4 space-y-3">
          {links.map((link) => (
            <a key={link.href} href={link.href} onClick={() => setIsOpen(false)} className="block text-gray-300 hover:text-white py-2">
              {link.label}
            </a>
          ))}
          <a
            href="https://baranavi.gumroad.com/"
            target="_blank"
            rel="noopener noreferrer"
            className="block bg-purple-600 text-white px-4 py-2 rounded-lg text-center font-bold"
          >
            زيارة المتجر
          </a>
        </div>
      )}
    </nav>
  );
}

// ============ FOOTER ============
function Footer() {
  return (
    <footer className="bg-gray-950 border-t border-gray-800 py-12 px-4">
      <div className="max-w-6xl mx-auto">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-8">
          {/* Brand */}
          <div>
            <div className="flex items-center gap-2 mb-4">
              <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center">
                <Zap className="w-4 h-4 text-white" />
              </div>
              <span className="font-black text-white text-lg">Studio-ZeroBaran</span>
            </div>
            <p className="text-gray-500 text-sm">
              استوديو الإنتاج المرئي والإعلاني الذاتي واللامركزي — منظومة أتمتة متكاملة بالذكاء الاصطناعي
            </p>
          </div>

          {/* Links */}
          <div>
            <h4 className="font-bold text-white mb-4">روابط سريعة</h4>
            <ul className="space-y-2">
              <li><a href="#services" className="text-gray-500 hover:text-purple-400 text-sm transition-colors">الخدمات</a></li>
              <li><a href="#how-it-works" className="text-gray-500 hover:text-purple-400 text-sm transition-colors">آلية العمل</a></li>
              <li><a href="#tech" className="text-gray-500 hover:text-purple-400 text-sm transition-colors">التقنيات</a></li>
              <li><a href="#contact" className="text-gray-500 hover:text-purple-400 text-sm transition-colors">تواصل معنا</a></li>
            </ul>
          </div>

          {/* Contact */}
          <div>
            <h4 className="font-bold text-white mb-4">تواصل</h4>
            <ul className="space-y-2">
              <li className="flex items-center gap-2 text-gray-500 text-sm">
                <Mail className="w-4 h-4" /> baranavisat@gmail.com
              </li>
              <li className="flex items-center gap-2 text-gray-500 text-sm" dir="ltr">
                <Phone className="w-4 h-4" /> +90 531 326 3722
              </li>
              <li className="flex items-center gap-2 text-gray-500 text-sm">
                <Globe className="w-4 h-4" /> baranavi.gumroad.com
              </li>
            </ul>
          </div>
        </div>

        {/* Bottom */}
        <div className="border-t border-gray-800 pt-8 flex flex-col md:flex-row items-center justify-between gap-4">
          <p className="text-gray-600 text-sm">
            © 2025 Studio-ZeroBaran. جميع الحقوق محفوظة.
          </p>
          <div className="flex items-center gap-2">
            <span className="text-gray-600 text-xs">صُنع بـ</span>
            <span className="text-red-500">❤</span>
            <span className="text-gray-600 text-xs">وذكاء اصطناعي مجاني</span>
          </div>
        </div>
      </div>
    </footer>
  );
}

// ============ DEMO SECTION ============
function DemoSection() {
  const [inputValue, setInputValue] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [showResult, setShowResult] = useState(false);

  const handleGenerate = () => {
    if (!inputValue.trim()) return;
    setIsGenerating(true);
    setShowResult(false);
    setTimeout(() => {
      setIsGenerating(false);
      setShowResult(true);
    }, 3000);
  };

  return (
    <section className="py-24 px-4 relative">
      <div className="absolute inset-0 bg-gradient-to-b from-gray-900 via-gray-950 to-gray-900"></div>
      <div className="relative z-10 max-w-4xl mx-auto">
        <div className="text-center mb-12">
          <div className="inline-flex items-center gap-2 bg-pink-500/10 border border-pink-500/30 rounded-full px-4 py-2 mb-4">
            <Sparkles className="w-4 h-4 text-pink-400" />
            <span className="text-pink-300 text-sm">تجربة تفاعلية</span>
          </div>
          <h2 className="text-4xl md:text-5xl font-black text-white mb-4">
            جرّب <span className="text-pink-400">الآن</span>
          </h2>
          <p className="text-gray-400 text-lg">أدخل فكرة منتجك وشاهد كيف يعمل النظام</p>
        </div>

        {/* Input Area */}
        <div className="bg-gray-900/80 border border-gray-800 rounded-2xl p-6">
          <div className="flex flex-col sm:flex-row gap-4">
            <input
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              placeholder="مثال: أريد إعلان لمنتج عسل طبيعي بتخفيض 20%"
              className="flex-1 bg-gray-800 border border-gray-700 rounded-xl px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:border-purple-500 transition-colors"
              dir="rtl"
            />
            <button
              onClick={handleGenerate}
              disabled={isGenerating || !inputValue.trim()}
              className="bg-gradient-to-r from-purple-600 to-pink-600 text-white px-6 py-3 rounded-xl font-bold hover:shadow-lg hover:shadow-purple-500/30 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
            >
              {isGenerating ? (
                <>
                  <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                  جاري التوليد...
                </>
              ) : (
                <>
                  <Sparkles className="w-5 h-5" />
                  توليد
                </>
              )}
            </button>
          </div>

          {/* Result */}
          {showResult && (
            <div className="mt-6 space-y-4 animate-fade-in">
              <div className="flex items-center gap-2 text-green-400">
                <CheckCircle className="w-5 h-5" />
                <span className="font-bold">تم التوليد بنجاح!</span>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* Generated Copy */}
                <div className="bg-gray-800/50 rounded-xl p-4 border border-gray-700">
                  <h4 className="text-purple-400 font-bold text-sm mb-2 flex items-center gap-1">
                    <Type className="w-4 h-4" /> النص الإعلاني
                  </h4>
                  <p className="text-gray-300 text-sm" dir="rtl">
                    🍯 عسل طبيعي 100% — خصم 20% لفترة محدودة!
                    <br />
                    من أجود المناحل إلى بيتك مباشرة.
                    <br />
                    #عسل_طبيعي #خصم #صحة #عافية
                  </p>
                </div>

                {/* Generated Image Placeholder */}
                <div className="bg-gray-800/50 rounded-xl p-4 border border-gray-700">
                  <h4 className="text-cyan-400 font-bold text-sm mb-2 flex items-center gap-1">
                    <Image className="w-4 h-4" /> الصورة المولّدة
                  </h4>
                  <div className="aspect-video bg-gradient-to-br from-amber-900/30 to-orange-900/30 rounded-lg flex items-center justify-center border border-amber-700/30">
                    <div className="text-center">
                      <div className="text-4xl mb-2">🍯✨</div>
                      <p className="text-amber-300 text-xs">صورة إعلانية جاهزة</p>
                    </div>
                  </div>
                </div>
              </div>

              <div className="bg-gray-800/50 rounded-xl p-4 border border-gray-700">
                <h4 className="text-green-400 font-bold text-sm mb-2 flex items-center gap-1">
                  <Send className="w-4 h-4" /> جاهز للنشر
                </h4>
                <p className="text-gray-400 text-sm">
                  ✅ تم إرسال التصميم لتليجرام — جاهز للنشر على إنستغرام، تويتر، ولينكد إن
                </p>
              </div>
            </div>
          )}
        </div>
      </div>
    </section>
  );
}

// ============ MAIN APP ============
export default function App() {
  return (
    <div className="min-h-screen bg-gray-950 text-white font-sans" dir="rtl">
      <Navbar />
      <HeroSection />
      <ServicesSection />
      <HowItWorksSection />
      <TechStackSection />
      <ArchitectureSection />
      <WhySection />
      <DemoSection />
      <ContactSection />
      <Footer />
    </div>
  );
}
