'use client';

import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import GlassCard from '../../components/ui/GlassCard';
import TaskCard from '../../components/task/TaskCard';
import TaskActionModal from '../../components/task/TaskActionModal';
import FocusModeToggle from '../../components/dashboard/FocusModeToggle';
import api from '../../lib/api';

// Define the task type
interface Task {
  id: string;
  title: string;
  completed: boolean;
  dueDate?: string;
  category?: string;
  createdAt: string;
  scheduled_time?: string;
}

interface ApiTaskResponse {
  id: number;
  title: string;
  completed: boolean;
  description?: string;
  created_at: string;
  due_date?: string;
  category?: string;
  scheduled_time?: string;
}

const DashboardPage = () => {
  const { user } = useAuth();
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [newTask, setNewTask] = useState('');
  const [scheduledTime, setScheduledTime] = useState('');
  
  // Modal state
  const [selectedTask, setSelectedTask] = useState<Task | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  // Load tasks from the backend API
  useEffect(() => {
    const loadTasks = async () => {
      setLoading(true);
      try {
        // First try to get tasks from backend API
        const response = await api.getTasks();

        if (response.success && response.data) {
          setTasks(response.data as Task[]);
          // Also save to offline storage for offline access
          api.saveTasksOffline(response.data as Task[]);
        } else {
          // If API fails, try offline storage
          const offlineTasks = await api.getTasksOffline();
          setTasks(offlineTasks);
        }
      } catch (error) {
        console.error('Error loading tasks:', error);
        // Try offline storage as last resort
        const offlineTasks = await api.getTasksOffline();
        setTasks(offlineTasks);
      } finally {
        setLoading(false);
      }
    };

    loadTasks();
  }, []);

  const handleAddTask = async (e: React.FormEvent) => {
    e.preventDefault();
    if (newTask.trim() === '') return;

    // Convert local time input to ISO string for backend
    let scheduledTimeISO: string | undefined;
    if (scheduledTime) {
      const today = new Date();
      const [hours, minutes] = scheduledTime.split(':').map(Number);
      today.setHours(hours, minutes, 0, 0);
      scheduledTimeISO = today.toISOString();
    }

    const taskData = {
      title: newTask,
      description: "",
      completed: false,
      scheduled_time: scheduledTimeISO,
    };

    try {
      // Call backend API to create the task
      const response = await api.createTask(taskData);

      if (response.success && response.data) {
        // Add the new task to the local state
        const newTaskItem = {
          id: (response.data as ApiTaskResponse).id.toString(),
          title: (response.data as ApiTaskResponse).title,
          completed: (response.data as ApiTaskResponse).completed,
          createdAt: (response.data as ApiTaskResponse).created_at || new Date().toISOString(),
          dueDate: (response.data as ApiTaskResponse).due_date,
          category: (response.data as ApiTaskResponse).category,
          scheduled_time: (response.data as ApiTaskResponse).scheduled_time,
        };
        setTasks(prev => [newTaskItem, ...prev]);
        setNewTask('');
        setScheduledTime('');

        // Update offline storage
        api.saveTasksOffline([newTaskItem, ...tasks]);
      } else {
        // If API fails, add to local state temporarily
        const localTask = {
          id: Date.now().toString(),
          title: newTask,
          completed: false,
          createdAt: new Date().toISOString(),
          scheduled_time: scheduledTimeISO,
        };
        setTasks(prev => [localTask, ...prev]);
        setNewTask('');
        setScheduledTime('');
        api.saveTasksOffline([localTask, ...tasks]);
        alert('Task saved locally. Will sync when online.');
      }
    } catch (error) {
      console.error('Error creating task:', error);
      const localTask = {
        id: Date.now().toString(),
        title: newTask,
        completed: false,
        createdAt: new Date().toISOString(),
        scheduled_time: scheduledTimeISO,
      };
      setTasks(prev => [localTask, ...prev]);
      setNewTask('');
      setScheduledTime('');
      api.saveTasksOffline([localTask, ...tasks]);
      alert('Task saved locally. Will sync when online.');
    }
  };

  const toggleTaskCompletion = async (id: string) => {
    try {
      const response = await api.toggleTaskComplete(Number(id));

      if (response.success && response.data) {
        const updatedTasks = tasks.map(t =>
          t.id === id ? { ...t, completed: (response.data as ApiTaskResponse).completed } : t
        );
        setTasks(updatedTasks);
        api.saveTasksOffline(updatedTasks);
      } else {
        const updatedTasks = tasks.map(t =>
          t.id === id ? { ...t, completed: !t.completed } : t
        );
        setTasks(updatedTasks);
        api.saveTasksOffline(updatedTasks);
      }
    } catch (error) {
      console.error('Error updating task:', error);
      const updatedTasks = tasks.map(t =>
        t.id === id ? { ...t, completed: !t.completed } : t
      );
      setTasks(updatedTasks);
      api.saveTasksOffline(updatedTasks);
    }
  };

  const handleTaskClick = (task: Task) => {
    if (!task.completed) {
      setSelectedTask(task);
      setIsModalOpen(true);
    }
  };

  const handleCompleteTask = async () => {
    if (!selectedTask) return;
    await toggleTaskCompletion(selectedTask.id);
  };

  const handleDelayTask = async (minutes: number) => {
    if (!selectedTask) return;
    
    try {
      const response = await api.delayTask(Number(selectedTask.id), minutes);
      
      if (response.success && response.data) {
        const updatedTask = response.data as ApiTaskResponse;
        const updatedTasks = tasks.map(t =>
          t.id === selectedTask.id 
            ? { ...t, scheduled_time: updatedTask.scheduled_time } 
            : t
        );
        setTasks(updatedTasks);
        api.saveTasksOffline(updatedTasks);
      }
    } catch (error) {
      console.error('Error delaying task:', error);
    }
  };

  return (
    <div className="p-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white">Dashboard</h1>
        <p className="text-gray-400">Welcome back, {user?.name || user?.email || 'User'}!</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 mb-8">
        <GlassCard className="lg:col-span-3">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-xl font-semibold">My Tasks</h2>
            <FocusModeToggle />
          </div>

          {/* Add Task Form */}
          <form onSubmit={handleAddTask} className="mb-6">
            <div className="flex flex-col sm:flex-row gap-2">
              <input
                type="text"
                value={newTask}
                onChange={(e) => setNewTask(e.target.value)}
                placeholder="Add a new task..."
                className="flex-1 px-4 py-2 bg-black/30 border border-white/10 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-white placeholder-gray-500"
              />
              <div className="flex gap-2">
                <div className="relative">
                  <input
                    type="time"
                    value={scheduledTime}
                    onChange={(e) => setScheduledTime(e.target.value)}
                    className="px-3 py-2 bg-black/30 border border-white/10 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 text-white [color-scheme:dark]"
                    title="Schedule time"
                  />
                </div>
                <button
                  type="submit"
                  className="px-4 py-2 bg-gradient-to-r from-blue-500 to-purple-500 text-white rounded-lg hover:opacity-90 transition-opacity whitespace-nowrap"
                >
                  Add Task
                </button>
              </div>
            </div>
            {scheduledTime && (
              <p className="text-xs text-orange-400 mt-2 flex items-center gap-1">
                <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                Task will be scheduled for {scheduledTime}
              </p>
            )}
          </form>

          {/* Tasks List */}
          {loading ? (
            <div className="flex justify-center items-center h-32">
              <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-blue-500"></div>
            </div>
          ) : tasks.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              <p>No tasks yet. Add your first task to get started!</p>
            </div>
          ) : (
            <div className="space-y-4">
              {tasks.map((task) => (
                <TaskCard
                  key={task.id}
                  task={task}
                  onToggle={toggleTaskCompletion}
                  onClick={handleTaskClick}
                />
              ))}
            </div>
          )}
        </GlassCard>

        {/* Right Panel */}
        <div className="space-y-6">
          <GlassCard>
            <h3 className="font-semibold mb-4">Today's Focus</h3>
            <div className="space-y-3">
              {tasks
                .filter(t => t.scheduled_time && !t.completed)
                .slice(0, 3)
                .map(task => (
                  <div key={task.id} className="p-3 bg-black/20 rounded-lg">
                    <p className="text-sm truncate">{task.title}</p>
                    <p className="text-xs text-orange-400">
                      {task.scheduled_time && new Date(task.scheduled_time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </p>
                  </div>
                ))}
              {tasks.filter(t => t.scheduled_time && !t.completed).length === 0 && (
                <p className="text-sm text-gray-500">No scheduled tasks</p>
              )}
            </div>
          </GlassCard>

          <GlassCard>
            <h3 className="font-semibold mb-4">Statistics</h3>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-gray-400">Completed</span>
                <span className="font-medium">{tasks.filter(t => t.completed).length}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Pending</span>
                <span className="font-medium">{tasks.filter(t => !t.completed).length}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Scheduled</span>
                <span className="font-medium">{tasks.filter(t => t.scheduled_time && !t.completed).length}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Total</span>
                <span className="font-medium">{tasks.length}</span>
              </div>
            </div>
          </GlassCard>

          <GlassCard>
            <h3 className="font-semibold mb-4">Quick Access</h3>
            <div className="space-y-2">
              <a href="/chat" className="block p-3 bg-black/20 rounded-lg hover:bg-black/30 transition-colors">
                <div className="flex justify-between items-center">
                  <span>AI Task Assistant</span>
                  <span className="text-xs bg-blue-500/20 text-blue-400 px-2 py-1 rounded">
                    New
                  </span>
                </div>
              </a>
              <a href="/dashboard/completed" className="block p-3 bg-black/20 rounded-lg hover:bg-black/30 transition-colors">
                <div className="flex justify-between items-center">
                  <span>Completed Tasks</span>
                  <span className="text-xs bg-green-500/20 text-green-400 px-2 py-1 rounded">
                    {tasks.filter(t => t.completed).length}
                  </span>
                </div>
              </a>
              <a href="/dashboard/pending" className="block p-3 bg-black/20 rounded-lg hover:bg-black/30 transition-colors">
                <div className="flex justify-between items-center">
                  <span>Pending Tasks</span>
                  <span className="text-xs bg-yellow-500/20 text-yellow-400 px-2 py-1 rounded">
                    {tasks.filter(t => !t.completed).length}
                  </span>
                </div>
              </a>
            </div>
          </GlassCard>
        </div>
      </div>

      {/* Task Action Modal */}
      <TaskActionModal
        isOpen={isModalOpen}
        taskTitle={selectedTask?.title || ''}
        onClose={() => {
          setIsModalOpen(false);
          setSelectedTask(null);
        }}
        onComplete={handleCompleteTask}
        onDelay={handleDelayTask}
      />
    </div>
  );
};

export default DashboardPage;