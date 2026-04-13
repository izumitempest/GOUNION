import { create } from 'zustand';
import { User } from './types';

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  login: (user: User, token: string) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>((set) => {
  // Initialize from localStorage
  const token = localStorage.getItem('access_token');
  const userStr = localStorage.getItem('user_data');
  let user = null;
  try {
    user = userStr ? JSON.parse(userStr) : null;
  } catch (e) {
    console.error("Failed to parse user data", e);
  }

  return {
    user: user,
    token: token,
    isAuthenticated: !!token,
    login: (user, token) => {
      localStorage.setItem('access_token', token);
      localStorage.setItem('user_data', JSON.stringify(user));
      set({ user, token, isAuthenticated: true });
    },
    logout: () => {
      localStorage.removeItem('access_token');
      localStorage.removeItem('user_data');
      set({ user: null, token: null, isAuthenticated: false });
    },
  };
});

interface UIState {
  sidebarOpen: boolean;
  toggleSidebar: () => void;
  setSidebarOpen: (open: boolean) => void;
}

export const useUIStore = create<UIState>((set) => ({
  sidebarOpen: false,
  toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),
  setSidebarOpen: (open) => set({ sidebarOpen: open }),
}));
