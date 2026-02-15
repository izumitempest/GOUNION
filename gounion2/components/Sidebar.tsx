
import React from 'react';
import { 
  Home, 
  Compass, 
  Bell, 
  Calendar, 
  Users, 
  Zap, 
  User,
  LogOut,
  Plus
} from 'lucide-react';

interface SidebarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  notificationCount: number;
}

const Sidebar: React.FC<SidebarProps> = ({ activeTab, setActiveTab, notificationCount }) => {
  const menuItems = [
    { id: 'home', label: 'Home', icon: Home },
    { id: 'explore', label: 'Explore', icon: Compass },
    { id: 'events', label: 'Events', icon: Calendar },
    { id: 'mentorship', label: 'Experts', icon: Users },
    { id: 'collab', label: 'Teams', icon: Zap },
    { id: 'notifications', label: 'Alerts', icon: Bell, badge: notificationCount },
  ];

  return (
    <aside className="fixed left-0 top-0 h-screen w-20 xl:w-72 bg-[#0a0a0c] border-r border-white/5 z-50 flex flex-col p-6">
      <div className="flex items-center gap-3 mb-10 px-2 group cursor-pointer" onClick={() => setActiveTab('home')}>
        <div className="w-10 h-10 bg-[#c4ff0e] rounded-2xl flex items-center justify-center text-black font-black text-xl shadow-[0_0_20px_rgba(196,255,14,0.3)] transition-transform group-hover:scale-110">
          U
        </div>
        <span className="hidden xl:block text-2xl font-black tracking-tighter text-white">GoUnion</span>
      </div>

      <nav className="flex-1 space-y-2">
        {menuItems.map((item) => (
          <button
            key={item.id}
            onClick={() => setActiveTab(item.id)}
            className={`w-full flex items-center justify-center xl:justify-start gap-4 px-4 py-4 rounded-2xl transition-all group relative ${
              activeTab === item.id 
                ? 'bg-white/5 text-[#c4ff0e]' 
                : 'text-zinc-500 hover:bg-white/5 hover:text-white'
            }`}
          >
            <item.icon className={`w-6 h-6 transition-all ${activeTab === item.id ? 'scale-110' : 'group-hover:scale-110'}`} />
            <span className={`hidden xl:block text-sm font-bold ${activeTab === item.id ? 'text-white' : ''}`}>{item.label}</span>
            {item.badge && activeTab !== item.id ? (
              <span className="absolute top-3 right-3 xl:static xl:ml-auto w-2 h-2 bg-purple-500 rounded-full" />
            ) : null}
            {activeTab === item.id && (
              <div className="absolute left-0 top-1/2 -translate-y-1/2 w-1 h-8 bg-[#c4ff0e] rounded-full shadow-[0_0_10px_#c4ff0e]" />
            )}
          </button>
        ))}
      </nav>

      <div className="mt-auto space-y-6 pt-6 border-t border-white/5">
        <button className="w-full h-14 bg-[#c4ff0e] text-black rounded-2xl font-black text-sm uppercase tracking-widest flex items-center justify-center gap-2 hover:opacity-90 transition-all shadow-[0_0_20px_rgba(196,255,14,0.2)]">
          <Plus className="w-5 h-5" />
          <span className="hidden xl:block">New Post</span>
        </button>
        
        <div className="flex items-center gap-3 px-2 group cursor-pointer hover:bg-white/5 p-2 rounded-2xl transition-all">
          <div className="w-10 h-10 rounded-full border border-white/10 overflow-hidden shrink-0">
             <img src="https://picsum.photos/seed/arivera/100/100" className="w-full h-full object-cover" />
          </div>
          <div className="hidden xl:block flex-1 min-w-0">
            <h4 className="text-sm font-bold text-white truncate">Alex Rivera</h4>
            <p className="text-xs text-zinc-500 font-medium">Stanford '25</p>
          </div>
          <LogOut className="hidden xl:block w-4 h-4 text-zinc-600 hover:text-white transition-colors" />
        </div>
      </div>
    </aside>
  );
};

export default Sidebar;
