import React, { useState } from "react";
import { NavLink, useNavigate } from "react-router-dom";
import {
  Home,
  Users,
  MessageSquare,
  User,
  MoreHorizontal,
  Bell,
  Compass,
  GraduationCap,
  ShieldCheck,
  Settings,
  LogOut,
  X,
} from "lucide-react";
import { useAuthStore } from "../../store";
import { useQuery } from "@tanstack/react-query";
import { api } from "../../services/api";
import { motion, AnimatePresence } from "framer-motion";

export const MobileNav = () => {
  const { user, logout } = useAuthStore();
  const navigate = useNavigate();
  const [showOthers, setShowOthers] = useState(false);

  const { data: unreadData } = useQuery({
    queryKey: ["notifications-unread"],
    queryFn: api.notifications.getUnreadCount,
    refetchInterval: 30000,
  });
  const unreadCount = unreadData?.count || 0;

  const NAV_ITEMS = [
    { icon: Home, label: "Feed", path: "/" },
    { icon: Users, label: "Groups", path: "/groups" },
    { icon: MessageSquare, label: "Chat", path: "/messages" },
    { icon: User, label: "Profile", path: `/profile/${user?.username}` },
  ];

  const OTHERS_ITEMS = [
    { icon: Bell, label: "Alerts", path: "/notifications", badge: unreadCount },
    { icon: Compass, label: "Discover", path: "/discover" },
    { icon: GraduationCap, label: "Alumni", path: "/alumni" },
    ...(user?.role === "admin" || user?.role === "moderator"
      ? [{ icon: ShieldCheck, label: "Admin Panel", path: "/admin" }]
      : []),
    { icon: Settings, label: "Settings", path: "/settings" },
  ];

  return (
    <>
      {/* Facebook-style top tab bar — mobile only */}
      <div className="md:hidden sticky top-16 left-0 right-0 w-full bg-[#0a0a0c]/95 backdrop-blur-xl border-b border-white/5 z-[99] flex items-center justify-around h-12">
        {NAV_ITEMS.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) =>
              `relative flex flex-col items-center justify-center h-full flex-1 transition-all duration-200 ${
                isActive ? "text-primary" : "text-zinc-500"
              }`
            }
          >
            {({ isActive }) => (
              <>
                <item.icon size={20} />
                <span className="text-[8px] mt-0.5 font-bold uppercase tracking-wider">
                  {item.label}
                </span>
                {isActive && (
                  <motion.div
                    layoutId="mobileActiveTab"
                    className="absolute bottom-0 left-2 right-2 h-[2px] bg-primary rounded-full"
                    transition={{ type: "spring", duration: 0.4 }}
                  />
                )}
              </>
            )}
          </NavLink>
        ))}

        {/* Others button */}
        <button
          onClick={() => setShowOthers(!showOthers)}
          className={`relative flex flex-col items-center justify-center h-full flex-1 transition-all duration-200 ${
            showOthers ? "text-primary" : "text-zinc-500"
          }`}
        >
          <MoreHorizontal size={20} />
          <span className="text-[8px] mt-0.5 font-bold uppercase tracking-wider">
            Others
          </span>
          {unreadCount > 0 && (
            <span className="absolute top-1 right-[25%] bg-red-500 text-white text-[7px] font-bold w-4 h-4 flex items-center justify-center rounded-full">
              {unreadCount > 9 ? "9+" : unreadCount}
            </span>
          )}
        </button>
      </div>

      {/* Others overlay menu */}
      <AnimatePresence>
        {showOthers && (
          <>
            {/* Backdrop */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="md:hidden fixed inset-0 bg-black/60 backdrop-blur-sm z-[200]"
              onClick={() => setShowOthers(false)}
            />

            {/* Grid menu */}
            <motion.div
              initial={{ opacity: 0, y: -20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ type: "spring", duration: 0.35 }}
              className="md:hidden fixed top-28 left-4 right-4 bg-[#111113] border border-white/10 rounded-2xl p-4 z-[201] shadow-[0_20px_60px_rgba(0,0,0,0.8)]"
            >
              <div className="flex items-center justify-between mb-4">
                <span className="text-[10px] font-black uppercase tracking-widest text-zinc-500">
                  More Options
                </span>
                <button
                  onClick={() => setShowOthers(false)}
                  className="text-zinc-500 hover:text-white transition-colors"
                >
                  <X size={18} />
                </button>
              </div>

              <div className="grid grid-cols-2 gap-3">
                {OTHERS_ITEMS.map((item) => (
                  <button
                    key={item.path}
                    onClick={() => {
                      setShowOthers(false);
                      navigate(item.path);
                    }}
                    className="flex flex-col items-center gap-2 p-4 bg-white/5 border border-white/5 rounded-xl hover:bg-white/10 transition-all active:scale-95 relative"
                  >
                    <div className="w-10 h-10 rounded-xl bg-violet-500/20 flex items-center justify-center">
                      <item.icon size={20} className="text-violet-400" />
                    </div>
                    <span className="text-[11px] font-bold text-zinc-300">
                      {item.label}
                    </span>
                    {"badge" in item && (item as any).badge > 0 && (
                      <span className="absolute top-2 right-2 bg-red-500 text-white text-[8px] font-bold px-1.5 py-0.5 rounded-full">
                        {(item as any).badge}
                      </span>
                    )}
                  </button>
                ))}
              </div>

              {/* Logout */}
              <button
                onClick={() => {
                  setShowOthers(false);
                  logout();
                }}
                className="w-full mt-4 flex items-center justify-center gap-2 p-3 bg-red-500/10 border border-red-500/20 rounded-xl text-red-400 hover:bg-red-500/20 transition-all active:scale-95"
              >
                <LogOut size={16} />
                <span className="text-[10px] font-black uppercase tracking-widest">
                  Logout Session
                </span>
              </button>
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </>
  );
};
