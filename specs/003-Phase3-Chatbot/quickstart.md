# Quickstart Guide: AI-Powered Todo Chatbot

## Prerequisites

- Python 3.11+
- Node.js 18+
- OpenAI API key
- MCP SDK
- PostgreSQL database (Neon recommended)

## Setup Backend

1. Install new dependencies:
```bash
pip install openai python-mcp-sdk
```

2. Add new models to your database:
```bash
# If using alembic for migrations
alembic revision --autogenerate -m "Add Conversation and Message models"
alembic upgrade head
```

3. Set environment variables:
```bash
OPENAI_API_KEY=your_openai_api_key
NEXT_PUBLIC_OPENAI_DOMAIN_KEY=your_domain_key
MCP_SERVER_PORT=3001
```

## Setup Frontend

1. Install ChatKit dependencies:
```bash
npm install @openai/chatkit
```

2. Configure environment variables:
```bash
NEXT_PUBLIC_OPENAI_DOMAIN_KEY=your_domain_key
```

## Run the Application

1. Start the MCP server:
```bash
cd backend/src/mcp
python server.py
```

2. Start the main backend:
```bash
cd backend
uvicorn main:app --reload
```

3. Start the frontend:
```bash
cd frontend
npm run dev
```

## Testing the Chatbot

1. Navigate to the chat interface (usually at `/chat`)
2. Authenticate with your credentials
3. Try natural language commands like:
   - "Add a task to buy groceries"
   - "Show me my pending tasks"
   - "Mark task 1 as completed"