"use client";

import React, { createContext, useContext, useState, useEffect } from 'react';
import { User } from '@/lib/types';
import apiClient from '@/lib/api';

interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  isAuthenticated: boolean;
  hasRole: (role: string) => boolean;
  isQAAdmin: boolean;
  isCoordinator: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check if user is already logged in
    const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;
    if (token) {
      fetchUser();
    } else {
      setLoading(false);
    }
  }, []);

  const fetchUser = async () => {
    try {
      const response = await apiClient.instance.get('/users/me/');
      setUser(response.data);
    } catch (error) {
      // Token invalid, clear it
      apiClient.setToken('');
      apiClient.setRefreshToken('');
    } finally {
      setLoading(false);
    }
  };

  const login = async (email: string, password: string) => {
    const response = await apiClient.instance.post('/auth/login/', {
      email,
      password,
    });
    
    const { access, refresh, user: userData } = response.data;
    apiClient.setToken(access);
    apiClient.setRefreshToken(refresh);
    setUser(userData);
  };

  const logout = () => {
    apiClient.setToken('');
    apiClient.setRefreshToken('');
    setUser(null);
    if (typeof window !== 'undefined') {
      window.location.href = '/login';
    }
  };

  const hasRole = (role: string): boolean => {
    if (!user) return false;
    return user.roles.some((r) => r.role === role);
  };

  const isQAAdmin = hasRole('QAAdmin') || hasRole('SuperAdmin') || (user?.is_staff ?? false);
  const isCoordinator = hasRole('DepartmentCoordinator');

  return (
    <AuthContext.Provider
      value={{
        user,
        loading,
        login,
        logout,
        isAuthenticated: !!user,
        hasRole,
        isQAAdmin,
        isCoordinator,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
