"use client";

import { AuthProvider } from '@/contexts/AuthContext';
import LoginPage from '@/app/login/page';

export default function LoginLayout() {
  return (
    <AuthProvider>
      <LoginPage />
    </AuthProvider>
  );
}
