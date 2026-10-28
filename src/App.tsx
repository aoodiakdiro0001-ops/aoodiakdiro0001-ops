import { useState, useEffect } from 'react';
import {
  Database, TrendingUp, BarChart3, LineChart, PieChart, Activity,
  Mail, Phone, ShoppingBag, Clock, Sparkles,
  ArrowRight, Star, Code, Workflow, Layers, Cloud,
  Github, ExternalLink, Menu, X, Hexagon, Brain, Cpu,
  ArrowUpRight, Terminal, Lock, Eye, Search,
  FileText, RefreshCw, DollarSign, Send,
  ChevronRight, Shield, Zap, Download, Upload,
  Filter, Table, GitBranch, Server, AlertCircle,
  Globe, Target
} from 'lucide-react';

// ============ ANIMATED BACKGROUND ============
function AnimatedBackground() {
  return (
    <div className="fixed inset-0 -z-10 overflow-hidden">
      <div className="absolute inset-0 bg-[#0a0f1e]"></div>
      <div className="absolute top-0 left-1/4 w-[600px] h-[600px] bg-blue-600/10 rounded-full filter blur-[180px] animate-pulse"></div>
      <div className="absolute bottom-0 right-1/4 w-[600px] h-[600px] bg-purple-600/10 rounded-full filter blur-[180px] animate-pulse" style={{ animationDelay: '2s' }}></div>
      <div className="absolute top-1/2 left-1/2 w-[400px] h-[400px] bg-green-600/8 rounded-full filter blur-[150px] animate-pulse" style={{ animationDelay: '4s' }}></div>
      <div className="absolute inset-0 opacity-[0.03]" style={{
        backgroundImage: 'linear-gradient(rgba(59,130,246,0.3) 1px, transparent 1px), linear-gradient(90deg, rgba(59,130,246,0.3) 1px, transparent 1px)',
        backgroundSize: '60px 60px'
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
    { href: '#demo', label: 'تجربة حية' },
    { href: '#tech', label: 'التقنيات' },
    { href: '#projects', label: 'مشاريع أخرى' },
    { href: '#contact', label: 'تواصل' },
  ];

  return (
    <nav className={`fixed top-0 left-0 right-0 z-50 transition-all duration-500 ${scrolled ? 'bg-[#0a0f1e]/80 backdrop-blur-2xl border-b border-white/5 shadow-2xl shadow-blue-500/5' : ''}`}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 py-4 flex items-center justify-between">
        <a href="#" className="flex items-center gap-3 group">
          <div className="relative">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-500 via-purple-500 to-green-500 flex items-center justify-center group-hover:scale-110 transition-transform duration-300">
              <Database className="w-5 h-5 text-white" />
            </div>
            <div className="absolute inset-0 rounded-xl bg-gradient-to-br from-blue-500 via-purple-500 to-green-500 blur-lg opacity-50 group-hover:opacity-80 transition-opacity"></div>
          </div>
          <div>
            <span className="font-black text-white text-sm sm:text-base block leading-none">Data-Nexus</span>
            <span className="text-[10px] text-blue-400 font-medium tracking-widest">ZEROBARAN</span>
          </div>
        </a>

        <div className="hidden lg:flex items-center gap-1">
          {links.map((link) => (
            <a key={link.href} href={link.href} className="text-gray-400 hover:text-white transition-colors text-sm font-medium px-3 py-2 rounded-lg hover:bg-white/5">
              {link.label}
            </a>
          ))}
          <a href="https://baranavi.gumroad.com/" target="_blank" rel="noopener noreferrer" className="mr-2 bg-gradient-to-r from-blue-600 to-purple-600 text-white px-5 py-2.5 rounded-xl text-sm font-bold hover:shadow-lg hover:shadow-blue-500/30 transition-all flex items-center gap-2">
            <ShoppingBag className="w-4 h-4" />
            المتجر
          </a>
        </div>

        <button onClick={() => setIsOpen(!isOpen)} className="lg:hidden text-white p-2">
          {isOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
        </button>
      </div>

      {isOpen && (
        <div className="lg:hidden bg-[#0a0f1e]/95 backdrop-blur-2xl border-b border-white/5 px-4 py-4 space-y-1">
          {links.map((link) => (
            <a key={link.href} href={link.href} onClick={() => setIsOpen(false)} className="block text-gray-300 hover:text-white py-3 px-4 rounded-lg hover:bg-white/5">
              {link.label}
            </a>
          ))}
          <a href="https://baranavi.gumroad.com/" target="_blank" rel="noopener noreferrer" className="block bg-gradient-to-r from-blue-600 to-purple-600 text-white px-4 py-3 rounded-xl text-center font-bold mt-2">
            زيارة المتجر
          </a>
        </div>
      )}
    </nav>
  );
}

// ============ HERO SECTION ============
function HeroSection() {
  const [dataPoints, setDataPoints] = useState(0);
  const [insights, setInsights] = useState(0);
  const [accuracy, setAccuracy] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setDataPoints(prev => Math.min(prev + Math.floor(Math.random() * 10000) + 1000, 2500000));
      setInsights(prev => Math.min(prev + Math.floor(Math.random() * 50) + 10, 1547));
      setAccuracy(prev => Math.min(prev + Math.random() * 0.5, 98.7));
    }, 100);
    return () => clearInterval(interval);
  }, []);

  return (
    <section className="relative min-h-screen flex items-center justify-center overflow-hidden pt-20">
      <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 py-20">
        <div className="text-center">
          {/* Badge */}
          <div className="inline-flex items-center gap-2 bg-blue-500/10 border border-blue-500/20 rounded-full px-5 py-2.5 mb-8 backdrop-blur-sm">
            <div className="relative">
              <div className="w-2 h-2 bg-blue-400 rounded-full"></div>
              <div className="absolute inset-0 w-2 h-2 bg-blue-400 rounded-full animate-ping"></div>
            </div>
            <span className="text-gray-300 text-sm font-medium">تحليل البيانات الذاتي — مجاني بالكامل</span>
          </div>

          {/* Main Title */}
          <h1 className="text-4xl sm:text-5xl md:text-6xl lg:text-7xl font-black text-white mb-6 tracking-tight leading-[1.1]">
            حوّل بياناتك إلى
            <br />
            <span className="bg-gradient-to-r from-blue-400 via-purple-400 to-green-400 bg-clip-text text-transparent">
              قرارات ذكية
            </span>
          </h1>

          <p className="text-lg md:text-xl text-gray-400 mb-10 max-w-3xl mx-auto leading-relaxed">
            منظومة ذكية متكاملة <span className="text-blue-400 font-semibold">تجمع، تنظف، وتحلل بياناتك</span> تلقائياً، وتولّد لوحات تحكم تفاعلية وتقارير تنبؤية دقيقة — <span className="text-green-400 font-semibold">بدون دفع دولار واحد</span>
          </p>

          {/* CTA */}
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center mb-16">
            <a href="#demo" className="group relative bg-gradient-to-r from-blue-600 to-purple-600 text-white px-8 py-4 rounded-2xl font-bold text-lg hover:shadow-2xl hover:shadow-blue-500/30 transition-all duration-300 flex items-center gap-3">
              <Activity className="w-5 h-5" />
              جرّب التحليل
              <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
              <div className="absolute inset-0 rounded-2xl bg-gradient-to-r from-blue-600 to-purple-600 blur-xl opacity-50 group-hover:opacity-80 transition-opacity -z-10"></div>
            </a>
            <a href="https://baranavi.gumroad.com/" target="_blank" rel="noopener noreferrer" className="border border-white/10 text-gray-300 px-8 py-4 rounded-2xl font-bold text-lg hover:border-blue-500/50 hover:text-white transition-all duration-300 flex items-center gap-2 backdrop-blur-sm">
              <Download className="w-5 h-5" />
              احصل عليه
            </a>
          </div>

          {/* Stats */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 max-w-4xl mx-auto">
            <div className="bg-white/5 border border-white/10 rounded-2xl p-4 backdrop-blur-sm">
              <div className="text-2xl font-black text-blue-400">{(dataPoints / 1000000).toFixed(1)}M</div>
              <div className="text-xs text-gray-500 mt-1">نقطة بيانات</div>
            </div>
            <div className="bg-white/5 border border-white/10 rounded-2xl p-4 backdrop-blur-sm">
              <div className="text-2xl font-black text-purple-400">{insights}</div>
              <div className="text-xs text-gray-500 mt-1">رؤى مستخرجة</div>
            </div>
            <div className="bg-white/5 border border-white/10 rounded-2xl p-4 backdrop-blur-sm">
              <div className="text-2xl font-black text-green-400">{accuracy.toFixed(1)}%</div>
              <div className="text-xs text-gray-500 mt-1">دقة التنبؤ</div>
            </div>
            <div className="bg-white/5 border border-white/10 rounded-2xl p-4 backdrop-blur-sm">
              <div className="text-2xl font-black text-yellow-400">0$</div>
              <div className="text-xs text-gray-500 mt-1">تكلفة التشغيل</div>
            </div>
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
      icon: <Database className="w-7 h-7" />,
      title: 'جمع البيانات الذكي',
      desc: 'ربط مصادر بيانات متعددة (CSV, JSON, SQL, APIs) وسحب البيانات تلقائياً',
      gradient: 'from-blue-500 to-cyan-500',
      glow: 'bg-blue-500/20',
    },
    {
      icon: <Filter className="w-7 h-7" />,
      title: 'تنظيف ومعالجة تلقائية',
      desc: 'إزالة القيم المفقودة والشوائب وتكرارات البيانات برمجياً بدقة متناهية',
      gradient: 'from-cyan-500 to-teal-500',
      glow: 'bg-cyan-500/20',
    },
    {
      icon: <Brain className="w-7 h-7" />,
      title: 'تحليل تنبؤي بالـ AI',
      desc: 'استخدام الذكاء الاصطناعي لتوقع الاتجاهات المستقبلية واستخراج التوصيات',
      gradient: 'from-purple-500 to-pink-500',
      glow: 'bg-purple-500/20',
    },
    {
      icon: <BarChart3 className="w-7 h-7" />,
      title: 'لوحات تحكم تفاعلية',
      desc: 'رسوم بيانية مذهلة ومؤشرات حيّة على Streamlit Cloud مجاناً',
      gradient: 'from-green-500 to-emerald-500',
      glow: 'bg-green-500/20',
    },
    {
      icon: <AlertCircle className="w-7 h-7" />,
      title: 'تنبيهات ذكية فورية',
      desc: 'إشعارات على تليجرام عند حدوث شذوذ في الأرقام أو تغيرات مهمة',
      gradient: 'from-orange-500 to-red-500',
      glow: 'bg-orange-500/20',
    },
    {
      icon: <Lock className="w-7 h-7" />,
      title: 'سيادة مطلقة على البيانات',
      desc: 'حماية بياناتك الحساسة وعدم تسريبها لشركات خارجية — كل شيء تحت سيطرتك',
      gradient: 'from-indigo-500 to-purple-500',
      glow: 'bg-indigo-500/20',
    },
  ];

  return (
    <section id="features" className="py-24 px-4 relative">
      <div className="max-w-7xl mx-auto">
        <div className="text-center mb-16">
          <div className="inline-flex items-center gap-2 bg-blue-500/10 border border-blue-500/20 rounded-full px-5 py-2 mb-6">
            <Sparkles className="w-4 h-4 text-blue-400" />
            <span className="text-blue-300 text-sm font-medium">القدرات</span>
          </div>
          <h2 className="text-4xl md:text-6xl font-black text-white mb-4">
            محلل بيانات <span className="bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">ذكي</span>
          </h2>
          <p className="text-gray-400 text-lg max-w-2xl mx-auto">
            6 قدرات أساسية لتحويل البيانات الخام إلى قرارات ذكية
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
      title: 'رفع البيانات',
      desc: 'ارفع ملفات CSV/JSON أو اربط بقواعد بيانات SQL أو APIs خارجية',
      color: 'from-blue-500 to-cyan-500',
    },
    {
      num: '02',
      icon: <Filter className="w-6 h-6" />,
      title: 'المعالجة والتنظيف',
      desc: 'GitHub Actions + Python ينظف البيانات ويزيل الأخطاء والتكرارات',
      color: 'from-cyan-500 to-teal-500',
    },
    {
      num: '03',
      icon: <Database className="w-6 h-6" />,
      title: 'التخزين الذكي',
      desc: 'Supabase يحفظ البيانات المعالجة في مستودع سحابي مجاني',
      color: 'from-teal-500 to-green-500',
    },
    {
      num: '04',
      icon: <Brain className="w-6 h-6" />,
      title: 'التحليل الذكي',
      desc: 'Gemini API يحلل الاتجاهات ويستخرج التوصيات الذكية',
      color: 'from-purple-500 to-pink-500',
    },
    {
      num: '05',
      icon: <BarChart3 className="w-6 h-6" />,
      title: 'العرض البصري',
      desc: 'Streamlit Dashboard يعرض رسوم بيانية تفاعلية مذهلة',
      color: 'from-green-500 to-emerald-500',
    },
    {
      num: '06',
      icon: <Send className="w-6 h-6" />,
      title: 'التقارير والتنبيهات',
      desc: 'Telegram Bot يرسل تقارير دورية وتنبيهات فورية',
      color: 'from-emerald-500 to-blue-500',
    },
  ];

  return (
    <section id="how-it-works" className="py-24 px-4 relative">
      <div className="max-w-6xl mx-auto">
        <div className="text-center mb-16">
          <div className="inline-flex items-center gap-2 bg-purple-500/10 border border-purple-500/20 rounded-full px-5 py-2 mb-6">
            <Workflow className="w-4 h-4 text-purple-400" />
            <span className="text-purple-300 text-sm font-medium">آلية العمل</span>
          </div>
          <h2 className="text-4xl md:text-6xl font-black text-white mb-4">
            من <span className="bg-gradient-to-r from-blue-400 to-cyan-400 bg-clip-text text-transparent">البيانات الخام</span> إلى <span className="bg-gradient-to-r from-green-400 to-emerald-400 bg-clip-text text-transparent">القرارات الذكية</span>
          </h2>
          <p className="text-gray-400 text-lg max-w-2xl mx-auto">
            6 خطوات فقط — من رفع البيانات إلى الحصول على رؤى قيمة
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {steps.map((step, i) => (
            <div key={i} className="relative bg-white/[0.03] border border-white/10 rounded-2xl p-6 hover:border-white/20 transition-all group">
              <div className="flex items-center gap-3 mb-4">
                <span className="text-4xl font-black text-gray-800 group-hover:text-gray-700 transition-colors">{step.num}</span>
                <div className={`w-10 h-10 rounded-lg bg-gradient-to-br ${step.color} flex items-center justify-center text-white`}>
                  {step.icon}
                </div>
              </div>
              <h3 className="text-lg font-bold text-white mb-2">{step.title}</h3>
              <p className="text-gray-400 text-sm">{step.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

// ============ LIVE DEMO SECTION ============
function DemoSection() {
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [stage, setStage] = useState(0);
  const [logs, setLogs] = useState<string[]>([]);

  const stages = [
    { status: 'loading', color: 'text-blue-400', text: '📥 جاري تحميل ملف البيانات: sales_2024.csv (2.3MB)...' },
    { status: 'cleaning', color: 'text-cyan-400', text: '🧹 تنظيف البيانات: إزالة 847 قيمة مفقودة، 234 مكرر...' },
    { status: 'processing', color: 'text-teal-400', text: '⚙️ معالجة ETL: دمج 5 جداول، حساب المؤشرات...' },
    { status: 'storing', color: 'text-green-400', text: '💾 حفظ في Supabase: 12,847 سجل في 3 جداول...' },
    { status: 'analyzing', color: 'text-purple-400', text: '🧠 Gemini API يحلل الاتجاهات ويستخرج الرؤى...' },
    { status: 'insights', color: 'text-pink-400', text: '💡 تم استخراج 15 رؤى مهمة و 3 توصيات عملية' },
    { status: 'dashboard', color: 'text-yellow-400', text: '📊 لوحة التحكم جاهزة! 8 رسوم بيانية تفاعلية' },
    { status: 'alert', color: 'text-orange-400', text: '🔔 تنبيه: ارتفاع 23% في المبيعات - فرصة نمو!' },
  ];

  const handleStart = () => {
    setIsAnalyzing(true);
    setStage(0);
    setLogs([]);

    let currentStage = 0;
    const timer = setInterval(() => {
      currentStage++;
      setStage(currentStage);
      setLogs(prev => [...prev, stages[currentStage].text]);
      if (currentStage >= stages.length - 1) {
        clearInterval(timer);
        setTimeout(() => setIsAnalyzing(false), 2000);
      }
    }, 1200);
  };

  return (
    <section id="demo" className="py-24 px-4 relative">
      <div className="max-w-5xl mx-auto">
        <div className="text-center mb-12">
          <div className="inline-flex items-center gap-2 bg-green-500/10 border border-green-500/20 rounded-full px-5 py-2 mb-6">
            <Activity className="w-4 h-4 text-green-400" />
            <span className="text-green-300 text-sm font-medium">محاكاة حية</span>
          </div>
          <h2 className="text-4xl md:text-5xl font-black text-white mb-4">
            شاهد <span className="bg-gradient-to-r from-blue-400 to-green-400 bg-clip-text text-transparent">التحليل الحي</span>
          </h2>
          <p className="text-gray-400 text-lg">محاكاة حية لكيفية تحليل النظام للبيانات</p>
        </div>

        <div className="bg-white/[0.03] border border-white/10 rounded-3xl overflow-hidden">
          {/* Terminal Header */}
          <div className="bg-gray-900/50 border-b border-white/10 px-4 py-3 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-red-500"></div>
              <div className="w-3 h-3 rounded-full bg-yellow-500"></div>
              <div className="w-3 h-3 rounded-full bg-green-500"></div>
            </div>
            <span className="text-xs text-gray-500 font-mono">data-nexus ~ analyzing</span>
            <Terminal className="w-4 h-4 text-gray-500" />
          </div>

          {/* Terminal Body */}
          <div className="p-6 font-mono text-sm min-h-[320px]">
            {logs.length === 0 ? (
              <div className="text-gray-500">
                <p>$ data-nexus --analyze sales_2024.csv</p>
                <p className="mt-2 text-gray-600">Press the button to start live analysis simulation...</p>
              </div>
            ) : (
              <div className="space-y-2">
                {logs.map((log, i) => (
                  <div key={i} className={`flex items-start gap-2 animate-fade-in ${stages[i].color}`}>
                    <span className="text-gray-600 text-xs mt-0.5">[{new Date().toLocaleTimeString('en-US', { hour12: false })}]</span>
                    <span>{log}</span>
                  </div>
                ))}
                {isAnalyzing && (
                  <div className="flex items-center gap-2 text-gray-500">
                    <div className="w-2 h-4 bg-blue-400 animate-pulse"></div>
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Control */}
          <div className="border-t border-white/10 p-4 bg-gray-900/30">
            <button
              onClick={handleStart}
              disabled={isAnalyzing}
              className="w-full bg-gradient-to-r from-blue-600 to-purple-600 text-white px-6 py-3 rounded-xl font-bold hover:shadow-lg hover:shadow-blue-500/30 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              {isAnalyzing ? (
                <>
                  <RefreshCw className="w-5 h-5 animate-spin" />
                  جاري التحليل...
                </>
              ) : (
                <>
                  <Activity className="w-5 h-5" />
                  بدء التحليل
                </>
              )}
            </button>
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
      icon: <Cpu className="w-6 h-6" />,
      name: 'Python + Pandas',
      role: 'محرك المعالجة',
      desc: 'سحب البيانات وتنظيفها وتنفيذ العمليات الحسابية المعقدة',
      color: 'from-blue-600 to-cyan-600',
    },
    {
      icon: <Github className="w-6 h-6" />,
      name: 'GitHub Actions',
      role: 'محرك التشغيل',
      desc: 'تنفيذ عمليات ETL دورياً مجاناً على خوادم GitHub',
      color: 'from-gray-600 to-gray-700',
    },
    {
      icon: <Brain className="w-6 h-6" />,
      name: 'Google Gemini API',
      role: 'العقل التحليلي',
      desc: 'تحليل الاتجاهات واستخراج التوصيات الذكية من البيانات',
      color: 'from-purple-600 to-pink-600',
    },
    {
      icon: <Database className="w-6 h-6" />,
      name: 'Supabase',
      role: 'مستودع البيانات',
      desc: 'تخزين الجداول الضخمة والسجلات الزمنية مجاناً',
      color: 'from-green-600 to-emerald-600',
    },
    {
      icon: <BarChart3 className="w-6 h-6" />,
      name: 'Streamlit Cloud',
      role: 'لوحة التحكم',
      desc: 'استضافة مجانية للوحة تحكم تفاعلية ورسوم بيانية',
      color: 'from-red-600 to-orange-600',
    },
    {
      icon: <Send className="w-6 h-6" />,
      name: 'Telegram Bot API',
      role: 'التنبيهات والتقارير',
      desc: 'إرسال تقارير دورية وتنبيهات فورية عند الشذوذ',
      color: 'from-sky-600 to-blue-600',
    },
  ];

  return (
    <section id="tech" className="py-24 px-4 relative">
      <div className="max-w-7xl mx-auto">
        <div className="text-center mb-16">
          <div className="inline-flex items-center gap-2 bg-green-500/10 border border-green-500/20 rounded-full px-5 py-2 mb-6">
            <Code className="w-4 h-4 text-green-400" />
            <span className="text-green-300 text-sm font-medium">التقنيات المجانية</span>
          </div>
          <h2 className="text-4xl md:text-6xl font-black text-white mb-4">
            <span className="bg-gradient-to-r from-green-400 to-emerald-400 bg-clip-text text-transparent">The Free Tech Stack</span>
          </h2>
          <p className="text-gray-400 text-lg max-w-2xl mx-auto">
            6 تقنيات مجانية بالكامل — صفر دولار تكلفة تشغيل
          </p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {techs.map((tech, i) => (
            <div key={i} className="group bg-white/[0.03] border border-white/10 rounded-2xl p-5 hover:border-white/20 transition-all duration-300 hover:-translate-y-1">
              <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${tech.color} flex items-center justify-center text-white mb-4 group-hover:scale-110 transition-transform`}>
                {tech.icon}
              </div>
              <h4 className="font-bold text-white text-sm mb-1">{tech.name}</h4>
              <p className="text-xs text-blue-400 font-medium mb-2">{tech.role}</p>
              <p className="text-xs text-gray-500 leading-relaxed">{tech.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

// ============ WHY SECTION ============
function WhySection() {
  const reasons = [
    {
      icon: <DollarSign className="w-7 h-7" />,
      title: 'توفير مالي فلكي',
      desc: 'أدوات تحليل البيانات المتقدمة تكلف ثروات — هنا بالمجان بالكامل',
      color: 'text-green-400',
      bg: 'bg-green-500/10',
    },
    {
      icon: <TrendingUp className="w-7 h-7" />,
      title: 'تحليل تنبؤي فوري',
      desc: 'لا يعرض الأرقام السابقة فقط، بل يتوقع الاتجاهات المستقبلية',
      color: 'text-blue-400',
      bg: 'bg-blue-500/10',
    },
    {
      icon: <Lock className="w-7 h-7" />,
      title: 'سيادة مطلقة للبيانات',
      desc: 'حماية بياناتك الحساسة وعدم تسريبها لشركات خارجية',
      color: 'text-purple-400',
      bg: 'bg-purple-500/10',
    },
    {
      icon: <Zap className="w-7 h-7" />,
      title: 'أتمتة كاملة',
      desc: 'من جمع البيانات إلى التقارير — كل شيء يعمل تلقائياً 24/7',
      color: 'text-yellow-400',
      bg: 'bg-yellow-500/10',
    },
  ];

  return (
    <section className="py-24 px-4 relative">
      <div className="max-w-6xl mx-auto">
        <div className="text-center mb-16">
          <div className="inline-flex items-center gap-2 bg-yellow-500/10 border border-yellow-500/20 rounded-full px-5 py-2 mb-6">
            <Star className="w-4 h-4 text-yellow-400" />
            <span className="text-yellow-300 text-sm font-medium">لماذا Data-Nexus؟</span>
          </div>
          <h2 className="text-4xl md:text-6xl font-black text-white mb-4">
            لماذا <span className="bg-gradient-to-r from-yellow-400 to-orange-400 bg-clip-text text-transparent">تحتاجه؟</span>
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
    { name: 'Studio-ZeroBaran', desc: 'استوديو الإنتاج المرئي والإعلاني', icon: <Layers className="w-5 h-5" />, gradient: 'from-purple-500 to-pink-500' },
    { name: 'PolyGlot-StreamBaran', desc: 'منظومة الترجمة والدبلجة الصوتية', icon: <Globe className="w-5 h-5" />, gradient: 'from-blue-500 to-cyan-500' },
    { name: 'AIOps-ZeroBaran', desc: 'المهندس الرقمي لإدارة الخوادم', icon: <Server className="w-5 h-5" />, gradient: 'from-emerald-500 to-blue-500' },
    { name: 'Lead-Sniper ZeroBaran', desc: 'منظومة صيد العملاء الذكية', icon: <Target className="w-5 h-5" />, gradient: 'from-orange-500 to-red-500' },
    { name: 'Spatial-ZeroBaran', desc: 'استوديو توليد المجسمات 3D', icon: <Hexagon className="w-5 h-5" />, gradient: 'from-pink-500 to-purple-500' },
    { name: 'AI Copywriter', desc: 'مولّد نصوص تسويقية ذكي', icon: <Brain className="w-5 h-5" />, gradient: 'from-cyan-500 to-blue-500' },
  ];

  return (
    <section id="projects" className="py-24 px-4 relative">
      <div className="max-w-7xl mx-auto">
        <div className="text-center mb-16">
          <div className="inline-flex items-center gap-2 bg-indigo-500/10 border border-indigo-500/20 rounded-full px-5 py-2 mb-6">
            <Layers className="w-4 h-4 text-indigo-400" />
            <span className="text-indigo-300 text-sm font-medium">مشاريع أخرى</span>
          </div>
          <h2 className="text-4xl md:text-5xl font-black text-white mb-4">
            من <span className="bg-gradient-to-r from-indigo-400 to-purple-400 bg-clip-text text-transparent">Studio-ZeroBaran</span>
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
            جاهز <span className="bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">لتحليل بياناتك؟</span>
          </h2>
          <p className="text-gray-400 text-lg">تواصل معنا واحصل على منظومة التحليل الذكية اليوم</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-5 mb-10">
          <a href="mailto:baranavisat@gmail.com" className="group bg-white/[0.03] border border-white/10 rounded-2xl p-6 text-center hover:border-blue-500/30 transition-all hover:-translate-y-1">
            <div className="w-14 h-14 rounded-xl bg-blue-500/10 flex items-center justify-center text-blue-400 mx-auto mb-4 group-hover:scale-110 transition-transform">
              <Mail className="w-6 h-6" />
            </div>
            <h4 className="font-bold text-white mb-1">البريد الإلكتروني</h4>
            <p className="text-gray-400 text-sm break-all">baranavisat@gmail.com</p>
          </a>

          <a href="tel:+905313263722" className="group bg-white/[0.03] border border-white/10 rounded-2xl p-6 text-center hover:border-purple-500/30 transition-all hover:-translate-y-1">
            <div className="w-14 h-14 rounded-xl bg-purple-500/10 flex items-center justify-center text-purple-400 mx-auto mb-4 group-hover:scale-110 transition-transform">
              <Phone className="w-6 h-6" />
            </div>
            <h4 className="font-bold text-white mb-1">الهاتف / واتساب</h4>
            <p className="text-gray-400 text-sm" dir="ltr">+90 531 326 3722</p>
          </a>

          <a href="https://baranavi.gumroad.com/" target="_blank" rel="noopener noreferrer" className="group bg-white/[0.03] border border-white/10 rounded-2xl p-6 text-center hover:border-green-500/30 transition-all hover:-translate-y-1">
            <div className="w-14 h-14 rounded-xl bg-green-500/10 flex items-center justify-center text-green-400 mx-auto mb-4 group-hover:scale-110 transition-transform">
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
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-500 via-purple-500 to-green-500 flex items-center justify-center">
                <Database className="w-5 h-5 text-white" />
              </div>
              <div>
                <span className="font-black text-white text-sm sm:text-base block leading-none">Data-Nexus</span>
                <span className="text-[10px] text-blue-400 font-medium tracking-widest">ZEROBARAN</span>
              </div>
            </div>
            <p className="text-gray-500 text-sm max-w-md leading-relaxed">
              منظومة تحليل وهندسة البيانات الذاتية واللامركزية — حوّل بياناتك الخام إلى قرارات ذكية بالمجان.
            </p>
          </div>

          <div>
            <h4 className="font-bold text-white mb-4 text-sm">روابط</h4>
            <ul className="space-y-2">
              <li><a href="#features" className="text-gray-500 hover:text-blue-400 text-sm transition-colors">المميزات</a></li>
              <li><a href="#how-it-works" className="text-gray-500 hover:text-blue-400 text-sm transition-colors">آلية العمل</a></li>
              <li><a href="#demo" className="text-gray-500 hover:text-blue-400 text-sm transition-colors">تجربة حية</a></li>
              <li><a href="#tech" className="text-gray-500 hover:text-blue-400 text-sm transition-colors">التقنيات</a></li>
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
                <ExternalLink className="w-3.5 h-3.5" /> baranavi.gumroad.com
              </li>
            </ul>
          </div>
        </div>

        <div className="border-t border-white/5 pt-8 flex flex-col md:flex-row items-center justify-between gap-4">
          <p className="text-gray-600 text-sm">
            © 2025 Data-Nexus ZeroBaran — Baran Avisat. جميع الحقوق محفوظة.
          </p>
          <div className="flex items-center gap-2 text-gray-600 text-xs">
            <span>صُنع بـ</span>
            <span className="text-red-500">❤</span>
            <span>وذكاء اصطناعي مجاني</span>
          </div>
        </div>
      </div>
    </footer>
  );
}

// ============ MAIN APP ============
export default function App() {
  return (
    <div className="min-h-screen bg-[#0a0f1e] text-white" dir="rtl" style={{ fontFamily: "'Tajawal', sans-serif" }}>
      <AnimatedBackground />
      <Navbar />
      <HeroSection />
      <FeaturesSection />
      <HowItWorksSection />
      <DemoSection />
      <TechStackSection />
      <WhySection />
      <OtherProjectsSection />
      <ContactSection />
      <Footer />
    </div>
  );
}
