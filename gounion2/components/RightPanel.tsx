
import React from 'react';
import { Search, TrendingUp, UserPlus, Sparkles } from 'lucide-react';
import { MOCK_USERS } from '../constants';

interface RightPanelProps { insights: string[]; loadingInsights: boolean; }

const RightPanel: React.FC<RightPanelProps> = ({ insights, loadingInsights }) => {
  return (
    <aside className="fixed right-0 top-0 h-screen w-80 xl:w-96 bg-[#0a0a0c] border-l border-white/5 z-40 hidden xl:flex flex-col py-10 px-8">
      
      {/* Search Bar */}
      <div className="relative mb-8 group">
        <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-zinc-500 group-focus-within:text-[#c4ff0e] transition-colors" />
        <input 
          type="text" 
          placeholder="Find peers or projects..." 
          className="w-full h-12 pl-12 pr-4 bg-white/5 border border-white/10 rounded-2xl text-xs font-bold outline-none focus:border-[#c4ff0e]/50 focus:bg-white/10 transition-all text-white placeholder:text-zinc-600"
        />
      </div>

      {/* University Spotlight */}
      <div className="glass-card p-6 rounded-[32px] mb-8 relative overflow-hidden group">
        <div className="absolute top-0 right-0 w-32 h-32 bg-[#c4ff0e]/10 blur-[50px] -mr-10 -mt-10" />
        <div className="flex items-center gap-2 text-[10px] font-black uppercase text-[#c4ff0e] tracking-widest mb-4">
            <TrendingUp className="w-3 h-3"/> Stanford Campus
        </div>
        <h3 className="text-xl font-black text-white mb-6">Stanford Hub</h3>
        <div className="grid grid-cols-2 gap-4 text-center">
            <div className="p-3 bg-white/5 rounded-2xl border border-white/5">
                <div className="text-lg font-black text-white">4.5k</div>
                <div className="text-[8px] font-bold text-zinc-500 uppercase">Scholars</div>
            </div>
            <div className="p-3 bg-[#c4ff0e]/10 rounded-2xl border border-[#c4ff0e]/10">
                <div className="text-lg font-black text-[#c4ff0e]">12</div>
                <div className="text-[8px] font-bold text-[#c4ff0e]/70 uppercase">Live Now</div>
            </div>
        </div>
      </div>

      {/* Quick Tips / Insights */}
      <div className="mb-8">
        <div className="flex items-center gap-2 mb-6 text-zinc-500 uppercase tracking-widest text-[10px] font-black">
          <Sparkles className="w-4 h-4 text-[#c4ff0e]" /> Smart Tips
        </div>
        <div className="space-y-4">
          {loadingInsights ? (
            <div className="animate-pulse space-y-3">
              <div className="h-16 bg-white/5 rounded-2xl" />
              <div className="h-16 bg-white/5 rounded-2xl" />
            </div>
          ) : (
            insights.map((insight, idx) => (
              <div key={idx} className="p-4 bg-white/5 rounded-2xl border border-transparent hover:border-white/10 transition-all cursor-pointer">
                <p className="text-xs text-zinc-400 font-medium leading-relaxed italic">
                  "{insight}"
                </p>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Recommended for You */}
      <div>
        <h4 className="text-[10px] font-black uppercase tracking-widest text-zinc-500 mb-6">Peers you may know</h4>
        <div className="space-y-5">
          {MOCK_USERS.map(user => (
            <div key={user.id} className="flex items-center gap-4 group cursor-pointer hover:translate-x-1 transition-transform">
              <div className="w-10 h-10 rounded-full border border-white/10 overflow-hidden shrink-0">
                <img src={user.avatar} className="w-full h-full object-cover" />
              </div>
              <div className="min-w-0">
                <h5 className="text-xs font-bold text-white truncate group-hover:text-[#c4ff0e] transition-colors">{user.name}</h5>
                <p className="text-[9px] font-medium text-zinc-500 truncate uppercase">{user.course}</p>
              </div>
              <button className="ml-auto p-2 bg-white/5 rounded-xl hover:bg-[#c4ff0e] hover:text-black transition-all">
                <UserPlus className="w-4 h-4" />
              </button>
            </div>
          ))}
        </div>
      </div>

      <footer className="mt-auto pt-8 flex flex-wrap gap-4 text-[9px] font-bold text-zinc-600 uppercase tracking-widest">
        <a href="#" className="hover:text-white transition-colors">Privacy</a>
        <a href="#" className="hover:text-white transition-colors">Safety</a>
        <a href="#" className="hover:text-white transition-colors">University Guide</a>
      </footer>
    </aside>
  );
};

export default RightPanel;
