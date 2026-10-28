import { useState, useEffect } from 'react';
import {
  Zap, Box, Image as ImageIcon, Paintbrush, Layers, Download,
  Mail, Phone, ShoppingBag, Clock, Sparkles,
  ArrowRight, Star, Code, Workflow, Database, Cloud,
  Github, ExternalLink, Menu, X, Hexagon, Brain, Cpu,
  ArrowUpRight, Terminal, Lock, Eye, Search,
  FileText, RefreshCw, DollarSign, Send,
  ChevronRight, BarChart3, Sparkle,
  Shield, MousePointer, EyeOff, Play,
  Rotate3D, Cuboid, Triangle, Circle, Square,
  Globe, Server, Target
} from 'lucide-react';

// ============ 3D ROTATING CUBE ============
function Cube3D() {
  return (
    <div className="relative w-32 h-32 md:w-48 md:h-48 perspective-1000">
      <div className="absolute inset-0 animate-spin-slow" style={{ 
        transformStyle: 'preserve-3d',
        animation: 'spin3d 8s linear infinite'
      }}>
        {/* Front */}
        <div className="absolute inset-0 bg-gradient-to-br from-purple-500/30 to-pink-500/30 border border-purple-400/50 backdrop-blur-sm"
          style={{ transform: 'translateZ(64px)' }}></div>
        {/* Back */}
        <div className="absolute inset-0 bg-gradient-to-br from-blue-500/30 to-cyan-500/30 border border-blue-400/50 backdrop-blur-sm"
          style={{ transform: 'translateZ(-64px) rotateY(180deg)' }}></div>
        {/* Left */}
        <div className="absolute inset-0 bg-gradient-to-br from-pink-500/30 to-red-500/30 border border-pink-400/50 backdrop-blur-sm"
          style={{ transform: 'translateX(-64px) rotateY(-90deg)' }}></div>
        {/* Right */}
        <div className="absolute inset-0 bg-gradient-to-br from-cyan-500/30 to-teal-500/30 border border-cyan-400/50 backdrop-blur-sm"
          style={{ transform: 'translateX(64px) rotateY(90deg)' }}></div>
        {/* Top */}
        <div className="absolute inset-0 bg-gradient-to-br from-purple-500/30 to-blue-500/30 border border-purple-400/50 backdrop-blur-sm"
          style={{ transform: 'translateY(-64px) rotateX(90deg)' }}></div>
        {/* Bottom */}
        <div className="absolute inset-0 bg-gradient-to-br from-pink-500/30 to-purple-500/30 border border-pink-400/50 backdrop-blur-sm"
          style={{ transform: 'translateY(64px) rotateX(-90deg)' }}></div>
      </div>
    </div>
  );
}

