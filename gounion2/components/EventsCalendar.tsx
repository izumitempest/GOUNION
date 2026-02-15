
import React, { useState } from 'react';
import { Calendar, MapPin, Clock, ArrowRight, CheckCircle } from 'lucide-react';
import { MOCK_EVENTS } from '../constants';

const EventsCalendar: React.FC = () => {
  const [filter, setFilter] = useState<'all' | 'academic' | 'social' | 'career'>('all');

  const filteredEvents = filter === 'all' 
    ? MOCK_EVENTS 
    : MOCK_EVENTS.filter(e => e.type === filter);

  return (
    <div className="max-w-4xl mx-auto py-12 px-6">
      <div className="mb-10 flex flex-col md:flex-row md:items-end justify-between gap-6">
        <div>
          <h1 className="text-4xl font-black text-white tracking-tighter mb-2">Campus Events</h1>
          <p className="text-zinc-500 text-sm font-medium">Explore and join upcoming academic and social activities.</p>
        </div>
        
        <div className="flex gap-2 overflow-x-auto pb-2 no-scrollbar">
          {(['all', 'academic', 'social', 'career'] as const).map((type) => (
            <button
              key={type}
              onClick={() => setFilter(type)}
              className={`px-5 py-2.5 rounded-2xl text-xs font-bold capitalize transition-all whitespace-nowrap border-2 ${
                filter === type 
                ? 'bg-[#c4ff0e] text-black border-[#c4ff0e]' 
                : 'bg-white/5 text-zinc-400 border-white/5 hover:border-white/20'
              }`}
            >
              {type}
            </button>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-1 gap-6">
        {filteredEvents.map((event) => (
          <div key={event.id} className="glass-card rounded-[40px] p-8 hover:translate-y-[-4px] transition-all group border border-white/5 hover:border-[#c4ff0e]/30">
            <div className="flex flex-col md:flex-row gap-8 items-start">
              <div className="bg-[#c4ff0e] p-6 rounded-[32px] flex flex-col items-center justify-center text-black min-w-[120px] shadow-[0_10px_30px_rgba(196,255,14,0.2)]">
                 <span className="text-xs font-black uppercase tracking-widest opacity-70">{event.date.split(' ')[0]}</span>
                 <span className="text-4xl font-black">{event.date.split(' ')[1].replace(',', '')}</span>
              </div>
              
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-3">
                  <span className="text-[10px] font-black uppercase text-[#c4ff0e] bg-[#c4ff0e]/10 px-3 py-1 rounded-full">#{event.type}</span>
                  <span className="text-[10px] font-bold text-zinc-500 uppercase tracking-widest">{event.university}</span>
                </div>
                <h3 className="text-2xl font-black text-white mb-4 group-hover:text-[#c4ff0e] transition-colors">{event.title}</h3>
                <p className="text-zinc-400 text-sm mb-6 leading-relaxed line-clamp-2">{event.description}</p>
                
                <div className="flex flex-wrap gap-6 text-xs font-bold text-zinc-500 uppercase tracking-widest">
                    <span className="flex items-center gap-2"><Clock className="w-4 h-4 text-[#c4ff0e]"/> {event.time}</span>
                    <span className="flex items-center gap-2"><MapPin className="w-4 h-4 text-[#c4ff0e]"/> {event.location}</span>
                    <span className="text-white">{event.attendees} Registered</span>
                </div>
              </div>
              
              <button className="w-full md:w-auto mt-6 md:mt-0 px-8 py-4 bg-white/5 hover:bg-[#c4ff0e] hover:text-black text-white rounded-[24px] font-black text-sm uppercase transition-all flex items-center justify-center gap-3">
                Register <ArrowRight className="w-5 h-5" />
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default EventsCalendar;
