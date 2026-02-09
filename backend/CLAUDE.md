# Backend Development Guidelines (FastAPI + SQLModel)

You are an expert Backend Engineer. This directory contains the Python FastAPI backend for the Todo application. All work must align with the Root `CLAUDE.md` and `AGENTS.md`.

## 🛠 Tech Stack
- **Framework**: FastAPI (Python 3.13+)
- **ORM**: SQLModel (pydantic + sqlalchemy)
- **Database**: Neon Serverless PostgreSQL
- **Auth**: JWT verification (Better Auth integration)

## 📁 Project Structure
- `main.py`: App entry point & middleware
- `models.py`: SQLModel definitions (Table & Data models)
- `db.py`: Neon engine & session configuration
- `routes/`: API endpoint logic (organized by resource)
- `auth.py`: JWT decoding & user validation logic

## 📏 Core Rules & Patterns
1. **Spec-Driven Mandate**: Read `@specs/api/rest-endpoints.md` and `@specs/database/schema.md` before implementation.
2. **User Isolation (Critical)**:
   - Extract `user_id` from the JWT `Authorization: Bearer <token>` header.
   - **MANDATORY**: Every database query must filter by the authenticated `user_id`.
   - Never trust a `user_id` provided in a request body if it conflicts with the JWT.
3. **Stateless Auth**: Do not use server-side sessions; rely strictly on JWT verification using the `BETTER_AUTH_SECRET`.
4. **Data Validation**: Use separate SQLModel classes for `Table` (database) vs `Create/Update` (API) schemas.
5. **Error Handling**: Use `fastapi.HTTPException` with appropriate status codes (e.g., 401 for auth failure, 404 for missing tasks).

## 🔧 Common Commands
- **Install Deps**: `uv sync`
- **Dev Server**: `uvicorn main:app --reload --port 8000`
- **Lint/Format**: `ruff check .` and `ruff format .`
- **Type Check**: `mypy .`

## 🚀 API Endpoint Reference
All endpoints must follow the `/api/` prefix.
- `GET /api/tasks`: List user's tasks
- `POST /api/tasks`: Create new task
- `PUT /api/tasks/{id}`: Update specific task
- `DELETE /api/tasks/{id}`: Delete specific task
- `PATCH /api/tasks/{id}/complete`: Toggle completion

## 📝 Task Execution
When implementing:
- Reference the specific Task ID from `speckit.tasks`.
- Ensure the Neon connection string is pulled from the `DATABASE_URL` environment variable.