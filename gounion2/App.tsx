
import React, { useState, useEffect } from 'react';
import Sidebar from './components/Sidebar';
import Feed from './components/Feed';
import RightPanel from './components/RightPanel';
import EventsCalendar from './components/EventsCalendar';
import MentorshipProgram from './components/MentorshipProgram';
import CollaborationHub from './components/CollaborationHub';
import { INITIAL_POSTS, CURRENT_USER, MOCK_NOTIFICATIONS } from './constants';
import { Post } from './types';
import { getAcademicInsights } from './services/geminiService';

const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState('home');
  const [posts] = useState<Post[]>(INITIAL_POSTS);
  const [insights, setInsights] = useState<string[]>([]);
  const [loadingInsights, setLoadingInsights] = useState(true);

  useEffect(() => {
    const fetchInsights = async () => {
      setLoadingInsights(true);
      const data = await getAcademicInsights(CURRENT_USER);
      setInsights(data);
      setLoadingInsights(false);
    };

    fetchInsights();
  }, []);

  const unreadCount = MOCK_NOTIFICATIONS.filter(n => !n.isRead).length;

  const renderContent = () => {
    switch (activeTab) {
      case 'home':
        return <Feed posts={posts} />;
      case 'events':
        return <EventsCalendar />;
      case 'mentorship':
        return <MentorshipProgram />;
      case 'collab':
        return <CollaborationHub />;
      case 'explore':
        return (
          <div className="max-w-4xl mx-auto py-12 px-6">
            <h1 className="text-4xl font-black text-white tracking-tighter mb-8">Discover Academia</h1>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              <div className="h-80 bg-gradient-to-br from-purple-600 to-indigo-900 rounded-[40px] p-10 text-white relative overflow-hidden group cursor-pointer border border-white/10 shadow-2xl">
                <div className="relative z-10 h-full flex flex-col justify-end">
                  <h3 className="text-3xl font-black mb-2 tracking-tight">Stanford Lab</h3>
                  <p className="text-indigo-100 font-medium">Read the latest on AI Safety.</p>
                </div>
                <div className="absolute top-0 right-0 w-64 h-64 bg-white/10 rounded-full blur-[80px] -mr-20 -mt-20"></div>
              </div>
              <div className="h-80 bg-[#141417] border border-white/5 rounded-[40px] p-10 text-white relative overflow-hidden group cursor-pointer shadow-2xl">
                <div className="relative z-10 h-full flex flex-col justify-end">
                  <h3 className="text-3xl font-black mb-2 tracking-tight text-[#c4ff0e]">Career Pathways</h3>
                  <p className="text-zinc-500 font-medium">Top tech firms are hiring. Apply now.</p>
                </div>
                <div className="absolute top-0 right-0 w-64 h-64 bg-[#c4ff0e]/5 rounded-full blur-[80px] -mr-20 -mt-20"></div>
              </div>
            </div>
          </div>
        );
      case 'notifications':
        return (
          <div className="max-w-2xl mx-auto py-12 px-4">
            <h1 className="text-3xl font-black text-white tracking-tighter mb-8">Activity</h1>
            <div className="space-y-4">
              {MOCK_NOTIFICATIONS.map(notification => (
                <div key={notification.id} className={`p-6 rounded-[32px] border transition-all flex items-start gap-4 ${notification.isRead ? 'bg-white/5 border-white/5' : 'bg-white/10 border-white/10 shadow-[0_10px_30px_rgba(0,0,0,0.2)]'}`}>
                  <img src={notification.sender.avatar} className="w-12 h-12 rounded-full border border-white/10" alt="Sender" />
                  <div className="flex-1">
                    <p className="text-sm text-zinc-300">
                      <span className="font-bold text-white">{notification.sender.name}</span> {notification.content}
                    </p>
                    <span className="text-[10px] font-black text-zinc-500 mt-2 block uppercase tracking-widest">{notification.timestamp}</span>
                  </div>
                  {!notification.isRead && <div className="w-2.5 h-2.5 bg-[#c4ff0e] rounded-full mt-2 shadow-[0_0_10px_#c4ff0e]"></div>}
                </div>
              ))}
            </div>
          </div>
        );
      default:
        return (
          <div className="flex flex-col items-center justify-center py-32 px-6 text-center">
            <div className="w-24 h-24 bg-white/5 rounded-[40px] flex items-center justify-center text-4xl mb-8 border border-white/5">
              {activeTab === 'messages' && '💬'}
              {activeTab === 'communities' && '🏫'}
              {activeTab === 'careers' && '💼'}
            </div>
            <h3 className="text-2xl font-black text-white mb-4 capitalize">{activeTab} Section</h3>
            <p className="text-zinc-500 max-w-xs font-medium">We're finalizing this feature for your university. Stay updated.</p>
          </div>
        );
    }
  };

  return (
    <div className="min-h-screen flex bg-[#0a0a0c]">
      <Sidebar 
        activeTab={activeTab} 
        setActiveTab={setActiveTab} 
        notificationCount={unreadCount} 
      />

      <main className="flex-1 lg:pl-20 xl:pl-72 xl:pr-96 min-h-screen">
        <header className="sticky top-0 z-30 bg-[#0a0a0c]/80 backdrop-blur-xl border-b border-white/5 lg:hidden px-6 h-20 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-[#c4ff0e] rounded-xl flex items-center justify-center text-black font-black text-xl">U</div>
            <span className="text-xl font-black tracking-tighter text-white">GoUnion</span>
          </div>
          <button className="p-3 bg-white/5 rounded-2xl text-white">
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 6h16M4 12h16m-7 6h7"></path></svg>
          </button>
        </header>

        <div className="pb-24 lg:pb-12">
          {renderContent()}
        </div>
      </main>

      <RightPanel 
        insights={insights} 
        loadingInsights={loadingInsights} 
      />
    </div>
  );
};

export default App;
