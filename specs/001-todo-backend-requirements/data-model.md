# Data Model: Todo Application Backend

## Entity: Task

### Fields
- **id** (Integer, Primary Key, Auto-generated)
  - Unique identifier for each task
  - Auto-incremented by the database
  - Required for all operations

- **user_id** (String, Foreign Key, Indexed)
  - Identifier for the user who owns the task
  - Extracted from JWT token in authentication process
  - Required field, indexed for performance
  - Critical for user data isolation

- **title** (String, Max Length 200, Required)
  - Title of the task
  - Minimum length: 1 character (validation required)
  - Maximum length: 200 characters
  - Required for creation

- **description** (Text, Optional)
  - Detailed description of the task
  - Nullable field
  - Optional for all operations

- **completed** (Boolean)
  - Status indicator for task completion
  - Default value: False
  - Can be toggled via API

- **created_at** (DateTime with Timezone)
  - Timestamp when the task was created
  - Automatically set by the system
  - Read-only from API perspective

- **updated_at** (DateTime with Timezone)
  - Timestamp when the task was last updated
  - Automatically updated by the system when modified
  - Read-only from API perspective

### Relationships
- **User** (One-to-Many)
  - Each user can have multiple tasks
  - Each task belongs to exactly one user
  - Enforced by user_id foreign key constraint

### Validation Rules
1. **Title Required**: Task.title must not be empty during creation (length > 0)
2. **Title Length**: Task.title must be 200 characters or less
3. **User Ownership**: All operations must verify Task.user_id matches authenticated user's ID
4. **Completed Default**: Task.completed defaults to False if not specified
5. **Immutable Fields**: Task.id, Task.created_at, and Task.user_id cannot be modified after creation

### State Transitions
- **Creation**: Task transitions from non-existent to created state
  - user_id is set from authenticated user context
  - title is set from request data
  - description is set from request data (optional)
  - completed is set to False (default)
  - created_at is set to current timestamp
  - updated_at is set to current timestamp

- **Update**: Task properties can be modified (except id, user_id)
  - title, description, completed can be updated
  - updated_at is automatically set to current timestamp

- **Completion Toggle**: Special update operation for completion status
  - completed field is toggled or set to specified value
  - updated_at is automatically set to current timestamp

- **Deletion**: Task transitions to deleted state (removed from database)
  - Only accessible to the owning user
  - Permanent deletion from database

### Indexes
1. **idx_tasks_user_id**: Index on user_id field for efficient user-specific queries
2. **idx_tasks_completed**: Index on completed field for efficient status filtering
3. **idx_tasks_user_id_completed**: Composite index for queries filtering by both user and status
4. **idx_tasks_created_at**: Index on created_at for chronological sorting

## Entity: User (Implicit via JWT)

### Attributes
- **user_id** (String)
  - Extracted from JWT token during authentication
  - Used to establish ownership of tasks
  - Required for all authenticated operations

### Relationships
- **Tasks** (One-to-Many)
  - One user can own multiple tasks
  - Access to tasks is restricted to the owning user

### Validation Rules
1. **Authentication Required**: All task operations require valid JWT token
2. **Ownership Verification**: User can only access tasks with matching user_id
3. **Token Validity**: JWT must be properly signed and not expired