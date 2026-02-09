# Architecture Specification: Phase-3 AI-Powered Todo Chatbot

**Document**: `specs/architecture/phase3-chatbot.md`
**Created**: 2026-02-07
**Status**: Draft
**Input**: Architecture design for AI-powered chatbot integration using OpenAI ChatKit, Agents SDK, and MCP tools

## Overview

This document describes the architecture for Phase-3: AI-Powered Todo Chatbot. The system extends the existing Phase-2 full-stack web application with AI capabilities while maintaining security, scalability, and user data isolation.

## Architecture Diagram

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────────┐
│   OpenAI        │    │   Frontend       │    │   Backend Services  │
│   ChatKit UI    │◄──►│   (Next.js)      │◄──►│                     │
│                 │    │                  │    │  ┌─────────────────┐│
│  (Natural      │    │  ┌─────────────┐ │    │  │ Chat Endpoint   ││
│   Language     │    │  │ ChatKit     │ │    │  │ (/api/{id}/chat)││
│   Interface)   │    │  │ Provider    │ │    │  └─────────────────┘│
└─────────────────┘    │  └─────────────┘ │    │         │          │
                       │        │         │    │         ▼          │
                       │        ▼         │    │  ┌─────────────────┐│
                       │  ┌─────────────┐ │    │  │ OpenAI Agents   ││
                       │  │ Chat UI     │ │    │  │ SDK             ││
                       │  │ Components  │ │    │  └─────────────────┘│
                       │  └─────────────┘ │    │         │          │
                       └──────────────────┘    │         ▼          │
                                               │  ┌─────────────────┐│
                                               │  │ MCP Server      ││
                                               │  │                 ││
                                               │  │┌───────────────┐││
                                               │  ││ add_task      │││
                                               │  │├───────────────┤││
                                               │  ││ list_tasks    │││
                                               │  │├───────────────┤││
                                               │  ││ update_task   │││
                                               │  │├───────────────┤││
                                               │  ││ complete_task │││
                                               │  │├───────────────┤││
                                               │  ││ delete_task   │││
                                               │  │└───────────────┘││
                                               │  └─────────────────┘│
                                               │         │          │
                                               │         ▼          │
                    ┌──────────────────────────┼─────────────────────┤
                    │                          │                     │
                    │  ┌─────────────────────┐ │  ┌─────────────────┐│
                    │  │  Neon PostgreSQL  │ ◄──► │  SQLModel       ││
                    │  │    Database       │ │  │  ORM            ││
                    │  │                   │ │  │                 ││
                    │  │  ┌───────────────┐│ │  │  ┌─────────────┐││
                    │  │  │  Conversations││ │  │  │User Session │││
                    │  │  │    Table      ││ │  │  │  Management │││
                    │  │  └───────────────┘│ │  │  │(Better Auth)│││
                    │  │  ┌───────────────┐│ │  │  └─────────────┘││
                    │  │  │  Messages     ││◄───┼──────────────────││
                    │  │  │    Table      ││ │  └─────────────────┘│
                    │  │  └───────────────┘│ │                     │
                    │  │  ┌───────────────┐│ │                     │
                    │  │  │  Tasks        ││ │                     │
                    │  │  │    Table      ││ │                     │
                    │  │  └───────────────┘│ │                     │
                    │  └─────────────────────┘ │                     │
                    └─────────────────────────────────────────────────┘
