'use client';

import React, { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { useAuth } from '../../../../contexts/AuthContext';
import GlassCard from '../../../../components/ui/GlassCard';
import api from '../../../../lib/api';

// Define the task type
interface Task {
  id: number;
  title: string;
  description: string;
  completed: boolean;
  created_at: string;
  updated_at: string;
}

const TaskDetailPage = () => {
  const { id } = useParams();
  const router = useRouter();
  const { isAuthenticated } = useAuth();
  const [task, setTask] = useState<Task | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/login');
      return;
    }

    const fetchTask = async () => {
      try {
        setLoading(true);
        const response = await api.getTask(Number(id));

        if (response.success && response.data) {
          setTask(response.data as Task);
        } else {
          setError('Failed to load task');
        }
      } catch (err) {
        setError('An error occurred while fetching the task');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchTask();
  }, [id, isAuthenticated, router]);

  const handleToggleComplete = async () => {
    if (!task) return;

    try {
      const response = await api.toggleTaskComplete(task.id);
      if (response.success && response.data) {
        setTask(response.data as Task);
      }
    } catch (err) {
      console.error('Error updating task:', err);
      alert('Failed to update task');
    }
  };

  const handleDelete = async () => {
    if (!task || !window.confirm('Are you sure you want to delete this task?')) return;

    try {
      const response = await api.deleteTask(task.id);
      if (response.success) {
        router.push('/dashboard');
        alert('Task deleted successfully');
      }
    } catch (err) {
      console.error('Error deleting task:', err);
      alert('Failed to delete task');
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
          <p className="mt-4 text-gray-400">Loading task...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-black p-4">
        <GlassCard className="p-8 max-w-md w-full text-center">
          <p className="text-red-400 mb-4">{error}</p>
          <button
            onClick={() => router.push('/dashboard')}
            className="px-4 py-2 bg-linear-to-r from-blue-500 to-purple-500 text-white rounded-lg hover:opacity-90 transition-opacity"
          >
            Go to Dashboard
          </button>
        </GlassCard>
      </div>
    );
  }

  if (!task) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-black p-4">
        <GlassCard className="p-8 max-w-md w-full text-center">
          <p className="text-gray-400 mb-4">Task not found</p>
          <button
            onClick={() => router.push('/dashboard')}
            className="px-4 py-2 bg-linear-to-r from-blue-500 to-purple-500 text-white rounded-lg hover:opacity-90 transition-opacity"
          >
            Go to Dashboard
          </button>
        </GlassCard>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-2xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white">Task Details</h1>
      </div>

      <GlassCard>
        <div className="flex justify-between items-start mb-6">
          <h2 className="text-2xl font-semibold">{task.title}</h2>
          <div className="flex gap-2">
            <button
              onClick={handleToggleComplete}
              className={`px-4 py-2 rounded-lg ${
                task.completed
                  ? 'bg-gray-600 hover:bg-gray-700'
                  : 'bg-linear-to-r from-blue-500 to-purple-500 hover:opacity-90'
              } text-white transition-opacity`}
            >
              {task.completed ? 'Mark Incomplete' : 'Mark Complete'}
            </button>
            <button
              onClick={handleDelete}
              className="px-4 py-2 bg-red-500/20 border border-red-500/30 text-red-300 rounded-lg hover:bg-red-500/30 transition-colors"
            >
              Delete
            </button>
          </div>
        </div>

        <div className="mb-6">
          <p className="text-gray-300 whitespace-pre-wrap">{task.description || 'No description provided.'}</p>
        </div>

        <div className="grid grid-cols-2 gap-4 text-sm">
          <div className="p-3 bg-black/20 rounded-lg">
            <p className="text-gray-400">Status</p>
            <p className={task.completed ? 'text-green-400' : 'text-yellow-400'}>
              {task.completed ? 'Completed' : 'Pending'}
            </p>
          </div>
          <div className="p-3 bg-black/20 rounded-lg">
            <p className="text-gray-400">Created</p>
            <p className="text-gray-300">
              {new Date(task.created_at).toLocaleDateString()}
            </p>
          </div>
          <div className="p-3 bg-black/20 rounded-lg">
            <p className="text-gray-400">Updated</p>
            <p className="text-gray-300">
              {new Date(task.updated_at).toLocaleDateString()}
            </p>
          </div>
        </div>
      </GlassCard>
    </div>
  );
};

export default TaskDetailPage;