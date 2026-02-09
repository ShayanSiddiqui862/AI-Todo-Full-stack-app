name: neon-db-architect
description: Expert in SQLModel and PostgreSQL schema design for Neon Serverless database. Use when defining tables, relationships, or database connection logic.


# Neon DB Architect Skill

This skill governs the design and evolution of the PostgreSQL database layer. It ensures that the schema strictly follows the "Evolution of Todo" requirements, focusing on multi-tenancy and high performance.

## 1. Schema Standards (SQLModel)
- **Table Definition**: Always use `table=True` in SQLModel classes for database entities.
- **Primary Keys**: Use `id: Optional[int] = Field(default=None, primary_key=True)` for tasks and string-based IDs for users to match Better Auth.
- **Foreign Keys**: Explicitly define `user_id: str = Field(foreign_key="user.id")` to ensure relational integrity.
- **Type Safety**: Use Pydantic field types for validation (e.g., `constr(min_length=1)` for required titles).

## 2. Multi-User Isolation
- **Mandatory User ID**: Every table that stores user-specific data (Tasks, Reminders, Conversations) MUST have a `user_id` column.
- **Relationship Mapping**: Use SQLModel's `Relationship` attribute to allow for easy joins (e.g., a User having a list of Tasks).
- **Index Optimization**: Always ensure an index is placed on the `user_id` column to optimize the mandatory filtering required for Phase II.

## 3. Neon Serverless Patterns
- **Connection Pooling**: Use the `DATABASE_URL` from environment variables and ensure the engine is configured to handle the serverless nature of Neon (e.g., proper session handling).
- **Stateless Sessions**: Implement a `get_session` generator for FastAPI dependency injection to ensure database connections are closed after every request.
- **Migration Strategy**: Before suggesting a code change to `models.py`, verify how it impacts the existing schema and suggest a migration path if necessary.

## 4. Implementation Guidelines
- **Add Task**: Ensure the `created_at` and `updated_at` timestamps are handled, ideally using SQL functions or Pydantic defaults.
- **Status Filtering**: Use boolean or Enum types for task completion status to allow for efficient server-side filtering.
- **Clean Models**: Keep database models in `backend/models.py` and separate them from API request/response schemas to maintain a clean architecture.

## 5. Verification Checklist
- [ ] Does every new table have a `user_id` foreign key?
- [ ] Are primary keys and unique constraints explicitly defined?
- [ ] Does the implementation avoid hardcoded connection strings?
- [ ] Are SQLModel relationships bidirectional where appropriate?

## 6. Workflow Constraints
- **Spec Authoritative**: Read `@specs/database/schema.md` before proposing any table modifications.
- **No Manual Edits**: If a schema change is needed, update the specification first, then let Claude Code generate the implementation.