```

## Component Architecture

### 1. Frontend Layer (OpenAI ChatKit)

**Components**:
- `<ChatKitProvider>`: Root provider component that manages the chat session
- `<Thread>`: Main conversation thread component
- `<MessageList>`: Displays the sequence of messages in the conversation
- `<SendMessageForm>`: Handles user input and message submission

**Responsibilities**:
- Provide the natural language interface for task management
- Authenticate users using JWT tokens from Better Auth
- Communicate with backend chat endpoint
- Display AI responses in a conversational format
- Maintain conversation history in the UI

**Configuration**:
- NEXT_PUBLIC_OPENAI_DOMAIN_KEY: Required for ChatKit hosting
- Authentication tokens passed from Better Auth system
- API endpoint configuration pointing to `/api/{user_id}/chat`

### 2. Backend API Layer (FastAPI)

**Endpoint**: `/api/{user_id}/chat`

**Characteristics**:
- Stateless request processing
- No conversation state stored in server memory
- Each request retrieves and stores conversation history from/to database

**Processing Flow**:
1. Validate JWT token and extract user context
2. Fetch conversation history from database
3. Store incoming user message to database
4. Initialize OpenAI Agent with context
5. Process message through Agent
6. Agent selects and executes appropriate MCP tools
7. Store AI response to database
8. Return response to client

**Dependencies**:
- Better Auth for JWT validation
- Neon PostgreSQL for conversation persistence
- OpenAI Agents SDK for AI processing
- MCP Client for tool invocation

### 3. AI Layer (OpenAI Agents SDK)

**Components**:
- AI Agent instance with conversation context
- Tool selection logic based on natural language input
- Response generation from tool outputs

**Responsibilities**:
- Interpret natural language user requests
- Select appropriate MCP tools based on intent
- Combine tool responses into coherent answers
- Maintain conversation context across interactions

**Configuration**:
- Model selection (GPT-4, GPT-4 Turbo, or latest appropriate model)
- Tool definitions linking to MCP server endpoints
- Context window management for conversation history

### 4. MCP Server Layer (Model Context Protocol)

**Architecture**: Separate service implementing MCP specification

**MCP Tools**:
- `add_task`: Create new tasks for the user
- `list_tasks`: Retrieve user's tasks with filtering
- `update_task`: Modify existing task properties
- `complete_task`: Mark tasks as completed
- `delete_task`: Remove tasks from user's list

**Characteristics**:
- Stateless operation - no persistent state between calls
- Direct database interactions using SQLModel
- User isolation enforcement
- Input validation and sanitization

**Dependencies**:
- Neon PostgreSQL database
- SQLModel ORM
- Authentication verification

### 5. Data Persistence Layer (Neon PostgreSQL + SQLModel)

**Entities**:
- `Conversation`: Stores conversation metadata and history
- `Message`: Individual messages between user and AI
- `Task`: User's todo items (extended from Phase-2 schema)

**Relationships**:
- One user to many conversations
- One conversation to many messages
- One user to many tasks

**Constraints**:
- Row-level security ensuring user data isolation
- Proper indexing for efficient querying
- Foreign key relationships maintaining data integrity

### 6. Authentication & Security Layer (Better Auth)

**Components**:
- JWT token generation and validation
- Session management
- User identity verification

**Integration Points**:
- Frontend authentication with token passing
- Backend API endpoint protection
- MCP tool access control

## Security Architecture

### Data Isolation
- Row-level security at database level
- User ID validation in all queries
- MCP tool validation ensuring user ownership

### Authentication Flow
1. User authenticates via Better Auth
2. JWT token issued and stored securely
3. Token passed to ChatKit components
4. Token validated on each backend request
5. User context extracted for database queries

### API Security
- Input sanitization on all endpoints
- Rate limiting to prevent abuse
- SQL injection prevention via ORM
- Proper error handling without information disclosure

## Scalability Considerations

### Horizontal Scaling
- Stateless backend allows for horizontal scaling
- Database connection pooling
- CDN for static assets
- MCP server containerization for independent scaling

### Performance Optimization
- Database indexing for frequent queries
- Connection pooling for database access
- Caching for frequently accessed user data
- Asynchronous processing where appropriate

## Deployment Architecture

### Frontend Deployment
- Static site hosting (Vercel, Netlify, or similar)
- Environment variable configuration for domain keys
- CDN distribution for global access

### Backend Deployment
- Containerized service (Docker)
- Auto-scaling based on request load
- Health checks for availability monitoring
- Blue-green deployment for zero-downtime updates

### MCP Server Deployment
- Separate container/service for isolation
- Independent scaling from main backend
- Health checks and monitoring
- Load balancing for high availability

## Monitoring & Observability

### Logging
- Structured logging for all components
- Conversation tracking for debugging
- Error logging with context
- Performance metrics collection

### Metrics
- API response times
- Database query performance
- Conversation success rates
- Tool usage statistics

### Alerting
- Service availability monitoring
- Error rate thresholds
- Performance degradation alerts
- Security incident notifications

## Integration Points

### Existing Systems
- Leverages existing Better Auth JWT system
- Extends Phase-2 task model with new functionality
- Maintains same database schema where applicable
- Integrates with existing deployment infrastructure

### External Services
- OpenAI API for agent processing
- OpenAI ChatKit for UI components
- MCP protocol for tool communication
- Neon PostgreSQL for managed database service