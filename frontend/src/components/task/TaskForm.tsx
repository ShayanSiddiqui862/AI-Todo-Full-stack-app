'use client';

import React, { useState } from 'react';

interface TaskFormData {
  title: string;
  description: string;
  priority: 'low' | 'medium' | 'high';
  tags: string[];
  dueDate: string;
  remindAt: string;
  recurrenceType: 'none' | 'daily' | 'weekly' | 'monthly';
  recurrenceInterval: number;
  scheduledTime: string;
}

interface TaskFormProps {
  onSubmit: (data: TaskFormData) => void;
}

const TaskForm: React.FC<TaskFormProps> = ({ onSubmit }) => {
  const [formData, setFormData] = useState<TaskFormData>({
    title: '',
    description: '',
    priority: 'medium',
    tags: [],
    dueDate: '',
    remindAt: '',
    recurrenceType: 'none',
    recurrenceInterval: 1,
    scheduledTime: '',
  });
  
  const [tagInput, setTagInput] = useState('');

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleAddTag = () => {
    if (tagInput.trim() && !formData.tags.includes(tagInput.trim())) {
      setFormData(prev => ({
        ...prev,
        tags: [...prev.tags, tagInput.trim()]
      }));
      setTagInput('');
    }
  };

  const handleRemoveTag = (tagToRemove: string) => {
    setFormData(prev => ({
      ...prev,
      tags: prev.tags.filter(tag => tag !== tagToRemove)
    }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(formData);
  };

  return (
    <form onSubmit={handleSubmit} className="mb-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
        <div className="md:col-span-2">
          <label htmlFor="title" className="block text-sm font-medium text-gray-300 mb-1">
            Task Title *
          </label>
          <input
            type="text"
            id="title"
            name="title"
            value={formData.title}
            onChange={handleChange}
            required
            className="w-full px-3 py-2 bg-black/30 border border-white/10 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-white placeholder-gray-500"
            placeholder="What needs to be done?"
          />
        </div>

        <div className="md:col-span-2">
          <label htmlFor="description" className="block text-sm font-medium text-gray-300 mb-1">
            Description
          </label>
          <textarea
            id="description"
            name="description"
            value={formData.description}
            onChange={handleChange}
            rows={2}
            className="w-full px-3 py-2 bg-black/30 border border-white/10 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-white placeholder-gray-500"
            placeholder="Add details about the task..."
          />
        </div>

        <div>
          <label htmlFor="priority" className="block text-sm font-medium text-gray-300 mb-1">
            Priority
          </label>
          <select
            id="priority"
            name="priority"
            value={formData.priority}
            onChange={handleChange}
            className="w-full px-3 py-2 bg-black/30 border border-white/10 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-white"
          >
            <option value="low">Low</option>
            <option value="medium">Medium</option>
            <option value="high">High</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-300 mb-1">
            Tags
          </label>
          <div className="flex">
            <input
              type="text"
              value={tagInput}
              onChange={(e) => setTagInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && (e.preventDefault(), handleAddTag())}
              className="flex-1 px-3 py-2 bg-black/30 border border-white/10 rounded-l-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-white placeholder-gray-500"
              placeholder="Add a tag..."
            />
            <button
              type="button"
              onClick={handleAddTag}
              className="px-3 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-r-lg"
            >
              Add
            </button>
          </div>
          
          {/* Display added tags */}
          <div className="mt-2 flex flex-wrap gap-1">
            {formData.tags.map((tag, index) => (
              <span 
                key={index} 
                className="inline-flex items-center px-2 py-1 bg-blue-500/20 text-blue-300 rounded text-xs"
              >
                {tag}
                <button
                  type="button"
                  onClick={() => handleRemoveTag(tag)}
                  className="ml-1 text-blue-200 hover:text-white"
                >
                  ×
                </button>
              </span>
            ))}
          </div>
        </div>

        <div>
          <label htmlFor="dueDate" className="block text-sm font-medium text-gray-300 mb-1">
            Due Date
          </label>
          <input
            type="date"
            id="dueDate"
            name="dueDate"
            value={formData.dueDate}
            onChange={handleChange}
            className="w-full px-3 py-2 bg-black/30 border border-white/10 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-white"
          />
        </div>

        <div>
          <label htmlFor="remindAt" className="block text-sm font-medium text-gray-300 mb-1">
            Reminder Time
          </label>
          <input
            type="datetime-local"
            id="remindAt"
            name="remindAt"
            value={formData.remindAt}
            onChange={handleChange}
            className="w-full px-3 py-2 bg-black/30 border border-white/10 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-white"
          />
        </div>

        <div>
          <label htmlFor="recurrenceType" className="block text-sm font-medium text-gray-300 mb-1">
            Recurrence
          </label>
          <select
            id="recurrenceType"
            name="recurrenceType"
            value={formData.recurrenceType}
            onChange={handleChange}
            className="w-full px-3 py-2 bg-black/30 border border-white/10 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-white"
          >
            <option value="none">No Recurrence</option>
            <option value="daily">Daily</option>
            <option value="weekly">Weekly</option>
            <option value="monthly">Monthly</option>
          </select>
        </div>

        {formData.recurrenceType !== 'none' && (
          <div>
            <label htmlFor="recurrenceInterval" className="block text-sm font-medium text-gray-300 mb-1">
              Repeat Every
            </label>
            <input
              type="number"
              id="recurrenceInterval"
              name="recurrenceInterval"
              min="1"
              value={formData.recurrenceInterval}
              onChange={handleChange}
              className="w-full px-3 py-2 bg-black/30 border border-white/10 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-white"
            />
          </div>
        )}

        <div>
          <label htmlFor="scheduledTime" className="block text-sm font-medium text-gray-300 mb-1">
            Schedule Time
          </label>
          <input
            type="time"
            id="scheduledTime"
            name="scheduledTime"
            value={formData.scheduledTime}
            onChange={handleChange}
            className="w-full px-3 py-2 bg-black/30 border border-white/10 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-white [color-scheme:dark]"
          />
        </div>
      </div>

      <button
        type="submit"
        className="w-full px-4 py-2 bg-gradient-to-r from-blue-500 to-purple-500 text-white rounded-lg hover:opacity-90 transition-opacity"
      >
        Add Task
      </button>
    </form>
  );
};

export default TaskForm;