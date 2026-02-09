# Feature Specification: Todo Backend Requirements - Phase II

**Feature Branch**: `001-todo-backend-requirements`
**Created**: 2026-01-10
**Status**: Draft
**Input**: User description: "Execute /sp.specify to generate the formal backend requirements for the Phase II Todo Web Application. The goal is to define the 'Source of Truth' for the API and Database layers. The specification must include: 1. Data Model (SQLModel & Neon DB): - Define the tasks table with fields: id (Primary Key), user_id (Foreign Key - String), title (String, max 200), description (Text, optional), completed (Boolean, default False), created_at (Timestamp), and updated_at (Timestamp) . - Define the indexing strategy for user_id and completed fields to optimize filtered queries . 2. REST API Contract: - Define endpoints: GET /api/tasks, POST /api/tasks, GET /api/tasks/{id}, PUT /api/tasks/{id}, DELETE /api/tasks/{id}, and PATCH /api/tasks/{id}/complete . - Specify that all request and response bodies must use Pydantic models. 3. Security & User Isolation: - Define the requirement for a JWT verification middleware using the BETTER_AUTH_SECRET . - Mandatory Constraint: Specify that every endpoint must extract the user_id from the JWT and ensure the user can only access or modify their own tasks. - Define error paths: Return 401 Unauthorized for missing/invalid tokens and 404 Not Found (or 403 Forbidden) if a user attempts to access a task ID they do not own. 4. Functional Logic: - Describe the logic for 'Mark as Complete' toggling and the validation rules for task creation (e.g., title cannot be empty) . Output the resulting specifications to specs/api/rest-endpoints.md and specs/database/schema.md as per the monorepo structure ."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Create New Task (Priority: P1)

As a registered user, I want to create a new task so that I can track my to-dos.

**Why this priority**: This is the core functionality of the todo application - without the ability to create tasks, the application has no value.

**Independent Test**: Can be fully tested by making a POST request to /api/tasks with valid task data and verifying that the task is created in the database and returned in the response with proper user association.

**Acceptance Scenarios**:

1. **Given** I am an authenticated user, **When** I submit a task with a title, **Then** the task is created with my user_id, completed status as false, and proper timestamps
2. **Given** I am an authenticated user, **When** I submit a task with missing title, **Then** the system returns an error indicating the title is required

---

### User Story 2 - View All My Tasks (Priority: P1)

As a registered user, I want to view all my tasks so that I can see what I need to do.

**Why this priority**: This is essential functionality that allows users to interact with their data and forms the basis of the todo experience.

**Independent Test**: Can be fully tested by making a GET request to /api/tasks and verifying that only tasks belonging to the authenticated user are returned.

**Acceptance Scenarios**:

1. **Given** I am an authenticated user with multiple tasks, **When** I request my tasks, **Then** I see only my tasks and not tasks belonging to other users
2. **Given** I am an authenticated user with no tasks, **When** I request my tasks, **Then** I receive an empty list

---

### User Story 3 - Update Task Details (Priority: P2)

As a registered user, I want to update my task details so that I can keep my todo list current.

**Why this priority**: Allows users to modify existing tasks, which is important for maintaining an accurate todo list.

**Independent Test**: Can be fully tested by making a PUT request to /api/tasks/{id} with updated task data and verifying the changes are persisted.

**Acceptance Scenarios**:

1. **Given** I am an authenticated user with an existing task, **When** I update the task details, **Then** the changes are saved and returned in the response
2. **Given** I am an authenticated user trying to update another user's task, **When** I make the update request, **Then** I receive a 404 or 403 error

---

### User Story 4 - Mark Task as Complete/Incomplete (Priority: P1)

As a registered user, I want to mark my tasks as complete or incomplete so that I can track my progress.

**Why this priority**: This is core functionality that allows users to indicate task completion status, which is fundamental to a todo application.

**Independent Test**: Can be fully tested by making a PATCH request to /api/tasks/{id}/complete and verifying the completion status is toggled or set as specified.

**Acceptance Scenarios**:

1. **Given** I am an authenticated user with an incomplete task, **When** I mark it as complete, **Then** the task's completed status changes to true
2. **Given** I am an authenticated user with a completed task, **When** I mark it as incomplete, **Then** the task's completed status changes to false

---

