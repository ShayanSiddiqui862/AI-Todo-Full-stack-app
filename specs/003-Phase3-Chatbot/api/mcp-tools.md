# API Specification: Model Context Protocol (MCP) Tools for Todo Operations

**Document**: `specs/api/mcp-tools.md`
**Created**: 2026-02-07
**Status**: Draft
**Input**: MCP tools specification for exposing todo operations as stateless services that interact with the database

## Overview

This specification defines the Model Context Protocol (MCP) tools that expose todo operations for use by the OpenAI Agent. These tools must be stateless and persist data through the database rather than maintaining state in memory.

## MCP Tool: add_task

### Purpose
Creates a new task for the authenticated user.

### Request Parameters
- `user_id`: UUID - The ID of the user requesting the operation
- `title`: String - The title of the task to be created
- `description`: String (optional) - Additional details about the task
- `due_date`: ISO 8601 datetime (optional) - Deadline for the task
- `priority`: Enum ('low' | 'medium' | 'high') (optional) - Priority level

### Response Format
```json
{
  "success": true,
  "task_id": "UUID",
  "message": "Task 'title' created successfully"
}
```

### Error Response
```json
{
  "success": false,
  "error_code": "string",
  "message": "Descriptive error message"
}
```

### Validation Rules
- `title` must not exceed 500 characters
- `due_date` must be a valid future date if provided
- User must exist and be authenticated
- User can only add tasks to their own list

## MCP Tool: list_tasks

### Purpose
Retrieves tasks for the authenticated user with optional filtering.

### Request Parameters
- `user_id`: UUID - The ID of the user requesting the operation
- `status`: Enum ('all' | 'pending' | 'completed' | 'deleted') (optional, default: 'all') - Filter by task status
- `limit`: Integer (optional, default: 50, max: 100) - Maximum number of tasks to return
- `offset`: Integer (optional, default: 0) - Number of tasks to skip for pagination
- `sort_by`: Enum ('created_at' | 'updated_at' | 'due_date' | 'priority') (optional, default: 'created_at') - Sort ordering
- `order`: Enum ('asc' | 'desc') (optional, default: 'desc') - Sort direction

### Response Format
```json
{
  "success": true,
  "tasks": [
    {
      "task_id": "UUID",
      "title": "string",
      "description": "string",
      "status": "enum",
      "due_date": "ISO 8601 datetime",
      "priority": "enum",
      "created_at": "ISO 8601 datetime",
      "updated_at": "ISO 8601 datetime"
    }
  ],
  "total_count": integer,
  "message": "Tasks retrieved successfully"
}
```

### Error Response
```json
{
  "success": false,
  "error_code": "string",
  "message": "Descriptive error message"
}
```

### Validation Rules
- User must exist and be authenticated
- User can only list their own tasks
- Pagination parameters must be valid integers

## MCP Tool: update_task

### Purpose
Updates properties of an existing task for the authenticated user.

### Request Parameters
- `user_id`: UUID - The ID of the user requesting the operation
- `task_id`: UUID - The ID of the task to update
- `title`: String (optional) - New title for the task
- `description`: String (optional) - New description for the task
- `due_date`: ISO 8601 datetime (optional) - New deadline for the task
- `priority`: Enum ('low' | 'medium' | 'high') (optional) - New priority level

### Response Format
```json
{
  "success": true,
  "task_id": "UUID",
  "message": "Task 'task_id' updated successfully"
}
```

### Error Response
```json
{
  "success": false,
  "error_code": "string",
  "message": "Descriptive error message"
}
```

### Validation Rules
- `task_id` must correspond to an existing task
- Task must belong to the requesting user
- User must exist and be authenticated
- Only one of the optional fields needs to be provided
- `due_date` must be a valid date if provided

## MCP Tool: complete_task

### Purpose
Marks an existing task as completed for the authenticated user.

### Request Parameters
- `user_id`: UUID - The ID of the user requesting the operation
- `task_id`: UUID - The ID of the task to mark as completed

### Response Format
```json
{
  "success": true,
  "task_id": "UUID",
  "message": "Task 'task_id' marked as completed"
}
```

### Error Response
```json
{
  "success": false,
  "error_code": "string",
  "message": "Descriptive error message"
}
```

### Validation Rules
- `task_id` must correspond to an existing task
- Task must belong to the requesting user
- User must exist and be authenticated
- Task must not already be completed

## MCP Tool: delete_task

### Purpose
Removes a task from the user's task list (soft delete with status update).

### Request Parameters
- `user_id`: UUID - The ID of the user requesting the operation
- `task_id`: UUID - The ID of the task to delete

### Response Format
```json
{
  "success": true,
  "task_id": "UUID",
  "message": "Task 'task_id' deleted successfully"
}
```

### Error Response
```json
{
  "success": false,
  "error_code": "string",
  "message": "Descriptive error message"
}
```

### Validation Rules
- `task_id` must correspond to an existing task
- Task must belong to the requesting user
- User must exist and be authenticated
- Deleted tasks are marked with status 'deleted' rather than physically removed

## Common Error Codes

- `INVALID_USER_ID`: Provided user ID is not a valid UUID
- `USER_NOT_FOUND`: No user exists with the provided ID
- `TASK_NOT_FOUND`: No task exists with the provided task ID
- `TASK_ACCESS_DENIED`: User is trying to access a task that doesn't belong to them
- `VALIDATION_ERROR`: Request parameters failed validation
- `DATABASE_ERROR`: Database operation failed
- `INTERNAL_ERROR`: Unexpected server error occurred

## Security Requirements

- Each tool must validate that the requesting user owns the target resource
- JWT authentication must be validated before executing any operations
- Input sanitization must be applied to prevent injection attacks
- All operations must be logged for audit purposes
- User isolation must be maintained - users cannot access others' tasks

## Performance Requirements

- Each tool must respond within 500ms for 95% of requests
- MCP server must handle at least 100 concurrent requests
- Database operations must use appropriate indexing
- Proper connection pooling must be implemented

## Statelessness Requirements

- No persistent state should be maintained between tool invocations
- All data must be retrieved from and persisted to the database
- Tools should not rely on server-side session data
- Each tool invocation should be treated as independent