import React from 'react';
import { useAuthStore } from '../store';
import { Shield, Bell, Lock, User, LogOut } from 'lucide-react';
import { motion } from 'framer-motion';

export const Settings = () => {
  const { user, logout } = useAuthStore();

  const settingsTabs = [
    { icon: User, label: "Account Profile", desc: "Manage your public presence" },
    { icon: Lock, label: "Privacy & Security", desc: "Control who sees your data" },
    { icon: Bell, label: "Push Notifications", desc: "Customize alert preferences" },
    { icon: Shield, label: "Data & Permissions", desc: "Manage integrations" },
  ];

  return (
    <div className="max-w-4xl mx-auto w-full pb-24 pt-8">
      <div className="mb-10 relative p-8 rounded-[2rem] glass-panel overflow-hidden border border-white/5 shadow-2xl">
        <h1 className="text-3xl font-black text-white tracking-tighter">Settings</h1>
        <p className="text-zinc-400 font-medium mt-1">Manage your platform preferences and security.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="space-y-4">
          <h2 className="text-sm font-bold text-white/50 uppercase tracking-widest pl-2">Preferences</h2>
          {settingsTabs.map((tab, i) => (
            <motion.button
              key={i}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              className="w-full text-left p-6 glass-panel rounded-3xl border border-white/5 hover:border-white/20 transition-all flex items-center gap-4 group"
            >
              <div className="w-12 h-12 rounded-2xl bg-white/5 flex items-center justify-center border border-white/10 group-hover:bg-white/10 transition-colors">
                <tab.icon className="text-white sm:text-white/70 group-hover:text-white" size={24} />
              </div>
              <div>
                <h3 className="font-bold text-white text-lg">{tab.label}</h3>
                <p className="text-xs font-medium text-white/40 mt-1">{tab.desc}</p>
              </div>
            </motion.button>
          ))}
        </div>

        <div className="space-y-4">
          <h2 className="text-sm font-bold text-white/50 uppercase tracking-widest pl-2">Danger Zone</h2>
          <div className="glass-panel rounded-3xl p-6 border border-red-500/10">
            <h3 className="font-bold text-white text-lg mb-2">Sign Out</h3>
            <p className="text-xs font-medium text-white/40 mb-6">Terminate your active session on this device.</p>
            <button
              onClick={logout}
              className="w-full py-4 bg-red-500/10 hover:bg-red-500/20 text-red-400 font-bold rounded-2xl flex items-center justify-center gap-2 border border-red-500/20 transition-all"
            >
              <LogOut size={18} /> Process Logout
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
