# Implementation Tasks: FastAPI Backend for Todo Application

**Feature**: FastAPI Backend for Todo Application
**Generated**: 2026-01-10
**Based on**: `/specs/001-todo-backend-requirements/plan.md` and `/specs/001-todo-backend-requirements/spec.md`

## Phase 1: Setup & Project Initialization

- [X] T001 Create backend directory structure with proper subdirectories
- [X] T002 Initialize Python project with requirements.txt/pyproject.toml including FastAPI, SQLModel, asyncpg, python-jose, and pydantic
- [X] T003 Set up environment configuration for DATABASE_URL and BETTER_AUTH_SECRET
- [X] T004 Create main.py with basic FastAPI application setup
- [X] T005 [P] Create tests directory structure (unit, integration, contract)

## Phase 2: Foundational Components

- [X] T006 Create db.py with SQLModel async engine initialization using DATABASE_URL
- [X] T007 Create get_session dependency for FastAPI with async context manager
- [X] T008 [P] Create models.py with Task and TaskBase SQLModel classes as defined in spec
- [X] T009 [P] Create schemas.py with Pydantic models (TaskCreate, TaskUpdate, TaskResponse)
- [X] T010 Create auth.py with verify_jwt dependency using BETTER_AUTH_SECRET
- [X] T011 Implement user_id extraction from JWT and proper error handling for 401 Unauthorized
- [X] T012 Set up proper field constraints (title max 200 chars, non-empty validation)
- [X] T013 Implement automatic timestamp management (created_at, updated_at)

## Phase 3: [US1] Create New Task

**Goal**: Enable users to create new tasks with proper validation and user association

**Independent Test**: Can be fully tested by making a POST request to /api/tasks with valid task data and verifying that the task is created in the database and returned in the response with proper user association.

**Implementation Tasks**:

- [X] T014 [US1] Create POST /api/tasks endpoint in routes/tasks.py
- [X] T015 [US1] Implement TaskCreate request validation using Pydantic schema
- [X] T016 [US1] Ensure user_id is extracted from JWT and associated with new task
- [X] T017 [US1] Apply validation rule: title cannot be empty during creation (FR-010)
- [X] T018 [US1] Apply validation rule: title must be 200 characters or less (FR-015)
- [X] T019 [US1] Set completed to False by default (FR-014)
- [X] T020 [US1] Set created_at and updated_at to current timestamp
- [X] T021 [US1] Return 201 Created with complete task data in response
- [X] T022 [US1] Return 400 Bad Request for validation failures
- [X] T023 [US1] Return 401 Unauthorized for invalid JWT
- [X] T024 [US1] Add route to main FastAPI app
- [ ] T025 [US1] [P] Write unit tests for POST /api/tasks endpoint
- [ ] T026 [US1] [P] Write integration tests for task creation functionality

## Phase 4: [US2] View All My Tasks

**Goal**: Allow users to view all their tasks with proper user isolation

**Independent Test**: Can be fully tested by making a GET request to /api/tasks and verifying that only tasks belonging to the authenticated user are returned.

**Implementation Tasks**:

- [X] T027 [US2] Create GET /api/tasks endpoint in routes/tasks.py
- [X] T028 [US2] Apply .where(Task.user_id == current_user_id) filter to database query
- [X] T029 [US2] Return array of TaskResponse objects
- [ ] T030 [US2] Support optional query parameters for filtering by completion status
- [X] T031 [US2] Return 200 OK with empty array if no tasks exist
- [X] T032 [US2] Return 401 Unauthorized for invalid JWT
- [X] T033 [US2] Add route to main FastAPI app
- [ ] T034 [US2] [P] Write unit tests for GET /api/tasks endpoint
- [ ] T035 [US2] [P] Write integration tests for viewing user tasks
- [ ] T036 [US2] [P] Write tests to verify user isolation (ensure users can't see others' tasks)

## Phase 5: [US4] Mark Task as Complete/Incomplete

**Goal**: Allow users to toggle or set completion status of their tasks

**Independent Test**: Can be fully tested by making a PATCH request to /api/tasks/{id}/complete and verifying the completion status is toggled or set as specified.

**Implementation Tasks**:

- [X] T037 [US4] Create PATCH /api/tasks/{id}/complete endpoint in routes/tasks.py
- [X] T038 [US4] Apply .where(Task.user_id == current_user_id) filter to verify task ownership
- [X] T039 [US4] Implement toggle logic when "completed" field is not provided in request
- [X] T040 [US4] Implement explicit set logic when "completed" field is provided
- [X] T041 [US4] Update updated_at timestamp when completion status changes
- [X] T042 [US4] Return 200 OK with updated task data
- [X] T043 [US4] Return 401 Unauthorized for invalid JWT
- [X] T044 [US4] Return 404 Not Found for non-existent or unauthorized tasks
- [X] T045 [US4] Add route to main FastAPI app
- [ ] T046 [US4] [P] Write unit tests for PATCH /api/tasks/{id}/complete endpoint
- [ ] T047 [US4] [P] Write integration tests for task completion toggling

## Phase 6: [US6] View Specific Task

**Goal**: Allow users to view details of a specific task with proper authorization

**Independent Test**: Can be fully tested by making a GET request to /api/tasks/{id} and verifying that only tasks belonging to the authenticated user are accessible.

**Implementation Tasks**:

