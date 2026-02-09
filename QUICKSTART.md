# Quickstart Guide: Todo Chatbot Advanced Features

This guide will help you get the Todo Chatbot with advanced features up and running locally using Dapr and Redpanda.

## Prerequisites

- Docker and Docker Compose
- Dapr CLI installed and initialized
- Python 3.11+
- Node.js 18+ (for frontend)

## Step 1: Initialize Dapr

```bash
dapr init
```

## Step 2: Clone the Repository

```bash
git clone <repository-url>
cd Todo-Full-stack
```

## Step 3: Start Infrastructure Services

```bash
# Start Kafka (via Redpanda), PostgreSQL, and other services
docker-compose up -d

# Wait for services to be ready (approximately 30 seconds)
sleep 30
```

## Step 4: Backend Setup

```bash
cd backend

# Install Python dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration if needed
```

## Step 5: Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Set up environment variables
cp .env.local.example .env.local
# Edit .env.local with your configuration if needed
```

## Step 6: Run the Application

### Terminal 1: Start the main API service with Dapr
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

### Terminal 2: Start the Notification Service
```bash
# From the project root
dapr run \
  --app-id notification-service \
  --app-port 8001 \
  --dapr-http-port 3501 \
  --dapr-grpc-port 50002 \
  --config ./dapr-components/config.yaml \
  --components-path ./dapr-components \
  -- python -m consumers.notification_service.main
```

### Terminal 3: Start the Recurring Task Service
```bash
# From the project root
dapr run \
  --app-id recurring-task-service \
  --app-port 8002 \
  --dapr-http-port 3502 \
  --dapr-grpc-port 50003 \
  --config ./dapr-components/config.yaml \
  --components-path ./dapr-components \
  -- python -m consumers.recurring_task_service.main
```

### Terminal 4: Start the Audit Service
```bash
# From the project root
dapr run \
  --app-id audit-service \
  --app-port 8003 \
  --dapr-http-port 3503 \
  --dapr-grpc-port 50004 \
  --config ./dapr-components/config.yaml \
  --components-path ./dapr-components \
  -- python -m consumers.audit_service.main
```

### Terminal 5: Start the Frontend
```bash
cd frontend
npm run dev
```

## Step 7: Verify Everything is Working

1. Visit the frontend at `http://localhost:3000`
2. Create a test task with advanced features:
   - Set a priority (low, medium, high)
   - Add tags (e.g., "work", "important")
   - Set a due date
   - Set a reminder time
   - Make it recurring (daily, weekly, or monthly)
3. Check the Dapr logs to verify events are being published:
   ```bash
   dapr logs chat-api
   dapr logs notification-service
   dapr logs recurring-task-service
   dapr logs audit-service
   ```

## Key Features to Test

### Recurring Tasks
1. Create a task with recurrence set to "daily"
2. Complete the task
3. Verify that a new instance of the task is automatically created

### Reminders
1. Create a task with a reminder set for a few minutes in the future
2. Wait for the reminder time
3. Check the notification service logs to verify the reminder was triggered

### Priorities & Tags
1. Create tasks with different priorities and tags
2. Use the filtering options to view tasks by priority or tag

### Search
1. Create tasks with different titles, descriptions, and tags
2. Use the search functionality to find tasks

## Troubleshooting

### Common Issues

1. **Services won't start**: Make sure Docker is running and you've initialized Dapr
2. **Port conflicts**: Check if ports 8000, 3000, 3500, 9092, or 5432 are already in use
3. **Database connection errors**: Ensure PostgreSQL container is running (`docker ps | grep postgres`)

### Useful Commands

- Check running containers: `docker ps`
- Check Dapr apps: `dapr list`
- Check Dapr logs: `dapr logs <app-id>`
- Check container logs: `docker logs <container-name>`

## Next Steps

Now that you have the system running, you can:
- Explore the API documentation at `http://localhost:8000/docs`
- Modify the consumer services to add custom logic
- Add new event types and handlers
- Experiment with different Dapr components