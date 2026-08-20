import { createContext, useContext, useState, ReactNode } from 'react';
import { AuthUser } from '../types';
import { authService } from '../services/auth.service';

interface AuthContextType {
  user: AuthUser | null;
  isAdmin: boolean;
  isEmploye: boolean;
  loginAdmin: (email: string, password: string) => Promise<void>;
  loginEmploye: (pin: string, site_id: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(authService.getCurrentUser());

  const loginAdmin = async (email: string, password: string) => {
    const data = await authService.loginAdmin(email, password);
    authService.storeAuth(data);
    setUser(data.user);
  };

  const loginEmploye = async (pin: string, site_id: string) => {
    const data = await authService.loginEmploye(pin, site_id);
    authService.storeAuth(data);
    setUser(data.user);
  };

  const logout = () => {
    authService.logout();
    setUser(null);
  };

  const value: AuthContextType = {
    user,
    isAdmin: user?.role === 'administratrice',
    isEmploye: user?.role === 'employe',
    loginAdmin,
    loginEmploye,
    logout,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth doit être utilisé dans AuthProvider');
  }
  return context;
}