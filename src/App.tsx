import { useState, useEffect } from 'react';
import {
  Zap, Globe, Mic, Video, Languages, Subtitles, Volume2, Play,
  Mail, Phone, ShoppingBag, Shield, Clock, Sparkles,
  ArrowRight, CheckCircle, Star, Code, FileAudio, FileVideo,
  Share2, Workflow, Database, Cloud, Github, ExternalLink,
  Menu, X, ChevronDown, Hexagon, Brain, Cpu, Wand2,
  Music, Radio, Headphones, MessageSquare, Send, Bot,
  ArrowUpRight, Download, Upload, RefreshCw, Layers,
  Lock, Palette, Megaphone
} from 'lucide-react';

// ============ ANIMATED BACKGROUND ============
function AnimatedBackground() {
  return (
    <div className="fixed inset-0 -z-10 overflow-hidden">
      <div className="absolute inset-0 bg-[#030712]"></div>
      <div className="absolute top-0 right-1/4 w-[600px] h-[600px] bg-blue-600/10 rounded-full filter blur-[180px] animate-pulse"></div>
      <div className="absolute bottom-0 left-1/4 w-[600px] h-[600px] bg-emerald-600/10 rounded-full filter blur-[180px] animate-pulse" style={{ animationDelay: '2s' }}></div>
      <div className="absolute top-1/2 left-1/2 w-[400px] h-[400px] bg-cyan-600/5 rounded-full filter blur-[150px] animate-pulse" style={{ animationDelay: '4s' }}></div>
      <div className="absolute inset-0 opacity-[0.02]" style={{
        backgroundImage: 'linear-gradient(rgba(255,255,255,0.1) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.1) 1px, transparent 1px)',
        backgroundSize: '80px 80px'
      }}></div>
    </div>
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
    { href: '#features', label: 'المميزات' },
    { href: '#how-it-works', label: 'آلية العمل' },
    { href: '#tech', label: 'التقنيات' },
    { href: '#languages', label: 'اللغات' },
    { href: '#projects', label: 'مشاريع أخرى' },
    { href: '#contact', label: 'تواصل' },
  ];

  return (
    <nav className={`fixed top-0 left-0 right-0 z-50 transition-all duration-500 ${scrolled ? 'bg-[#030712]/80 backdrop-blur-2xl border-b border-white/5 shadow-2xl shadow-blue-500/5' : ''}`}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 py-4 flex items-center justify-between">
        <a href="#" className="flex items-center gap-3 group">
          <div className="relative">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-500 via-cyan-500 to-emerald-500 flex items-center justify-center group-hover:scale-110 transition-transform duration-300">
              <Languages className="w-5 h-5 text-white" />
            </div>
            <div className="absolute inset-0 rounded-xl bg-gradient-to-br from-blue-500 via-cyan-500 to-emerald-500 blur-lg opacity-50 group-hover:opacity-80 transition-opacity"></div>
          </div>
          <div>
            <span className="font-black text-white text-sm sm:text-base block leading-none">PolyGlot</span>
            <span className="text-[10px] text-cyan-400 font-medium tracking-widest">STREAMBARAN</span>
          </div>
        </a>

        <div className="hidden lg:flex items-center gap-1">
          {links.map((link) => (
            <a key={link.href} href={link.href} className="text-gray-400 hover:text-white transition-colors text-sm font-medium px-3 py-2 rounded-lg hover:bg-white/5">
              {link.label}
            </a>
          ))}
          <a href="https://baranavi.gumroad.com/" target="_blank" rel="noopener noreferrer" className="mr-2 bg-gradient-to-r from-blue-600 to-cyan-600 text-white px-5 py-2.5 rounded-xl text-sm font-bold hover:shadow-lg hover:shadow-blue-500/30 transition-all flex items-center gap-2">
            <ShoppingBag className="w-4 h-4" />
            المتجر
          </a>
        </div>

        <button onClick={() => setIsOpen(!isOpen)} className="lg:hidden text-white p-2">
          {isOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
        </button>
      </div>

      {isOpen && (
        <div className="lg:hidden bg-[#030712]/95 backdrop-blur-2xl border-b border-white/5 px-4 py-4 space-y-1">
          {links.map((link) => (
            <a key={link.href} href={link.href} onClick={() => setIsOpen(false)} className="block text-gray-300 hover:text-white py-3 px-4 rounded-lg hover:bg-white/5">
              {link.label}
            </a>
          ))}
          <a href="https://baranavi.gumroad.com/" target="_blank" rel="noopener noreferrer" className="block bg-gradient-to-r from-blue-600 to-cyan-600 text-white px-4 py-3 rounded-xl text-center font-bold mt-2">
            زيارة المتجر
          </a>
        </div>
      )}
    </nav>
  );
}

// ============ HERO SECTION ============
function HeroSection() {
  const [currentLang, setCurrentLang] = useState(0);
  const languages = ['English', 'Türkçe', 'العربية', 'Français', 'Deutsch', 'Español', '中文', '日本語', '한국어', 'हिन्दी'];

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentLang((prev) => (prev + 1) % languages.length);
    }, 1500);
    return () => clearInterval(interval);
  }, []);

  return (
    <section className="relative min-h-screen flex items-center justify-center overflow-hidden pt-20">
      <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 py-20">
        <div className="text-center">
          {/* Badge */}
          <div className="inline-flex items-center gap-2 bg-blue-500/10 border border-blue-500/20 rounded-full px-5 py-2.5 mb-8 backdrop-blur-sm">
            <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
            <span className="text-gray-300 text-sm font-medium">منظومة الترجمة والدبلجة الذاتية اللامركزية</span>
          </div>

          {/* Main Title */}
          <h1 className="text-4xl sm:text-5xl md:text-6xl lg:text-7xl font-black text-white mb-6 tracking-tight leading-[1.1]">
            ترجم، فرّغ، ودبلج
            <br />
            <span className="bg-gradient-to-r from-blue-400 via-cyan-400 to-emerald-400 bg-clip-text text-transparent">
              أي فيديو بالعالم
            </span>
          </h1>

          {/* Animated Languages */}
          <div className="h-16 flex items-center justify-center mb-8">
            <div className="bg-white/5 border border-white/10 rounded-2xl px-8 py-3 backdrop-blur-sm">
              <span className="text-2xl md:text-3xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-cyan-400 transition-all">
                {languages[currentLang]}
              </span>
            </div>
          </div>

          <p className="text-lg md:text-xl text-gray-400 mb-10 max-w-3xl mx-auto leading-relaxed">
            نظام ذكي متكامل يأخذ رابط فيديو أو ملف صوتي، ويفرّغه بدقة، ويترجمه باحترافية، ويولّد تعليقاً صوتياً بشرياً طبيعياً — <span className="text-cyan-400 font-semibold">بدون دفع دولار واحد</span>
          </p>

          {/* CTA */}
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center mb-16">
            <a href="#features" className="group relative bg-gradient-to-r from-blue-600 to-cyan-600 text-white px-8 py-4 rounded-2xl font-bold text-lg hover:shadow-2xl hover:shadow-blue-500/30 transition-all duration-300 flex items-center gap-3">
              <Play className="w-5 h-5" />
              جرّب الآن
              <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
              <div className="absolute inset-0 rounded-2xl bg-gradient-to-r from-blue-600 to-cyan-600 blur-xl opacity-50 group-hover:opacity-80 transition-opacity -z-10"></div>
            </a>
            <a href="https://baranavi.gumroad.com/" target="_blank" rel="noopener noreferrer" className="border border-white/10 text-gray-300 px-8 py-4 rounded-2xl font-bold text-lg hover:border-blue-500/50 hover:text-white transition-all duration-300 flex items-center gap-2 backdrop-blur-sm">
              <ShoppingBag className="w-5 h-5" />
              احصل عليه
            </a>
          </div>

          {/* Stats */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 max-w-3xl mx-auto">
            {[
              { num: '50+', label: 'لغة مدعومة', color: 'text-blue-400' },
              { num: '99%', label: 'دقة التفريغ', color: 'text-cyan-400' },
              { num: '0$', label: 'تكلفة التشغيل', color: 'text-emerald-400' },
              { num: '24/7', label: 'تشغيل آلي', color: 'text-purple-400' },
            ].map((stat, i) => (
              <div key={i} className="bg-white/5 border border-white/10 rounded-2xl p-4 backdrop-blur-sm">
                <div className={`text-2xl md:text-3xl font-black ${stat.color}`}>{stat.num}</div>
                <div className="text-xs md:text-sm text-gray-500 mt-1">{stat.label}</div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}

// ============ FEATURES SECTION ============
function FeaturesSection() {
  const features = [
    {
      icon: <FileAudio className="w-7 h-7" />,
      title: 'تفريغ صوتي دقيق',
      desc: 'استخراج النص من أي فيديو أو ملف صوتي بدقة مذهلة مع توقيت كل كلمة',
      gradient: 'from-blue-500 to-cyan-500',
      glow: 'bg-blue-500/20',
    },
    {
      icon: <Languages className="w-7 h-7" />,
      title: 'ترجمة احترافية سياقية',
      desc: 'ترجمة ذكية تفهم السياق والمصطلحات القانونية والتسويقية — ليست ترجمة حرفية',
      gradient: 'from-cyan-500 to-emerald-500',
      glow: 'bg-cyan-500/20',
    },
    {
      icon: <Mic className="w-7 h-7" />,
      title: 'دبلجة صوتية واقعية',
      desc: 'توليد تعليق صوتي بشري طبيعي بأصوات Microsoft العصبية — ذكر/أنثى، سرعات مختلفة',
      gradient: 'from-emerald-500 to-green-500',
      glow: 'bg-emerald-500/20',
    },
    {
      icon: <Subtitles className="w-7 h-7" />,
      title: 'ترجمة مرئية (Subtitles)',
      desc: 'إضافة ترجمة مدمجة على الفيديو بتصميم احترافي متزامن مع الصوت',
      gradient: 'from-purple-500 to-pink-500',
      glow: 'bg-purple-500/20',
    },
    {
      icon: <Video className="w-7 h-7" />,
      title: 'إنتاج فيديو نهائي',
      desc: 'دمج الصوت والترجمة وإخراج فيديو جاهز للنشر على يوتيوب وتيك توك',
      gradient: 'from-pink-500 to-red-500',
      glow: 'bg-pink-500/20',
    },
    {
      icon: <Globe className="w-7 h-7" />,
      title: 'عولمة المحتوى',
      desc: 'حوّل أي فيديو من العربية للإنجليزية أو التركية أو أي لغة — افتح أسواقاً عالمية',
      gradient: 'from-orange-500 to-yellow-500',
      glow: 'bg-orange-500/20',
    },
  ];

  return (
    <section id="features" className="py-24 px-4 relative">
      <div className="max-w-7xl mx-auto">
        <div className="text-center mb-16">
          <div className="inline-flex items-center gap-2 bg-blue-500/10 border border-blue-500/20 rounded-full px-5 py-2 mb-6">
            <Sparkles className="w-4 h-4 text-blue-400" />
            <span className="text-blue-300 text-sm font-medium">المميزات</span>
          </div>
          <h2 className="text-4xl md:text-6xl font-black text-white mb-4">
            ماذا يفعل <span className="bg-gradient-to-r from-blue-400 to-cyan-400 bg-clip-text text-transparent">النظام؟</span>
          </h2>
          <p className="text-gray-400 text-lg max-w-2xl mx-auto">
            6 قدرات أساسية تعمل بتناغم لإنتاج محتوى مترجم ومدبلج احترافي
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {features.map((feature, i) => (
            <div key={i} className="group relative bg-white/[0.03] border border-white/10 rounded-3xl p-6 hover:border-white/20 transition-all duration-500 hover:-translate-y-2 overflow-hidden">
              <div className={`absolute -top-20 -right-20 w-40 h-40 ${feature.glow} rounded-full filter blur-[80px] opacity-0 group-hover:opacity-100 transition-opacity duration-500`}></div>
              <div className={`w-14 h-14 rounded-2xl bg-gradient-to-br ${feature.gradient} flex items-center justify-center text-white mb-5 group-hover:scale-110 group-hover:rotate-3 transition-all duration-500 shadow-lg`}>
                {feature.icon}
              </div>
              <h3 className="text-xl font-bold text-white mb-2">{feature.title}</h3>
              <p className="text-gray-400 text-sm leading-relaxed">{feature.desc}</p>
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
      icon: <Upload className="w-6 h-6" />,
      title: 'إرسال الفيديو/الصوت',
      desc: 'أرسل رابط فيديو أو ارفع ملف صوتي عبر تليجرام أو واجهة الويب',
      color: 'from-blue-500 to-cyan-500',
      borderColor: 'border-blue-500',
    },
    {
      num: '02',
      icon: <FileAudio className="w-6 h-6" />,
      title: 'استخراج الصوت والتفريغ',
      desc: 'FFmpeg يفصل الصوت + Whisper يفرّغه لنص مع توقيت كل كلمة بدقة',
      color: 'from-cyan-500 to-teal-500',
      borderColor: 'border-cyan-500',
    },
    {
      num: '03',
      icon: <Brain className="w-6 h-6" />,
      title: 'الترجمة الذكية',
      desc: 'Gemini API يترجم النص باحترافية سياقية — يفهم المصطلحات والسياق',
      color: 'from-teal-500 to-emerald-500',
      borderColor: 'border-teal-500',
    },
    {
      num: '04',
      icon: <Mic className="w-6 h-6" />,
      title: 'توليد التعليق الصوتي',
      desc: 'Edge-TTS يولّد صوت بشري طبيعي واقعي باللغة المطلوبة — ذكر/أنثى',
      color: 'from-emerald-500 to-green-500',
      borderColor: 'border-emerald-500',
    },
    {
      num: '05',
      icon: <Video className="w-6 h-6" />,
      title: 'الدمج والتسليم',
      desc: 'FFmpeg يدمج الصوت والترجمة على الفيديو ويخرجه جاهزاً عبر تليجرام',
      color: 'from-green-500 to-blue-500',
      borderColor: 'border-green-500',
    },
  ];

  return (
    <section id="how-it-works" className="py-24 px-4 relative">
      <div className="max-w-6xl mx-auto">
        <div className="text-center mb-16">
          <div className="inline-flex items-center gap-2 bg-cyan-500/10 border border-cyan-500/20 rounded-full px-5 py-2 mb-6">
            <Workflow className="w-4 h-4 text-cyan-400" />
            <span className="text-cyan-300 text-sm font-medium">آلية العمل</span>
          </div>
          <h2 className="text-4xl md:text-6xl font-black text-white mb-4">
            5 خطوات فقط <span className="bg-gradient-to-r from-cyan-400 to-emerald-400 bg-clip-text text-transparent">للفيديو النهائي</span>
          </h2>
          <p className="text-gray-400 text-lg max-w-2xl mx-auto">
            من الرابط إلى الفيديو المدبلج الجاهز للنشر — كل شيء آلي
          </p>
        </div>

        <div className="relative">
          <div className="absolute left-8 lg:left-1/2 top-0 bottom-0 w-px bg-gradient-to-b from-blue-500 via-cyan-500 to-emerald-500 hidden md:block"></div>

          <div className="space-y-8">
            {steps.map((step, i) => (
              <div key={i} className={`flex flex-col md:flex-row items-start md:items-center gap-6 ${i % 2 === 1 ? 'md:flex-row-reverse' : ''}`}>
                <div className={`flex-1 ${i % 2 === 1 ? 'md:text-left' : 'md:text-right'}`}>
                  <div className="bg-white/[0.03] border border-white/10 rounded-2xl p-6 hover:border-white/20 transition-all">
                    <div className="flex items-center gap-3 mb-3">
                      <span className="text-3xl font-black text-gray-700">{step.num}</span>
                      <div className={`w-10 h-10 rounded-lg bg-gradient-to-br ${step.color} flex items-center justify-center text-white`}>
                        {step.icon}
                      </div>
                    </div>
                    <h3 className="text-xl font-bold text-white mb-2">{step.title}</h3>
                    <p className="text-gray-400 text-sm">{step.desc}</p>
                  </div>
                </div>
                <div className="hidden md:flex w-4 h-4 rounded-full bg-cyan-500 border-4 border-[#030712] z-10 shrink-0 mx-8"></div>
                <div className="flex-1 hidden md:block"></div>
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
      desc: 'الخادم المجاني الذي ينفذ كل مراحل المعالجة آلياً',
      color: 'from-gray-600 to-gray-700',
    },
    {
      icon: <FileAudio className="w-6 h-6" />,
      name: 'Whisper (OpenAI)',
      role: 'محرك التفريغ الصوتي',
      desc: 'تفريغ النصوص بدقة مذهلة من أي ملف صوتي أو فيديو',
      color: 'from-blue-600 to-blue-700',
    },
    {
      icon: <Brain className="w-6 h-6" />,
      name: 'Google Gemini API',
      role: 'محرك الترجمة الذكية',
      desc: 'ترجمة سياقية احترافية تفهم المصطلحات والسياق',
      color: 'from-cyan-600 to-teal-600',
    },
    {
      icon: <Mic className="w-6 h-6" />,
      name: 'Edge-TTS',
      role: 'محرك توليد الصوت',
      desc: 'أصوات Microsoft العصبية الطبيعية — مجاناً بدون حدود',
      color: 'from-emerald-600 to-green-600',
    },
    {
      icon: <Video className="w-6 h-6" />,
      name: 'FFmpeg',
      role: 'محرك الدمج والتصدير',
      desc: 'تركيب الصوت والترجمة على الفيديو وإخراج المنتج النهائي',
      color: 'from-orange-600 to-red-600',
    },
    {
      icon: <Database className="w-6 h-6" />,
      name: 'Supabase',
      role: 'التخزين وإدارة البيانات',
      desc: 'تخزين الملفات والنتائج بشكل آمن ومنظم',
      color: 'from-green-600 to-emerald-600',
    },
    {
      icon: <Send className="w-6 h-6" />,
      name: 'Telegram Bot',
      role: 'واجهة التحكم والتسليم',
      desc: 'استقبال الطلبات وتسليم الفيديوهات النهائية',
      color: 'from-sky-600 to-blue-600',
    },
    {
      icon: <Cloud className="w-6 h-6" />,
      name: 'Vercel + Next.js',
      role: 'الاستضافة والواجهة',
      desc: 'واجهة مستخدم عصرية ونشر سريع',
      color: 'from-gray-700 to-gray-800',
    },
  ];

  return (
    <section id="tech" className="py-24 px-4 relative">
      <div className="max-w-7xl mx-auto">
        <div className="text-center mb-16">
          <div className="inline-flex items-center gap-2 bg-emerald-500/10 border border-emerald-500/20 rounded-full px-5 py-2 mb-6">
            <Code className="w-4 h-4 text-emerald-400" />
            <span className="text-emerald-300 text-sm font-medium">التقنيات المجانية</span>
          </div>
          <h2 className="text-4xl md:text-6xl font-black text-white mb-4">
            <span className="bg-gradient-to-r from-emerald-400 to-cyan-400 bg-clip-text text-transparent">The Free Tech Stack</span>
          </h2>
          <p className="text-gray-400 text-lg max-w-2xl mx-auto">
            8+ تقنيات وأدوات مجانية بالكامل — صفر دولار تكلفة تشغيل
          </p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {techs.map((tech, i) => (
            <div key={i} className="group bg-white/[0.03] border border-white/10 rounded-2xl p-5 hover:border-white/20 transition-all duration-300 hover:-translate-y-1">
              <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${tech.color} flex items-center justify-center text-white mb-4 group-hover:scale-110 transition-transform`}>
                {tech.icon}
              </div>
              <h4 className="font-bold text-white text-sm mb-1">{tech.name}</h4>
              <p className="text-xs text-cyan-400 font-medium mb-2">{tech.role}</p>
              <p className="text-xs text-gray-500 leading-relaxed">{tech.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

// ============ LANGUAGES SECTION ============
function LanguagesSection() {
  const languages = [
    { name: 'English', flag: '🇬🇧', code: 'en' },
    { name: 'Türkçe', flag: '🇹🇷', code: 'tr' },
    { name: 'العربية', flag: '🇸🇦', code: 'ar' },
    { name: 'Français', flag: '🇫🇷', code: 'fr' },
    { name: 'Deutsch', flag: '🇩🇪', code: 'de' },
    { name: 'Español', flag: '🇪🇸', code: 'es' },
    { name: '中文', flag: '🇨🇳', code: 'zh' },
    { name: '日本語', flag: '🇯🇵', code: 'ja' },
    { name: '한국어', flag: '🇰🇷', code: 'ko' },
    { name: 'हिन्दी', flag: '🇮🇳', code: 'hi' },
    { name: 'Русский', flag: '🇷🇺', code: 'ru' },
    { name: 'Português', flag: '🇧🇷', code: 'pt' },
    { name: 'Italiano', flag: '🇮🇹', code: 'it' },
    { name: 'Nederlands', flag: '🇳🇱', code: 'nl' },
    { name: 'Polski', flag: '🇵🇱', code: 'pl' },
    { name: 'Svenska', flag: '🇸🇪', code: 'sv' },
  ];

  return (
    <section id="languages" className="py-24 px-4 relative">
      <div className="max-w-7xl mx-auto">
        <div className="text-center mb-16">
          <div className="inline-flex items-center gap-2 bg-purple-500/10 border border-purple-500/20 rounded-full px-5 py-2 mb-6">
            <Globe className="w-4 h-4 text-purple-400" />
            <span className="text-purple-300 text-sm font-medium">اللغات المدعومة</span>
          </div>
          <h2 className="text-4xl md:text-6xl font-black text-white mb-4">
            <span className="bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">50+ لغة</span> مدعومة
          </h2>
          <p className="text-gray-400 text-lg max-w-2xl mx-auto">
            ترجم أي محتوى لأي لغة في العالم — افتح أسواقاً جديدة
          </p>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-8 gap-3">
          {languages.map((lang, i) => (
            <div key={i} className="group bg-white/[0.03] border border-white/10 rounded-xl p-3 text-center hover:border-purple-500/30 transition-all hover:-translate-y-0.5">
              <div className="text-2xl mb-1">{lang.flag}</div>
              <p className="text-xs font-bold text-white">{lang.name}</p>
              <p className="text-[10px] text-gray-500 font-mono">{lang.code}</p>
            </div>
          ))}
        </div>

        <div className="text-center mt-8">
          <p className="text-gray-500 text-sm">+ المزيد من اللغات يتم إضافتها باستمرار</p>
        </div>
      </div>
    </section>
  );
}

// ============ DEMO SECTION ============
function DemoSection() {
  const [url, setUrl] = useState('');
  const [targetLang, setTargetLang] = useState('en');
  const [isProcessing, setIsProcessing] = useState(false);
  const [stage, setStage] = useState(0);
  const [showResult, setShowResult] = useState(false);

  const stages = [
    'جاري تحميل الفيديو...',
    'استخراج الصوت...',
    'تفريغ النص بـ Whisper...',
    'ترجمة بـ Gemini...',
    'توليد الصوت بـ Edge-TTS...',
    'دمج الترجمة والصوت...',
    'جاهز! ✅',
  ];

  const handleProcess = () => {
    if (!url.trim()) return;
    setIsProcessing(true);
    setShowResult(false);
    setStage(0);

    let currentStage = 0;
    const timer = setInterval(() => {
      currentStage++;
      setStage(currentStage);
      if (currentStage >= stages.length - 1) {
        clearInterval(timer);
        setTimeout(() => {
          setIsProcessing(false);
          setShowResult(true);
        }, 500);
      }
    }, 800);
  };

  return (
    <section className="py-24 px-4 relative">
      <div className="max-w-4xl mx-auto">
        <div className="text-center mb-12">
          <div className="inline-flex items-center gap-2 bg-pink-500/10 border border-pink-500/20 rounded-full px-5 py-2 mb-6">
            <Play className="w-4 h-4 text-pink-400" />
            <span className="text-pink-300 text-sm font-medium">تجربة تفاعلية</span>
          </div>
          <h2 className="text-4xl md:text-5xl font-black text-white mb-4">
            جرّب <span className="bg-gradient-to-r from-pink-400 to-purple-400 bg-clip-text text-transparent">الآن</span>
          </h2>
          <p className="text-gray-400 text-lg">أدخل رابط فيديو وشاهد كيف يعمل النظام</p>
        </div>

        <div className="bg-white/[0.03] border border-white/10 rounded-3xl p-6 md:p-8">
          {/* Input */}
          <div className="space-y-4">
            <div>
              <label className="text-sm text-gray-400 mb-2 block">رابط الفيديو</label>
              <input
                type="text"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                placeholder="https://youtube.com/watch?v=..."
                className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white placeholder-gray-600 focus:outline-none focus:border-blue-500 transition-colors"
                dir="ltr"
              />
            </div>

            <div>
              <label className="text-sm text-gray-400 mb-2 block">اللغة المستهدفة</label>
              <select
                value={targetLang}
                onChange={(e) => setTargetLang(e.target.value)}
                className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white focus:outline-none focus:border-blue-500 transition-colors"
              >
                <option value="en" className="bg-gray-900">🇬🇧 English</option>
                <option value="tr" className="bg-gray-900">🇹🇷 Türkçe</option>
                <option value="ar" className="bg-gray-900">🇸🇦 العربية</option>
                <option value="fr" className="bg-gray-900">🇫🇷 Français</option>
                <option value="de" className="bg-gray-900">🇩🇪 Deutsch</option>
                <option value="es" className="bg-gray-900">🇪🇸 Español</option>
              </select>
            </div>

            <button
              onClick={handleProcess}
              disabled={isProcessing || !url.trim()}
              className="w-full bg-gradient-to-r from-blue-600 to-cyan-600 text-white px-6 py-4 rounded-xl font-bold hover:shadow-lg hover:shadow-blue-500/30 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              {isProcessing ? (
                <>
                  <RefreshCw className="w-5 h-5 animate-spin" />
                  جاري المعالجة...
                </>
              ) : (
                <>
                  <Wand2 className="w-5 h-5" />
                  ابدأ الترجمة والدبلجة
                </>
              )}
            </button>
          </div>

          {/* Progress */}
          {isProcessing && (
            <div className="mt-6 space-y-2">
              {stages.map((s, i) => (
                <div key={i} className={`flex items-center gap-3 p-2 rounded-lg transition-all ${i <= stage ? 'opacity-100' : 'opacity-30'}`}>
                  {i < stage ? (
                    <CheckCircle className="w-5 h-5 text-green-400 shrink-0" />
                  ) : i === stage ? (
                    <div className="w-5 h-5 border-2 border-blue-400 border-t-transparent rounded-full animate-spin shrink-0"></div>
                  ) : (
                    <div className="w-5 h-5 rounded-full border border-gray-700 shrink-0"></div>
                  )}
                  <span className={`text-sm ${i <= stage ? 'text-white' : 'text-gray-600'}`}>{s}</span>
                </div>
              ))}
            </div>
          )}

          {/* Result */}
          {showResult && (
            <div className="mt-6 space-y-4 animate-fade-in">
              <div className="flex items-center gap-2 text-green-400">
                <CheckCircle className="w-5 h-5" />
                <span className="font-bold">تم بنجاح!</span>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="bg-white/5 rounded-xl p-4 border border-white/10">
                  <h4 className="text-blue-400 font-bold text-sm mb-2 flex items-center gap-1">
                    <FileAudio className="w-4 h-4" /> النص المفرّغ
                  </h4>
                  <p className="text-gray-400 text-xs" dir="ltr">
                    [00:00.00 → 00:03.50] Welcome to our tutorial...
                    <br />[00:03.50 → 00:07.20] Today we will learn about...
                    <br />[00:07.20 → 00:11.00] Let's get started...
                  </p>
                </div>

                <div className="bg-white/5 rounded-xl p-4 border border-white/10">
                  <h4 className="text-cyan-400 font-bold text-sm mb-2 flex items-center gap-1">
                    <Languages className="w-4 h-4" /> الترجمة
                  </h4>
                  <p className="text-gray-400 text-xs" dir="rtl">
                    [00:00 → 00:03] مرحباً بكم في درسنا...
                    <br />[00:03 → 00:07] سنتعلم اليوم عن...
                    <br />[00:07 → 00:11] هيا نبدأ...
                  </p>
                </div>
              </div>

              <div className="bg-white/5 rounded-xl p-4 border border-white/10">
                <h4 className="text-emerald-400 font-bold text-sm mb-2 flex items-center gap-1">
                  <Video className="w-4 h-4" /> الفيديو النهائي
                </h4>
                <div className="aspect-video bg-gradient-to-br from-blue-900/20 to-cyan-900/20 rounded-lg flex items-center justify-center border border-blue-700/20">
                  <div className="text-center">
                    <Play className="w-12 h-12 text-white/50 mx-auto mb-2" />
                    <p className="text-blue-300 text-sm">فيديو مدبلج جاهز</p>
                    <p className="text-gray-500 text-xs mt-1">مع ترجمة مدمجة + تعليق صوتي</p>
                  </div>
                </div>
              </div>

              <div className="flex gap-3">
                <button className="flex-1 bg-gradient-to-r from-blue-600 to-cyan-600 text-white px-4 py-3 rounded-xl text-sm font-bold flex items-center justify-center gap-2">
                  <Download className="w-4 h-4" />
                  تحميل الفيديو
                </button>
                <button className="flex-1 bg-white/5 border border-white/10 text-white px-4 py-3 rounded-xl text-sm font-bold flex items-center justify-center gap-2 hover:bg-white/10 transition-colors">
                  <Send className="w-4 h-4" />
                  إرسال لتليجرام
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </section>
  );
}

// ============ WHY SECTION ============
function WhySection() {
  const reasons = [
    {
      icon: <Shield className="w-7 h-7" />,
      title: 'توفير مالي ضخم',
      desc: 'خدمات الدبلجة المهنية تكلف مئات الدولارات — هنا بالمجان تماماً',
      color: 'text-blue-400',
      bg: 'bg-blue-500/10',
    },
    {
      icon: <Globe className="w-7 h-7" />,
      title: 'عولمة المحتوى',
      desc: 'حوّل أي فيديو لأي لغة وافتح أسواقاً عالمية لمنتجك أو قناتك',
      color: 'text-cyan-400',
      bg: 'bg-cyan-500/10',
    },
    {
      icon: <Lock className="w-7 h-7" />,
      title: 'السيادة والخصوصية',
      desc: 'معالجة عبر مكتبات مفتوحة المصدر — لا تسريب لبياناتك التجارية',
      color: 'text-emerald-400',
      bg: 'bg-emerald-500/10',
    },
    {
      icon: <Clock className="w-7 h-7" />,
      title: 'سرعة فائقة',
      desc: 'من الرابط إلى الفيديو المدبلج في دقائق معدودة — بدون انتظار',
      color: 'text-purple-400',
      bg: 'bg-purple-500/10',
    },
  ];

  return (
    <section className="py-24 px-4 relative">
      <div className="max-w-6xl mx-auto">
        <div className="text-center mb-16">
          <div className="inline-flex items-center gap-2 bg-yellow-500/10 border border-yellow-500/20 rounded-full px-5 py-2 mb-6">
            <Star className="w-4 h-4 text-yellow-400" />
            <span className="text-yellow-300 text-sm font-medium">لماذا نحن؟</span>
          </div>
          <h2 className="text-4xl md:text-6xl font-black text-white mb-4">
            لماذا <span className="bg-gradient-to-r from-yellow-400 to-orange-400 bg-clip-text text-transparent">PolyGlot؟</span>
          </h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {reasons.map((reason, i) => (
            <div key={i} className="flex gap-4 bg-white/[0.03] border border-white/10 rounded-2xl p-6 hover:border-white/20 transition-all">
              <div className={`w-14 h-14 rounded-xl ${reason.bg} flex items-center justify-center ${reason.color} shrink-0`}>
                {reason.icon}
              </div>
              <div>
                <h3 className="text-xl font-bold text-white mb-2">{reason.title}</h3>
                <p className="text-gray-400 text-sm">{reason.desc}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

// ============ OTHER PROJECTS SECTION ============
function OtherProjectsSection() {
  const projects = [
    { name: 'Studio-ZeroBaran', desc: 'استوديو الإنتاج المرئي والإعلاني', icon: <Palette className="w-5 h-5" />, gradient: 'from-purple-500 to-pink-500' },
    { name: 'CryptoVault Pro', desc: 'محفظة رقمية متعددة السلاسل', icon: <Hexagon className="w-5 h-5" />, gradient: 'from-cyan-500 to-blue-500' },
    { name: 'AI Copywriter', desc: 'مولّد نصوص تسويقية ذكي', icon: <Brain className="w-5 h-5" />, gradient: 'from-pink-500 to-red-500' },
    { name: 'DesignForge', desc: 'مصمم جرافيك آلي', icon: <Wand2 className="w-5 h-5" />, gradient: 'from-orange-500 to-yellow-500' },
    { name: 'SocialPilot', desc: 'مدير سوشيال ميديا آلي', icon: <Megaphone className="w-5 h-5" />, gradient: 'from-green-500 to-emerald-500' },
    { name: 'CodeMentor AI', desc: 'مساعد برمجة ذكي', icon: <Code className="w-5 h-5" />, gradient: 'from-indigo-500 to-purple-500' },
  ];

  return (
    <section id="projects" className="py-24 px-4 relative">
      <div className="max-w-7xl mx-auto">
        <div className="text-center mb-16">
          <div className="inline-flex items-center gap-2 bg-purple-500/10 border border-purple-500/20 rounded-full px-5 py-2 mb-6">
            <Layers className="w-4 h-4 text-purple-400" />
            <span className="text-purple-300 text-sm font-medium">مشاريع أخرى</span>
          </div>
          <h2 className="text-4xl md:text-5xl font-black text-white mb-4">
            من <span className="bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">Studio-ZeroBaran</span>
          </h2>
          <p className="text-gray-400 text-lg">مشاريع عظيمة أخرى من نفس الاستوديو</p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {projects.map((project, i) => (
            <a key={i} href="https://baranavi.gumroad.com/" target="_blank" rel="noopener noreferrer" className="group bg-white/[0.03] border border-white/10 rounded-2xl p-5 hover:border-white/20 transition-all hover:-translate-y-1">
              <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${project.gradient} flex items-center justify-center text-white mb-4 group-hover:scale-110 transition-transform`}>
                {project.icon}
              </div>
              <h4 className="font-bold text-white mb-1">{project.name}</h4>
              <p className="text-gray-500 text-sm">{project.desc}</p>
              <div className="flex items-center gap-1 text-purple-400 text-xs font-medium mt-3 group-hover:gap-2 transition-all">
                اكتشف المزيد <ArrowUpRight className="w-3 h-3" />
              </div>
            </a>
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
      <div className="max-w-5xl mx-auto">
        <div className="text-center mb-16">
          <div className="inline-flex items-center gap-2 bg-blue-500/10 border border-blue-500/20 rounded-full px-5 py-2 mb-6">
            <Mail className="w-4 h-4 text-blue-400" />
            <span className="text-blue-300 text-sm font-medium">تواصل معنا</span>
          </div>
          <h2 className="text-4xl md:text-6xl font-black text-white mb-4">
            جاهز <span className="bg-gradient-to-r from-blue-400 to-cyan-400 bg-clip-text text-transparent">للانطلاق؟</span>
          </h2>
          <p className="text-gray-400 text-lg">تواصل معنا وحوّل محتواك لعالمي</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-5 mb-10">
          <a href="mailto:baranavisat@gmail.com" className="group bg-white/[0.03] border border-white/10 rounded-2xl p-6 text-center hover:border-blue-500/30 transition-all hover:-translate-y-1">
            <div className="w-14 h-14 rounded-xl bg-blue-500/10 flex items-center justify-center text-blue-400 mx-auto mb-4 group-hover:scale-110 transition-transform">
              <Mail className="w-6 h-6" />
            </div>
            <h4 className="font-bold text-white mb-1">البريد الإلكتروني</h4>
            <p className="text-gray-400 text-sm break-all">baranavisat@gmail.com</p>
          </a>

          <a href="tel:+905313263722" className="group bg-white/[0.03] border border-white/10 rounded-2xl p-6 text-center hover:border-cyan-500/30 transition-all hover:-translate-y-1">
            <div className="w-14 h-14 rounded-xl bg-cyan-500/10 flex items-center justify-center text-cyan-400 mx-auto mb-4 group-hover:scale-110 transition-transform">
              <Phone className="w-6 h-6" />
            </div>
            <h4 className="font-bold text-white mb-1">الهاتف / واتساب</h4>
            <p className="text-gray-400 text-sm" dir="ltr">+90 531 326 3722</p>
          </a>

          <a href="https://baranavi.gumroad.com/" target="_blank" rel="noopener noreferrer" className="group bg-white/[0.03] border border-white/10 rounded-2xl p-6 text-center hover:border-emerald-500/30 transition-all hover:-translate-y-1">
            <div className="w-14 h-14 rounded-xl bg-emerald-500/10 flex items-center justify-center text-emerald-400 mx-auto mb-4 group-hover:scale-110 transition-transform">
              <ShoppingBag className="w-6 h-6" />
            </div>
            <h4 className="font-bold text-white mb-1">المتجر</h4>
            <p className="text-gray-400 text-sm">baranavi.gumroad.com</p>
          </a>
        </div>

        {/* Payment */}
        <div className="bg-white/[0.03] border border-white/10 rounded-2xl p-8">
          <h3 className="text-xl font-bold text-white text-center mb-6 flex items-center justify-center gap-2">
            <Shield className="w-5 h-5 text-green-400" />
            طرق الدفع المتاحة
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-white/5 rounded-xl p-5 text-center border border-white/5">
              <div className="text-3xl mb-3">🏦</div>
              <h4 className="font-bold text-white text-sm mb-1">تحويل بنكي</h4>
              <p className="text-gray-500 text-xs">ليرة تركية / دولار</p>
            </div>
            <div className="bg-white/5 rounded-xl p-5 text-center border border-white/5">
              <div className="text-3xl mb-3">₿</div>
              <h4 className="font-bold text-white text-sm mb-1">بيتكوين</h4>
              <p className="text-gray-500 text-xs">دفع آمن ومباشر</p>
            </div>
            <div className="bg-white/5 rounded-xl p-5 text-center border border-white/5">
              <div className="text-3xl mb-3">💎</div>
              <h4 className="font-bold text-white text-sm mb-1">USDT / Crypto</h4>
              <p className="text-gray-500 text-xs">عملات رقمية</p>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

// ============ FOOTER ============
function Footer() {
  return (
    <footer className="border-t border-white/5 py-12 px-4">
      <div className="max-w-7xl mx-auto">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-10">
          <div className="md:col-span-2">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-500 via-cyan-500 to-emerald-500 flex items-center justify-center">
                <Languages className="w-5 h-5 text-white" />
              </div>
              <div>
                <span className="font-black text-white text-sm sm:text-base block leading-none">PolyGlot</span>
                <span className="text-[10px] text-cyan-400 font-medium tracking-widest">STREAMBARAN</span>
              </div>
            </div>
            <p className="text-gray-500 text-sm max-w-md leading-relaxed">
              منظومة الترجمة الذاتية والدبلجة الصوتية اللامركزية — ترجم، فرّغ، ودبلج أي فيديو بالعالم مجاناً بالكامل.
            </p>
          </div>

          <div>
            <h4 className="font-bold text-white mb-4 text-sm">روابط</h4>
            <ul className="space-y-2">
              <li><a href="#features" className="text-gray-500 hover:text-blue-400 text-sm transition-colors">المميزات</a></li>
              <li><a href="#how-it-works" className="text-gray-500 hover:text-blue-400 text-sm transition-colors">آلية العمل</a></li>
              <li><a href="#tech" className="text-gray-500 hover:text-blue-400 text-sm transition-colors">التقنيات</a></li>
              <li><a href="#languages" className="text-gray-500 hover:text-blue-400 text-sm transition-colors">اللغات</a></li>
            </ul>
          </div>

          <div>
            <h4 className="font-bold text-white mb-4 text-sm">تواصل</h4>
            <ul className="space-y-2">
              <li className="flex items-center gap-2 text-gray-500 text-sm">
                <Mail className="w-3.5 h-3.5" /> baranavisat@gmail.com
              </li>
              <li className="flex items-center gap-2 text-gray-500 text-sm" dir="ltr">
                <Phone className="w-3.5 h-3.5" /> +90 531 326 3722
              </li>
              <li className="flex items-center gap-2 text-gray-500 text-sm">
                <Globe className="w-3.5 h-3.5" /> baranavi.gumroad.com
              </li>
            </ul>
          </div>
        </div>

        <div className="border-t border-white/5 pt-8 flex flex-col md:flex-row items-center justify-between gap-4">
          <p className="text-gray-600 text-sm">
            © 2025 PolyGlot-StreamBaran — Baran Avisat. جميع الحقوق محفوظة.
          </p>
          <div className="flex items-center gap-4">
            <a href="#" className="text-gray-600 hover:text-white text-sm transition-colors">سياسة الخصوصية</a>
            <a href="#" className="text-gray-600 hover:text-white text-sm transition-colors">الشروط</a>
          </div>
        </div>
      </div>
    </footer>
  );
}

// ============ MAIN APP ============
export default function App() {
  return (
    <div className="min-h-screen bg-[#030712] text-white" dir="rtl" style={{ fontFamily: "'Tajawal', sans-serif" }}>
      <AnimatedBackground />
      <Navbar />
      <HeroSection />
      <FeaturesSection />
      <HowItWorksSection />
      <TechStackSection />
      <LanguagesSection />
      <DemoSection />
      <WhySection />
      <OtherProjectsSection />
      <ContactSection />
      <Footer />
    </div>
  );
}
