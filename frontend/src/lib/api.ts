// Centralized API client for communication with FastAPI backend
// Located at /frontend/lib/api.ts as specified in requirements

interface ApiResponse<T = any> {
  data?: T;
  error?: string;
  success: boolean;
}

class ApiClient {
  private baseUrl: string;
  private token: string | null = null;

  constructor() {
    this.baseUrl = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000'; // Backend FastAPI server
  }

  // Set authentication token
  setToken(token: string) {
    this.token = token;
  }

  // Remove authentication token
  removeToken() {
    this.token = null;
  }

  // Generic request method with JWT token handling
  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<ApiResponse<T>> {
    const url = `${this.baseUrl}${endpoint}`;

    // Use in-memory token, or fallback to localStorage token (handles race conditions on page load)
    const token = this.token || (typeof window !== 'undefined' ? localStorage.getItem('authToken') : null);

    const headers = {
      'Content-Type': 'application/json',
      ...(token && { 'Authorization': `Bearer ${token}` }),
      ...options.headers,
    };

    try {
      const response = await fetch(url, {
        ...options,
        headers,
      });

      // Handle different response status codes appropriately
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        const errorMessage = errorData.detail || `HTTP error! status: ${response.status}`;
        throw new Error(errorMessage);
      }

      // Some endpoints might not return JSON (e.g., DELETE requests)
      const contentType = response.headers.get('content-type');
      let data = null;
      if (contentType && contentType.includes('application/json')) {
        data = await response.json();
      }

      return { data, success: true };
    } catch (error: any) {
      console.error('API request failed:', error);
      return { error: error.message || 'Request failed', success: false };
    }
  }

  // Authentication methods - Updated to match actual backend routes
  async login(username: string, password: string) {
    // Backend expects username (not email) for login
    return this.request('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify({ username, password }),
    });
  }

  async signup(email: string, password: string, name: string) {
    // Backend expects username field as well as full_name
    return this.request('/api/auth/register', {
      method: 'POST',
      body: JSON.stringify({
        email,
        password,
        username: name.toLowerCase().replace(/\s+/g, '_'), // Generate username from name
        full_name: name
      }),
    });
  }

  async logout(refreshToken: string) {
    // Backend logout requires the refresh token
    return this.request('/api/auth/logout', {
      method: 'POST',
      body: JSON.stringify({ refresh_token: refreshToken }),
    });
  }

  // User methods - Updated to match actual backend routes
  async getUserProfile() {
    return this.request('/api/auth/me');  // Actual backend endpoint for user profile
  }

  // Additional authentication methods
  async refreshToken(refreshToken: string) {
    return this.request('/api/auth/refresh', {
      method: 'POST',
      body: JSON.stringify({ refresh_token: refreshToken }),
    });
  }

  async initiateGoogleAuth() {
    return this.request('/api/auth/google', {
      method: 'GET',
    });
  }

  async completeGoogleAuth(code: string) {
    return this.request('/api/auth/google/callback', {
      method: 'POST',
      body: JSON.stringify({ code }),
    });
  }

  // Task methods - Updated to match actual backend routes
  async getTasks() {
    return this.request('/api/tasks');  // Actual backend endpoint for getting tasks
  }

  async getCompletedTasks() {
    return this.request('/api/tasks/completed');  // Backend endpoint for completed tasks
  }

  async getPendingTasks() {
    return this.request('/api/tasks/pending');  // Backend endpoint for pending tasks
  }

  async getTask(taskId: number) {
    return this.request(`/api/tasks/${taskId}`);  // Backend endpoint for specific task
  }

  async createTask(taskData: any) {
    return this.request('/api/tasks', {  // Actual backend endpoint for creating tasks
      method: 'POST',
      body: JSON.stringify(taskData),
    });
  }

  async updateTask(taskId: number, taskData: any) {
    return this.request(`/api/tasks/${taskId}`, {  // Actual backend endpoint for updating tasks
      method: 'PUT',
      body: JSON.stringify(taskData),
    });
  }

  // Advanced task features API methods
  async searchTasks(query: string, userId?: string, limit: number = 20, offset: number = 0) {
    const params = new URLSearchParams({
      query,
      limit: limit.toString(),
      offset: offset.toString(),
    });
    if (userId) params.append('user_id', userId);
    
    return this.request(`/api/tasks/search?${params}`);
  }

  async getTasksWithFilters(
    userId: string,
    priority?: 'low' | 'medium' | 'high',
    tags?: string[],
    dueDateStart?: string,
    dueDateEnd?: string,
    completed?: boolean,
    sortBy: 'created_at' | 'due_date' | 'priority' = 'created_at',
    sortOrder: 'asc' | 'desc' = 'desc'
  ) {
    const params = new URLSearchParams({ user_id: userId });
    
    if (priority) params.append('priority', priority);
    if (tags) tags.forEach(tag => params.append('tags', tag));
    if (dueDateStart) params.append('due_date_start', dueDateStart);
    if (dueDateEnd) params.append('due_date_end', dueDateEnd);
    if (completed !== undefined) params.append('completed', completed.toString());
    params.append('sort_by', sortBy);
    params.append('sort_order', sortOrder);
    
    return this.request(`/api/tasks?${params}`);
  }

  async deleteTask(taskId: number) {
    return this.request(`/api/tasks/${taskId}`, {  // Actual backend endpoint for deleting tasks
      method: 'DELETE',
    });
  }

  async toggleTaskComplete(taskId: number) {
    return this.request(`/api/tasks/${taskId}/complete`, {  // Actual backend endpoint for toggling completion
      method: 'PATCH',
      body: JSON.stringify({}), // Empty body for toggle
    });
  }

  async delayTask(taskId: number, delayMinutes: number) {
    return this.request(`/api/tasks/${taskId}/delay`, {
      method: 'PATCH',
      body: JSON.stringify({ delay_minutes: delayMinutes }),
    });
  }

  // Offline capability with localStorage fallback
  async getTasksOffline(): Promise<any[]> {
    if (typeof window !== 'undefined') {
      const cachedTasks = localStorage.getItem('tasks');
      return cachedTasks ? JSON.parse(cachedTasks) : [];
    }
    return [];
  }

  async saveTasksOffline(tasks: any[]) {
    if (typeof window !== 'undefined') {
      localStorage.setItem('tasks', JSON.stringify(tasks));
    }
  }
}

// Create singleton instance
const api = new ApiClient();
export default api;

// Export types
export type { ApiResponse };