'use client';

import React from 'react';
import ProtectedRoute from '../../components/route/ProtectedRoute';
import Sidebar from '../../components/dashboard/Sidebar';
import { useAuth } from '../../contexts/AuthContext';

const DashboardLayout = ({ children }: { children: React.ReactNode }) => {
  const { isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-black">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
          <p className="mt-4 text-gray-400">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <ProtectedRoute>
      <div className="flex min-h-screen bg-black text-white">
        <Sidebar />
        <main className="flex-1 ml-16 md:ml-64 transition-all duration-300">
          {children}
        </main>
      </div>
    </ProtectedRoute>
  );
};

export default DashboardLayout;