// ============ ANIMATED BACKGROUND ============
function AnimatedBackground() {
  return (
    <div className="fixed inset-0 -z-10 overflow-hidden">
      <div className="absolute inset-0 bg-[#0a0515]"></div>
      <div className="absolute top-0 left-1/4 w-[600px] h-[600px] bg-purple-600/10 rounded-full filter blur-[180px] animate-pulse"></div>
      <div className="absolute bottom-0 right-1/4 w-[600px] h-[600px] bg-pink-600/10 rounded-full filter blur-[180px] animate-pulse" style={{ animationDelay: '2s' }}></div>
      <div className="absolute top-1/2 left-1/2 w-[400px] h-[400px] bg-blue-600/8 rounded-full filter blur-[150px] animate-pulse" style={{ animationDelay: '4s' }}></div>
      <div className="absolute inset-0 opacity-[0.03]" style={{
        backgroundImage: 'linear-gradient(rgba(168,85,247,0.3) 1px, transparent 1px), linear-gradient(90deg, rgba(168,85,247,0.3) 1px, transparent 1px)',
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
    { href: '#demo', label: 'تجربة حية' },
    { href: '#tech', label: 'التقنيات' },
    { href: '#projects', label: 'مشاريع أخرى' },
    { href: '#contact', label: 'تواصل' },
  ];

  return (
    <nav className={`fixed top-0 left-0 right-0 z-50 transition-all duration-500 ${scrolled ? 'bg-[#0a0515]/80 backdrop-blur-2xl border-b border-white/5 shadow-2xl shadow-purple-500/5' : ''}`}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 py-4 flex items-center justify-between">
        <a href="#" className="flex items-center gap-3 group">
          <div className="relative">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-purple-500 via-pink-500 to-blue-500 flex items-center justify-center group-hover:scale-110 transition-transform duration-300">
              <Cuboid className="w-5 h-5 text-white" />
            </div>
            <div className="absolute inset-0 rounded-xl bg-gradient-to-br from-purple-500 via-pink-500 to-blue-500 blur-lg opacity-50 group-hover:opacity-80 transition-opacity"></div>
          </div>
          <div>
            <span className="font-black text-white text-sm sm:text-base block leading-none">Spatial</span>
            <span className="text-[10px] text-purple-400 font-medium tracking-widest">ZEROBARAN</span>
          </div>
        </a>

        <div className="hidden lg:flex items-center gap-1">
          {links.map((link) => (
            <a key={link.href} href={link.href} className="text-gray-400 hover:text-white transition-colors text-sm font-medium px-3 py-2 rounded-lg hover:bg-white/5">
              {link.label}
            </a>
          ))}
          <a href="https://baranavi.gumroad.com/" target="_blank" rel="noopener noreferrer" className="mr-2 bg-gradient-to-r from-purple-600 to-pink-600 text-white px-5 py-2.5 rounded-xl text-sm font-bold hover:shadow-lg hover:shadow-purple-500/30 transition-all flex items-center gap-2">
            <ShoppingBag className="w-4 h-4" />
            المتجر
          </a>
        </div>

        <button onClick={() => setIsOpen(!isOpen)} className="lg:hidden text-white p-2">
          {isOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
        </button>
      </div>

      {isOpen && (
        <div className="lg:hidden bg-[#0a0515]/95 backdrop-blur-2xl border-b border-white/5 px-4 py-4 space-y-1">
          {links.map((link) => (
            <a key={link.href} href={link.href} onClick={() => setIsOpen(false)} className="block text-gray-300 hover:text-white py-3 px-4 rounded-lg hover:bg-white/5">
              {link.label}
            </a>
          ))}
          <a href="https://baranavi.gumroad.com/" target="_blank" rel="noopener noreferrer" className="block bg-gradient-to-r from-purple-600 to-pink-600 text-white px-4 py-3 rounded-xl text-center font-bold mt-2">
            زيارة المتجر
          </a>
        </div>
      )}
    </nav>
  );
}

// ============ HERO SECTION ============
function HeroSection() {
  const [models, setModels] = useState(0);
  const [polygons, setPolygons] = useState(0);
  const [time, setTime] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setModels(prev => Math.min(prev + Math.floor(Math.random() * 5) + 1, 847));
      setPolygons(prev => Math.min(prev + Math.floor(Math.random() * 10000) + 1000, 2500000));
      setTime(prev => Math.min(prev + 0.1, 8.3));
    }, 100);
    return () => clearInterval(interval);
  }, []);

  return (
    <section className="relative min-h-screen flex items-center justify-center overflow-hidden pt-20">
      <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 py-20">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
          {/* Content */}
          <div>
            {/* Badge */}
            <div className="inline-flex items-center gap-2 bg-purple-500/10 border border-purple-500/20 rounded-full px-5 py-2.5 mb-8 backdrop-blur-sm">
              <div className="relative">
                <div className="w-2 h-2 bg-purple-400 rounded-full"></div>
                <div className="absolute inset-0 w-2 h-2 bg-purple-400 rounded-full animate-ping"></div>
              </div>
              <span className="text-gray-300 text-sm font-medium">توليد 3D On-Demand — مجاني بالكامل</span>
            </div>

            {/* Main Title */}
            <h1 className="text-4xl sm:text-5xl md:text-6xl font-black text-white mb-6 tracking-tight leading-[1.1]">
              حوّل أفكارك إلى
              <br />
              <span className="bg-gradient-to-r from-purple-400 via-pink-400 to-blue-400 bg-clip-text text-transparent">
                مجسمات 3D
              </span>
            </h1>

            <p className="text-lg md:text-xl text-gray-400 mb-10 leading-relaxed">
              منظومة أتمتة ذكية تحوّل <span className="text-purple-400 font-semibold">النصوص والصور إلى مجسمات ثلاثية الأبعاد</span> جاهزة للاستخدام في Unreal Engine و Unity و Blender — <span className="text-pink-400 font-semibold">بدون دفع دولار واحد</span>
            </p>

            {/* CTA */}
            <div className="flex flex-col sm:flex-row gap-4 mb-12">
              <a href="#demo" className="group relative bg-gradient-to-r from-purple-600 to-pink-600 text-white px-8 py-4 rounded-2xl font-bold text-lg hover:shadow-2xl hover:shadow-purple-500/30 transition-all duration-300 flex items-center gap-3">
                <Play className="w-5 h-5" />
                جرّب التوليد
                <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                <div className="absolute inset-0 rounded-2xl bg-gradient-to-r from-purple-600 to-pink-600 blur-xl opacity-50 group-hover:opacity-80 transition-opacity -z-10"></div>
              </a>
              <a href="https://baranavi.gumroad.com/" target="_blank" rel="noopener noreferrer" className="border border-white/10 text-gray-300 px-8 py-4 rounded-2xl font-bold text-lg hover:border-purple-500/50 hover:text-white transition-all duration-300 flex items-center gap-2 backdrop-blur-sm">
                <Download className="w-5 h-5" />
                احصل عليه
              </a>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-3 gap-4">
              <div className="bg-white/5 border border-white/10 rounded-2xl p-4 backdrop-blur-sm">
                <div className="text-2xl font-black text-purple-400">{models}</div>
                <div className="text-xs text-gray-500 mt-1">مجسم مولّد</div>
              </div>
              <div className="bg-white/5 border border-white/10 rounded-2xl p-4 backdrop-blur-sm">
                <div className="text-2xl font-black text-pink-400">{(polygons / 1000000).toFixed(1)}M</div>
                <div className="text-xs text-gray-500 mt-1">مضلع معالج</div>
              </div>
              <div className="bg-white/5 border border-white/10 rounded-2xl p-4 backdrop-blur-sm">
                <div className="text-2xl font-black text-blue-400">{time.toFixed(1)}s</div>
                <div className="text-xs text-gray-500 mt-1">زمن التوليد</div>
              </div>
            </div>
          </div>

          {/* 3D Cube Visual */}
          <div className="flex justify-center items-center">
            <div className="relative">
              <Cube3D />
              <div className="absolute inset-0 bg-gradient-to-r from-purple-500/20 to-pink-500/20 rounded-full blur-3xl"></div>
            </div>
          </div>
        </div>
      </div>

      <style>{`
        @keyframes spin3d {
          0% { transform: rotateX(0deg) rotateY(0deg); }
          100% { transform: rotateX(360deg) rotateY(360deg); }
        }
      `}</style>
    </section>
  );
}

