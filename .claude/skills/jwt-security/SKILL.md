name: jwt-security
description: Expert security skill for orchestrating the JWT handshake between Better Auth (Frontend) and FastAPI (Backend). Use when implementing API clients, middleware, or database queries.


# JWT Security Skill (Phase II Guardian)

This skill enforces the secure identity flow across the monorepo. It ensures that the backend correctly verifies the user's identity without direct session sharing with the frontend.

## 1. Security Architecture (The Handshake)
- **Frontend Role**: Better Auth issues a JWT upon login. The frontend must capture this token and persist it in the `Authorization: Bearer <token>` header for all subsequent API requests.
- **Backend Role**: FastAPI acts as the Resource Server. It must intercept requests, verify the JWT signature using the `BETTER_AUTH_SECRET`, and decode the payload to identify the user.

## 2. Implementation Guardrails
- **Secret Synchronization**: Both `frontend/.env` and `backend/.env` MUST use the exact same `BETTER_AUTH_SECRET`.
- **Mandatory User Isolation**: Every SQLModel query generated must include a `.where(Task.user_id == authenticated_user_id)` clause to prevent cross-user data leaks.
- **Standardized Responses**: 
  - Requests with missing or invalid tokens must return `401 Unauthorized`.
  - Operations on tasks not owned by the user must return `403 Forbidden` or `404 Not Found` to prevent ID enumeration.

## 3. Implementation Patterns

### Backend Middleware (FastAPI)
When generating backend code, always include a dependency or middleware that:
1. Extracts the token from the `Authorization` header.
2. Verifies the signature against the shared secret.
3. Returns a `User` object or `user_id` string to the route handler.

### Frontend API Client (Next.js)
When generating the API client (`/lib/api.ts`), ensure:
1. The client retrieves the current session token from Better Auth.
2. The token is appended to the `headers` object of the `fetch` or `axios` call.

## 4. Verification Checklist
- [ ] Is the `user_id` in the URL (e.g., `/api/{user_id}/tasks`) being cross-referenced with the `sub` claim in the JWT? 
- [ ] Does the backend code use a stateless verification method (no database lookups for the session itself)? 
- [ ] Are all 5 Basic Level features (Add, Delete, Update, View, Complete) wrapped in this security layer? 

## 5. Workflow Constraints
- **No Manual Edits**: If the generated auth logic is flawed, you must refine the specification in `@specs/features/authentication.md` rather than patching the code manually.
- **Task Mapping**: Every auth-related code change must be linked to a Task ID from `speckit.tasks`.