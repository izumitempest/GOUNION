
import React, { useState } from 'react';
import { Plus, UserPlus, Tags, Sparkles, Layers, Zap } from 'lucide-react';
import { MOCK_PROJECT_CALLS, CURRENT_USER } from '../constants';

const CollaborationHub: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'browse' | 'my-projects'>('browse');

  return (
    <div className="max-w-5xl mx-auto py-12 px-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 mb-12">
        <div>
          <h1 className="text-4xl font-black text-white tracking-tighter mb-2">Team Hub</h1>
          <p className="text-zinc-500 text-sm font-medium">Find students to team up with on exciting projects.</p>
        </div>
        <button className="h-14 px-8 bg-[#c4ff0e] text-black rounded-2xl font-black text-sm uppercase tracking-widest flex items-center justify-center gap-3 hover:opacity-90 transition-all shadow-[0_10px_30px_rgba(196,255,14,0.3)]">
          <Plus className="w-5 h-5" /> Start Project
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          {/* Stats Sidebar */}
          <div className="lg:col-span-4 space-y-6">
            <div className="glass-card p-8 rounded-[40px] border border-white/5 relative overflow-hidden group">
              <div className="absolute bottom-0 left-0 w-32 h-32 bg-purple-600/10 blur-[50px] -ml-10 -mb-10" />
              <h3 className="text-xs font-black uppercase text-zinc-500 mb-6 tracking-widest">Your Stack</h3>
              <div className="flex flex-wrap gap-2 mb-8">
                {CURRENT_USER.skills?.map(skill => (
                  <span key={skill} className="px-3 py-1.5 bg-white/5 border border-white/10 text-[10px] font-black uppercase text-white rounded-xl">
                    {skill}
                  </span>
                ))}
              </div>
              <button className="w-full py-4 bg-white/5 border border-dashed border-white/20 text-[10px] font-black uppercase text-zinc-400 rounded-2xl hover:border-[#c4ff0e] hover:text-[#c4ff0e] transition-all">
                Add New Skill
              </button>
            </div>

            <div className="p-8 bg-[#141417] border border-white/5 rounded-[40px]">
                <div className="flex items-center gap-2 text-[10px] font-black uppercase text-purple-400 mb-6 tracking-widest">
                    <Zap className="w-3 h-3"/> Active Teams
                </div>
                <div className="flex items-center gap-4 mb-4 p-4 bg-white/5 rounded-2xl border border-white/5">
                    <div className="w-10 h-10 bg-purple-500 rounded-xl flex items-center justify-center text-white font-bold">A</div>
                    <div>
                        <h4 className="text-xs font-bold text-white">AI Safety Club</h4>
                        <p className="text-[8px] font-bold text-zinc-500 uppercase">3 Active Tasks</p>
                    </div>
                </div>
            </div>
          </div>

          {/* Project Feed */}
          <div className="lg:col-span-8 space-y-8">
            <div className="flex gap-10 border-b border-white/5 mb-4">
              <button 
                onClick={() => setActiveTab('browse')}
                className={`pb-4 text-xs font-black uppercase tracking-widest relative transition-all ${activeTab === 'browse' ? 'text-white' : 'text-zinc-600'}`}
              >
                Discover
                {activeTab === 'browse' && <div className="absolute bottom-[-1px] left-0 right-0 h-1 bg-[#c4ff0e] rounded-full shadow-[0_0_10px_#c4ff0e]"></div>}
              </button>
              <button 
                onClick={() => setActiveTab('my-projects')}
                className={`pb-4 text-xs font-black uppercase tracking-widest relative transition-all ${activeTab === 'my-projects' ? 'text-white' : 'text-zinc-600'}`}
              >
                Managed
                {activeTab === 'my-projects' && <div className="absolute bottom-[-1px] left-0 right-0 h-1 bg-[#c4ff0e] rounded-full shadow-[0_0_10px_#c4ff0e]"></div>}
              </button>
            </div>

            <div className="space-y-6">
              {MOCK_PROJECT_CALLS.map(project => (
                <div key={project.id} className="glass-card p-8 rounded-[40px] group border border-white/5 hover:border-purple-500/30 transition-all">
                  <div className="flex justify-between items-start mb-6">
                    <div>
                        <div className="flex items-center gap-2 text-[8px] font-black uppercase text-zinc-500 tracking-widest mb-2">
                           <Sparkles className="w-3 h-3 text-[#c4ff0e]"/> Project Call
                        </div>
                        <h4 className="text-2xl font-black text-white group-hover:text-[#c4ff0e] transition-colors">{project.title}</h4>
                    </div>
                    <div className="text-[10px] font-bold text-zinc-600 uppercase">{project.timestamp}</div>
                  </div>

                  <p className="text-sm font-medium text-zinc-400 leading-relaxed mb-8">
                    {project.description}
                  </p>

                  <div className="p-6 bg-white/5 rounded-[32px] border border-white/5 mb-8">
                    <div className="flex items-center gap-2 text-[9px] font-black uppercase tracking-widest text-zinc-500 mb-4">
                      <Layers className="w-4 h-4" /> Skills to Master
                    </div>
                    <div className="flex flex-wrap gap-2">
                      {project.skillsNeeded.map(skill => (
                        <span key={skill} className="px-3 py-1.5 bg-black text-white border border-white/5 text-[9px] font-black uppercase rounded-lg">
                          {skill}
                        </span>
                      ))}
                    </div>
                  </div>

                  <div className="flex items-center justify-between pt-6 border-t border-white/5">
                    <div className="flex items-center gap-3">
                        <img src={project.creator.avatar} className="w-8 h-8 rounded-full border border-white/10" />
                        <span className="text-[10px] font-black uppercase text-white">{project.creator.name}</span>
                    </div>
                    <button className="px-6 py-3 bg-[#c4ff0e] text-black rounded-2xl text-[10px] font-black uppercase tracking-widest hover:scale-105 transition-all shadow-[0_10px_20px_rgba(196,255,14,0.1)] flex items-center gap-2">
                      <UserPlus className="w-4 h-4" /> Join Team
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
      </div>
    </div>
  );
};

export default CollaborationHub;
