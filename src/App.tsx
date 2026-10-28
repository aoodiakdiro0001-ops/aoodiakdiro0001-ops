import { useState, useEffect } from 'react';
import {
  Image as ImageIcon, Camera, Sparkles, Wand2, Layers, Download,
  Mail, Phone, ShoppingBag, Clock, Star,
  ArrowRight, Code, Workflow, Cloud,
  Github, ExternalLink, Menu, X, Hexagon, Brain, Cpu,
  ArrowUpRight, Terminal, Lock, Zap, Palette,
  RefreshCw, DollarSign, Send, Shield,
  Upload, Scissors, Sun, Box, Eye,
  Aperture, Focus, Contrast, Move
} from 'lucide-react';

// ============ ANIMATED BACKGROUND ============
function AnimatedBackground() {
  return (
    <div className="fixed inset-0 -z-10 overflow-hidden">
      <div className="absolute inset-0 bg-[#0a0510]"></div>
      <div className="absolute top-0 left-1/4 w-[600px] h-[600px] bg-pink-600/10 rounded-full filter blur-[180px] animate-pulse"></div>
      <div className="absolute bottom-0 right-1/4 w-[600px] h-[600px] bg-purple-600/10 rounded-full filter blur-[180px] animate-pulse" style={{ animationDelay: '2s' }}></div>
      <div className="absolute top-1/2 left-1/2 w-[400px] h-[400px] bg-cyan-600/8 rounded-full filter blur-[150px] animate-pulse" style={{ animationDelay: '4s' }}></div>
      <div className="absolute inset-0 opacity-[0.03]" style={{
        backgroundImage: 'linear-gradient(rgba(236,72,153,0.3) 1px, transparent 1px), linear-gradient(90deg, rgba(236,72,153,0.3) 1px, transparent 1px)',
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
    <nav className={`fixed top-0 left-0 right-0 z-50 transition-all duration-500 ${scrolled ? 'bg-[#0a0510]/80 backdrop-blur-2xl border-b border-white/5 shadow-2xl shadow-pink-500/5' : ''}`}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 py-4 flex items-center justify-between">
        <a href="#" className="flex items-center gap-3 group">
          <div className="relative">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-pink-500 via-purple-500 to-cyan-500 flex items-center justify-center group-hover:scale-110 transition-transform duration-300">
              <Aperture className="w-5 h-5 text-white" />
            </div>
            <div className="absolute inset-0 rounded-xl bg-gradient-to-br from-pink-500 via-purple-500 to-cyan-500 blur-lg opacity-50 group-hover:opacity-80 transition-opacity"></div>
          </div>
          <div>
            <span className="font-black text-white text-sm sm:text-base block leading-none">Pixel-Zero</span>
            <span className="text-[10px] text-pink-400 font-medium tracking-widest">BARAN</span>
          </div>
        </a>

        <div className="hidden lg:flex items-center gap-1">
          {links.map((link) => (
            <a key={link.href} href={link.href} className="text-gray-400 hover:text-white transition-colors text-sm font-medium px-3 py-2 rounded-lg hover:bg-white/5">
              {link.label}
            </a>
          ))}
          <a href="https://baranavi.gumroad.com/" target="_blank" rel="noopener noreferrer" className="mr-2 bg-gradient-to-r from-pink-600 to-purple-600 text-white px-5 py-2.5 rounded-xl text-sm font-bold hover:shadow-lg hover:shadow-pink-500/30 transition-all flex items-center gap-2">
            <ShoppingBag className="w-4 h-4" />
            المتجر
          </a>
        </div>

        <button onClick={() => setIsOpen(!isOpen)} className="lg:hidden text-white p-2">
          {isOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
        </button>
      </div>

      {isOpen && (
        <div className="lg:hidden bg-[#0a0510]/95 backdrop-blur-2xl border-b border-white/5 px-4 py-4 space-y-1">
          {links.map((link) => (
            <a key={link.href} href={link.href} onClick={() => setIsOpen(false)} className="block text-gray-300 hover:text-white py-3 px-4 rounded-lg hover:bg-white/5">
              {link.label}
            </a>
          ))}
          <a href="https://baranavi.gumroad.com/" target="_blank" rel="noopener noreferrer" className="block bg-gradient-to-r from-pink-600 to-purple-600 text-white px-4 py-3 rounded-xl text-center font-bold mt-2">
            زيارة المتجر
          </a>
        </div>
      )}
    </nav>
  );
}

// ============ HERO SECTION ============
function HeroSection() {
  const [images, setImages] = useState(0);
  const [backgrounds, setBackgrounds] = useState(0);
  const [time, setTime] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setImages(prev => Math.min(prev + Math.floor(Math.random() * 20) + 5, 1547));
      setBackgrounds(prev => Math.min(prev + Math.floor(Math.random() * 100) + 20, 8923));
      setTime(prev => Math.min(prev + 0.05, 1.8));
    }, 100);
    return () => clearInterval(interval);
  }, []);

  return (
    <section className="relative min-h-screen flex items-center justify-center overflow-hidden pt-20">
      <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 py-20">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
          {/* Content */}
          <div>
            <div className="inline-flex items-center gap-2 bg-pink-500/10 border border-pink-500/20 rounded-full px-5 py-2.5 mb-8 backdrop-blur-sm">
              <div className="relative">
                <div className="w-2 h-2 bg-pink-400 rounded-full"></div>
                <div className="absolute inset-0 w-2 h-2 bg-pink-400 rounded-full animate-ping"></div>
              </div>
              <span className="text-gray-300 text-sm font-medium">استوديو صور ذكي — مجاني بالكامل</span>
            </div>

            <h1 className="text-4xl sm:text-5xl md:text-6xl font-black text-white mb-6 tracking-tight leading-[1.1]">
              صورك الاحترافية
              <br />
              <span className="bg-gradient-to-r from-pink-400 via-purple-400 to-cyan-400 bg-clip-text text-transparent">
                بضغطة زر واحدة
              </span>
            </h1>

            <p className="text-lg md:text-xl text-gray-400 mb-10 leading-relaxed">
              نظام ذكي متكامل <span className="text-pink-400 font-semibold">يزيل الخلفيات، يعيد الإضاءة، ويولّد لقطات تسويقية احترافية</span> للمنتجات والأشخاص — <span className="text-cyan-400 font-semibold">بدون دفع دولار واحد</span>
            </p>

            <div className="flex flex-col sm:flex-row gap-4 mb-12">
              <a href="#demo" className="group relative bg-gradient-to-r from-pink-600 to-purple-600 text-white px-8 py-4 rounded-2xl font-bold text-lg hover:shadow-2xl hover:shadow-pink-500/30 transition-all duration-300 flex items-center gap-3">
                <Wand2 className="w-5 h-5" />
                جرّب الآن
                <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                <div className="absolute inset-0 rounded-2xl bg-gradient-to-r from-pink-600 to-purple-600 blur-xl opacity-50 group-hover:opacity-80 transition-opacity -z-10"></div>
              </a>
              <a href="https://baranavi.gumroad.com/" target="_blank" rel="noopener noreferrer" className="border border-white/10 text-gray-300 px-8 py-4 rounded-2xl font-bold text-lg hover:border-pink-500/50 hover:text-white transition-all duration-300 flex items-center gap-2 backdrop-blur-sm">
                <Download className="w-5 h-5" />
                احصل عليه
              </a>
            </div>

            <div className="grid grid-cols-3 gap-4">
              <div className="bg-white/5 border border-white/10 rounded-2xl p-4 backdrop-blur-sm">
                <div className="text-2xl font-black text-pink-400">{images}</div>
                <div className="text-xs text-gray-500 mt-1">صورة معالجة</div>
              </div>
              <div className="bg-white/5 border border-white/10 rounded-2xl p-4 backdrop-blur-sm">
                <div className="text-2xl font-black text-purple-400">{backgrounds.toLocaleString()}</div>
                <div className="text-xs text-gray-500 mt-1">خلفية مولّدة</div>
              </div>
              <div className="bg-white/5 border border-white/10 rounded-2xl p-4 backdrop-blur-sm">
                <div className="text-2xl font-black text-cyan-400">{time.toFixed(1)}s</div>
                <div className="text-xs text-gray-500 mt-1">زمن المعالجة</div>
              </div>
            </div>
          </div>

          {/* Visual */}
          <div className="relative flex justify-center items-center">
            <div className="relative w-80 h-80">
              {/* Before Image */}
              <div className="absolute top-0 right-0 w-48 h-48 rounded-2xl bg-gradient-to-br from-gray-700 to-gray-800 border-2 border-gray-600 shadow-2xl transform rotate-6 overflow-hidden">
                <div className="absolute inset-0 flex items-center justify-center">
                  <div className="text-center">
                    <Box className="w-16 h-16 text-gray-500 mx-auto mb-2" />
                    <p className="text-xs text-gray-400">قبل</p>
                  </div>
                </div>
                <div className="absolute bottom-2 right-2 bg-red-500/80 text-white text-xs px-2 py-1 rounded">BEFORE</div>
              </div>

              {/* After Image */}
              <div className="absolute bottom-0 left-0 w-56 h-56 rounded-2xl bg-gradient-to-br from-pink-500/20 via-purple-500/20 to-cyan-500/20 border-2 border-pink-500/50 shadow-2xl transform -rotate-6 overflow-hidden backdrop-blur-sm">
                <div className="absolute inset-0 flex items-center justify-center">
                  <div className="text-center">
                    <Sparkles className="w-20 h-20 text-pink-400 mx-auto mb-2" />
                    <p className="text-xs text-pink-300">بعد</p>
                  </div>
                </div>
                <div className="absolute bottom-2 left-2 bg-pink-500/80 text-white text-xs px-2 py-1 rounded">AFTER</div>
              </div>

              {/* Magic Wand */}
              <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-20 h-20 rounded-full bg-gradient-to-br from-pink-500 to-purple-500 flex items-center justify-center shadow-2xl animate-pulse">
                <Wand2 className="w-10 h-10 text-white" />
              </div>
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
      icon: <Scissors className="w-7 h-7" />,
      title: 'إزالة الخلفيات بدقة',
      desc: 'عزل المنتجات والأشخاص عن الخلفية بدقة متناهية خلال ثانية واحدة',
      gradient: 'from-pink-500 to-rose-500',
      glow: 'bg-pink-500/20',
    },
    {
      icon: <Sun className="w-7 h-7" />,
      title: 'إعادة الإضاءة الذكية',
      desc: 'ضبط زوايا الإضاءة والظلال لتبدو طبيعية 100% كأنها من استوديو احترافي',
      gradient: 'from-yellow-500 to-orange-500',
      glow: 'bg-yellow-500/20',
    },
    {
      icon: <Palette className="w-7 h-7" />,
      title: 'خلفيات تسويقية فاخرة',
      desc: 'توليد خلفيات واقعية تناسب الهوية التجارية — شاطئ، ستوديو، طاولة خشبية',
      gradient: 'from-purple-500 to-pink-500',
      glow: 'bg-purple-500/20',
    },
    {
      icon: <Camera className="w-7 h-7" />,
      title: 'تصوير افتراضي احترافي',
      desc: 'Product/Portrait Virtual Photography — لقطات تسويقية بجودة عالمية',
      gradient: 'from-cyan-500 to-blue-500',
      glow: 'bg-cyan-500/20',
    },
    {
      icon: <Layers className="w-7 h-7" />,
      title: 'معالجة بالجملة',
      desc: 'معالجة عشرات الصور دفعة واحدة — Bulk Processing فائق السرعة',
      gradient: 'from-green-500 to-emerald-500',
      glow: 'bg-green-500/20',
    },
    {
      icon: <Lock className="w-7 h-7" />,
      title: 'ملكية كاملة',
      desc: 'جميع الصور المعالجة ملكك — استخدمها تجارياً بدون قيود أو علامات مائية',
      gradient: 'from-indigo-500 to-purple-500',
      glow: 'bg-indigo-500/20',
    },
  ];

  return (
    <section id="features" className="py-24 px-4 relative">
      <div className="max-w-7xl mx-auto">
        <div className="text-center mb-16">
          <div className="inline-flex items-center gap-2 bg-pink-500/10 border border-pink-500/20 rounded-full px-5 py-2 mb-6">
            <Sparkles className="w-4 h-4 text-pink-400" />
            <span className="text-pink-300 text-sm font-medium">القدرات</span>
          </div>
          <h2 className="text-4xl md:text-6xl font-black text-white mb-4">
            استوديو صور <span className="bg-gradient-to-r from-pink-400 to-purple-400 bg-clip-text text-transparent">ذكي</span>
          </h2>
          <p className="text-gray-400 text-lg max-w-2xl mx-auto">
            6 قدرات أساسية لتعديل الصور وإنتاج لقطات تسويقية احترافية
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
      title: 'رفع الصورة',
      desc: 'ارفع صورة المنتج أو التصميم الخام عبر تليجرام أو واجهة الويب',
      color: 'from-pink-500 to-rose-500',
    },
    {
      num: '02',
      icon: <Scissors className="w-6 h-6" />,
      title: 'عزل وإزالة الخلفية',
      desc: 'مكتبة rembg تعزل المنتج بدقة مذهلة خلال ثانية واحدة',
      color: 'from-rose-500 to-red-500',
    },
    {
      num: '03',
      icon: <Brain className="w-6 h-6" />,
      title: 'توليد الخلفية والإضاءة',
      desc: 'Gemini/Hugging Face يولدان خلفية تسويقية فاخرة مع إضاءة واقعية',
      color: 'from-purple-500 to-pink-500',
    },
    {
      num: '04',
      icon: <Contrast className="w-6 h-6" />,
      title: 'الدمج والتعديل النهائي',
      desc: 'دمج المنتج في الخلفية مع ضبط الظلال والأبعاد بدقة',
      color: 'from-cyan-500 to-blue-500',
    },
    {
      num: '05',
      icon: <Download className="w-6 h-6" />,
      title: 'التسليم الفوري',
      desc: 'PNG عالي الدقة بخلفية شفافة أو إعلانية جاهز للاستخدام فوراً',
      color: 'from-green-500 to-emerald-500',
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
            من <span className="bg-gradient-to-r from-pink-400 to-rose-400 bg-clip-text text-transparent">صورة عادية</span> إلى <span className="bg-gradient-to-r from-purple-400 to-cyan-400 bg-clip-text text-transparent">لقطة احترافية</span>
          </h2>
          <p className="text-gray-400 text-lg max-w-2xl mx-auto">
            5 خطوات فقط — من رفع الصورة إلى النتيجة الاحترافية
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
  const [isProcessing, setIsProcessing] = useState(false);
  const [stage, setStage] = useState(0);
  const [logs, setLogs] = useState<string[]>([]);
  const [imageType, setImageType] = useState('product');

  const stages = [
    { status: 'uploading', color: 'text-pink-400', text: '📥 استلام الصورة: product_shot.jpg (2.4MB)...' },
    { status: 'analyzing', color: 'text-purple-400', text: '🔍 تحليل الصورة: اكتشاف المنتج، الأبعاد، الإضاءة...' },
    { status: 'removing', color: 'text-rose-400', text: '✂️ rembg يعزل المنتج عن الخلفية بدقة 99.8%...' },
    { status: 'generating', color: 'text-cyan-400', text: '🎨 Gemini يولد خلفية تسويقية: "طاولة خشبية أنيقة مع إضاءة ناعمة"' },
    { status: 'relighting', color: 'text-yellow-400', text: '💡 ضبط الإضاءة والظلال لتبدو طبيعية 100%...' },
    { status: 'merging', color: 'text-green-400', text: '🔗 دمج المنتج في الخلفية مع تحسين الجودة...' },
    { status: 'ready', color: 'text-emerald-400', text: '✨ الصورة الاحترافية جاهزة! PNG 4K بخلفية شفافة + نسخة إعلانية' },
  ];

  const handleStart = () => {
    setIsProcessing(true);
    setStage(0);
    setLogs([]);

    let currentStage = 0;
    const timer = setInterval(() => {
      currentStage++;
      setStage(currentStage);
      setLogs(prev => [...prev, stages[currentStage].text]);
      if (currentStage >= stages.length - 1) {
        clearInterval(timer);
        setTimeout(() => setIsProcessing(false), 2000);
      }
    }, 1200);
  };

  return (
    <section id="demo" className="py-24 px-4 relative">
      <div className="max-w-5xl mx-auto">
        <div className="text-center mb-12">
          <div className="inline-flex items-center gap-2 bg-cyan-500/10 border border-cyan-500/20 rounded-full px-5 py-2 mb-6">
            <Wand2 className="w-4 h-4 text-cyan-400" />
            <span className="text-cyan-300 text-sm font-medium">محاكاة حية</span>
          </div>
          <h2 className="text-4xl md:text-5xl font-black text-white mb-4">
            شاهد <span className="bg-gradient-to-r from-pink-400 to-cyan-400 bg-clip-text text-transparent">السحر يحدث</span>
          </h2>
          <p className="text-gray-400 text-lg">اختر نوع الصورة وشاهد كيف يعمل النظام</p>
        </div>

        <div className="bg-white/[0.03] border border-white/10 rounded-3xl overflow-hidden">
          {/* Input */}
          <div className="p-6 border-b border-white/10">
            <div className="grid grid-cols-3 gap-3 mb-4">
              {[
                { id: 'product', label: 'منتج', icon: <Box className="w-4 h-4" /> },
                { id: 'portrait', label: 'شخص', icon: <Eye className="w-4 h-4" /> },
                { id: 'design', label: 'تصميم', icon: <Palette className="w-4 h-4" /> },
              ].map((type) => (
                <button
                  key={type.id}
                  onClick={() => setImageType(type.id)}
                  className={`flex items-center justify-center gap-2 p-3 rounded-xl border transition-all ${
                    imageType === type.id
                      ? 'bg-pink-500/20 border-pink-500/50 text-pink-300'
                      : 'bg-white/5 border-white/10 text-gray-400 hover:border-white/20'
                  }`}
                >
                  {type.icon}
                  <span className="text-sm font-medium">{type.label}</span>
                </button>
              ))}
            </div>
          </div>

          {/* Terminal Header */}
          <div className="bg-gray-900/50 border-b border-white/10 px-4 py-3 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-red-500"></div>
              <div className="w-3 h-3 rounded-full bg-yellow-500"></div>
              <div className="w-3 h-3 rounded-full bg-green-500"></div>
            </div>
            <span className="text-xs text-gray-500 font-mono">pixel-zerobaran ~ processing</span>
            <Terminal className="w-4 h-4 text-gray-500" />
          </div>

          {/* Terminal Body */}
          <div className="p-6 font-mono text-sm min-h-[300px]">
            {logs.length === 0 ? (
              <div className="text-gray-500">
                <p>$ pixel-process --type {imageType} --output professional</p>
                <p className="mt-2 text-gray-600">Press the button to start live processing simulation...</p>
              </div>
            ) : (
              <div className="space-y-2">
                {logs.map((log, i) => (
                  <div key={i} className={`flex items-start gap-2 animate-fade-in ${stages[i].color}`}>
                    <span className="text-gray-600 text-xs mt-0.5">[{new Date().toLocaleTimeString('en-US', { hour12: false })}]</span>
                    <span>{log}</span>
                  </div>
                ))}
                {isProcessing && (
                  <div className="flex items-center gap-2 text-gray-500">
                    <div className="w-2 h-4 bg-pink-400 animate-pulse"></div>
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Control */}
          <div className="border-t border-white/10 p-4 bg-gray-900/30">
            <button
              onClick={handleStart}
              disabled={isProcessing}
              className="w-full bg-gradient-to-r from-pink-600 to-purple-600 text-white px-6 py-3 rounded-xl font-bold hover:shadow-lg hover:shadow-pink-500/30 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              {isProcessing ? (
                <>
                  <RefreshCw className="w-5 h-5 animate-spin" />
                  جاري المعالجة...
                </>
              ) : (
                <>
                  <Wand2 className="w-5 h-5" />
                  ابدأ المعالجة السحرية
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
      icon: <Github className="w-6 h-6" />,
      name: 'GitHub Actions',
      role: 'محرك التشغيل السحابي',
      desc: 'خادم مجاني لتنفيذ عمليات المعالجة المجدولة',
      color: 'from-gray-600 to-gray-700',
    },
    {
      icon: <Scissors className="w-6 h-6" />,
      name: 'Python + rembg',
      role: 'محرك إزالة الخلفيات',
      desc: 'عزل الخلفيات بدقة مذهلة ومجانية بالكامل',
      color: 'from-pink-600 to-rose-600',
    },
    {
      icon: <Brain className="w-6 h-6" />,
      name: 'Gemini / Hugging Face',
      role: 'العقل البصري',
      desc: 'توليد خلفيات واقعية وإضاءة احترافية بالذكاء',
      color: 'from-purple-600 to-pink-600',
    },
    {
      icon: <Cloud className="w-6 h-6" />,
      name: 'Supabase Storage',
      role: 'الأرشيف والتخزين',
      desc: 'حفظ الصور الأصلية والمعالجة وربطها بالمستخدمين',
      color: 'from-green-600 to-emerald-600',
    },
    {
      icon: <Send className="w-6 h-6" />,
      name: 'Telegram Bot API',
      role: 'قناة الاستقبال والتسليم',
      desc: 'إرسال الصور واستلام النتائج الاحترافية فوراً',
      color: 'from-sky-600 to-blue-600',
    },
    {
      icon: <Cpu className="w-6 h-6" />,
      name: 'OpenCV + Pillow',
      role: 'معالجة الصور',
      desc: 'تعديل الأبعاد، تحسين الجودة، وتجهيز الصور محلياً',
      color: 'from-cyan-600 to-teal-600',
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
            <span className="bg-gradient-to-r from-green-400 to-cyan-400 bg-clip-text text-transparent">The Free Tech Stack</span>
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
              <p className="text-xs text-pink-400 font-medium mb-2">{tech.role}</p>
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
      desc: 'استئجار استوديو أو اشتراكات أدوات التعديل تكلف آلاف الدولارات — هنا بالمجان',
      color: 'text-green-400',
      bg: 'bg-green-500/10',
    },
    {
      icon: <Zap className="w-7 h-7" />,
      title: 'السرعة والإنتاج الفوري',
      desc: 'معالجة عشرات الصور خلال ثوانٍ معدودة — Bulk Processing فائق',
      color: 'text-yellow-400',
      bg: 'bg-yellow-500/10',
    },
    {
      icon: <Camera className="w-7 h-7" />,
      title: 'الجودة والواقعية',
      desc: 'دمج المنتجات في بيئات طبيعية مع ظلال وإضاءة متوافقة تماماً',
      color: 'text-pink-400',
      bg: 'bg-pink-500/10',
    },
    {
      icon: <Lock className="w-7 h-7" />,
      title: 'بدون خبرة تصميم',
      desc: 'لا حاجة لبرامج معقدة — بضغطة زر واحدة تحصل على نتيجة احترافية',
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
            <span className="text-yellow-300 text-sm font-medium">لماذا Pixel-Zero؟</span>
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
    { name: 'PolyGlot-StreamBaran', desc: 'منظومة الترجمة والدبلجة الصوتية', icon: <Focus className="w-5 h-5" />, gradient: 'from-blue-500 to-cyan-500' },
    { name: 'AIOps-ZeroBaran', desc: 'المهندس الرقمي لإدارة الخوادم', icon: <Cpu className="w-5 h-5" />, gradient: 'from-emerald-500 to-blue-500' },
    { name: 'Lead-Sniper ZeroBaran', desc: 'منظومة صيد العملاء الذكية', icon: <Move className="w-5 h-5" />, gradient: 'from-orange-500 to-red-500' },
    { name: 'Spatial-ZeroBaran', desc: 'استوديو توليد المجسمات 3D', icon: <Hexagon className="w-5 h-5" />, gradient: 'from-pink-500 to-purple-500' },
    { name: 'Data-Nexus ZeroBaran', desc: 'منظومة تحليل وهندسة البيانات', icon: <Aperture className="w-5 h-5" />, gradient: 'from-cyan-500 to-blue-500' },
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
          <div className="inline-flex items-center gap-2 bg-pink-500/10 border border-pink-500/20 rounded-full px-5 py-2 mb-6">
            <Mail className="w-4 h-4 text-pink-400" />
            <span className="text-pink-300 text-sm font-medium">تواصل معنا</span>
          </div>
          <h2 className="text-4xl md:text-6xl font-black text-white mb-4">
            جاهز <span className="bg-gradient-to-r from-pink-400 to-purple-400 bg-clip-text text-transparent">لصور احترافية؟</span>
          </h2>
          <p className="text-gray-400 text-lg">تواصل معنا واحصل على استوديو الصور الذكي اليوم</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-5 mb-10">
          <a href="mailto:baranavisat@gmail.com" className="group bg-white/[0.03] border border-white/10 rounded-2xl p-6 text-center hover:border-pink-500/30 transition-all hover:-translate-y-1">
            <div className="w-14 h-14 rounded-xl bg-pink-500/10 flex items-center justify-center text-pink-400 mx-auto mb-4 group-hover:scale-110 transition-transform">
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

          <a href="https://baranavi.gumroad.com/" target="_blank" rel="noopener noreferrer" className="group bg-white/[0.03] border border-white/10 rounded-2xl p-6 text-center hover:border-cyan-500/30 transition-all hover:-translate-y-1">
            <div className="w-14 h-14 rounded-xl bg-cyan-500/10 flex items-center justify-center text-cyan-400 mx-auto mb-4 group-hover:scale-110 transition-transform">
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
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-pink-500 via-purple-500 to-cyan-500 flex items-center justify-center">
                <Aperture className="w-5 h-5 text-white" />
              </div>
              <div>
                <span className="font-black text-white text-sm sm:text-base block leading-none">Pixel-Zero</span>
                <span className="text-[10px] text-pink-400 font-medium tracking-widest">BARAN</span>
              </div>
            </div>
            <p className="text-gray-500 text-sm max-w-md leading-relaxed">
              استوديو تعديل ومعالجة الصور والتصميم الذاتي اللامركزي — صورك الاحترافية بضغطة زر واحدة وبالمجان.
            </p>
          </div>

          <div>
            <h4 className="font-bold text-white mb-4 text-sm">روابط</h4>
            <ul className="space-y-2">
              <li><a href="#features" className="text-gray-500 hover:text-pink-400 text-sm transition-colors">المميزات</a></li>
              <li><a href="#how-it-works" className="text-gray-500 hover:text-pink-400 text-sm transition-colors">آلية العمل</a></li>
              <li><a href="#demo" className="text-gray-500 hover:text-pink-400 text-sm transition-colors">تجربة حية</a></li>
              <li><a href="#tech" className="text-gray-500 hover:text-pink-400 text-sm transition-colors">التقنيات</a></li>
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
            © 2025 Pixel-ZeroBaran — Baran Avisat. جميع الحقوق محفوظة.
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
    <div className="min-h-screen bg-[#0a0510] text-white" dir="rtl" style={{ fontFamily: "'Tajawal', sans-serif" }}>
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
