# Evolution of Todo - Phase III Constitution
## AI-Powered Todo Chatbot - Supreme Law of Development

This constitution serves as the supreme law governing all development activities for Phase III: AI-Powered Todo Chatbot. All implementations must adhere to these principles without exception.

## 1. Fundamental Principles

### 1.1 Spec-Driven Development (SDD)
- **No code shall be written without a corresponding Task ID** derived from `sp.plan` and `sp.specify`
- All development must follow the SDD-RP (Spec-Driven Development with Recursive Planning) methodology
- Iterative refinement of specifications is mandatory until code generation achieves correctness
- Manual coding is strictly forbidden - all code must be generated from verified specifications

### 1.2 The Stateless Agent Pattern
- The entire chatbot architecture must follow the Stateless Agent Pattern
- **The Chat API endpoint (POST /api/chat) must be completely stateless**
- All conversation history and state must be persisted to Neon PostgreSQL database, never held in server memory
- Each API request must be self-contained with all necessary context retrieved from the database

### 1.3 Strict Agentic Workflow
The following **Stateless Request Cycle** is mandatory for all implementations:

1. Receive user message
2. Fetch conversation history from DB
3. Store user message in DB
4. Run Agent (OpenAI Agents SDK) with MCP Tools
5. Agent invokes MCP Tools (stateless logic)
6. Store Assistant response in DB
7. Return response to client

## 2. Technology Stack & Versioning Requirements

### 2.1 Frontend
- **OpenAI ChatKit** for conversational UI components
- Next.js 16+ with App Router
- TypeScript for type safety
- Tailwind CSS for responsive styling

### 2.2 Backend
- **Python 3.13+** (minimum version requirement)
- FastAPI for web framework
- OpenAI Agents SDK for AI orchestration
- Model Context Protocol (MCP) Official SDK
- SQLModel for database ORM
- Neon Serverless PostgreSQL for persistence
- Better Auth for JWT security

### 2.3 MCP Server Components
- Dedicated MCP server for tool integration
- Stateful business logic encapsulation within MCP tools
- Stateless agent communication with MCP tools only

## 3. Architectural Patterns

### 3.1 Three-Tier Architecture
```
[OpenAI ChatKit UI] ↔ [FastAPI Chat Endpoint] ↔ [MCP Tools Server] ↔ [Neon PostgreSQL]
```

### 3.2 Interaction Flow
- Frontend (ChatKit) communicates with backend via stateless API calls
- Backend fetches context from database before invoking agent
- Agent operates entirely statelessly, accessing business logic through MCP tools
- MCP tools handle all database interactions and business logic
- All conversation state persists in Neon PostgreSQL

### 3.3 MCP Tool Specifications
The following MCP tools are **mandatory** and must be implemented:

#### 3.3.1 add_task
- Creates a new task for the authenticated user
- Validates input parameters and creates record in DB
- Returns task ID upon successful creation

#### 3.3.2 list_tasks
- Retrieves tasks with filters (status, priority, date ranges)
- Enforces row-level security (user isolation)
- Returns paginated results when appropriate

#### 3.3.3 complete_task
- Toggles task completion status
- Updates timestamp and preserves audit trail
- Validates user ownership before allowing operation

#### 3.3.4 delete_task
- Removes task from user's collection
- Implements soft-delete pattern where appropriate
- Maintains referential integrity

#### 3.3.5 update_task
- Modifies task title, description, or metadata
- Preserves original creation timestamp
- Updates modification timestamp

## 4. Coding Standards

### 4.1 Python Standards
- **Type Hints Mandatory**: All functions must include proper type annotations
- **SQLModel Usage**: All database models must inherit from SQLModel
- **Error Handling**: Implement comprehensive error handling with proper logging
- **Async/await**: Use asynchronous patterns for all I/O operations
- **Dependency Injection**: Use FastAPI's built-in DI system

### 4.2 Database Schema Standards
- Use UUID primary keys for all tables
- Implement proper foreign key relationships
- Apply indexes strategically for performance
- Include created_at and updated_at timestamps
- Use soft deletion where audit trail is important

### 4.3 MCP Tool Implementation
- Each MCP tool must be a separate Python module
- Tools must implement proper input/output schemas
- Business logic validation within each tool
- Consistent error response format across all tools

## 5. Security Mandates

### 5.1 Authentication & Authorization
- **Better Auth Integration**: Must utilize existing JWT authentication from Phase II
- **Row-Level Security**: Agent must strictly enforce user isolation
- **JWT Token Validation**: Validate token on every API request
- **Scope Verification**: Verify agent permissions before executing operations

### 5.2 Data Isolation Requirements
- An agent acting for User A must never access User B's tasks via MCP tools
- All database queries must include user_id filters
- MCP tools must validate user ownership before any operations
- Implement proper multi-tenancy patterns

### 5.3 Frontend Security
- **Domain Allowlist**: Frontend URL must be configured in OpenAI's security settings for ChatKit
- CORS policies must be properly configured
- Client-side token storage must follow security best practices
- Implement proper request rate limiting

### 5.4 MCP Server Security
- Secure communication between agent and MCP tools
- Input validation on all MCP tool parameters
- Implement proper authentication for MCP endpoints
- Audit logging for all MCP tool invocations

## 6. Quality Assurance Requirements

### 6.1 Testing Standards
- Unit tests for all MCP tools
- Integration tests for agent-tool interactions
- End-to-end tests for complete conversation flows
- Security testing for authentication and authorization

### 6.2 Performance Benchmarks
- API response times under 500ms for 95th percentile
- MCP tool execution times under 200ms for 95th percentile
- Database query optimization for all common operations
- Proper connection pooling configuration

## 7. Compliance & Validation

All implementations must undergo compliance validation against this constitution before acceptance. Any deviation requires explicit constitutional amendment through formal change management process.

---

*This constitution is effective immediately and governs all Phase III development activities. Amendments require approval from the Chief System Architect.*