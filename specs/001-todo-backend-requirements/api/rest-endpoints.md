# REST API Specification: Todo Application

## Overview

This document defines the REST API contract for the Todo application backend. All endpoints require authentication via JWT token and enforce user data isolation.

## Authentication

All API endpoints (except authentication endpoints) require a valid JWT token in the Authorization header:
```
Authorization: Bearer <JWT_TOKEN>
```

The JWT token must be verified using the BETTER_AUTH_SECRET, and the user_id must be extracted from the token to enforce user data isolation.

## Base URL

All endpoints are prefixed with `/api/`

## Data Models

### Task Model

Request and response bodies must use Pydantic models with the following structure:

```python
class TaskBase:
    title: str (max 200 characters)
    description: Optional[str] (Text field)
    completed: bool (default False)

class TaskCreate(TaskBase):
    title: str (required, max 200 characters)

class TaskUpdate(TaskBase):
    title: Optional[str] (max 200 characters)

class TaskResponse(TaskBase):
    id: int (Primary Key)
    user_id: str (Foreign Key)
    created_at: datetime
    updated_at: datetime
```

### Complete Task Request Model

For PATCH /api/tasks/{id}/complete endpoint:
```python
class TaskCompleteRequest:
    completed: bool (optional - if provided, sets completion status; if not provided, toggles current status)
```

### Error Response Model

All error responses follow this structure:
```python
class ErrorResponse:
    error: str (error message)
    code: str (error code)
```

## Endpoints

### Create Task
- **Method**: POST
- **Path**: `/tasks`
- **Description**: Creates a new task for the authenticated user
- **Request Body**: TaskCreate model
- **Headers**:
  - Content-Type: application/json
  - Authorization: Bearer <JWT_TOKEN>
- **Success Response**:
  - Status: 201 Created
  - Body: TaskResponse model
- **Error Responses**:
  - 400 Bad Request: Validation error (e.g., empty title, title too long)
  - 401 Unauthorized: Invalid or missing JWT token
- **Validation**:
  - Title is required and cannot be empty
  - Title must be 200 characters or less
  - Description is optional
  - Completed defaults to False

### Get All Tasks
- **Method**: GET
- **Path**: `/tasks`
- **Description**: Retrieves all tasks for the authenticated user
- **Headers**:
  - Authorization: Bearer <JWT_TOKEN>
- **Query Parameters**:
  - completed: Optional boolean to filter by completion status
  - limit: Optional integer to limit results
  - offset: Optional integer for pagination
- **Success Response**:
  - Status: 200 OK
  - Body: Array of TaskResponse models
- **Error Responses**:
  - 401 Unauthorized: Invalid or missing JWT token

### Get Specific Task
- **Method**: GET
- **Path**: `/tasks/{id}`
- **Description**: Retrieves a specific task for the authenticated user
- **Path Parameter**: id (task ID)
- **Headers**:
  - Authorization: Bearer <JWT_TOKEN>
- **Success Response**:
  - Status: 200 OK
  - Body: TaskResponse model
- **Error Responses**:
  - 401 Unauthorized: Invalid or missing JWT token
  - 404 Not Found: Task does not exist or belongs to another user

### Update Task
- **Method**: PUT
- **Path**: `/tasks/{id}`
- **Description**: Updates a specific task for the authenticated user
- **Path Parameter**: id (task ID)
- **Request Body**: TaskUpdate model
- **Headers**:
  - Content-Type: application/json
  - Authorization: Bearer <JWT_TOKEN>
- **Success Response**:
  - Status: 200 OK
  - Body: TaskResponse model with updated_at timestamp
- **Error Responses**:
  - 400 Bad Request: Validation error
  - 401 Unauthorized: Invalid or missing JWT token
  - 404 Not Found: Task does not exist or belongs to another user
- **Validation**:
  - Title must be 200 characters or less if provided
  - Updated_at timestamp is automatically updated

### Delete Task
- **Method**: DELETE
- **Path**: `/tasks/{id}`
- **Description**: Deletes a specific task for the authenticated user
- **Path Parameter**: id (task ID)
- **Headers**:
  - Authorization: Bearer <JWT_TOKEN>
- **Success Response**:
  - Status: 200 OK
  - Body: { "message": "Task deleted successfully" }
- **Error Responses**:
  - 401 Unauthorized: Invalid or missing JWT token
  - 404 Not Found: Task does not exist or belongs to another user

### Update Task Completion Status
- **Method**: PATCH
- **Path**: `/tasks/{id}/complete`
- **Description**: Updates the completion status of a specific task for the authenticated user
- **Path Parameter**: id (task ID)
- **Request Body**: TaskCompleteRequest model
- **Headers**:
  - Content-Type: application/json
  - Authorization: Bearer <JWT_TOKEN>
- **Success Response**:
  - Status: 200 OK
  - Body: TaskResponse model with updated completion status and updated_at timestamp
- **Error Responses**:
  - 400 Bad Request: Invalid request body
  - 401 Unauthorized: Invalid or missing JWT token
  - 404 Not Found: Task does not exist or belongs to another user
- **Logic**:
  - If request body contains "completed" field, set task completion status to that value
  - If request body does not contain "completed" field, toggle current completion status
  - Updated_at timestamp is automatically updated

## Security & User Isolation

- All endpoints must verify JWT token using BETTER_AUTH_SECRET
- All endpoints must extract user_id from JWT and ensure user can only access or modify their own tasks
- Return 401 Unauthorized for missing/invalid tokens
- Return 404 Not Found (or 403 Forbidden) if a user attempts to access a task ID they do not own
- All database queries must be filtered by user_id extracted from JWT

## Validation Rules

- Task title cannot be empty during creation
- Task title must be 200 characters or less
- All timestamps (created_at, updated_at) are managed by the system
- Only the task owner can modify task details