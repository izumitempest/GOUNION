
import React, { useState } from 'react';
import { UserCheck, Search, Star, MessageSquare, Video, ShieldCheck, Filter, ArrowRight } from 'lucide-react';
import { MOCK_USERS } from '../constants';

const MentorshipProgram: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [activeMentorshipTab, setActiveMentorshipTab] = useState<'browse' | 'requests'>('browse');

  const mentors = MOCK_USERS.filter(u => u.isMentor);

  return (
    <div className="max-w-4xl mx-auto py-12 px-6">
      <div className="mb-10">
        <h1 className="text-4xl font-black text-white tracking-tighter mb-2">Mentor Network</h1>
        <p className="text-zinc-500 text-sm font-medium">Connect with top-tier seniors and alumni for exclusive guidance.</p>
      </div>

      <div className="flex gap-4 mb-8">
        <button 
          onClick={() => setActiveMentorshipTab('browse')}
          className={`flex-1 py-4 rounded-2xl font-black text-xs uppercase tracking-widest transition-all border-2 ${activeMentorshipTab === 'browse' ? 'bg-[#c4ff0e] text-black border-[#c4ff0e] shadow-[0_10px_20px_rgba(196,255,14,0.2)]' : 'bg-white/5 text-zinc-500 border-white/5 hover:border-white/10'}`}
        >
          Discover Mentors
        </button>
        <button 
          onClick={() => setActiveMentorshipTab('requests')}
          className={`flex-1 py-4 rounded-2xl font-black text-xs uppercase tracking-widest transition-all border-2 ${activeMentorshipTab === 'requests' ? 'bg-[#c4ff0e] text-black border-[#c4ff0e] shadow-[0_10px_20px_rgba(196,255,14,0.2)]' : 'bg-white/5 text-zinc-500 border-white/5 hover:border-white/10'}`}
        >
          My Sessions
        </button>
      </div>

      {activeMentorshipTab === 'browse' ? (
        <div className="space-y-8">
          <div className="relative group">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-zinc-500 group-focus-within:text-[#c4ff0e] transition-colors" />
            <input 
              type="text" 
              placeholder="Search expertise (e.g. 'LLMs', 'UI/UX', 'Law')..." 
              className="w-full h-14 pl-12 pr-4 bg-white/5 border border-white/10 rounded-2xl text-sm font-bold outline-none focus:border-[#c4ff0e]/50 focus:bg-white/10 transition-all text-white placeholder:text-zinc-600"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {mentors.map((mentor) => (
              <div key={mentor.id} className="glass-card rounded-[40px] p-8 border border-white/5 hover:border-[#c4ff0e]/30 transition-all group">
                <div className="flex items-start gap-5 mb-6">
                  <div className="relative">
                    <div className="w-20 h-20 rounded-3xl story-ring p-[2px]">
                      <div className="w-full h-full rounded-3xl border-2 border-black overflow-hidden">
                        <img src={mentor.avatar} className="w-full h-full object-cover" alt={mentor.name} />
                      </div>
                    </div>
                    <div className="absolute -bottom-1 -right-1 bg-[#c4ff0e] p-1.5 rounded-xl shadow-lg border-2 border-black">
                      <ShieldCheck className="w-4 h-4 text-black" />
                    </div>
                  </div>
                  <div className="flex-1 min-w-0 pt-1">
                    <h4 className="font-black text-white text-xl group-hover:text-[#c4ff0e] transition-colors truncate">{mentor.name}</h4>
                    <p className="text-[10px] font-bold text-zinc-500 uppercase tracking-widest mt-1">{mentor.university}</p>
                    <div className="flex items-center gap-1.5 mt-2">
                      <Star className="w-3.5 h-3.5 text-[#c4ff0e] fill-[#c4ff0e]" />
                      <span className="text-xs font-black text-white">4.9</span>
                      <span className="text-[10px] text-zinc-500 font-bold uppercase ml-1">24 Reviews</span>
                    </div>
                  </div>
                </div>

                <div className="mb-8">
                  <div className="text-[9px] font-black text-zinc-500 uppercase tracking-widest mb-3">Core Expertise</div>
                  <div className="flex flex-wrap gap-2">
                    {mentor.expertise?.map(exp => (
                      <span key={exp} className="px-3 py-1.5 bg-white/5 border border-white/10 text-[#c4ff0e] text-[9px] font-black uppercase rounded-xl">
                        {exp}
                      </span>
                    ))}
                  </div>
                </div>

                <div className="flex gap-3">
                  <button className="flex-1 h-12 bg-white/5 hover:bg-white/10 text-white rounded-2xl font-black text-[10px] uppercase tracking-widest transition-all flex items-center justify-center gap-2">
                    <MessageSquare className="w-4 h-4" /> Message
                  </button>
                  <button className="flex-1 h-12 bg-[#c4ff0e] text-black rounded-2xl font-black text-[10px] uppercase tracking-widest transition-all flex items-center justify-center gap-2 shadow-[0_5px_15px_rgba(196,255,14,0.1)] hover:scale-[1.02]">
                    <Video className="w-4 h-4" /> Book Call
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      ) : (
        <div className="text-center py-24 glass-card rounded-[48px] border-2 border-dashed border-white/5">
          <div className="w-20 h-20 bg-white/5 rounded-full flex items-center justify-center mx-auto mb-6">
            <UserCheck className="w-10 h-10 text-zinc-600" />
          </div>
          <h3 className="text-xl font-black text-white mb-2">No Active Sessions</h3>
          <p className="text-zinc-500 text-sm font-medium max-w-xs mx-auto mb-8">Ready to level up? Connect with a mentor to start your first session.</p>
          <button 
            onClick={() => setActiveMentorshipTab('browse')}
            className="px-8 py-4 bg-[#c4ff0e] text-black rounded-2xl font-black text-xs uppercase tracking-widest hover:opacity-90 transition-all"
          >
            Find a Mentor
          </button>
        </div>
      )}
    </div>
  );
};

export default MentorshipProgram;
