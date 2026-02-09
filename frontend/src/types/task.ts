export interface Task {
  id: string;
  title: string;
  description?: string;
  completed: boolean;
  priority: 'low' | 'medium' | 'high';
  tags: string[];
  dueDate?: string;
  remindAt?: string;
  recurrenceType: 'none' | 'daily' | 'weekly' | 'monthly';
  recurrenceInterval: number;
  createdAt: string;
  scheduled_time?: string;
}