// ============ FEATURES SECTION ============
function FeaturesSection() {
  const features = [
    {
      icon: <ImageIcon className="w-7 h-7" />,
      title: 'توليد من صور 2D',
      desc: 'حوّل أي صورة ثنائية الأبعاد إلى مجسم ثلاثي الأبعاد كامل خلال ثوانٍ',
      gradient: 'from-purple-500 to-pink-500',
      glow: 'bg-purple-500/20',
    },
    {
      icon: <Brain className="w-7 h-7" />,
      title: 'توليد من النصوص',
      desc: 'اكتب وصفاً نصياً مثل "كرسي فايكنج خشبي" واحصل على مجسم 3D جاهز',
      gradient: 'from-pink-500 to-red-500',
      glow: 'bg-pink-500/20',
    },
    {
      icon: <Layers className="w-7 h-7" />,
      title: 'تقليل المضلعات',
      desc: 'Decimation آلي لتخفيض حجم المجسم من 50MB إلى 2MB مع الحفاظ على التفاصيل',
      gradient: 'from-blue-500 to-cyan-500',
      glow: 'bg-blue-500/20',
    },
    {
      icon: <Paintbrush className="w-7 h-7" />,
      title: 'توليد الإكساءات',
      desc: 'إنشاء خرائط UV Mapping وإكساءات احترافية تلقائياً',
      gradient: 'from-cyan-500 to-teal-500',
      glow: 'bg-cyan-500/20',
    },
    {
      icon: <Box className="w-7 h-7" />,
      title: 'تصدير متعدد',
      desc: 'دعم صيغ GLB, OBJ, FBX — جاهزة للسحب والإسقاط في أي محرك ألعاب',
      gradient: 'from-orange-500 to-yellow-500',
      glow: 'bg-orange-500/20',
    },
    {
      icon: <Lock className="w-7 h-7" />,
      title: 'ملكية كاملة',
      desc: 'جميع المجسمات المولّدة ملكك — استخدمها تجارياً بدون قيود',
      gradient: 'from-green-500 to-emerald-500',
      glow: 'bg-green-500/20',
    },
  ];

  return (
    <section id="features" className="py-24 px-4 relative">
      <div className="max-w-7xl mx-auto">
        <div className="text-center mb-16">
          <div className="inline-flex items-center gap-2 bg-purple-500/10 border border-purple-500/20 rounded-full px-5 py-2 mb-6">
            <Sparkle className="w-4 h-4 text-purple-400" />
            <span className="text-purple-300 text-sm font-medium">القدرات</span>
          </div>
          <h2 className="text-4xl md:text-6xl font-black text-white mb-4">
            استوديو 3D <span className="bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">ذكي</span>
          </h2>
          <p className="text-gray-400 text-lg max-w-2xl mx-auto">
            6 قدرات أساسية لتوليد ومعالجة المجسمات ثلاثية الأبعاد
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
      icon: <Send className="w-6 h-6" />,
      title: 'إرسال الفكرة',
      desc: 'أرسل صورة أو وصفاً نصياً عبر تليجرام أو واجهة الويب',
      color: 'from-purple-500 to-pink-500',
    },
    {
      num: '02',
      icon: <Brain className="w-6 h-6" />,
      title: 'التوليد المبدئي',
      desc: 'TripoSR/Shap-E يولّد مجسم 3D خام بصيغة GLB/OBJ خلال 10 ثوانٍ',
      color: 'from-pink-500 to-red-500',
    },
    {
      num: '03',
      icon: <Cpu className="w-6 h-6" />,
      title: 'المعالجة الآلية',
      desc: 'Blender Headless يقلل المضلعات ويحسن الإكساء ويضغط الملف',
      color: 'from-blue-500 to-cyan-500',
    },
    {
      num: '04',
      icon: <Database className="w-6 h-6" />,
      title: 'التخزين',
      desc: 'رفع الملف النهائي إلى Supabase Storage مع معاينة GIF متحركة',
      color: 'from-cyan-500 to-teal-500',
    },
    {
      num: '05',
      icon: <Download className="w-6 h-6" />,
      title: 'التسليم',
      desc: 'رابط تنزيل مباشر على تليجرام — جاهز للسحب والإسقاط في مشروعك',
      color: 'from-green-500 to-emerald-500',
    },
  ];

  return (
    <section id="how-it-works" className="py-24 px-4 relative">
      <div className="max-w-6xl mx-auto">
        <div className="text-center mb-16">
          <div className="inline-flex items-center gap-2 bg-pink-500/10 border border-pink-500/20 rounded-full px-5 py-2 mb-6">
            <Workflow className="w-4 h-4 text-pink-400" />
            <span className="text-pink-300 text-sm font-medium">آلية العمل</span>
          </div>
          <h2 className="text-4xl md:text-6xl font-black text-white mb-4">
            من <span className="bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">الفكرة</span> إلى <span className="bg-gradient-to-r from-blue-400 to-cyan-400 bg-clip-text text-transparent">المجسم</span>
          </h2>
          <p className="text-gray-400 text-lg max-w-2xl mx-auto">
            5 خطوات فقط — من الصورة إلى المجسم الجاهز للاستخدام
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
  const [isGenerating, setIsGenerating] = useState(false);
  const [stage, setStage] = useState(0);
  const [logs, setLogs] = useState<string[]>([]);
  const [prompt, setPrompt] = useState('');

  const stages = [
    { status: 'receiving', color: 'text-purple-400', text: '📥 استلام الوصف: "كرسي خشبي قديم بأسلوب فايكنج"...' },
    { status: 'generating', color: 'text-pink-400', text: '🧠 TripoSR يولّد شبكة المجسم 3D الأولية...' },
    { status: 'mesh', color: 'text-blue-400', text: '✅ تم توليد المجسم: 12,847 مضلع | 48MB' },
    { status: 'processing', color: 'text-cyan-400', text: '⚙️ Blender Headless: تقليل المضلعات + UV Mapping...' },
    { status: 'optimizing', color: 'text-teal-400', text: '📦 الضغط: 48MB → 2.1MB (95.8% تقليل)' },
    { status: 'ready', color: 'text-green-400', text: '🎉 المجسم جاهز! 2,156 مضلع | 2.1MB | GLB' },
  ];

  const handleStart = () => {
    if (!prompt.trim()) return;
    setIsGenerating(true);
    setStage(0);
    setLogs([]);

    let currentStage = 0;
    const timer = setInterval(() => {
      currentStage++;
      setStage(currentStage);
      setLogs(prev => [...prev, stages[currentStage].text]);
      if (currentStage >= stages.length - 1) {
        clearInterval(timer);
        setTimeout(() => setIsGenerating(false), 2000);
      }
    }, 1200);
  };

  return (
    <section id="demo" className="py-24 px-4 relative">
      <div className="max-w-5xl mx-auto">
        <div className="text-center mb-12">
          <div className="inline-flex items-center gap-2 bg-pink-500/10 border border-pink-500/20 rounded-full px-5 py-2 mb-6">
            <Play className="w-4 h-4 text-pink-400" />
            <span className="text-pink-300 text-sm font-medium">محاكاة حية</span>
          </div>
          <h2 className="text-4xl md:text-5xl font-black text-white mb-4">
            جرّب <span className="bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">التوليد الآن</span>
          </h2>
          <p className="text-gray-400 text-lg">اكتب وصفاً وشاهد كيف يولّد النظام المجسم 3D</p>
        </div>

        <div className="bg-white/[0.03] border border-white/10 rounded-3xl overflow-hidden">
          {/* Input */}
          <div className="p-6 border-b border-white/10">
            <input
              type="text"
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder='مثال: "سيارة رياضية حمراء" أو "تنين خيالي"...'
              className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white placeholder-gray-600 focus:outline-none focus:border-purple-500 transition-colors"
              dir="rtl"
            />
          </div>

          {/* Terminal Header */}
          <div className="bg-gray-900/50 border-b border-white/10 px-4 py-3 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-red-500"></div>
              <div className="w-3 h-3 rounded-full bg-yellow-500"></div>
              <div className="w-3 h-3 rounded-full bg-green-500"></div>
            </div>
            <span className="text-xs text-gray-500 font-mono">spatial-zerobaran ~ generating</span>
            <Terminal className="w-4 h-4 text-gray-500" />
          </div>

          {/* Terminal Body */}
          <div className="p-6 font-mono text-sm min-h-[280px]">
            {logs.length === 0 ? (
              <div className="text-gray-500">
                <p>$ spatial-generate --prompt "your description"</p>
                <p className="mt-2 text-gray-600">Enter a description and press Generate...</p>
              </div>
            ) : (
              <div className="space-y-2">
                {logs.map((log, i) => (
                  <div key={i} className={`flex items-start gap-2 animate-fade-in ${stages[i].color}`}>
                    <span className="text-gray-600 text-xs mt-0.5">[{new Date().toLocaleTimeString('en-US', { hour12: false })}]</span>
                    <span>{log}</span>
                  </div>
                ))}
                {isGenerating && (
                  <div className="flex items-center gap-2 text-gray-500">
                    <div className="w-2 h-4 bg-purple-400 animate-pulse"></div>
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Control */}
          <div className="border-t border-white/10 p-4 bg-gray-900/30">
            <button
              onClick={handleStart}
              disabled={isGenerating || !prompt.trim()}
              className="w-full bg-gradient-to-r from-purple-600 to-pink-600 text-white px-6 py-3 rounded-xl font-bold hover:shadow-lg hover:shadow-purple-500/30 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              {isGenerating ? (
                <>
                  <RefreshCw className="w-5 h-5 animate-spin" />
                  جاري التوليد...
                </>
              ) : (
                <>
                  <Cuboid className="w-5 h-5" />
                  توليد المجسم 3D
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
      desc: 'خوادم مجانية GPU/CPU لمعالجة خوارزميات التوليد',
      color: 'from-gray-600 to-gray-700',
    },
    {
      icon: <Brain className="w-6 h-6" />,
      name: 'TripoSR / Shap-E',
      role: 'محرك التوليد 3D',
      desc: 'نماذج مفتوحة المصدر تحول الصورة/النص إلى مجسم GLB/OBJ',
      color: 'from-purple-600 to-pink-600',
    },
    {
      icon: <Cuboid className="w-6 h-6" />,
      name: 'Blender Headless',
      role: 'محرك المعالجة',
      desc: 'تشغيل بلندر بدون واجهة لتقليل المضلعات وتحسين الإكساء',
      color: 'from-orange-600 to-red-600',
    },
    {
      icon: <Database className="w-6 h-6" />,
      name: 'Supabase Storage',
      role: 'أرشيف المكتبة',
      desc: 'حفظ ملفات المجسمات والوصلات للرجوع والتنزيل',
      color: 'from-green-600 to-emerald-600',
    },
    {
      icon: <Send className="w-6 h-6" />,
      name: 'Telegram Bot',
      role: 'واجهة التحكم',
      desc: 'استقبال الأوامر وتوفير روابط تنزيل الأصول الجاهزة',
      color: 'from-sky-600 to-blue-600',
    },
    {
      icon: <Cloud className="w-6 h-6" />,
      name: 'Hugging Face Spaces',
      role: 'استضافة النماذج',
      desc: 'تشغيل نماذج AI المجانية على خوادم مجانية',
      color: 'from-yellow-600 to-orange-600',
    },
  ];

  return (
    <section id="tech" className="py-24 px-4 relative">
      <div className="max-w-7xl mx-auto">
        <div className="text-center mb-16">
          <div className="inline-flex items-center gap-2 bg-blue-500/10 border border-blue-500/20 rounded-full px-5 py-2 mb-6">
            <Code className="w-4 h-4 text-blue-400" />
            <span className="text-blue-300 text-sm font-medium">التقنيات المجانية</span>
          </div>
          <h2 className="text-4xl md:text-6xl font-black text-white mb-4">
            <span className="bg-gradient-to-r from-blue-400 to-cyan-400 bg-clip-text text-transparent">The Free Tech Stack</span>
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
              <p className="text-xs text-purple-400 font-medium mb-2">{tech.role}</p>
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
      title: 'توفير مالي هائل',
      desc: 'بناء مكتبة مجسمات احترافية يكلف آلاف الدولارات — هنا بالمجان',
      color: 'text-green-400',
      bg: 'bg-green-500/10',
    },
    {
      icon: <Clock className="w-7 h-7" />,
      title: 'تسريع خطوط الإنتاج',
      desc: 'اختصار أسابيع من النمذجة اليدوية إلى دقائق معدودة',
      color: 'text-purple-400',
      bg: 'bg-purple-500/10',
    },
    {
      icon: <Cpu className="w-7 h-7" />,
      title: 'أتمتة التنظيف',
      desc: 'تنظيف هيكلي وتحسين أداء المجسمات ليعمل بسلاسة على كافة الأجهزة',
      color: 'text-blue-400',
      bg: 'bg-blue-500/10',
    },
    {
      icon: <Lock className="w-7 h-7" />,
      title: 'ملكية تجارية كاملة',
      desc: 'استخدم المجسمات المولّدة في مشاريعك التجارية بدون قيود',
      color: 'text-pink-400',
      bg: 'bg-pink-500/10',
    },
  ];

  return (
    <section className="py-24 px-4 relative">
      <div className="max-w-6xl mx-auto">
        <div className="text-center mb-16">
          <div className="inline-flex items-center gap-2 bg-yellow-500/10 border border-yellow-500/20 rounded-full px-5 py-2 mb-6">
            <Star className="w-4 h-4 text-yellow-400" />
            <span className="text-yellow-300 text-sm font-medium">لماذا Spatial؟</span>
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
    { name: 'CryptoVault Pro', desc: 'محفظة رقمية متعددة السلاسل', icon: <Hexagon className="w-5 h-5" />, gradient: 'from-cyan-500 to-blue-500' },
    { name: 'AI Copywriter', desc: 'مولّد نصوص تسويقية ذكي', icon: <Brain className="w-5 h-5" />, gradient: 'from-pink-500 to-red-500' },
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
          <div className="inline-flex items-center gap-2 bg-purple-500/10 border border-purple-500/20 rounded-full px-5 py-2 mb-6">
            <Mail className="w-4 h-4 text-purple-400" />
            <span className="text-purple-300 text-sm font-medium">تواصل معنا</span>
          </div>
          <h2 className="text-4xl md:text-6xl font-black text-white mb-4">
            جاهز <span className="bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">للإبداع ثلاثي الأبعاد؟</span>
          </h2>
          <p className="text-gray-400 text-lg">تواصل معنا واحصل على استوديو 3D الذكي اليوم</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-5 mb-10">
          <a href="mailto:baranavisat@gmail.com" className="group bg-white/[0.03] border border-white/10 rounded-2xl p-6 text-center hover:border-purple-500/30 transition-all hover:-translate-y-1">
            <div className="w-14 h-14 rounded-xl bg-purple-500/10 flex items-center justify-center text-purple-400 mx-auto mb-4 group-hover:scale-110 transition-transform">
              <Mail className="w-6 h-6" />
            </div>
            <h4 className="font-bold text-white mb-1">البريد الإلكتروني</h4>
            <p className="text-gray-400 text-sm break-all">baranavisat@gmail.com</p>
          </a>

          <a href="tel:+905313263722" className="group bg-white/[0.03] border border-white/10 rounded-2xl p-6 text-center hover:border-pink-500/30 transition-all hover:-translate-y-1">
            <div className="w-14 h-14 rounded-xl bg-pink-500/10 flex items-center justify-center text-pink-400 mx-auto mb-4 group-hover:scale-110 transition-transform">
              <Phone className="w-6 h-6" />
            </div>
            <h4 className="font-bold text-white mb-1">الهاتف / واتساب</h4>
            <p className="text-gray-400 text-sm" dir="ltr">+90 531 326 3722</p>
          </a>

          <a href="https://baranavi.gumroad.com/" target="_blank" rel="noopener noreferrer" className="group bg-white/[0.03] border border-white/10 rounded-2xl p-6 text-center hover:border-blue-500/30 transition-all hover:-translate-y-1">
            <div className="w-14 h-14 rounded-xl bg-blue-500/10 flex items-center justify-center text-blue-400 mx-auto mb-4 group-hover:scale-110 transition-transform">
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
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-purple-500 via-pink-500 to-blue-500 flex items-center justify-center">
                <Cuboid className="w-5 h-5 text-white" />
              </div>
              <div>
                <span className="font-black text-white text-sm sm:text-base block leading-none">Spatial</span>
                <span className="text-[10px] text-purple-400 font-medium tracking-widest">ZEROBARAN</span>
              </div>
            </div>
            <p className="text-gray-500 text-sm max-w-md leading-relaxed">
              الاستوديو الذاتي لتوليد ومعالجة المجسمات ثلاثية الأبعاد — حوّل أفكارك إلى مجسمات 3D جاهزة للاستخدام بالمجان.
            </p>
          </div>

          <div>
            <h4 className="font-bold text-white mb-4 text-sm">روابط</h4>
            <ul className="space-y-2">
              <li><a href="#features" className="text-gray-500 hover:text-purple-400 text-sm transition-colors">المميزات</a></li>
              <li><a href="#how-it-works" className="text-gray-500 hover:text-purple-400 text-sm transition-colors">آلية العمل</a></li>
              <li><a href="#demo" className="text-gray-500 hover:text-purple-400 text-sm transition-colors">تجربة حية</a></li>
              <li><a href="#tech" className="text-gray-500 hover:text-purple-400 text-sm transition-colors">التقنيات</a></li>
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
            © 2025 Spatial-ZeroBaran — Baran Avisat. جميع الحقوق محفوظة.
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
    <div className="min-h-screen bg-[#0a0515] text-white" dir="rtl" style={{ fontFamily: "'Tajawal', sans-serif" }}>
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
