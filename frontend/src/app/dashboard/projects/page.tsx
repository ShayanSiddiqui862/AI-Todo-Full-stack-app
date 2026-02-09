'use client';

import React from 'react';
import { useAuth } from '../../../contexts/AuthContext';
import GlassCard from '../../../components/ui/GlassCard';

const ProjectsPage = () => {
  const { isAuthenticated, user } = useAuth();

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-black p-4">
        <div className="text-center">
          <p className="text-gray-400">Redirecting to login...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white">Projects</h1>
        <p className="text-gray-400">Manage your task projects</p>
      </div>

      <GlassCard>
        <div className="text-center py-12">
          <div className="text-6xl mb-4">📁</div>
          <h2 className="text-2xl font-semibold mb-2">Projects Feature</h2>
          <p className="text-gray-400 mb-6">
            This is where you'll manage your task projects and organize tasks into different categories.
          </p>
          <p className="text-gray-500 text-sm">
            Welcome, {user?.name || user?.email || 'User'}! This feature is coming soon.
          </p>
        </div>
      </GlassCard>
    </div>
  );
};

export default ProjectsPage;