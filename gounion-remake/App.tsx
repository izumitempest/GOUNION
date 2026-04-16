import React from "react";
import {
  HashRouter,
  Routes,
  Route,
  Navigate,
  useLocation,
} from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { Sidebar } from "./components/layout/Sidebar";
import { RightSidebar } from "./components/layout/RightSidebar";
import { TopNav } from "./components/layout/TopNav";
import { MobileNav } from "./components/layout/MobileNav";
import { Dashboard } from "./pages/Dashboard";
import { Login } from "./pages/Login";
import { ForgotPassword } from "./pages/ForgotPassword";
import { ResetPassword } from "./pages/ResetPassword";
import { Groups } from "./pages/Groups";
import { Messages } from "./pages/Messages";
import { Profile } from "./pages/Profile";
import { Alumni } from "./pages/Alumni";
import { GroupDetails } from "./pages/GroupDetails";
import { AdminPanel } from "./pages/AdminPanel";
import { Settings } from "./pages/Settings";
import { Notifications } from "./pages/Notifications";
import { SearchPage } from "./pages/Search";
import { useAuthStore } from "./store";
import { useEffect } from "react";
import { ToastProvider } from "./components/ui/Toast";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60, // 1 minute
      refetchOnWindowFocus: false,
    },
  },
});

// Layout Component to wrap authenticated routes
const AppLayout = ({ children }: { children?: React.ReactNode }) => {
  const { user } = useAuthStore();
  // If user exists, default to they ARE NOT verified until proven otherwise
  const isVerified = user ? (user.is_verified === true) : true; 

  return (
    <div className="flex flex-col h-screen bg-[#030303] text-white selection:bg-white/20 relative">
      {!isVerified && (
        <div className="bg-primary/20 border-b border-primary/20 py-3 px-4 flex items-center justify-center gap-4 animate-in slide-in-from-top duration-500 z-[110]">
          <div className="w-1.5 h-1.5 rounded-full bg-primary animate-pulse shadow-[0_0_10px_#c4ff0e]" />
          <p className="text-[10px] md:text-[11px] font-black uppercase tracking-[0.2em] text-primary">
            Security Check: Please confirm your campus email
          </p>
          <button className="bg-primary text-black px-4 py-1.5 rounded-full text-[9px] font-black uppercase tracking-widest hover:scale-105 transition-transform active:scale-95 shadow-[0_0_30px_rgba(196,255,14,0.3)]">
            Resend
          </button>
        </div>
      )}
      
      <TopNav />

      <div className="flex flex-1 overflow-hidden">
        <Sidebar />
        <main className="flex-1 overflow-y-auto hide-scrollbar md:pl-64 lg:pr-80 pb-28 md:pb-0">
          <div className="px-4 py-6 md:px-8 max-w-5xl mx-auto">
            {children}
          </div>
        </main>
        <RightSidebar />
        <MobileNav />
      </div>
    </div>
  );
};

const PrivateRoute = ({ children }: { children?: React.ReactNode }) => {
  const { isAuthenticated } = useAuthStore();
  if (!isAuthenticated) return <Navigate to="/login" replace />;
  return <AppLayout>{children}</AppLayout>;
};

const useWebSocket = () => {
  const { user, isAuthenticated } = useAuthStore();

  useEffect(() => {
    if (!isAuthenticated || !user?.id) return;

    const API_URL = import.meta.env.VITE_API_URL || 'https://gounion-backend.onrender.com';
    const wsUrl = API_URL.replace('http', 'ws') + `/ws/${user.id}`;
    const socket = new WebSocket(wsUrl);

    socket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.type === 'new_message') {
          const msg = data.message;
          // Invalidate affected queries for instant refresh
          queryClient.invalidateQueries({ queryKey: ["messages", msg.conversation_id.toString()] });
          queryClient.invalidateQueries({ queryKey: ["chats"] });
          queryClient.invalidateQueries({ queryKey: ["notifications-unread"] });
        }
      } catch (e) {
        console.error("WS Message error", e);
      }
    };

    socket.onclose = () => {
      console.log("WS Disconnected. Reconnecting in 5s...");
      // Optional: Auto-reconnect logic
    };

    return () => socket.close();
  }, [isAuthenticated, user?.id]);
};

const AppRoutes = () => {
  const { isAuthenticated } = useAuthStore();
  const location = useLocation();

  useWebSocket();

  const PUBLIC_ROUTES = ["/login", "/forgot-password", "/reset-password"];
  if (!isAuthenticated && !PUBLIC_ROUTES.includes(location.pathname)) {
    return <Navigate to="/login" replace />;
  }

  return (
    <Routes>
      <Route
        path="/login"
        element={isAuthenticated ? <Navigate to="/" /> : <Login />}
      />
      <Route path="/forgot-password" element={<ForgotPassword />} />
      <Route path="/reset-password" element={<ResetPassword />} />
      <Route
        path="/"
        element={
          <PrivateRoute>
            <Dashboard />
          </PrivateRoute>
        }
      />
      <Route
        path="/groups"
        element={
          <PrivateRoute>
            <Groups />
          </PrivateRoute>
        }
      />
      <Route
        path="/groups/:id"
        element={
          <PrivateRoute>
            <GroupDetails />
          </PrivateRoute>
        }
      />
      <Route
        path="/messages"
        element={
          <PrivateRoute>
            <Messages />
          </PrivateRoute>
        }
      />
      <Route
        path="/alumni"
        element={
          <PrivateRoute>
            <Alumni />
          </PrivateRoute>
        }
      />
      <Route
        path="/profile/:username"
        element={
          <PrivateRoute>
            <Profile />
          </PrivateRoute>
        }
      />
      <Route
        path="/admin"
        element={
          <PrivateRoute>
            <AdminPanel />
          </PrivateRoute>
        }
      />
      <Route
        path="/discover"
        element={
          <PrivateRoute>
            <Alumni />
          </PrivateRoute>
        }
      />
      <Route
        path="/settings"
        element={
          <PrivateRoute>
            <Settings />
          </PrivateRoute>
        }
      />
      <Route
        path="/notifications"
        element={
          <PrivateRoute>
            <Notifications />
          </PrivateRoute>
        }
      />
      <Route
        path="/search"
        element={
          <PrivateRoute>
            <SearchPage />
          </PrivateRoute>
        }
      />
      <Route path="*" element={<Navigate to="/" />} />
    </Routes>
  );
};

const App = () => {
  return (
    <QueryClientProvider client={queryClient}>
      <ToastProvider>
        <HashRouter>
          <AppRoutes />
        </HashRouter>
      </ToastProvider>
    </QueryClientProvider>
  );
};

export default App;
