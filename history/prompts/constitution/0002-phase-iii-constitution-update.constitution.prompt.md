---
id: 0002
title: Phase III Constitution Update
stage: constitution
date: 2026-02-07
surface: evolution-of-todo
model: claude-sonnet-4-5-20250929
feature: evolution-of-todo
branch: 002-focusflow-frontend
user: user1
command: "/sp.constitution"
labels: [update, constitution, governance, architecture, phase-iii, ai-chatbot]
links:
  spec:
  ticket:
  adr:
  pr:
files:
  - .specify/memory/constitution.md
tests:
  - none
---

## Prompt

Update the project constitution for the 'Evolution of Todo' Phase III transformation from Full-Stack Web App to AI-Powered Todo Chatbot.

Define new non-negotiables and architectural standards based on the following transformation criteria:

1. Technology Stack Evolution: Transition from traditional web application to AI-powered chatbot using OpenAI ChatKit for frontend and OpenAI Agents SDK with Model Context Protocol (MCP) tools for backend processing.

2. Architectural Paradigm Shift: Implement stateless agent pattern where the Chat API endpoint (POST /api/chat) must be completely stateless with all conversation history persisted to Neon PostgreSQL database, never held in server memory.

3. MCP Tool Integration: Define mandatory MCP tools for task management (add_task, list_tasks, complete_task, delete_task, update_task) that encapsulate business logic while maintaining strict separation from the stateless agent.

4. Agentic Workflow Standards: Establish the stateless request cycle that includes fetching conversation history from DB, storing user message in DB, running agent with MCP tools, and storing assistant response in DB.

5. Security Continuity: Maintain existing Better Auth JWT authentication while extending row-level security to ensure agents enforce user isolation when accessing MCP tools.

## Response snapshot

Updated the project constitution file with the following key changes for Phase III:

- Technology Stack: Introduced OpenAI ChatKit, OpenAI Agents SDK, and Model Context Protocol (MCP) tools
- Stateless Agent Pattern: Defined requirement for completely stateless chat API with database-persisted state
- MCP Tool Specifications: Established mandatory tools (add_task, list_tasks, complete_task, delete_task, update_task)
- Three-Tier Architecture: Defined interaction flow between ChatKit UI, FastAPI Chat Endpoint, MCP Tools Server, and Neon PostgreSQL
- Agentic Workflow: Documented the stateless request cycle for processing conversations
- Enhanced Security: Extended row-level security to ensure proper user isolation in MCP tool access

Updated version to 2.0.0 to reflect major architectural transformation from Phase II (Full-Stack Web App) to Phase III (AI-Powered Chatbot).

## Outcome

- ✅ Impact: Project constitution successfully updated for Phase III AI-Powered Todo Chatbot architecture
- 🧪 Tests: No tests required for constitution update
- 📁 Files: Updated .specify/memory/constitution.md with new principles for AI chatbot architecture
- 🔁 Next prompts: Can proceed with Phase III feature specifications using new constitutional guidelines
- 🧠 Reflection: Constitution now properly governs development of AI-powered chatbot with MCP tools

## Evaluation notes (flywheel)

- Failure modes addressed: Preventing stateful chatbot implementations that violate the stateless agent pattern
- Graders run and results (PASS/FAIL): Not applicable
- Prompt variant (if applicable): Not applicable
- Next experiment (smallest change to try): Proceed with Phase III feature specification following new constitutional guidelines