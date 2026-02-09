# Neon Database Setup Guide

This document explains how to set up and configure the Neon database for the RAG Chatbot application.

## Overview

The application uses Neon (PostgreSQL) database to store:
- User credentials (username, email, password hashes)
- Chat sessions (per user)
- Chat messages (user and assistant messages)

## Environment Configuration

1. Create a Neon database project at [neon.tech](https://neon.tech)
2. Get your connection string from the Neon dashboard
3. Add the following to your `.env` file:

```bash
DATABASE_URL=postgresql://username:password@ep-xxxxx.us-east-1.aws.neon.tech/dbname?sslmode=require
```

## Database Schema

The application automatically creates the following tables:

### users table
- `id`: SERIAL PRIMARY KEY
- `username`: VARCHAR(255) UNIQUE NOT NULL
- `password_hash`: VARCHAR(255) NOT NULL
- `email`: VARCHAR(255) UNIQUE
- `created_at`: TIMESTAMP DEFAULT CURRENT_TIMESTAMP
- `updated_at`: TIMESTAMP DEFAULT CURRENT_TIMESTAMP

### chat_sessions table
- `id`: SERIAL PRIMARY KEY
- `user_id`: INTEGER REFERENCES users(id) ON DELETE CASCADE
- `session_title`: VARCHAR(255)
- `created_at`: TIMESTAMP DEFAULT CURRENT_TIMESTAMP
- `updated_at`: TIMESTAMP DEFAULT CURRENT_TIMESTAMP

### chat_messages table
- `id`: SERIAL PRIMARY KEY
- `session_id`: INTEGER REFERENCES chat_sessions(id) ON DELETE CASCADE
- `user_id`: INTEGER REFERENCES users(id) ON DELETE CASCADE
- `role`: VARCHAR(50) NOT NULL ('user' or 'assistant')
- `content`: TEXT NOT NULL
- `timestamp`: TIMESTAMP DEFAULT CURRENT_TIMESTAMP

## Database Service

The `NeonDBService` class provides the following functionality:

### Connection Management
- Connection pooling with asyncpg
- Automatic table creation on startup
- Error handling for connection failures

### User Operations
- `create_user(username, password_hash, email)`: Create a new user
- `get_user_by_username(username)`: Retrieve user by username
- `update_user_password(username, new_password_hash)`: Update user password
- `update_user_email(username, new_email)`: Update user email

### Chat Session Operations
- `create_chat_session(user_id, session_title)`: Create a new chat session
- `get_chat_session_by_id(session_id)`: Get session by ID
- `get_user_sessions(user_id)`: Get all sessions for a user
- `update_session_title(session_id, title)`: Update session title

### Chat Message Operations
- `add_chat_message(session_id, user_id, role, content)`: Add a message to a session
- `get_chat_messages_by_session(session_id)`: Get all messages for a session

## Integration Points

### Authentication
- The authentication module uses Neon DB to store and retrieve user credentials
- Frontend uses Better Auth components that communicate with Next.js API proxy
- Next.js proxy forwards requests to FastAPI backend which stores data in Neon DB
- Passwords are hashed using SHA-256 (should use bcrypt in production)

### RAG Queries
- Each RAG query creates a chat session and stores the user query and AI response
- Sessions are linked to authenticated users

### Session Management
- The sessions API manages chat sessions in the database
- Provides endpoints for creating, retrieving, and managing chat sessions

## Error Handling

The database service includes proper error handling:
- Connection errors are caught and logged
- Database operations are wrapped in transactions where appropriate
- Foreign key constraints ensure data integrity

## Security Considerations

- Use environment variables for database credentials
- Enable SSL mode for production deployments
- Implement proper input validation
- Consider using bcrypt for password hashing instead of SHA-256