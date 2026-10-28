import { useState, useEffect, useRef } from 'react';
import {
  Zap, Eye, Palette, Send, Bot, Cpu, Layers, Rocket,
  Mail, Phone, Globe, Shield, Clock, Sparkles,
  ArrowRight, CheckCircle, Star, Code, Image, Type,
  Share2, BarChart3, Workflow, Database, Cloud,
  Github, ExternalLink, Menu, X, ChevronDown,
  Monitor, Smartphone, ShoppingBag, Video, Music,
  FileText, Lock, Heart, Award, TrendingUp, Users,
  Play, ArrowUpRight, Hexagon, Triangle, Circle,
  Boxes, CpuIcon, Brain, Wand2, Paintbrush, Camera,
  Megaphone, Target, Lightbulb, Flame, Gem
} from 'lucide-react';

// ============ ANIMATED BACKGROUND ============
function AnimatedBackground() {
  return (
    <div className="fixed inset-0 -z-10 overflow-hidden">
      <div className="absolute inset-0 bg-[#050510]"></div>
      <div className="absolute top-0 left-1/4 w-[500px] h-[500px] bg-purple-600/10 rounded-full filter blur-[150px] animate-pulse"></div>
      <div className="absolute bottom-0 right-1/4 w-[500px] h-[500px] bg-cyan-600/10 rounded-full filter blur-[150px] animate-pulse" style={{ animationDelay: '2s' }}></div>
      <div className="absolute top-1/2 left-1/2 w-[400px] h-[400px] bg-pink-600/5 rounded-full filter blur-[120px] animate-pulse" style={{ animationDelay: '4s' }}></div>
      {/* Grid */}
      <div className="absolute inset-0 opacity-[0.03]" style={{
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
    { href: '#projects', label: 'المشاريع' },
    { href: '#capabilities', label: 'القدرات' },
    { href: '#tech', label: 'التقنيات' },
    { href: '#about', label: 'عن الاستوديو' },
    { href: '#contact', label: 'تواصل' },
  ];

  return (
    <nav className={`fixed top-0 left-0 right-0 z-50 transition-all duration-500 ${scrolled ? 'bg-[#050510]/80 backdrop-blur-2xl border-b border-white/5 shadow-2xl shadow-purple-500/5' : ''}`}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 py-4 flex items-center justify-between">
        <a href="#" className="flex items-center gap-3 group">
          <div className="relative">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-purple-500 via-pink-500 to-cyan-500 flex items-center justify-center group-hover:scale-110 transition-transform duration-300">
              <Hexagon className="w-5 h-5 text-white" />
            </div>
            <div className="absolute inset-0 rounded-xl bg-gradient-to-br from-purple-500 via-pink-500 to-cyan-500 blur-lg opacity-50 group-hover:opacity-80 transition-opacity"></div>
          </div>
          <div>
            <span className="font-black text-white text-lg block leading-none">Studio</span>
            <span className="text-[10px] text-purple-400 font-medium tracking-widest">ZEROBARAN</span>
          </div>
        </a>

        <div className="hidden md:flex items-center gap-1">
          {links.map((link) => (
            <a key={link.href} href={link.href} className="text-gray-400 hover:text-white transition-colors text-sm font-medium px-4 py-2 rounded-lg hover:bg-white/5">
              {link.label}
            </a>
          ))}
          <a
            href="https://baranavi.gumroad.com/"
            target="_blank"
            rel="noopener noreferrer"
            className="mr-2 bg-gradient-to-r from-purple-600 to-pink-600 text-white px-5 py-2.5 rounded-xl text-sm font-bold hover:shadow-lg hover:shadow-purple-500/30 transition-all flex items-center gap-2"
          >
            <ShoppingBag className="w-4 h-4" />
            المتجر
          </a>
        </div>

        <button onClick={() => setIsOpen(!isOpen)} className="md:hidden text-white p-2">
          {isOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
        </button>
      </div>

      {isOpen && (
        <div className="md:hidden bg-[#050510]/95 backdrop-blur-2xl border-b border-white/5 px-4 py-4 space-y-1">
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
  const [count, setCount] = useState({ projects: 0, tools: 0, designs: 0 });

  useEffect(() => {
    const targets = { projects: 12, tools: 8, designs: 1000 };
    const duration = 2000;
    const steps = 60;
    const interval = duration / steps;
    let step = 0;

    const timer = setInterval(() => {
      step++;
      const progress = step / steps;
      setCount({
        projects: Math.floor(targets.projects * progress),
        tools: Math.floor(targets.tools * progress),
        designs: Math.floor(targets.designs * progress),
      });
      if (step >= steps) clearInterval(timer);
    }, interval);

    return () => clearInterval(timer);
  }, []);

  return (
    <section className="relative min-h-screen flex items-center justify-center overflow-hidden pt-20">
      <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 py-20">
        <div className="text-center">
          {/* Badge */}
          <div className="inline-flex items-center gap-2 bg-white/5 border border-white/10 rounded-full px-5 py-2.5 mb-8 backdrop-blur-sm">
            <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
            <span className="text-gray-300 text-sm font-medium">نظام أتمتة ذكي — يعمل 24/7</span>
          </div>

          {/* Main Title */}
          <h1 className="text-5xl sm:text-6xl md:text-7xl lg:text-8xl font-black text-white mb-6 tracking-tight leading-[1.1]">
            نصمم مشاريع
            <br />
            <span className="relative inline-block">
              <span className="bg-gradient-to-r from-purple-400 via-pink-400 to-cyan-400 bg-clip-text text-transparent">
                لا مثيل لها
              </span>
              <svg className="absolute -bottom-2 left-0 w-full" height="8" viewBox="0 0 200 8" fill="none">
                <path d="M0 4C50 0 150 8 200 4" stroke="url(#grad)" strokeWidth="3" strokeLinecap="round"/>
                <defs>
                  <linearGradient id="grad" x1="0" y1="0" x2="200" y2="0">
                    <stop offset="0%" stopColor="#a855f7"/>
                    <stop offset="50%" stopColor="#ec4899"/>
                    <stop offset="100%" stopColor="#06b6d4"/>
                  </linearGradient>
                </defs>
              </svg>
            </span>
          </h1>

          <p className="text-lg md:text-xl text-gray-400 mb-10 max-w-3xl mx-auto leading-relaxed">
            استوديو إنتاج مرئي وإعلاني ذاتي يعتمد على <span className="text-purple-400 font-semibold">8+ نماذج ذكاء اصطناعي مجانية</span> لتوليد مشاريع احترافية كاملة — من الفكرة إلى المنتج النهائي
          </p>

          {/* CTA */}
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center mb-16">
            <a href="#projects" className="group relative bg-gradient-to-r from-purple-600 to-pink-600 text-white px-8 py-4 rounded-2xl font-bold text-lg hover:shadow-2xl hover:shadow-purple-500/30 transition-all duration-300 flex items-center gap-3">
              <Sparkles className="w-5 h-5" />
              استكشف المشاريع
              <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
              <div className="absolute inset-0 rounded-2xl bg-gradient-to-r from-purple-600 to-pink-600 blur-xl opacity-50 group-hover:opacity-80 transition-opacity -z-10"></div>
            </a>
            <a href="https://baranavi.gumroad.com/" target="_blank" rel="noopener noreferrer" className="border border-white/10 text-gray-300 px-8 py-4 rounded-2xl font-bold text-lg hover:border-purple-500/50 hover:text-white transition-all duration-300 flex items-center gap-2 backdrop-blur-sm">
              <ShoppingBag className="w-5 h-5" />
              زيارة المتجر
            </a>
          </div>

          {/* Stats */}
          <div className="grid grid-cols-3 gap-4 max-w-2xl mx-auto">
            {[
              { num: count.projects, suffix: '+', label: 'مشروع متكامل', color: 'text-purple-400' },
              { num: count.tools, suffix: '+', label: 'أداة ذكاء اصطناعي', color: 'text-pink-400' },
              { num: count.designs, suffix: '+', label: 'تصميم مولّد', color: 'text-cyan-400' },
            ].map((stat, i) => (
              <div key={i} className="bg-white/5 border border-white/10 rounded-2xl p-4 backdrop-blur-sm">
                <div className={`text-3xl md:text-4xl font-black ${stat.color}`}>
                  {stat.num}{stat.suffix}
                </div>
                <div className="text-xs md:text-sm text-gray-500 mt-1">{stat.label}</div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}

// ============ PROJECT CARD ============
interface Project {
  id: number;
  title: string;
  titleEn: string;
  description: string;
  category: string;
  icon: React.ReactNode;
  gradient: string;
  glowColor: string;
  features: string[];
  status: 'live' | 'beta' | 'coming';
}

function ProjectCard({ project, onClick }: { project: Project; onClick: () => void }) {
  return (
    <div
      onClick={onClick}
      className="group relative bg-white/[0.03] border border-white/10 rounded-3xl p-6 cursor-pointer hover:border-white/20 transition-all duration-500 hover:-translate-y-2 overflow-hidden"
    >
      {/* Glow Effect */}
      <div className={`absolute -top-20 -right-20 w-40 h-40 ${project.glowColor} rounded-full filter blur-[80px] opacity-0 group-hover:opacity-100 transition-opacity duration-500`}></div>

      {/* Status Badge */}
      <div className="absolute top-4 left-4">
        {project.status === 'live' && (
          <span className="bg-green-500/20 text-green-400 text-[10px] font-bold px-2 py-1 rounded-full flex items-center gap-1">
            <span className="w-1.5 h-1.5 bg-green-400 rounded-full animate-pulse"></span>
            LIVE
          </span>
        )}
        {project.status === 'beta' && (
          <span className="bg-yellow-500/20 text-yellow-400 text-[10px] font-bold px-2 py-1 rounded-full">BETA</span>
        )}
        {project.status === 'coming' && (
          <span className="bg-purple-500/20 text-purple-400 text-[10px] font-bold px-2 py-1 rounded-full">SOON</span>
        )}
      </div>

      {/* Icon */}
      <div className={`w-16 h-16 rounded-2xl bg-gradient-to-br ${project.gradient} flex items-center justify-center text-white mb-5 group-hover:scale-110 group-hover:rotate-3 transition-all duration-500 shadow-lg`}>
        {project.icon}
      </div>

      {/* Content */}
      <h3 className="text-xl font-bold text-white mb-1 group-hover:text-transparent group-hover:bg-clip-text group-hover:bg-gradient-to-r group-hover:from-purple-400 group-hover:to-pink-400 transition-all">
        {project.title}
      </h3>
      <p className="text-xs text-gray-500 font-mono mb-3">{project.titleEn}</p>
      <p className="text-gray-400 text-sm mb-4 line-clamp-2">{project.description}</p>

      {/* Features */}
      <div className="flex flex-wrap gap-1.5 mb-4">
        {project.features.slice(0, 3).map((f, i) => (
          <span key={i} className="text-[10px] bg-white/5 text-gray-400 px-2 py-1 rounded-md border border-white/5">
            {f}
          </span>
        ))}
      </div>

      {/* Footer */}
      <div className="flex items-center justify-between pt-4 border-t border-white/5">
        <span className="text-xs text-gray-500">{project.category}</span>
        <div className="flex items-center gap-1 text-purple-400 text-sm font-medium group-hover:gap-2 transition-all">
          التفاصيل
          <ArrowUpRight className="w-4 h-4" />
        </div>
      </div>
    </div>
  );
}

// ============ PROJECTS SECTION ============
function ProjectsSection() {
  const [selectedProject, setSelectedProject] = useState<Project | null>(null);

  const projects: Project[] = [
    {
      id: 1,
      title: 'Studio-ZeroBaran',
      titleEn: 'Visual Production Studio',
      description: 'منظومة أتمتة وإنتاج محتوى مرئي وإعلاني متكاملة — تأخذ فكرة وتولّد صور ونصوص وتصاميم احترافية',
      category: 'إنتاج مرئي',
      icon: <Palette className="w-7 h-7" />,
      gradient: 'from-purple-500 to-pink-500',
      glowColor: 'bg-purple-500/30',
      features: ['Gemini API', 'Hugging Face', 'Pillow', 'Auto-Publish'],
      status: 'live',
    },
    {
      id: 2,
      title: 'CryptoVault Pro',
      titleEn: 'Multi-Chain Wallet Manager',
      description: 'محفظة رقمية متعددة السلاسل تدعم EVM و Solana مع واجهة احترافية وتتبع المحفظة لحظياً',
      category: 'بلوكتشين',
      icon: <Gem className="w-7 h-7" />,
      gradient: 'from-cyan-500 to-blue-500',
      glowColor: 'bg-cyan-500/30',
      features: ['EVM', 'Solana', 'USDT', 'Real-time'],
      status: 'live',
    },
    {
      id: 3,
      title: 'AI Copywriter',
      titleEn: 'Marketing Copy Generator',
      description: 'مولّد نصوص تسويقية ذكي — يكتب إعلانات، أوصاف منتجات، ومنشورات سوشيال ميديا باحترافية',
      category: 'ذكاء اصطناعي',
      icon: <Brain className="w-7 h-7" />,
      gradient: 'from-pink-500 to-red-500',
      glowColor: 'bg-pink-500/30',
      features: ['Gemini', 'Groq', 'Multi-lang', 'SEO'],
      status: 'live',
    },
    {
      id: 4,
      title: 'DesignForge',
      titleEn: 'AI Design Generator',
      description: 'مصمم جرافيك آلي — يولّد شعارات، بوسترات، وMockups منتجات بدقة احترافية خلال ثوانٍ',
      category: 'تصميم',
      icon: <Paintbrush className="w-7 h-7" />,
      gradient: 'from-orange-500 to-yellow-500',
      glowColor: 'bg-orange-500/30',
      features: ['Flux', 'Stable Diffusion', 'SVG', 'Export'],
      status: 'beta',
    },
    {
      id: 5,
      title: 'SocialPilot',
      titleEn: 'Auto Social Media Manager',
      description: 'مدير سوشيال ميديا آلي — ينشر محتوى مجدول على جميع المنصات ويحلل الأداء',
      category: 'تسويق',
      icon: <Megaphone className="w-7 h-7" />,
      gradient: 'from-green-500 to-emerald-500',
      glowColor: 'bg-green-500/30',
      features: ['Scheduler', 'Analytics', 'Multi-platform', 'AI'],
      status: 'beta',
    },
    {
      id: 6,
      title: 'VideoGen Studio',
      titleEn: 'Short Video Generator',
      description: 'مولّد فيديوهات قصيرة — يحول النصوص والصور لفيديوهات Reels وTikTok احترافية',
      category: 'فيديو',
      icon: <Video className="w-7 h-7" />,
      gradient: 'from-red-500 to-pink-500',
      glowColor: 'bg-red-500/30',
      features: ['FFmpeg', 'AI Voice', 'Templates', '4K'],
      status: 'coming',
    },
    {
      id: 7,
      title: 'CodeMentor AI',
      titleEn: 'AI Code Assistant',
      description: 'مساعد برمجة ذكي — يكتب، يراجع، ويصحح الأكواد بأكثر من 20 لغة برمجة',
      category: 'برمجة',
      icon: <Code className="w-7 h-7" />,
      gradient: 'from-indigo-500 to-purple-500',
      glowColor: 'bg-indigo-500/30',
      features: ['20+ Languages', 'Debug', 'Refactor', 'Tests'],
      status: 'live',
    },
    {
      id: 8,
      title: 'DataPulse',
      titleEn: 'Real-time Analytics Dashboard',
      description: 'لوحة تحكم تحليلية لحظية — تعرض بيانات المبيعات والأداء مع رسوم بيانية تفاعلية',
      category: 'تحليلات',
      icon: <BarChart3 className="w-7 h-7" />,
      gradient: 'from-teal-500 to-cyan-500',
      glowColor: 'bg-teal-500/30',
      features: ['Real-time', 'Charts', 'Export', 'API'],
      status: 'live',
    },
    {
      id: 9,
      title: 'EcomBoost',
      titleEn: 'E-commerce Automation',
      description: 'أتمتة متاجر إلكترونية — إدارة المنتجات، الطلبات، والعملاء بذكاء اصطناعي',
      category: 'تجارة',
      icon: <ShoppingBag className="w-7 h-7" />,
      gradient: 'from-amber-500 to-orange-500',
      glowColor: 'bg-amber-500/30',
      features: ['Auto-listing', 'Pricing AI', 'Inventory', 'Reports'],
      status: 'beta',
    },
    {
      id: 10,
      title: 'SecureVault',
      titleEn: 'Password & Secrets Manager',
      description: 'مدير كلمات مرور آمن — تشفير محلي كامل مع مزامنة مشفرة بين الأجهزة',
      category: 'أمان',
      icon: <Lock className="w-7 h-7" />,
      gradient: 'from-slate-500 to-gray-600',
      glowColor: 'bg-slate-500/30',
      features: ['AES-256', 'Zero-knowledge', 'Sync', '2FA'],
      status: 'live',
    },
    {
      id: 11,
      title: 'MusicLab AI',
      titleEn: 'AI Music & Sound Generator',
      description: 'مولّد موسيقى ومؤثرات صوتية — ينتج موسيقى خلفية وأصوات فريدة بدون حقوق ملكية',
      category: 'صوتيات',
      icon: <Music className="w-7 h-7" />,
      gradient: 'from-violet-500 to-purple-500',
      glowColor: 'bg-violet-500/30',
      features: ['Royalty-free', 'Custom', 'Stems', 'WAV/MP3'],
      status: 'coming',
    },
    {
      id: 12,
      title: 'DocuFlow',
      titleEn: 'Smart Document Processor',
      description: 'معالج مستندات ذكي — يستخرج البيانات من PDF والصور ويحوّلها لقواعد بيانات منظمة',
      category: 'إنتاجية',
      icon: <FileText className="w-7 h-7" />,
      gradient: 'from-blue-500 to-indigo-500',
      glowColor: 'bg-blue-500/30',
      features: ['OCR', 'PDF', 'Tables', 'Export'],
      status: 'live',
    },
  ];

  return (
    <section id="projects" className="py-24 px-4 relative">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-16">
          <div className="inline-flex items-center gap-2 bg-purple-500/10 border border-purple-500/20 rounded-full px-5 py-2 mb-6">
            <Flame className="w-4 h-4 text-purple-400" />
            <span className="text-purple-300 text-sm font-medium">معرض المشاريع</span>
          </div>
          <h2 className="text-4xl md:text-6xl font-black text-white mb-4">
            مشاريع <span className="bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">عظيمة</span>
          </h2>
          <p className="text-gray-400 text-lg max-w-2xl mx-auto">
            12 مشروعاً احترافياً كاملاً — كل واحد مصمم ليكون الأفضل في مجاله
          </p>
        </div>

        {/* Projects Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-5">
          {projects.map((project) => (
            <ProjectCard key={project.id} project={project} onClick={() => setSelectedProject(project)} />
          ))}
        </div>
      </div>

      {/* Project Detail Modal */}
      {selectedProject && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center p-4" onClick={() => setSelectedProject(null)}>
          <div className="absolute inset-0 bg-black/80 backdrop-blur-sm"></div>
          <div className="relative bg-[#0a0a1a] border border-white/10 rounded-3xl max-w-lg w-full p-8 max-h-[90vh] overflow-y-auto" onClick={(e) => e.stopPropagation()}>
            <button onClick={() => setSelectedProject(null)} className="absolute top-4 left-4 text-gray-500 hover:text-white transition-colors">
              <X className="w-6 h-6" />
            </button>

            <div className={`w-20 h-20 rounded-2xl bg-gradient-to-br ${selectedProject.gradient} flex items-center justify-center text-white mb-6 shadow-2xl`}>
              {selectedProject.icon}
            </div>

            <h3 className="text-2xl font-black text-white mb-1">{selectedProject.title}</h3>
            <p className="text-sm text-gray-500 font-mono mb-4">{selectedProject.titleEn}</p>
            <p className="text-gray-400 mb-6">{selectedProject.description}</p>

            <div className="mb-6">
              <h4 className="text-white font-bold mb-3">المميزات:</h4>
              <div className="grid grid-cols-2 gap-2">
                {selectedProject.features.map((f, i) => (
                  <div key={i} className="flex items-center gap-2 bg-white/5 rounded-lg px-3 py-2">
                    <CheckCircle className="w-4 h-4 text-green-400 shrink-0" />
                    <span className="text-sm text-gray-300">{f}</span>
                  </div>
                ))}
              </div>
            </div>

            <div className="flex items-center justify-between pt-4 border-t border-white/10">
              <span className="text-xs text-gray-500 bg-white/5 px-3 py-1 rounded-full">{selectedProject.category}</span>
              <a href="https://baranavi.gumroad.com/" target="_blank" rel="noopener noreferrer" className="bg-gradient-to-r from-purple-600 to-pink-600 text-white px-5 py-2 rounded-xl text-sm font-bold flex items-center gap-2">
                <ShoppingBag className="w-4 h-4" />
                احصل عليه
              </a>
            </div>
          </div>
        </div>
      )}
    </section>
  );
}

// ============ AI MODELS SECTION ============
function AIModelsSection() {
  const models = [
    { name: 'Google Gemini', type: 'نصوص + رؤية', color: 'from-blue-500 to-cyan-500', desc: 'صياغة نصوص تسويقية وتحليل صور' },
    { name: 'Groq (Llama)', type: 'نصوص فائقة السرعة', color: 'from-orange-500 to-red-500', desc: 'توليد محتوى نصي بسرعة خارقة' },
    { name: 'Hugging Face', type: 'توليد صور', color: 'from-yellow-500 to-orange-500', desc: 'Flux & Stable Diffusion للصور' },
    { name: 'Stable Diffusion', type: 'صور احترافية', color: 'from-purple-500 to-pink-500', desc: 'توليد صور بدقة 4K' },
    { name: 'FLUX.1', type: 'صور واقعية', color: 'from-pink-500 to-rose-500', desc: 'أحدث نموذج لتوليد الصور الواقعية' },
    { name: 'Whisper', type: 'تحويل صوت لنص', color: 'from-green-500 to-emerald-500', desc: 'تفريغ الصوتيات بدقة عالية' },
    { name: 'Bark', type: 'توليد صوت', color: 'from-indigo-500 to-blue-500', desc: 'تحويل النص لكلام طبيعي' },
    { name: 'Real-ESRGAN', type: 'تحسين جودة', color: 'from-teal-500 to-cyan-500', desc: 'رفع دقة الصور 4x بالذكاء' },
  ];

  return (
    <section id="capabilities" className="py-24 px-4 relative">
      <div className="max-w-7xl mx-auto">
        <div className="text-center mb-16">
          <div className="inline-flex items-center gap-2 bg-cyan-500/10 border border-cyan-500/20 rounded-full px-5 py-2 mb-6">
            <Brain className="w-4 h-4 text-cyan-400" />
            <span className="text-cyan-300 text-sm font-medium">أسطول الذكاء الاصطناعي</span>
          </div>
          <h2 className="text-4xl md:text-6xl font-black text-white mb-4">
            <span className="bg-gradient-to-r from-cyan-400 to-blue-400 bg-clip-text text-transparent">8+ نماذج</span> تحت القيادة
          </h2>
          <p className="text-gray-400 text-lg max-w-2xl mx-auto">
            كل هذه النماذج مجانية وتعمل معاً بتناغم لإنتاج مشاريع عظيمة
          </p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {models.map((model, i) => (
            <div key={i} className="group bg-white/[0.03] border border-white/10 rounded-2xl p-5 hover:border-white/20 transition-all duration-300 hover:-translate-y-1">
              <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${model.color} flex items-center justify-center text-white mb-4 group-hover:scale-110 transition-transform`}>
                <Cpu className="w-5 h-5" />
              </div>
              <h4 className="font-bold text-white mb-1">{model.name}</h4>
              <p className="text-xs text-purple-400 font-medium mb-2">{model.type}</p>
              <p className="text-xs text-gray-500">{model.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

// ============ TECH STACK SECTION ============
function TechStackSection() {
  const techs = [
    { icon: <Github className="w-5 h-5" />, name: 'GitHub Actions', cat: 'أتمتة' },
    { icon: <Brain className="w-5 h-5" />, name: 'Gemini API', cat: 'ذكاء' },
    { icon: <Image className="w-5 h-5" />, name: 'Hugging Face', cat: 'صور' },
    { icon: <Palette className="w-5 h-5" />, name: 'Pillow', cat: 'تصميم' },
    { icon: <Database className="w-5 h-5" />, name: 'Supabase', cat: 'بيانات' },
    { icon: <Send className="w-5 h-5" />, name: 'Telegram Bot', cat: 'نشر' },
    { icon: <Cloud className="w-5 h-5" />, name: 'Vercel', cat: 'استضافة' },
    { icon: <Code className="w-5 h-5" />, name: 'React + Vite', cat: 'واجهة' },
    { icon: <Monitor className="w-5 h-5" />, name: 'Tailwind CSS', cat: 'تصميم' },
    { icon: <Cpu className="w-5 h-5" />, name: 'Groq API', cat: 'سرعة' },
    { icon: <Music className="w-5 h-5" />, name: 'Bark TTS', cat: 'صوت' },
    { icon: <Camera className="w-5 h-5" />, name: 'Real-ESRGAN', cat: 'جودة' },
  ];

  return (
    <section id="tech" className="py-24 px-4 relative">
      <div className="max-w-7xl mx-auto">
        <div className="text-center mb-16">
          <div className="inline-flex items-center gap-2 bg-green-500/10 border border-green-500/20 rounded-full px-5 py-2 mb-6">
            <Boxes className="w-4 h-4 text-green-400" />
            <span className="text-green-300 text-sm font-medium">كلها مجانية</span>
          </div>
          <h2 className="text-4xl md:text-6xl font-black text-white mb-4">
            التقنيات <span className="bg-gradient-to-r from-green-400 to-emerald-400 bg-clip-text text-transparent">المجانية</span>
          </h2>
          <p className="text-gray-400 text-lg">12+ أداة وتقنية — صفر تكاليف اشتراك</p>
        </div>

        <div className="flex flex-wrap justify-center gap-3">
          {techs.map((tech, i) => (
            <div key={i} className="group flex items-center gap-3 bg-white/[0.03] border border-white/10 rounded-xl px-4 py-3 hover:border-green-500/30 transition-all hover:-translate-y-0.5">
              <div className="text-green-400">{tech.icon}</div>
              <div>
                <p className="text-sm font-bold text-white">{tech.name}</p>
                <p className="text-[10px] text-gray-500">{tech.cat}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

// ============ ABOUT SECTION ============
function AboutSection() {
  return (
    <section id="about" className="py-24 px-4 relative">
      <div className="max-w-5xl mx-auto">
        <div className="bg-gradient-to-br from-white/[0.05] to-white/[0.02] border border-white/10 rounded-3xl p-8 md:p-12 relative overflow-hidden">
          {/* Decorative */}
          <div className="absolute -top-20 -right-20 w-60 h-60 bg-purple-500/10 rounded-full filter blur-[80px]"></div>
          <div className="absolute -bottom-20 -left-20 w-60 h-60 bg-cyan-500/10 rounded-full filter blur-[80px]"></div>

          <div className="relative z-10">
            <div className="flex items-center gap-2 mb-6">
              <Award className="w-5 h-5 text-yellow-400" />
              <span className="text-yellow-400 text-sm font-medium">عن الاستوديو</span>
            </div>

            <h2 className="text-3xl md:text-5xl font-black text-white mb-6 leading-tight">
              نصنع المستقبل
              <br />
              <span className="bg-gradient-to-r from-purple-400 via-pink-400 to-cyan-400 bg-clip-text text-transparent">بأيدينا</span>
            </h2>

            <div className="space-y-4 text-gray-400 leading-relaxed text-lg">
              <p>
                <span className="text-white font-bold">Studio-ZeroBaran</span> هو استوديو إنتاج مرئي وإعلاني ذاتي ولا مركزي، يجمع بين قوة <span className="text-purple-400">8+ نماذج ذكاء اصطناعي مجانية</span> لإنتاج مشاريع كاملة واحترافية.
              </p>
              <p>
                فلسفتنا بسيطة: <span className="text-cyan-400 font-semibold">لا تدفع اشتراكات باهظة</span> — استخدم الموارد المجانية بذكاء، وستحصل على نتائج تفوق المدفوعة.
              </p>
              <p>
                كل مشروع نصممه هنا هو <span className="text-pink-400 font-semibold">نظام متكامل</span> — ليس مجرد أداة واحدة، بل منظومة تعمل بتناغم لإنتاج محتوى لا مثيل له.
              </p>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-10">
              {[
                { icon: <Heart className="w-5 h-5" />, label: 'شغف', value: '∞' },
                { icon: <Target className="w-5 h-5" />, label: 'دقة', value: '100%' },
                { icon: <TrendingUp className="w-5 h-5" />, label: 'نمو', value: '24/7' },
                { icon: <Users className="w-5 h-5" />, label: 'رضا', value: '⭐⭐⭐⭐⭐' },
              ].map((item, i) => (
                <div key={i} className="bg-white/5 rounded-xl p-4 text-center border border-white/5">
                  <div className="text-purple-400 flex justify-center mb-2">{item.icon}</div>
                  <div className="text-white font-bold text-lg">{item.value}</div>
                  <div className="text-gray-500 text-xs">{item.label}</div>
                </div>
              ))}
            </div>
          </div>
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
            <Lightbulb className="w-4 h-4 text-pink-400" />
            <span className="text-pink-300 text-sm font-medium">لنبدأ مشروعك</span>
          </div>
          <h2 className="text-4xl md:text-6xl font-black text-white mb-4">
            جاهز <span className="bg-gradient-to-r from-pink-400 to-purple-400 bg-clip-text text-transparent">للانطلاق؟</span>
          </h2>
          <p className="text-gray-400 text-lg">تواصل معنا الآن وحوّل فكرتك لمشروع عظيم</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-5 mb-10">
          <a href="mailto:baranavisat@gmail.com" className="group bg-white/[0.03] border border-white/10 rounded-2xl p-6 text-center hover:border-purple-500/30 transition-all hover:-translate-y-1">
            <div className="w-14 h-14 rounded-xl bg-purple-500/10 flex items-center justify-center text-purple-400 mx-auto mb-4 group-hover:scale-110 transition-transform">
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

          <a href="https://baranavi.gumroad.com/" target="_blank" rel="noopener noreferrer" className="group bg-white/[0.03] border border-white/10 rounded-2xl p-6 text-center hover:border-pink-500/30 transition-all hover:-translate-y-1">
            <div className="w-14 h-14 rounded-xl bg-pink-500/10 flex items-center justify-center text-pink-400 mx-auto mb-4 group-hover:scale-110 transition-transform">
              <ShoppingBag className="w-6 h-6" />
            </div>
            <h4 className="font-bold text-white mb-1">المتجر</h4>
            <p className="text-gray-400 text-sm">baranavi.gumroad.com</p>
          </a>
        </div>

        {/* Payment Methods */}
        <div className="bg-white/[0.03] border border-white/10 rounded-2xl p-8">
          <h3 className="text-xl font-bold text-white text-center mb-6 flex items-center justify-center gap-2">
            <Shield className="w-5 h-5 text-green-400" />
            طرق الدفع المتاحة
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-white/5 rounded-xl p-5 text-center border border-white/5">
              <div className="text-3xl mb-3">🏦</div>
              <h4 className="font-bold text-white text-sm mb-1">تحويل بنكي</h4>
              <p className="text-gray-500 text-xs">ليرة تركية / دولار أمريكي</p>
            </div>
            <div className="bg-white/5 rounded-xl p-5 text-center border border-white/5">
              <div className="text-3xl mb-3">₿</div>
              <h4 className="font-bold text-white text-sm mb-1">بيتكوين</h4>
              <p className="text-gray-500 text-xs">دفع آمن ومباشر</p>
            </div>
            <div className="bg-white/5 rounded-xl p-5 text-center border border-white/5">
              <div className="text-3xl mb-3">💎</div>
              <h4 className="font-bold text-white text-sm mb-1">USDT / Crypto</h4>
              <p className="text-gray-500 text-xs">عملات رقمية متنوعة</p>
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
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-purple-500 via-pink-500 to-cyan-500 flex items-center justify-center">
                <Hexagon className="w-5 h-5 text-white" />
              </div>
              <div>
                <span className="font-black text-white text-lg block leading-none">Studio</span>
                <span className="text-[10px] text-purple-400 font-medium tracking-widest">ZEROBARAN</span>
              </div>
            </div>
            <p className="text-gray-500 text-sm max-w-md leading-relaxed">
              استوديو الإنتاج المرئي والإعلاني الذاتي واللامركزي — نصمم مشاريع عظيمة لا مثيل لها باستخدام الذكاء الاصطناعي المجاني.
            </p>
          </div>

          <div>
            <h4 className="font-bold text-white mb-4 text-sm">روابط</h4>
            <ul className="space-y-2">
              <li><a href="#projects" className="text-gray-500 hover:text-purple-400 text-sm transition-colors">المشاريع</a></li>
              <li><a href="#capabilities" className="text-gray-500 hover:text-purple-400 text-sm transition-colors">القدرات</a></li>
              <li><a href="#tech" className="text-gray-500 hover:text-purple-400 text-sm transition-colors">التقنيات</a></li>
              <li><a href="#contact" className="text-gray-500 hover:text-purple-400 text-sm transition-colors">تواصل</a></li>
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
            © 2025 Studio-ZeroBaran — Baran Avisat. جميع الحقوق محفوظة.
          </p>
          <div className="flex items-center gap-2 text-gray-600 text-xs">
            <span>صُنع بـ</span>
            <Heart className="w-3 h-3 text-red-500 fill-red-500" />
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
    <div className="min-h-screen bg-[#050510] text-white" dir="rtl" style={{ fontFamily: "'Tajawal', sans-serif" }}>
      <AnimatedBackground />
      <Navbar />
      <HeroSection />
      <ProjectsSection />
      <AIModelsSection />
      <TechStackSection />
      <AboutSection />
      <ContactSection />
      <Footer />
    </div>
  );
}
