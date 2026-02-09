# API Specification: Chat Endpoints for AI-Powered Todo Chatbot

**Document**: `specs/api/chat-endpoints.md`
**Created**: 2026-02-07
**Status**: Draft
**Input**: API endpoints for the AI-powered chatbot backend with stateless request processing and conversation persistence

## Overview

This specification defines the API endpoints required for the AI-powered chatbot functionality. The backend implements a stateless architecture where all conversation state is persisted to the database rather than held in server memory.

## Endpoint: POST /api/{user_id}/chat

### Purpose
Process chat messages from authenticated users through the OpenAI Agents SDK and return AI-generated responses.

### Request Parameters
- **Path Parameter**: `{user_id}` - UUID of the authenticated user (extracted from JWT)
- **Headers**:
  - `Authorization`: Bearer {jwt_token} - User authentication token
  - `Content-Type`: application/json

### Request Body
```json
{
  "message": "string",
  "thread_id": "string (optional)",
  "metadata": {
    "timestamp": "ISO 8601 datetime",
    "client_info": "string"
  }
}
```

### Response Body (Success)
```json
{
  "response": "string",
  "thread_id": "string",
  "conversation_id": "UUID",
  "created_at": "ISO 8601 datetime",
  "status": "success"
}
```

### Response Body (Error)
```json
{
  "error": "string",
  "code": "string",
  "status": "error"
}
```

### Authentication & Authorization
- All requests must include a valid JWT token in the Authorization header
- The `user_id` in the path must match the user ID in the JWT token
- User must be authorized to access their own chat endpoints
- Row-level security ensures users can only access their own conversations

### State Management
- All conversation state must be persisted to the database
- No conversation state should be stored in server memory
- Conversation history is retrieved from database before processing each message
- Each response is stored to the database after processing

### Processing Flow
1. Validate JWT token and extract user context
2. Fetch conversation history from database for the user
3. Store incoming message to database
4. Initialize OpenAI Agent with user's conversation history
5. Execute agent to process the message and select appropriate MCP tools
6. Agent interacts with MCP tools as needed
7. Receive agent response
8. Store agent response to database
9. Return response to client

### Error Handling
- **400 Bad Request**: Invalid request format, missing required fields
- **401 Unauthorized**: Invalid or missing JWT token
- **403 Forbidden**: User attempting to access another user's endpoint
- **404 Not Found**: User ID not found in system
- **500 Internal Server Error**: Server processing error, MCP tool failure

## Database Interactions

### Conversation Entity
- `conversation_id`: UUID (Primary Key)
- `user_id`: UUID (Foreign Key to users table)
- `created_at`: DateTime
- `updated_at`: DateTime
- `metadata`: JSON

### Message Entity
- `message_id`: UUID (Primary Key)
- `conversation_id`: UUID (Foreign Key to conversations table)
- `sender`: Enum ('user' | 'assistant')
- `content`: Text
- `timestamp`: DateTime
- `metadata`: JSON

## Rate Limiting
- Per-user rate limiting: 100 requests per minute
- Global rate limiting: 1000 requests per minute

## Security Measures
- Input sanitization on all user messages to prevent injection attacks
- JWT token validation with proper signature verification
- User ID validation to prevent access to other users' conversations
- SQL injection prevention through parameterized queries
- Proper logging of all chat interactions for security auditing

## Performance Requirements
- Response time: 95% of requests under 3 seconds
- Database connection pooling with maximum 20 concurrent connections
- Proper caching of user profiles and frequently accessed data
- Asynchronous processing where possible

## Validation Requirements
- Validate user_id format is a proper UUID
- Validate message length is not more than 10,000 characters
- Validate JWT token has not expired
- Validate user account is active and not suspended