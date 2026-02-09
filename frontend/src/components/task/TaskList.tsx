'use client';

import React, { useState, useEffect } from 'react';
import TaskCard from './TaskCard';
import { Task } from '../../types/task';

interface TaskListProps {
  tasks: Task[];
  onToggle: (id: string) => void;
  onClick: (task: Task) => void;
}

const TaskList: React.FC<TaskListProps> = ({ tasks, onToggle, onClick }) => {
  const [filter, setFilter] = useState<'all' | 'active' | 'completed'>('all');
  const [sortBy, setSortBy] = useState<'date' | 'priority' | 'title'>('date');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');
  const [priorityFilter, setPriorityFilter] = useState<string>('all');
  const [tagFilter, setTagFilter] = useState<string>('all');

  // Get unique tags from tasks for filter dropdown
  const allTags = Array.from(
    new Set(tasks.flatMap(task => task.tags || []))
  );

  // Apply filters and sorting
  const filteredAndSortedTasks = tasks
    .filter(task => {
      // Apply completion filter
      if (filter === 'active' && task.completed) return false;
      if (filter === 'completed' && !task.completed) return false;
      
      // Apply priority filter
      if (priorityFilter !== 'all' && task.priority !== priorityFilter) return false;
      
      // Apply tag filter
      if (tagFilter !== 'all' && task.tags && !task.tags.includes(tagFilter)) return false;
      
      return true;
    })
    .sort((a, b) => {
      let comparison = 0;
      
      switch (sortBy) {
        case 'date':
          comparison = new Date(a.createdAt).getTime() - new Date(b.createdAt).getTime();
          break;
        case 'priority':
          // Define priority order: high > medium > low
          const priorityOrder = { high: 3, medium: 2, low: 1 };
          comparison = priorityOrder[b.priority as keyof typeof priorityOrder] - priorityOrder[a.priority as keyof typeof priorityOrder];
          break;
        case 'title':
          comparison = a.title.localeCompare(b.title);
          break;
      }
      
      return sortOrder === 'asc' ? comparison : -comparison;
    });

  return (
    <div className="space-y-4">
      {/* Filters and Sorting Controls */}
      <div className="flex flex-wrap gap-4 p-4 bg-black/20 rounded-lg">
        <div>
          <label className="block text-xs text-gray-400 mb-1">Status</label>
          <select
            value={filter}
            onChange={(e) => setFilter(e.target.value as 'all' | 'active' | 'completed')}
            className="px-3 py-1 bg-black/30 border border-white/10 rounded text-white text-sm"
          >
            <option value="all">All Tasks</option>
            <option value="active">Active</option>
            <option value="completed">Completed</option>
          </select>
        </div>
        
        <div>
          <label className="block text-xs text-gray-400 mb-1">Priority</label>
          <select
            value={priorityFilter}
            onChange={(e) => setPriorityFilter(e.target.value)}
            className="px-3 py-1 bg-black/30 border border-white/10 rounded text-white text-sm"
          >
            <option value="all">All Priorities</option>
            <option value="high">High</option>
            <option value="medium">Medium</option>
            <option value="low">Low</option>
          </select>
        </div>
        
        <div>
          <label className="block text-xs text-gray-400 mb-1">Tag</label>
          <select
            value={tagFilter}
            onChange={(e) => setTagFilter(e.target.value)}
            className="px-3 py-1 bg-black/30 border border-white/10 rounded text-white text-sm"
          >
            <option value="all">All Tags</option>
            {allTags.map((tag, index) => (
              <option key={index} value={tag}>{tag}</option>
            ))}
          </select>
        </div>
        
        <div>
          <label className="block text-xs text-gray-400 mb-1">Sort By</label>
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value as 'date' | 'priority' | 'title')}
            className="px-3 py-1 bg-black/30 border border-white/10 rounded text-white text-sm"
          >
            <option value="date">Date</option>
            <option value="priority">Priority</option>
            <option value="title">Title</option>
          </select>
        </div>
        
        <div>
          <label className="block text-xs text-gray-400 mb-1">Order</label>
          <select
            value={sortOrder}
            onChange={(e) => setSortOrder(e.target.value as 'asc' | 'desc')}
            className="px-3 py-1 bg-black/30 border border-white/10 rounded text-white text-sm"
          >
            <option value="desc">Descending</option>
            <option value="asc">Ascending</option>
          </select>
        </div>
      </div>

      {/* Tasks List */}
      {filteredAndSortedTasks.length === 0 ? (
        <div className="text-center py-8 text-gray-500">
          <p>No tasks match the current filters.</p>
        </div>
      ) : (
        <div className="space-y-4">
          {filteredAndSortedTasks.map((task) => (
            <TaskCard
              key={task.id}
              task={task}
              onToggle={onToggle}
              onClick={onClick}
            />
          ))}
        </div>
      )}
    </div>
  );
};

export default TaskList;