### User Story 5 - Delete Task (Priority: P2)

As a registered user, I want to delete tasks I no longer need so that I can keep my todo list organized.

**Why this priority**: Allows users to remove tasks they no longer need, which is important for maintaining a clean and relevant todo list.

**Independent Test**: Can be fully tested by making a DELETE request to /api/tasks/{id} and verifying the task is removed from the database.

**Acceptance Scenarios**:

1. **Given** I am an authenticated user with an existing task, **When** I delete the task, **Then** the task is removed from the database and the response confirms deletion
2. **Given** I am an authenticated user trying to delete another user's task, **When** I make the delete request, **Then** I receive a 404 or 403 error

---

### User Story 6 - View Specific Task (Priority: P2)

As a registered user, I want to view details of a specific task so that I can see its full information.

**Why this priority**: Allows users to access detailed information about a specific task, which is useful for complex todo items.

**Independent Test**: Can be fully tested by making a GET request to /api/tasks/{id} and verifying that only tasks belonging to the authenticated user are accessible.

**Acceptance Scenarios**:

1. **Given** I am an authenticated user with an existing task, **When** I request the specific task, **Then** I receive the complete task details
2. **Given** I am an authenticated user trying to access another user's task, **When** I make the request, **Then** I receive a 404 or 403 error

---

### Edge Cases

- What happens when a user tries to access a task ID that doesn't exist?
- How does the system handle malformed JWT tokens?
- What happens when a user tries to create a task with a title longer than 200 characters?
- How does the system handle concurrent updates to the same task?
- What happens when the database is temporarily unavailable during a request?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide a data model for tasks with fields: id (Primary Key), user_id (Foreign Key), title (String, max 200), description (Text, optional), completed (Boolean, default False), created_at (Timestamp), and updated_at (Timestamp)
- **FR-002**: System MUST implement indexing on user_id and completed fields to optimize filtered queries
- **FR-003**: System MUST provide REST API endpoints: GET /api/tasks, POST /api/tasks, GET /api/tasks/{id}, PUT /api/tasks/{id}, DELETE /api/tasks/{id}, and PATCH /api/tasks/{id}/complete
- **FR-004**: System MUST use Pydantic models for all request and response bodies to ensure type safety and validation
- **FR-005**: System MUST implement JWT verification middleware using BETTER_AUTH_SECRET for authentication
- **FR-006**: System MUST extract user_id from JWT token and ensure users can only access or modify their own tasks
- **FR-007**: System MUST return 401 Unauthorized for missing or invalid JWT tokens
- **FR-008**: System MUST return 404 Not Found (or 403 Forbidden) when a user attempts to access a task ID they do not own
- **FR-009**: System MUST implement logic for toggling task completion status via PATCH /api/tasks/{id}/complete endpoint
- **FR-010**: System MUST validate that task title cannot be empty during creation
- **FR-011**: System MUST automatically update the updated_at timestamp whenever a task is modified
- **FR-012**: System MUST prevent access to tasks that belong to other users, ensuring complete data isolation
- **FR-013**: System MUST return appropriate HTTP status codes for all operations (200 for success, 201 for creation, 400 for bad request, etc.)
- **FR-014**: System MUST support creating tasks with optional descriptions and automatically set completed to false by default
- **FR-015**: System MUST enforce maximum length of 200 characters for task titles

### Key Entities *(include if feature involves data)*

- **Task**: Represents a user's to-do item with attributes for id, user_id, title, description, completion status, and timestamps. Each task is uniquely owned by a single user.
- **User**: Represents an authenticated user identified by user_id extracted from JWT token. Users can only access tasks associated with their user_id.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can create new tasks in under 2 seconds from authenticated state
- **SC-002**: Users can retrieve their list of tasks in under 2 seconds for up to 1000 tasks
- **SC-003**: 100% of users can only access their own tasks (no cross-user data leakage)
- **SC-004**: 99.9% of API requests return successful responses under normal operating conditions
- **SC-005**: Task creation fails with appropriate error messages when validation requirements are not met (e.g., empty title)
- **SC-006**: Users can toggle task completion status with immediate feedback and updated timestamp
- **SC-007**: Authentication and authorization checks are performed consistently across all endpoints
- **SC-008**: Database queries for user-specific tasks return results efficiently using proper indexing
