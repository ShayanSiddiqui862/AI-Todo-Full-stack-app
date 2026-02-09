# Quickstart Guide: Todo Backend Development

## Prerequisites

- Python 3.11+
- Poetry or pip for dependency management
- Neon Serverless PostgreSQL database instance
- BETTER_AUTH_SECRET environment variable set

## Environment Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Todo-Full-stack
   ```

2. **Navigate to backend directory**
   ```bash
   cd backend
   ```

3. **Install dependencies**
   ```bash
   # Using poetry
   poetry install

   # Or using pip
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Create a `.env` file in the backend directory:
   ```env
   DATABASE_URL=postgresql+asyncpg://username:password@host:port/database_name
   BETTER_AUTH_SECRET=your_jwt_secret_here
   ```

## Project Structure

```
backend/
├── main.py              # FastAPI application entry point
├── db.py               # Database engine and session setup
├── models.py           # SQLModel definitions for Task entity
├── auth.py             # JWT verification middleware and user context
├── routes/
│   └── tasks.py        # Task CRUD endpoint implementations
├── schemas.py          # Pydantic schemas for API requests/responses
└── tests/
    ├── unit/
    ├── integration/
    └── contract/
```

## Key Components

### 1. Database Layer (`db.py`)
- Async engine setup for Neon PostgreSQL
- Session dependency for FastAPI
- Connection pooling configuration

### 2. Data Models (`models.py`)
- Task SQLModel with all required fields
- Automatic timestamp management
- Proper field validations

### 3. Authentication (`auth.py`)
- JWT verification using BETTER_AUTH_SECRET
- User context extraction from tokens
- 401 Unauthorized handling

### 4. API Routes (`routes/tasks.py`)
- Complete CRUD operations for tasks
- User isolation enforcement
- Proper error handling

### 5. API Schemas (`schemas.py`)
- Request/response validation models
- Different schemas for create/read/update operations
- Type safety between API and database

## Running the Application

1. **Start the development server**
   ```bash
   uvicorn main:app --reload
   ```

2. **Access the API**
   - API documentation: http://localhost:8000/docs
   - API base URL: http://localhost:8000/api/

3. **Example API call**
   ```bash
   # Get all tasks (requires valid JWT in Authorization header)
   curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
        http://localhost:8000/api/tasks
   ```

## Testing

1. **Run unit tests**
   ```bash
   pytest tests/unit/
   ```

2. **Run integration tests**
   ```bash
   pytest tests/integration/
   ```

3. **Run all tests with coverage**
   ```bash
   pytest --cov=backend/ --cov-report=html
   ```

## Key Development Patterns

### Database Session Management
```python
from db import get_session

async def some_endpoint(session: AsyncSession = Depends(get_session)):
    # Session automatically closed after request
    pass
```

### Authentication Dependency
```python
from auth import verify_jwt

async def protected_endpoint(
    current_user_id: str = Depends(verify_jwt),
    session: AsyncSession = Depends(get_session)
):
    # Get only user's tasks
    tasks = await session.exec(
        select(Task).where(Task.user_id == current_user_id)
    )
```

### User Isolation Pattern
```python
# ALWAYS filter by user_id
result = await session.exec(
    select(Task).where(
        Task.id == task_id,
        Task.user_id == current_user_id  # Critical for security
    )
)
```

## Common Commands

- **Format code**: `black . && isort .`
- **Lint code**: `flake8 .` or `pylint .`
- **Run tests**: `pytest`
- **Check types**: `mypy .`
- **Serve docs**: `uvicorn main:app --reload --port 8001`

## Troubleshooting

1. **Database connection issues**
   - Verify DATABASE_URL is correctly set
   - Check Neon PostgreSQL connection settings
   - Ensure database credentials are valid

2. **JWT authentication failures**
   - Confirm BETTER_AUTH_SECRET matches the one used to create tokens
   - Verify JWT format and signature
   - Check token expiration

3. **User isolation not working**
   - Ensure all database queries include `.where(Task.user_id == current_user_id)`
   - Verify verify_jwt dependency is properly applied to routes