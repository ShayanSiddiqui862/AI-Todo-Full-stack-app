# Todo Full-Stack Web Application - Project Guidelines

This file defines the project-specific guidelines for the Todo Full-Stack Web Application. This is Phase II of the project which transforms a console app into a modern multi-user web application with persistent storage.

## Task Context

**Project:** Todo Full-Stack Web Application
**Objective:** Transform the console app into a modern multi-user web application with persistent storage using Next.js, FastAPI, SQLModel, Neon PostgreSQL, and Better Auth.
**Development Approach:** Agentic Dev Stack workflow using Claude Code + Spec-Kit Plus: Write spec → Generate plan → Break into tasks → Implement via Claude Code.

**Your Success is Measured By:**
- Successfully implementing all 5 Basic Level features as a web application
- Building a responsive frontend with Next.js 16+ App Router
- Creating robust RESTful API endpoints with Python FastAPI
- Properly integrating with Neon Serverless PostgreSQL using SQLModel ORM
- Implementing secure authentication with Better Auth
- Following Spec-Driven Development practices throughout the project

## Technology Stack

| Layer      | Technology              |
|------------|-------------------------|
| Frontend   | Next.js 16+ (App Router)|
| Backend    | Python FastAPI          |
| ORM        | SQLModel                |
| Database   | Neon Serverless PostgreSQL |
| Spec-Driven| Claude Code + Spec-Kit Plus |
| Authentication | Better Auth         |

## Core Requirements

### Basic Level Functionality
- **Multi-user Support:** Application must support multiple concurrent users with individual todo lists
- **Persistent Storage:** Todos must be stored in Neon Serverless PostgreSQL database
- **Responsive UI:** Frontend must be responsive and work well on different device sizes
- **Authentication:** Secure user signup/signin functionality using Better Auth
- **Full CRUD Operations:** Create, Read, Update, Delete operations for todos
- **RESTful API:** Well-designed REST endpoints for all functionality

### Development Guidelines Specific to This Project

#### 1. Architecture Patterns:
- Follow Next.js App Router conventions for frontend routing
- Use FastAPI for backend API development with proper Pydantic models
- Leverage SQLModel for database modeling and ORM operations
- Implement proper separation of concerns between frontend and backend
- Follow RESTful API design principles

#### 2. Authentication & Authorization:
- Implement user registration and login flows using Better Auth
- Protect API endpoints appropriately
- Ensure users can only access their own todos
- Handle session management properly

#### 3. Database Design:
- Design efficient database schemas using SQLModel
- Implement proper relationships between users and todos
- Use Neon Serverless PostgreSQL features appropriately
- Consider indexing strategies for performance

#### 4. Frontend Best Practices:
- Use Next.js App Router features (loading states, error boundaries, etc.)
- Implement responsive design with Tailwind CSS or similar
- Ensure good UX with proper loading states and error handling
- Follow accessibility best practices

## Development Workflow

### 1. Spec-Driven Development Process:
- Begin each feature with a detailed specification document
- Generate architectural plans before implementation
- Break plans into testable tasks
- Implement using Claude Code following the Agentic Dev Stack approach

### 2. Implementation Order:
1. Set up project infrastructure (Next.js, FastAPI, database connection)
2. Implement authentication system (Better Auth)
3. Create database models and API endpoints
4. Build frontend UI components
5. Integrate frontend with backend APIs
6. Test and iterate

### 3. Testing Strategy:
- Unit tests for backend API endpoints
- Component tests for frontend components
- Integration tests for full user flows
- End-to-end tests covering critical user journeys

## Default Policies for This Project

- Prioritize security in all implementation decisions
- Follow Next.js best practices for performance and SEO
- Maintain clean separation between frontend and backend concerns
- Use TypeScript for frontend type safety where applicable
- Follow Python best practices for backend code
- Implement proper error handling and logging
- Ensure database migrations are handled properly
- Follow accessibility standards for inclusive design

## Project Structure

- `.specify/memory/constitution.md` — Project principles
- `specs/<feature>/spec.md` — Feature requirements
- `specs/<feature>/plan.md` — Architecture decisions
- `specs/<feature>/tasks.md` — Testable tasks with cases
- `frontend/` — Next.js application code
- `backend/` — FastAPI application code
- `history/prompts/` — Prompt History Records
- `history/adr/` — Architecture Decision Records
- `.specify/` — SpecKit Plus templates and scripts

## Quality Standards

- Code follows established patterns for Next.js and FastAPI
- Proper error handling throughout the application
- Efficient database queries with appropriate indexing
- Responsive design that works across devices
- Secure authentication and authorization
- Comprehensive test coverage for critical paths
- Proper documentation for APIs and components

## Active Technologies
- Python 3.11 + FastAPI, SQLModel, Neon PostgreSQL driver, Better Auth for JWT handling (001-todo-backend-requirements)
- Neon Serverless PostgreSQL with SQLModel ORM (001-todo-backend-requirements)

## Recent Changes
- 001-todo-backend-requirements: Added Python 3.11 + FastAPI, SQLModel, Neon PostgreSQL driver, Better Auth for JWT handling
