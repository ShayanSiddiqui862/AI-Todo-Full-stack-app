# Quickstart Guide: Advanced Todo Features with Event-Driven Architecture

## Prerequisites

- Docker and Docker Compose
- Dapr CLI installed and initialized
- Python 3.11+
- Access to Neon PostgreSQL database

## Setup Instructions

### 1. Initialize Dapr
```bash
dapr init
```

### 2. Clone and Navigate to Project
```bash
git clone <repository-url>
cd Todo-Full-stack
```

### 3. Start Infrastructure Services
```bash
# Start Kafka (via Redpanda), PostgreSQL, and other services
docker-compose up -d

# Wait for services to be ready
sleep 30
```

### 4. Install Python Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 5. Configure Environment Variables
Create a `.env` file in the backend directory:
```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/todo_app
DAPR_HTTP_PORT=3500
DAPR_GRPC_PORT=50001
OPENAI_API_KEY=<your-openai-key>
```

## Running the Application

### 1. Run the Main API Service with Dapr
```bash
# From the project root
dapr run \
  --app-id chat-api \
  --app-port 8000 \
  --dapr-http-port 3500 \
  --dapr-grpc-port 50001 \
  --config ./dapr-components/config.yaml \
  --components-path ./dapr-components \
  -- python -m backend.src.main
```

### 2. Run Consumer Services
In separate terminals:

```bash
# Notification Service
dapr run \
  --app-id notification-service \
  --app-port 8001 \
  --dapr-http-port 3501 \
  --dapr-grpc-port 50002 \
  --config ./dapr-components/config.yaml \
  --components-path ./dapr-components \
  -- python -m consumers.notification_service.main
```

```bash
# Recurring Task Service
dapr run \
  --app-id recurring-task-service \
  --app-port 8002 \
  --dapr-http-port 3502 \
  --dapr-grpc-port 50003 \
  --config ./dapr-components/config.yaml \
  --components-path ./dapr-components \
  -- python -m consumers.recurring_task_service.main
```

### 3. Run the Frontend
```bash
cd frontend
npm install
npm run dev
```

## Key Features Walkthrough

### Creating a Recurring Task
```bash
curl -X POST http://localhost:8000/tasks/ \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Morning Exercise",
    "description": "Daily morning workout routine",
    "user_id": "user123",
    "recurrence_type": "daily",
    "recurrence_interval": 1,
    "due_date": "2026-02-09T08:00:00Z"
  }'
```

### Setting a Task with Reminder
```bash
curl -X POST http://localhost:8000/tasks/ \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Team Meeting",
    "description": "Weekly team sync",
    "user_id": "user123",
    "due_date": "2026-02-09T10:00:00Z",
    "remind_at": "2026-02-09T09:30:00Z",
    "priority": "high",
    "tags": ["work", "meeting"]
  }'
```

### Filtering Tasks by Priority
```bash
curl "http://localhost:8000/tasks/?user_id=user123&priority=high"
```

### Searching Tasks
```bash
curl "http://localhost:8000/tasks/search?query=meeting&user_id=user123"
```

## Dapr Components Overview

### Pub/Sub (Kafka)
- Component name: `kafka-pubsub`
- Topics: `task-events`, `reminders`, `task-updates`
- Used for: Event-driven communication between services

### State Store (PostgreSQL)
- Component name: `statestore`
- Used for: Storing temporary state and caching

### Secrets Store (Kubernetes)
- Component name: `kubernetes-secrets`
- Used for: Secure access to API keys and credentials

## Troubleshooting

### Common Issues

1. **Dapr Sidecar Not Starting**
   - Ensure Dapr is properly initialized: `dapr uninstall && dapr init`
   - Check if ports are available: `lsof -i :3500` (or relevant port)

2. **Kafka Connection Issues**
   - Verify Redpanda is running: `docker ps | grep redpanda`
   - Check connectivity: `telnet localhost 9092`

3. **Database Connection Issues**
   - Verify PostgreSQL is running: `docker ps | grep postgres`
   - Check connection string in environment variables

### Useful Commands

- Check Dapr sidecar logs: `dapr logs <app-id>`
- List running Dapr apps: `dapr list`
- Check component health: `dapr components`
- View sent events: Check the `task_events` table in PostgreSQL

## Next Steps

1. Explore the API documentation at `http://localhost:8000/docs`
2. Customize the Dapr components in `./dapr-components/`
3. Add more consumer services for additional functionality
4. Implement the frontend components to support new features