import api from './api';
import { AuthUser } from '../types';

export interface LoginResponse {
  access: string;
  refresh?: string;
  user: AuthUser;
}

export const authService = {
  async loginAdmin(email: string, password: string): Promise<LoginResponse> {
    const response = await api.post<LoginResponse>('/auth/login/', { email, password });
    return response.data;
  },

  async loginEmploye(pin: string, site_id: string): Promise<LoginResponse> {
    const response = await api.post<LoginResponse>('/auth/login-pin/', { pin, site_id });
    return response.data;
  },

  logout(): void {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');
  },

  getCurrentUser(): AuthUser | null {
    const user = localStorage.getItem('user');
    return user ? JSON.parse(user) : null;
  },

  storeAuth(data: LoginResponse): void {
    localStorage.setItem('access_token', data.access);
    if (data.refresh) {
      localStorage.setItem('refresh_token', data.refresh);
    }
    localStorage.setItem('user', JSON.stringify(data.user));
  },
};