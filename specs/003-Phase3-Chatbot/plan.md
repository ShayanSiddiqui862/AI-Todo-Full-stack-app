# Implementation Plan: AI-Powered Todo Chatbot

**Branch**: `003-ai-chatbot-integration` | **Date**: 2026-02-07 | **Spec**: [link](spec.md)
**Input**: Feature specification from `/specs/[###-feature-name]/spec.md`

## Summary

Implement an AI-powered chatbot interface that allows authenticated users to manage their Todo list via natural language using OpenAI ChatKit UI, Agents SDK, and MCP tools. The system will follow a stateless architecture pattern where conversation history is persisted to the database rather than held in server memory.

## Technical Context

**Language/Version**: Python 3.11, TypeScript/JavaScript for frontend
**Primary Dependencies**: FastAPI, OpenAI Agents SDK, OpenAI ChatKit, MCP SDK, SQLModel, Next.js
**Storage**: PostgreSQL (Neon) with SQLModel ORM
**Testing**: pytest for backend, Jest/React Testing Library for frontend
**Target Platform**: Web application (Next.js frontend + FastAPI backend)
**Project Type**: Web application with separate frontend and backend
**Performance Goals**: 95% of chatbot responses delivered within 3 seconds
**Constraints**: Stateless API server, user data isolation, JWT authentication
**Scale/Scope**: Support for multiple concurrent users with isolated data

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

The implementation follows the required stateless architecture pattern with conversation history stored in the database rather than server memory. All user data will be properly isolated using user_id foreign keys and authentication checks.

## Project Structure

### Documentation (this feature)

```text
specs/003-ai-chatbot-integration/
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
├── src/
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── task.py
│   │   └── chat.py                    # New: Conversation and Message models
│   ├── services/
│   │   ├── __init__.py
│   │   ├── chat_service.py            # New: Chat business logic
│   │   ├── task_service.py
│   │   └── mcp_service.py             # New: MCP tools implementation
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── tasks.py
│   │   ├── auth.py
│   │   └── chat.py                    # New: Chat API endpoints
│   ├── mcp/
│   │   ├── __init__.py
│   │   ├── server.py                  # New: MCP server implementation
│   │   └── tools.py                   # New: MCP tools definitions
│   ├── agents/
│   │   ├── __init__.py
│   │   └── runner.py                  # New: OpenAI Agent runner
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py
│   └── __init__.py
├── main.py
├── db.py
├── schemas.py
└── requirements.txt

frontend/
├── src/
│   ├── app/
│   │   ├── chat/                      # New: Chat interface page
│   │   │   ├── page.tsx
│   │   │   └── layout.tsx
│   │   └── dashboard/
│   │       └── page.tsx               # Updated: Add chat navigation
│   ├── components/
│   │   ├── Chat/
│   │   │   ├── ChatInterface.tsx      # New: ChatKit integration
│   │   │   ├── ChatProviderWrapper.tsx # New: ChatKit provider wrapper
│   │   │   └── index.ts
│   │   └── index.ts
│   ├── lib/
│   │   ├── api/
│   │   │   └── chat.ts                # New: Chat API utilities
│   │   └── types/
│   │       └── chat.ts                # New: Chat-related TypeScript types
│   └── hooks/
│       └── useAuth.ts
└── package.json
```

**Structure Decision**: Web application with separate frontend and backend. The backend will be extended with new chat-related models, services, and routes. The frontend will include a new chat page integrated with OpenAI ChatKit.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| MCP Server | Required by OpenAI Agents SDK for tool integration | Direct API calls would bypass the MCP protocol requirements |
| Stateless Architecture | Required by spec for scalability and reliability | Stateful server would not scale well and violate requirements |