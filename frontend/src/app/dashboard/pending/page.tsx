'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '../../../contexts/AuthContext';
import GlassCard from '../../../components/ui/GlassCard';
import TaskCard from '../../../components/task/TaskCard';
import api from '../../../lib/api';

// Define the task type
interface Task {
  id: number;
  title: string;
  description: string;
  completed: boolean;
  created_at: string;
  updated_at: string;
}

const PendingTasksPage = () => {
  const router = useRouter();
  const { isAuthenticated } = useAuth();
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/login');
      return;
    }

    const fetchTasks = async () => {
      try {
        setLoading(true);
        const response = await api.getPendingTasks();

        if (response.success && response.data) {
          setTasks(response.data as Task[]);
        } else {
          setError('Failed to load pending tasks');
        }
      } catch (err) {
        console.error(err);
        setError('An error occurred while fetching pending tasks');
      } finally {
        setLoading(false);
      }
    };

    fetchTasks();
  }, [isAuthenticated, router]);

  const toggleTaskCompletion = async (taskId: number) => {
    try {
      const response = await api.toggleTaskComplete(taskId);
      if (response.success && response.data) {
        // Remove the task from the pending list since it's now completed
        setTasks(prev => prev.filter(task => task.id !== taskId));
      }
    } catch (err) {
      console.error('Error updating task:', err);
      alert('Failed to update task');
    }
  };

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-black p-4">
        <div className="text-center">
          <p className="text-gray-400">Redirecting to login...</p>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-black p-4">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
          <p className="mt-4 text-gray-400">Loading pending tasks...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white">Pending Tasks</h1>
        <p className="text-gray-400">View your pending tasks</p>
      </div>

      {error && (
        <div className="mb-6 p-3 bg-red-500/20 border border-red-500/30 rounded-lg text-red-300 text-sm">
          {error}
        </div>
      )}

      <GlassCard>
        {tasks.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-gray-500">No pending tasks</p>
            <button
              onClick={() => router.push('/dashboard')}
              className="mt-4 px-4 py-2 bg-linear-to-r from-blue-500 to-purple-500 text-white rounded-lg hover:opacity-90 transition-opacity"
            >
              View All Tasks
            </button>
          </div>
        ) : (
          <div className="space-y-4">
            {tasks.map((task) => (
              <TaskCard
                key={task.id}
                task={{
                  id: task.id.toString(),
                  title: task.title,
                  completed: task.completed,
                  createdAt: task.created_at,
                }}
                onToggle={() => toggleTaskCompletion(task.id)}
              />
            ))}
          </div>
        )}
      </GlassCard>

      <div className="mt-6 text-center">
        <button
          onClick={() => router.push('/dashboard')}
          className="px-4 py-2 bg-linear-to-r from-blue-500 to-purple-500 text-white rounded-lg hover:opacity-90 transition-opacity"
        >
          Back to Dashboard
        </button>
      </div>
    </div>
  );
};

export default PendingTasksPage;