# Phase V Part A – Tasks
**Feature Branch**: 001-advanced-todo-features
**Estimated total effort**: 40–60 hours

## Phase 0: Preparation & Setup

- [X] T001 Create dapr-components directory structure in backend/
- [X] T002 Set up docker-compose.yml with Redpanda and PostgreSQL services
- [X] T003 [P] Update requirements.txt with Dapr SDK and kafka-python dependencies

## Phase 1: Database & Models

- [X] T004 Create updated Task model with new fields (priority, tags, due_date, etc.) in backend/src/models/task.py
- [X] T005 Create TaskCreate and TaskUpdate schemas in backend/src/models/task.py
- [X] T006 Create TaskEvents model for tracking events in backend/src/models/event.py
- [X] T007 Create ScheduledJobs model for job tracking in backend/src/models/job.py
- [X] T008 Create Alembic migration script for database schema changes in backend/src/db/migrations/001_advanced_features.py
- [X] T009 [P] Update existing Task model to include new fields while maintaining backward compatibility

## Phase 2: Dapr Infrastructure

- [X] T010 Create Dapr pubsub component YAML for Kafka in dapr-components/pubsub.yaml
- [X] T011 Create Dapr state store component YAML for PostgreSQL in dapr-components/statestore.yaml
- [X] T012 Create Dapr secrets component YAML in dapr-components/secrets.yaml
- [X] T013 Create Dapr jobs component YAML in dapr-components/bindings-jobs.yaml
- [X] T014 Implement Dapr client helper functions in backend/src/services/dapr_client.py
- [X] T015 [P] Create configuration files for Dapr components

## Phase 3: [US1] Recurring Tasks Implementation

- [X] T016 [US1] Implement calculate_next_occurrence function for recurrence logic in backend/src/services/recurrence.py
- [X] T017 [US1] Implement create_next_recurring_instance function in backend/src/services/recurrence.py
- [X] T018 [US1] Update create_task endpoint to schedule recurring tasks via Dapr Jobs API in backend/src/api/tasks.py
- [X] T019 [US1] Update complete_task endpoint to create next recurring instance in backend/src/api/tasks.py
- [X] T020 [US1] Create recurring_task_service consumer stub in consumers/recurring_task_service/main.py
- [ ] T021 [US1] [P] Add recurrence_type and recurrence_interval validation in models

## Phase 4: [US2] Due Dates & Reminders Implementation

- [X] T022 [US2] Update create_task endpoint to schedule reminders via Dapr Jobs API in backend/src/api/tasks.py
- [X] T023 [US2] Update update_task endpoint to reschedule reminders when dates change in backend/src/api/tasks.py
- [X] T024 [US2] Create notification_service consumer stub in consumers/notification_service/main.py
- [X] T025 [US2] Implement reminder event publishing in backend/src/services/event_publisher.py
- [ ] T026 [US2] [P] Add due_date and remind_at validation in models

## Phase 5: [US3] Priorities & Tags Implementation

- [X] T027 [US3] Update Task model to support priority field with enum validation
- [X] T028 [US3] Update get_tasks endpoint to filter by priority in backend/src/api/tasks.py
- [X] T029 [US3] Update Task model to support tags array field with PostgreSQL JSONB
- [X] T030 [US3] Update get_tasks endpoint to filter by tags in backend/src/api/tasks.py
- [X] T031 [US3] [P] Add tag search functionality to search endpoint

## Phase 6: [US4] Search & Filter Implementation

- [X] T032 [US4] Create search endpoint with full-text search capability in backend/src/api/tasks.py
- [X] T033 [US4] Update get_tasks endpoint to support multiple filter parameters in backend/src/api/tasks.py
- [X] T034 [US4] Update get_tasks endpoint to support sorting by various fields in backend/src/api/tasks.py
- [X] T035 [US4] Implement PostgreSQL full-text search indexes for efficient searching
- [X] T036 [US4] [P] Add comprehensive query parameter validation for search filters

## Phase 7: Frontend Updates

- [X] T037 Update TaskForm component to include new fields (priority, tags, due_date, etc.) in frontend/src/components/TaskForm.jsx
- [X] T038 Update TaskList component to support filtering and sorting in frontend/src/components/TaskList.jsx
- [X] T039 Update TaskCard component to display priority, tags, due dates in frontend/src/components/TaskCard.jsx
- [X] T040 Update API service to handle new endpoint parameters in frontend/src/services/api.js
- [X] T041 [P] Add date picker component for due_date and remind_at fields

## Phase 8: Event-Driven Architecture

- [X] T042 Create event publisher service to handle task-events in backend/src/services/event_publisher.py
- [X] T043 Create event subscriber stubs for audit_service in consumers/audit_service/main.py
- [X] T044 Update task endpoints to publish appropriate events (created, updated, completed) in backend/src/api/tasks.py
- [X] T045 [P] Implement event schema validation for task-events, reminders, and task-updates

## Phase 9: Testing & Validation

- [X] T046 Create unit tests for recurrence calculation logic in tests/unit/test_recurrence.py
- [X] T047 Create unit tests for reminder scheduling in tests/unit/test_reminders.py
- [X] T048 Create integration tests for Dapr pub/sub functionality in tests/integration/test_event_flow.py
- [X] T049 Create API contract tests for new endpoints in tests/contract/test_openapi.py
- [X] T050 [P] Create mock Dapr components for testing in tests/conftest.py

## Phase 10: Polish & Cross-Cutting Concerns

- [X] T051 Update README with setup instructions for new features and Dapr integration
- [X] T052 Add architecture diagram to documentation showing event-driven flow
- [X] T053 Create quickstart guide for local development with Dapr and Redpanda
- [X] T054 [P] Add error handling and logging for Dapr integration points
- [X] T055 Perform end-to-end testing of all new features with Dapr and event flow

## Dependencies

- T001-T003: Base setup tasks with no dependencies
- T004-T009: Depend on T001-T003 (database models depend on project structure)
- T010-T015: Depend on T001-T003 (Dapr components depend on project structure)
- T016-T021: Depend on T004-T009 (recurring tasks depend on models)
- T022-T026: Depend on T004-T009 and T014-T015 (reminders depend on models and Dapr)
- T027-T031: Depend on T004-T009 (priority/tags depend on models)
- T032-T036: Depend on T004-T009 (search/filter depend on models)
- T037-T041: Depend on T004-T009 and API endpoints (frontend depends on backend)
- T042-T045: Depend on T010-T015 and T004-T009 (events depend on Dapr and models)
- T046-T050: Depend on all previous phases (testing covers all functionality)
- T051-T055: Depend on all previous phases (documentation covers complete feature)

## Parallel Execution Examples

- T004-T009 can be done in parallel with T010-T015 (models and Dapr components are independent)
- T016-T021 (recurring tasks) can be developed in parallel with T022-T026 (reminders)
- T027-T031 (priorities/tags) can be developed in parallel with T032-T036 (search/filter)
- T037-T041 (frontend) can be developed in parallel with backend API development
- T046-T050 (testing) can begin as soon as individual components are implemented

## Implementation Strategy

1. **MVP Scope**: Focus on US1 (Recurring Tasks) and US2 (Reminders) for initial working system
2. **Incremental Delivery**: Each user story phase delivers independently testable functionality
3. **Backward Compatibility**: Ensure existing Phase IV functionality remains intact throughout development
4. **Event-Driven First**: Implement event publishing before consumer logic to establish the architecture early