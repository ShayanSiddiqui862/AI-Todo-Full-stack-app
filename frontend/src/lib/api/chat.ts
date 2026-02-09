import { BACKEND_URL } from '@/lib/config';

// Define types for chat API requests and responses
export interface ChatRequest {
  message: string;
  thread_id?: string;
  metadata?: Record<string, any>;
}

export interface ChatResponse {
  response: string;
  thread_id?: string;
  conversation_id: string;
  created_at: string; // ISO date string
  status: string;
}

export interface ErrorResponse {
  error: string;
  code: string;
  status: string;
}

/**
 * Sends a message to the chat API and returns the response.
 * 
 * @param message The user's message to send
 * @param userId The ID of the authenticated user
 * @param conversationId Optional conversation ID for continuity
 * @returns Promise resolving to the chat response
 */
export const sendMessage = async (
  message: string,
  userId: string,
  conversationId?: string
): Promise<ChatResponse> => {
  try {
    // Construct the request body
    const requestBody: ChatRequest = {
      message,
      thread_id: conversationId,
      metadata: {
        timestamp: new Date().toISOString(),
        source: 'frontend-chat-component'
      }
    };

    // Get the authentication token
    // In a real implementation, this would come from your auth context
    const token = localStorage.getItem('authToken');

    // Make the API request
    const response = await fetch(`${BACKEND_URL}/api/users/${userId}/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`, // Include auth token in header
      },
      body: JSON.stringify(requestBody),
    });

    // Check if the response is OK
    if (!response.ok) {
      const errorData: ErrorResponse = await response.json().catch(() => ({
        error: 'Unknown error',
        code: 'UNKNOWN',
        status: 'error'
      }));

      throw new Error(`Chat API error: ${errorData.error} (${errorData.code})`);
    }

    // Parse and return the response
    const data: ChatResponse = await response.json();
    return data;
  } catch (error) {
    // Handle network errors or parsing errors
    if (error instanceof Error) {
      throw new Error(`Network error: ${error.message}`);
    } else {
      throw new Error('Unknown error occurred while sending message');
    }
  }
};

/**
 * Gets conversation history from the API.
 * 
 * @param userId The ID of the authenticated user
 * @param conversationId The ID of the conversation to retrieve
 * @returns Promise resolving to an array of messages
 */
export const getConversationHistory = async (
  userId: string,
  conversationId: string
): Promise<any[]> => { // Using 'any' temporarily until we define message types
  try {
    // Get the authentication token
    const token = localStorage.getItem('authToken');

    // Make the API request
    const response = await fetch(`${BACKEND_URL}/api/users/${userId}/conversations/${conversationId}/messages`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`, // Include auth token in header
      },
    });

    // Check if the response is OK
    if (!response.ok) {
      const errorData: ErrorResponse = await response.json().catch(() => ({
        error: 'Unknown error',
        code: 'UNKNOWN',
        status: 'error'
      }));

      throw new Error(`Get conversation history API error: ${errorData.error} (${errorData.code})`);
    }

    // Parse and return the response
    const data: any[] = await response.json(); // Using 'any' temporarily
    return data;
  } catch (error) {
    // Handle network errors or parsing errors
    if (error instanceof Error) {
      throw new Error(`Network error: ${error.message}`);
    } else {
      throw new Error('Unknown error occurred while getting conversation history');
    }
  }
};

/**
 * Creates a new conversation.
 * 
 * @param userId The ID of the authenticated user
 * @param title Optional title for the conversation
 * @returns Promise resolving to the new conversation data
 */
export const createConversation = async (
  userId: string,
  title?: string
): Promise<any> => { // Using 'any' temporarily until we define conversation types
  try {
    // Get the authentication token
    const token = localStorage.getItem('authToken');

    // Construct the request body
    const requestBody = {
      title: title || `New Chat ${new Date().toISOString()}`
    };

    // Make the API request
    const response = await fetch(`${BACKEND_URL}/api/users/${userId}/conversations`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`, // Include auth token in header
      },
      body: JSON.stringify(requestBody),
    });

    // Check if the response is OK
    if (!response.ok) {
      const errorData: ErrorResponse = await response.json().catch(() => ({
        error: 'Unknown error',
        code: 'UNKNOWN',
        status: 'error'
      }));

      throw new Error(`Create conversation API error: ${errorData.error} (${errorData.code})`);
    }

    // Parse and return the response
    const data: any = await response.json(); // Using 'any' temporarily
    return data;
  } catch (error) {
    // Handle network errors or parsing errors
    if (error instanceof Error) {
      throw new Error(`Network error: ${error.message}`);
    } else {
      throw new Error('Unknown error occurred while creating conversation');
    }
  }
};