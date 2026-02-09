# Implementation Plan: FastAPI Backend for Todo Application

**Branch**: `001-todo-backend-requirements` | **Date**: 2026-01-10 | **Spec**: [link](./spec.md)
**Input**: Feature specification from `/specs/001-todo-backend-requirements/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Implementation of a FastAPI backend for the Todo application with SQLModel ORM, Neon PostgreSQL database, and JWT-based authentication. The system will enforce strict user data isolation by filtering all database queries by user_id extracted from JWT tokens. The backend will provide a complete REST API for task management with proper security, validation, and error handling.

## Technical Context

**Language/Version**: Python 3.11
**Primary Dependencies**: FastAPI, SQLModel, Neon PostgreSQL driver, Better Auth for JWT handling
**Storage**: Neon Serverless PostgreSQL with SQLModel ORM
**Testing**: pytest for unit and integration testing
**Target Platform**: Linux server environment
**Project Type**: web (backend for web application)
**Performance Goals**: <200ms response time for typical operations, support 1000 concurrent users
**Constraints**: <200ms p95 response time, proper user isolation, 90% test coverage for API layer
**Scale/Scope**: Multi-user support, up to 10k users, individual task management per user

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Tech Stack Constraint**: ✅ Adheres to designated stack (Python FastAPI, SQLModel, Neon PostgreSQL)
- **Security Through Authentication**: ✅ Will implement JWT verification using BETTER_AUTH_SECRET
- **User Data Isolation (NON-NEGOTIABLE)**: ✅ Every database query will be filtered by user_id from JWT
- **Asynchronous I/O Operations**: ✅ All database operations will use async/await patterns
- **Test Coverage Standard**: ✅ Plan includes 90% test coverage requirement for API layer
- **Performance Over Brevity**: ✅ Implementation prioritizes performance and security over code brevity

## Project Structure

### Documentation (this feature)

```text
specs/001-todo-backend-requirements/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
backend/
├── main.py              # FastAPI application entry point
├── db.py               # Database engine and session setup
├── models.py           # SQLModel definitions for Task entity
├── auth.py             # JWT verification middleware and user context
├── routes/
│   └── tasks.py        # Task CRUD endpoint implementations
├── schemas.py          # Pydantic schemas for API requests/responses
└── tests/
    ├── unit/
    ├── integration/
    └── contract/
```

**Structure Decision**: Selected web application structure with dedicated backend directory for FastAPI application. This follows the constitution's requirement for Python FastAPI backend with proper separation of concerns between models, routes, authentication, and database layers.

## Phase 0: Research & Analysis

### Research Tasks Identified

1. **Database Setup**: Investigate best practices for SQLModel engine initialization with Neon Serverless PostgreSQL
2. **JWT Integration**: Research Better Auth JWT token decoding and verification patterns
3. **FastAPI Dependencies**: Best practices for dependency injection in FastAPI for database sessions and authentication
4. **SQLModel Relationships**: Proper implementation of user_id foreign key relationships
5. **Async Session Management**: Best practices for async database session handling in FastAPI

## Phase 1: Design & Architecture

### 1. Database & Engine Setup (db.py)
- Initialize SQLModel engine with DATABASE_URL for Neon Serverless PostgreSQL
- Create get_session dependency for FastAPI to manage stateless database sessions
- Implement async context managers for proper session handling
- Configure connection pooling and error handling

### 2. SQLModel Implementation (models.py)
- Implement Task and TaskBase classes as defined in spec
- Create separate Pydantic schemas for TaskCreate, TaskRead, and TaskUpdate
- Define proper field constraints (title max 200 chars, non-empty validation)
- Implement automatic timestamp management (created_at, updated_at)

### 3. JWT Middleware & Security (auth.py)
- Implement verify_jwt dependency using BETTER_AUTH_SECRET
- Extract user_id from JWT and pass to route handlers
- Handle JWT validation errors appropriately
- Return 401 Unauthorized for invalid tokens

### 4. Route Layer (routes/tasks.py)
- Implement all required endpoints: GET, POST, PUT, DELETE, PATCH
- Apply .where(Task.user_id == current_user_id) filter to all database operations
- Implement proper validation and error handling
- Return appropriate HTTP status codes

### 5. API Schemas (schemas.py)
- Define Pydantic models for request/response validation
- Create TaskCreate, TaskRead, TaskUpdate schemas
- Implement proper field validation based on requirements
- Ensure type safety between API and database layers

## Phase 2: Implementation Plan

Detailed implementation tasks will be generated in the tasks.md file following the completion of research and design phases.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |
