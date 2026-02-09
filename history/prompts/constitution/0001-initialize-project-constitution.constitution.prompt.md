---
id: 0001
title: Initialize Project Constitution
stage: constitution
date: 2026-01-10
surface: project-setup
model: claude-sonnet-4-5-20250929
feature: none
branch: main
user: user1
command: "/sp.constitution"
labels: [initialization, constitution, governance, architecture]
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

Initialize the project constitution for the 'Evolution of Todo' Phase II.

Define our non-negotiables and architectural standards based on the following criteria:

1. Tech Stack Constraints: We are strictly using Next.js 16+ (App Router) for the frontend, Python FastAPI for the backend, SQLModel as our ORM, and Neon Serverless PostgreSQL for our database. 2. Security Mandate: We use Better Auth with a shared JWT secret (BETTER_AUTH_SECRET) for stateless authentication between the frontend and backend. 3. User Isolation Principle: Every database query must be filtered by the user_id extracted from the JWT. Cross-user data leakage is a critical failure. 4. Coding Standards: We prioritize performance over brevity. We require asynchronous patterns (async/await) for all I/O operations and 90% test coverage for the API layer. 5. Workflow Rule: Strictly adhere to the Spec-Driven Development (SDD) lifecycle: Specify → Plan → Tasks → Implement. No code is to be generated without a valid Task ID.

## Response snapshot

Created the project constitution file with the following key principles:
- Tech Stack Constraint: Strict adherence to Next.js 16+, FastAPI, SQLModel, Neon PostgreSQL
- Security Through Authentication: Better Auth with JWT for stateless auth
- User Data Isolation: Mandatory user_id filtering from JWT (non-negotiable)
- Asynchronous I/O Operations: All I/O must use async/await patterns
- Test Coverage Standard: 90% coverage for API layer
- Performance Over Brevity: Prioritize efficiency over code conciseness

Also included additional constraints for technology standards, security requirements, and development workflow following Spec-Driven Development lifecycle.

## Outcome

- ✅ Impact: Project constitution established with clear architectural principles
- 🧪 Tests: No tests required for constitution creation
- 📁 Files: Created .specify/memory/constitution.md with 6 core principles and governance rules
- 🔁 Next prompts: Can proceed with feature specification using SDD lifecycle
- 🧠 Reflection: Constitution provides clear governance framework for future development

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): Not applicable
- Prompt variant (if applicable): Not applicable
- Next experiment (smallest change to try): Proceed with feature specification phase