- [X] T048 [US6] Create GET /api/tasks/{id} endpoint in routes/tasks.py
- [X] T049 [US6] Apply .where(Task.user_id == current_user_id) filter to verify task ownership
- [X] T050 [US6] Return TaskResponse object with complete task details
- [X] T051 [US6] Return 200 OK with task data
- [X] T052 [US6] Return 401 Unauthorized for invalid JWT
- [X] T053 [US6] Return 404 Not Found for non-existent or unauthorized tasks
- [X] T054 [US6] Add route to main FastAPI app
- [ ] T055 [US6] [P] Write unit tests for GET /api/tasks/{id} endpoint
- [ ] T056 [US6] [P] Write integration tests for viewing specific task
- [ ] T057 [US6] [P] Write tests to verify user isolation for individual tasks

## Phase 7: [US3] Update Task Details

**Goal**: Allow users to update their task details while maintaining proper validation

**Independent Test**: Can be fully tested by making a PUT request to /api/tasks/{id} with updated task data and verifying the changes are persisted.

**Implementation Tasks**:

- [X] T058 [US3] Create PUT /api/tasks/{id} endpoint in routes/tasks.py
- [X] T059 [US3] Apply .where(Task.user_id == current_user_id) filter to verify task ownership
- [X] T060 [US3] Implement TaskUpdate request validation using Pydantic schema
- [X] T061 [US3] Update task fields (title, description, completed) as specified
- [X] T062 [US3] Apply validation rules for title (max 200 chars, if provided)
- [X] T063 [US3] Update updated_at timestamp when task is modified
- [X] T064 [US3] Return 200 OK with updated task data
- [X] T065 [US3] Return 401 Unauthorized for invalid JWT
- [X] T066 [US3] Return 404 Not Found for non-existent or unauthorized tasks
- [X] T067 [US3] Return 400 Bad Request for validation failures
- [X] T068 [US3] Add route to main FastAPI app
- [ ] T069 [US3] [P] Write unit tests for PUT /api/tasks/{id} endpoint
- [ ] T070 [US3] [P] Write integration tests for task updates
- [ ] T071 [US3] [P] Write tests to verify user isolation during updates

## Phase 8: [US5] Delete Task

**Goal**: Allow users to delete tasks they no longer need

**Independent Test**: Can be fully tested by making a DELETE request to /api/tasks/{id} and verifying the task is removed from the database.

**Implementation Tasks**:

- [X] T072 [US5] Create DELETE /api/tasks/{id} endpoint in routes/tasks.py
- [X] T073 [US5] Apply .where(Task.user_id == current_user_id) filter to verify task ownership
- [X] T074 [US5] Remove task from database
- [X] T075 [US5] Return 200 OK with success message
- [X] T076 [US5] Return 401 Unauthorized for invalid JWT
- [X] T077 [US5] Return 404 Not Found for non-existent or unauthorized tasks
- [X] T078 [US5] Add route to main FastAPI app
- [ ] T079 [US5] [P] Write unit tests for DELETE /api/tasks/{id} endpoint
- [ ] T080 [US5] [P] Write integration tests for task deletion
- [ ] T081 [US5] [P] Write tests to verify user isolation during deletion

## Phase 9: Security & User Isolation Verification

**Goal**: Ensure comprehensive security implementation and user data isolation

**Implementation Tasks**:

- [X] T082 Create comprehensive tests to verify that a user cannot access another user's tasks
- [X] T083 [P] Write integration tests for all endpoints to verify user isolation
- [X] T084 Implement standardized error responses for 401 Unauthorized and 404 Not Found scenarios
- [X] T085 Verify that every database operation includes .where(Task.user_id == current_user_id) filter
- [X] T086 Test edge cases: malformed JWT tokens, non-existent task IDs, etc.
- [ ] T087 Ensure 90% API test coverage standard is met across all endpoints

## Phase 10: Polish & Cross-Cutting Concerns

**Goal**: Complete the implementation with proper documentation, error handling, and quality assurance

**Implementation Tasks**:

- [X] T088 Add comprehensive error handling throughout all endpoints
- [ ] T089 Implement proper logging for security events and errors
- [X] T090 Add API documentation with Swagger/OpenAPI
- [X] T091 Perform security audit to verify all isolation mechanisms
- [ ] T092 Run all tests and ensure 90%+ coverage is achieved
- [ ] T093 Optimize database queries and add proper indexing as specified
- [ ] T094 Update README with API usage instructions
- [X] T095 Perform final integration testing of all user stories

## Dependencies

- **US1 (Create Task)**: Depends on foundational components (T001-T013)
- **US2 (View All Tasks)**: Depends on foundational components (T001-T013)
- **US4 (Mark Complete)**: Depends on foundational components (T001-T013)
- **US6 (View Specific Task)**: Depends on foundational components (T001-T013)
- **US3 (Update Task)**: Depends on US6 (for retrieving existing task)
- **US5 (Delete Task)**: Depends on foundational components (T001-T013)

## Parallel Execution Opportunities

- Tasks T008-T009 (models and schemas) can be developed in parallel with T006-T007 (database setup)
- All user story phases can have their unit tests (marked [P]) developed in parallel with implementation
- Multiple endpoints can be developed simultaneously after foundational components are complete

## Implementation Strategy

1. **MVP Scope**: Complete Phase 1, 2, and US1 (Task Creation) for minimal viable product
2. **Incremental Delivery**: Each user story phase adds complete, testable functionality
3. **Security First**: User isolation and authentication implemented early in foundational components
4. **Test Coverage**: Target 90%+ coverage throughout development process