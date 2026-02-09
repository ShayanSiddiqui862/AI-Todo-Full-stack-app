---
id: 0001
title: Create Todo Backend Requirements Spec
stage: spec
date: 2026-01-10
surface: api-design
model: claude-sonnet-4-5-20250929
feature: 001-todo-backend-requirements
branch: 001-todo-backend-requirements
user: user1
command: "/sp.specify"
labels: [specification, api, database, security]
links:
  spec: ../specs/001-todo-backend-requirements/spec.md
  ticket:
  adr:
  pr:
files:
  - specs/001-todo-backend-requirements/spec.md
  - specs/001-todo-backend-requirements/api-rest-endpoints.md
  - specs/001-todo-backend-requirements/database-schema.md
  - specs/001-todo-backend-requirements/checklists/requirements.md
tests:
  - none
---

## Prompt

Execute /sp.specify to generate the formal backend requirements for the Phase II Todo Web Application.

The goal is to define the 'Source of Truth' for the API and Database layers. The specification must include:

1. Data Model (SQLModel & Neon DB): - Define the tasks table with fields: id (Primary Key), user_id (Foreign Key - String), title (String, max 200), description (Text, optional), completed (Boolean, default False), created_at (Timestamp), and updated_at (Timestamp) . - Define the indexing strategy for user_id and completed fields to optimize filtered queries .

2. REST API Contract: - Define endpoints: GET /api/tasks, POST /api/tasks, GET /api/tasks/{id}, PUT /api/tasks/{id}, DELETE /api/tasks/{id}, and PATCH /api/tasks/{id}/complete . - Specify that all request and response bodies must use Pydantic models.

3. Security & User Isolation: - Define the requirement for a JWT verification middleware using the BETTER_AUTH_SECRET . - Mandatory Constraint: Specify that every endpoint must extract the user_id from the JWT and ensure the user can only access or modify their own tasks. - Define error paths: Return 401 Unauthorized for missing/invalid tokens and 404 Not Found (or 403 Forbidden) if a user attempts to access a task ID they do not own.

4. Functional Logic: - Describe the logic for 'Mark as Complete' toggling and the validation rules for task creation (e.g., title cannot be empty) .

Output the resulting specifications to specs/api/rest-endpoints.md and specs/database/schema.md as per the monorepo structure.

## Response snapshot

Successfully created comprehensive backend requirements specification for the Todo Web Application. Created:

1. Main specification file (spec.md) with user scenarios, functional requirements, and success criteria
2. API specification (api-rest-endpoints.md) defining all REST endpoints with authentication, data models, and security requirements
3. Database schema specification (database-schema.md) with table structure, indexing strategy, and SQLModel definitions
4. Quality checklist to validate the specification

The specification covers all requested elements: data model with proper fields and indexing, REST API contract with all required endpoints using Pydantic models, security & user isolation with JWT verification and user_id extraction, and functional logic for task completion toggling and validation rules.

## Outcome

- ✅ Impact: Complete backend requirements specification created for Todo application
- 🧪 Tests: No automated tests needed for specification creation
- 📁 Files: Created 4 files with comprehensive backend requirements (main spec, API contract, database schema, quality checklist)
- 🔁 Next prompts: Ready to proceed with /sp.plan to create implementation plan
- 🧠 Reflection: Specification comprehensively covers all requirements with proper user isolation, security, and API design

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): Not applicable
- Prompt variant (if applicable): Not applicable
- Next experiment (smallest change to try): Proceed with planning phase using /sp.plan
