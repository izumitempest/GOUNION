import React, { useState, useEffect } from 'react';
import { motion } from 'motion/react';
import { 
  ArrowRight, 
  Download, 
  MessageSquare, 
  Users, 
  Globe, 
  ShieldAlert, 
  GraduationCap,
  Menu,
  X,
  Smartphone,
  Zap
} from 'lucide-react';

export default function App() {
  const [isScrolled, setIsScrolled] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 50);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return (
    <div className="min-h-screen bg-[var(--color-bg)] text-[var(--color-ink)] selection:bg-[var(--color-accent)] selection:text-[var(--color-bg)]">
      {/* Navigation */}
      <nav className={`fixed top-0 w-full z-50 transition-all duration-300 ${isScrolled ? 'bg-[var(--color-bg)]/80 backdrop-blur-md brutal-border-b' : 'bg-transparent'}`}>
        <div className="max-w-7xl mx-auto px-6 h-20 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-[var(--color-accent)] rounded-sm flex items-center justify-center">
              <Zap className="w-5 h-5 text-[var(--color-bg)]" />
            </div>
            <span className="font-display font-bold text-xl tracking-tight">GoUnion</span>
          </div>
          
          <div className="hidden md:flex items-center gap-8 text-sm font-medium">
            <a href="#features" className="hover:text-[var(--color-accent)] transition-colors">Features</a>
            <a href="#preview" className="hover:text-[var(--color-accent)] transition-colors">Preview</a>
            <a href="https://gounion-frontend.onrender.com" className="hover:text-[var(--color-accent)] transition-colors">Web App</a>
            <a href="#download" className="bg-[var(--color-ink)] text-[var(--color-bg)] px-5 py-2.5 rounded-full hover:bg-[var(--color-accent)] transition-colors flex items-center gap-2">
              <Download className="w-4 h-4" />
              Download APK
            </a>
          </div>

          <button className="md:hidden text-[var(--color-ink)]" onClick={() => setMobileMenuOpen(!mobileMenuOpen)}>
            {mobileMenuOpen ? <X /> : <Menu />}
          </button>
        </div>
      </nav>

      {/* Mobile Menu */}
      {mobileMenuOpen && (
        <div className="fixed inset-0 z-40 bg-[var(--color-bg)] pt-24 px-6 md:hidden">
          <div className="flex flex-col gap-6 text-2xl font-display">
            <a href="#features" onClick={() => setMobileMenuOpen(false)}>Features</a>
            <a href="#preview" onClick={() => setMobileMenuOpen(false)}>Preview</a>
            <a href="https://gounion-frontend.onrender.com" onClick={() => setMobileMenuOpen(false)}>Web App</a>
            <a href="#download" onClick={() => setMobileMenuOpen(false)} className="text-[var(--color-accent)]">Download APK</a>
          </div>
        </div>
      )}

      {/* Hero */}
      <section className="pt-40 pb-20 px-6 max-w-7xl mx-auto relative">
        <div className="absolute top-1/4 right-10 w-96 h-96 bg-[var(--color-accent)]/10 rounded-full blur-[120px] -z-10"></div>
        <div className="absolute bottom-1/4 left-10 w-72 h-72 bg-blue-500/10 rounded-full blur-[100px] -z-10"></div>
        
        <div className="grid lg:grid-cols-2 gap-16 items-center">
          <div>
            <motion.div 
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
              className="inline-block border border-[var(--color-accent)]/30 text-[var(--color-accent)] px-4 py-1.5 rounded-full text-xs font-bold tracking-wider uppercase mb-8"
            >
              v1.0 is now live
            </motion.div>
            
            <motion.h1 
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.1 }}
              className="font-display text-6xl md:text-8xl font-bold leading-[0.9] tracking-tighter mb-8 text-balance"
            >
              THE CAMPUS <br/>
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-[var(--color-ink)] to-[var(--color-ink-muted)]">NETWORK.</span>
            </motion.h1>
            
            <motion.p 
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.2 }}
              className="text-xl text-[var(--color-ink-muted)] mb-10 max-w-lg text-balance leading-relaxed"
            >
              GoUnion connects your entire campus. Real-time chat, unfiltered stories, and alumni networking in one place. Drop the generic groups, join the union.
            </motion.p>
            
            <motion.div 
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.3 }}
              className="flex flex-col sm:flex-row gap-4"
            >
              <a href="#download" className="bg-[var(--color-accent)] text-[var(--color-bg)] px-8 py-4 rounded-full font-bold text-lg hover:bg-[var(--color-accent-hover)] transition-colors flex items-center justify-center gap-2">
                <Download className="w-5 h-5" />
                Download APK
              </a>
              <a href="https://gounion-frontend.onrender.com" className="brutal-border px-8 py-4 rounded-full font-bold text-lg hover:bg-[var(--color-surface)] transition-colors flex items-center justify-center gap-2">
                Open Web App
                <ArrowRight className="w-5 h-5" />
              </a>
            </motion.div>

            <motion.div 
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 1, delay: 0.6 }}
              className="mt-16 grid grid-cols-3 gap-8 pt-8 border-t border-[var(--color-ink)]/10"
            >
              <div>
                <div className="font-display text-3xl font-bold text-[var(--color-accent)]">15k+</div>
                <div className="text-sm text-[var(--color-ink-muted)] uppercase tracking-wider mt-1">Active Users</div>
              </div>
              <div>
                <div className="font-display text-3xl font-bold text-[var(--color-accent)]">&lt;50ms</div>
                <div className="text-sm text-[var(--color-ink-muted)] uppercase tracking-wider mt-1">Message Latency</div>
              </div>
              <div>
                <div className="font-display text-3xl font-bold text-[var(--color-accent)]">100%</div>
                <div className="text-sm text-[var(--color-ink-muted)] uppercase tracking-wider mt-1">Free Forever</div>
              </div>
            </motion.div>
          </div>
          
          <div className="relative hidden lg:block h-[700px]">
             <motion.div 
               initial={{ opacity: 0, scale: 0.9, rotate: 5 }}
               animate={{ opacity: 1, scale: 1, rotate: 0 }}
               transition={{ duration: 0.8, delay: 0.2, type: "spring" }}
               className="absolute top-10 right-10 w-[320px] h-[650px] bg-[var(--color-surface)] brutal-border rounded-[40px] p-2 shadow-2xl z-20"
             >
               <div className="w-full h-full rounded-[32px] overflow-hidden relative bg-black">
                 <img src="/screenshot-feed.png" alt="App Feed" className="w-full h-full object-cover opacity-80" />
                 <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-transparent"></div>
                 <div className="absolute bottom-8 left-6 right-6">
                    <div className="flex items-center gap-3 mb-4">
                      <div className="w-10 h-10 rounded-full bg-gray-300 overflow-hidden">
                        <img src="https://picsum.photos/seed/user1/100/100" alt="User" />
                      </div>
                      <div>
                        <div className="font-bold text-sm">Sarah Jenkins</div>
                        <div className="text-xs text-gray-400">Computer Science '25</div>
                      </div>
                    </div>
                    <p className="text-sm">Just finished the final project for CS401. Anyone up for coffee at the library cafe? ☕️</p>
                 </div>
               </div>
             </motion.div>
             
             <motion.div 
               initial={{ opacity: 0, scale: 0.9, rotate: -15 }}
               animate={{ opacity: 1, scale: 1, rotate: -10 }}
               transition={{ duration: 0.8, delay: 0.4, type: "spring" }}
               className="absolute top-32 left-0 w-[280px] h-[580px] bg-[var(--color-surface)] brutal-border rounded-[36px] p-2 shadow-2xl z-10"
             >
               <div className="w-full h-full rounded-[28px] overflow-hidden bg-black">
                 <img src="/screenshot-chat.png" alt="App Chat" className="w-full h-full object-cover opacity-50 grayscale" />
               </div>
             </motion.div>
          </div>
        </div>
      </section>

      {/* Features */}
      <section id="features" className="py-32 px-6 bg-[var(--color-surface)] relative">
        <div className="max-w-7xl mx-auto">
          <div className="mb-20 md:w-2/3">
            <h2 className="font-display text-5xl md:text-7xl font-bold tracking-tighter mb-6">EVERYTHING YOU NEED. <br/><span className="text-[var(--color-ink-muted)]">NOTHING YOU DON'T.</span></h2>
            <p className="text-xl text-[var(--color-ink-muted)]">Built specifically for the chaos and community of campus life.</p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            <FeatureCard 
              icon={<MessageSquare className="w-6 h-6" />}
              title="Real-time Messaging"
              desc="Lightning-fast WebSocket chat. Share media, voice notes, and files instantly without leaving the app."
              delay={0.1}
            />
            <FeatureCard 
              icon={<Users className="w-6 h-6" />}
              title="Campus Groups"
              desc="Create or join communities. From study groups to frat houses, complete with robust moderation tools."
              delay={0.2}
            />
            <FeatureCard 
              icon={<Smartphone className="w-6 h-6" />}
              title="Stories & Feed"
              desc="Share ephemeral stories or post to the infinite-scroll campus feed. See what's happening right now."
              delay={0.3}
            />
            <FeatureCard 
              icon={<Globe className="w-6 h-6" />}
              title="Global Search"
              desc="Find anyone, any post, or any group instantly. The entire campus directory in your pocket."
              delay={0.4}
            />
            <FeatureCard 
              icon={<ShieldAlert className="w-6 h-6" />}
              title="Admin & Moderation"
              desc="Keep communities safe with role management, content reports, and automated spam filters."
              delay={0.5}
            />
            <FeatureCard 
              icon={<GraduationCap className="w-6 h-6" />}
              title="Alumni Network"
              desc="Don't lose touch after graduation. Connect across departments and graduation years."
              delay={0.6}
            />
          </div>
        </div>
      </section>

      {/* App Preview */}
      <section id="preview" className="py-32 overflow-hidden">
        <div className="max-w-7xl mx-auto px-6 mb-16 flex justify-between items-end">
          <h2 className="font-display text-5xl md:text-7xl font-bold tracking-tighter">INSIDE <br/>THE UNION.</h2>
          <div className="hidden md:flex gap-4">
            <div className="w-12 h-12 rounded-full brutal-border flex items-center justify-center hover:bg-[var(--color-surface)] cursor-pointer">
              <ArrowRight className="w-5 h-5 rotate-180" />
            </div>
            <div className="w-12 h-12 rounded-full brutal-border flex items-center justify-center hover:bg-[var(--color-surface)] cursor-pointer">
              <ArrowRight className="w-5 h-5" />
            </div>
          </div>
        </div>
        
        <div className="flex gap-8 px-6 overflow-x-auto no-scrollbar pb-12 snap-x">
          {/* Spacer for first item alignment */}
          <div className="w-[10vw] shrink-0 hidden md:block"></div>
          
          <PreviewMockup src="/screenshot-feed.png" title="Campus Feed" />
          <PreviewMockup src="/screenshot-chat.png" title="Direct Messages" />
          
          {/* Spacer for last item alignment */}
          <div className="w-[10vw] shrink-0 hidden md:block"></div>
        </div>
      </section>

      {/* Download CTA */}
      <section id="download" className="py-32 px-6 bg-[var(--color-accent)] text-[var(--color-bg)] relative overflow-hidden">
        {/* Background typographic texture */}
        <div className="absolute inset-0 opacity-10 font-display font-black text-[20vw] leading-none whitespace-nowrap flex flex-col justify-center select-none pointer-events-none">
          <div className="-ml-20">DOWNLOAD DOWNLOAD</div>
          <div className="-ml-40">GOUNION GOUNION</div>
        </div>
        
        <div className="max-w-4xl mx-auto text-center relative z-10">
          <h2 className="font-display text-6xl md:text-8xl font-bold tracking-tighter mb-8">GET IT ON <br/>YOUR DEVICE.</h2>
          <p className="text-xl md:text-2xl font-medium mb-12 opacity-80">Join thousands of students already on the network.</p>
          
          <div className="flex flex-col sm:flex-row items-center justify-center gap-6">
            <a href="/GoUnion.apk" download className="bg-[var(--color-bg)] text-[var(--color-ink)] px-10 py-5 rounded-full font-bold text-xl hover:scale-105 transition-transform flex items-center gap-3 shadow-2xl">
              <Download className="w-6 h-6" />
              Download APK
            </a>
            <a href="https://gounion-frontend.onrender.com" className="bg-transparent border-2 border-[var(--color-bg)] text-[var(--color-bg)] px-10 py-5 rounded-full font-bold text-xl hover:bg-[var(--color-bg)] hover:text-[var(--color-ink)] transition-colors flex items-center gap-3">
              Open Web App
            </a>
          </div>
          
          <div className="mt-12 flex flex-wrap justify-center gap-8 text-sm font-bold uppercase tracking-wider opacity-70">
            <div>Version 1.0</div>
            <div>•</div>
            <div>Signed Release</div>
            <div>•</div>
            <div>Requires Android 8.0+</div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-12 px-6 border-t border-[var(--color-ink)]/10">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row justify-between items-center gap-6">
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 bg-[var(--color-ink)] rounded-sm flex items-center justify-center">
              <Zap className="w-3 h-3 text-[var(--color-bg)]" />
            </div>
            <span className="font-display font-bold text-lg tracking-tight">GoUnion</span>
          </div>
          
          <div className="flex gap-8 text-sm text-[var(--color-ink-muted)]">
            <a href="https://gounion-frontend.onrender.com" className="hover:text-[var(--color-ink)] transition-colors">Web App</a>
            <a href="mailto:support@gounion.app" className="hover:text-[var(--color-ink)] transition-colors">Contact</a>
            <a href="#" className="hover:text-[var(--color-ink)] transition-colors">Privacy Policy</a>
          </div>
          
          <div className="text-sm text-[var(--color-ink-muted)]">
            &copy; {new Date().getFullYear()} GoUnion Inc. All rights reserved.
          </div>
        </div>
      </footer>
    </div>
  );
}

