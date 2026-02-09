# Database Schema Specification: Todo Application

## Overview

This document defines the database schema for the Todo application using SQLModel with Neon PostgreSQL as the database backend. The schema enforces user data isolation and supports efficient querying patterns.

## Database Engine

Neon Serverless PostgreSQL is used as the production database for this application.

## Tables

### tasks table

The tasks table stores all user tasks with proper user isolation and efficient indexing.

**Table Definition:**

```sql
CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    completed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

**Field Descriptions:**

- `id`: Primary Key - Auto-incrementing integer identifier for the task
- `user_id`: Foreign Key - String identifier for the user who owns the task, extracted from JWT
- `title`: String (max 200 characters) - Required title for the task
- `description`: Text (optional) - Optional detailed description of the task
- `completed`: Boolean - Flag indicating whether the task is completed (defaults to FALSE)
- `created_at`: Timestamp with timezone - Automatically set when the record is created
- `updated_at`: Timestamp with timezone - Automatically updated when the record is modified

## Indexing Strategy

To optimize filtered queries, the following indexes are implemented:

```sql
-- Index on user_id to optimize queries that filter by user
CREATE INDEX idx_tasks_user_id ON tasks (user_id);

-- Index on completed to optimize queries that filter by completion status
CREATE INDEX idx_tasks_completed ON tasks (completed);

-- Composite index on user_id and completed to optimize queries that filter by both
CREATE INDEX idx_tasks_user_id_completed ON tasks (user_id, completed);

-- Index on created_at to optimize chronological queries
CREATE INDEX idx_tasks_created_at ON tasks (created_at);
```

**Index Rationale:**

1. **idx_tasks_user_id**: Critical for enforcing user data isolation - all queries must filter by user_id
2. **idx_tasks_completed**: Essential for filtering tasks by completion status (completed/incomplete)
3. **idx_tasks_user_id_completed**: Optimizes common queries that filter by both user and completion status
4. **idx_tasks_created_at**: Supports chronological sorting and time-based queries

## SQLModel Definition

Using SQLModel ORM, the task model is defined as:

```python
from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class TaskBase(SQLModel):
    title: str = Field(max_length=200, min_length=1)
    description: Optional[str] = Field(default=None)
    completed: bool = Field(default=False)

class Task(TaskBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Triggers for automatic timestamp updates would be handled in the application layer
```

## Constraints

1. **Primary Key Constraint**: `id` field must be unique and non-null
2. **Not Null Constraints**: `user_id` and `title` fields must not be null
3. **Length Constraints**: `title` field must be between 1 and 200 characters
4. **Default Value Constraints**:
   - `completed` field defaults to FALSE
   - `created_at` field defaults to current timestamp
   - `updated_at` field defaults to current timestamp

## Data Isolation Requirements

- Every query must include a WHERE clause filtering by `user_id`
- No direct access to tasks belonging to other users is allowed
- The application layer must extract user_id from JWT token and apply it to all database queries
- Queries that don't filter by user_id are considered security violations

## Query Optimization Guidelines

1. Always filter by `user_id` in WHERE clauses to leverage `idx_tasks_user_id`
2. When filtering by completion status, include `user_id` to leverage composite index
3. Use the composite index `idx_tasks_user_id_completed` for queries that filter by both fields
4. Sort by `created_at` for chronological ordering
5. Use LIMIT and OFFSET for pagination

## Migration Strategy

Initial schema creation should include:
1. Create the tasks table with all fields and constraints
2. Create all specified indexes
3. Verify proper functioning with test queries
4. Ensure all existing data conforms to new constraints (if migrating from existing schema)

## Security Considerations

- Direct database access should be restricted to the application layer
- No raw SQL execution without proper sanitization
- All user data must be properly isolated using user_id filtering
- Audit logs should be maintained for any administrative access to the database