function FeatureCard({ icon, title, desc, delay }: { icon: React.ReactNode, title: string, desc: string, delay: number }) {
  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: "-100px" }}
      transition={{ duration: 0.5, delay }}
      className="bg-[var(--color-bg)] brutal-border p-8 rounded-2xl hover:brutal-border-accent transition-colors group"
    >
      <div className="w-12 h-12 rounded-full bg-[var(--color-surface)] flex items-center justify-center mb-6 text-[var(--color-ink)] group-hover:bg-[var(--color-accent)] group-hover:text-[var(--color-bg)] transition-colors">
        {icon}
      </div>
      <h3 className="font-display text-2xl font-bold mb-3">{title}</h3>
      <p className="text-[var(--color-ink-muted)] leading-relaxed">{desc}</p>
    </motion.div>
  );
}

function PreviewMockup({ src, title }: { src: string, title: string }) {
  return (
    <div className="shrink-0 snap-center">
      <div className="w-[280px] md:w-[320px] h-[600px] md:h-[680px] bg-[var(--color-surface)] brutal-border rounded-[40px] p-2 shadow-2xl mb-6">
        <div className="w-full h-full rounded-[32px] overflow-hidden bg-black">
          <img src={src} alt={title} className="w-full h-full object-cover opacity-80 hover:opacity-100 transition-opacity duration-500" />
        </div>
      </div>
      <div className="text-center font-display font-bold text-xl uppercase tracking-widest">{title}</div>
    </div>
  );
}
