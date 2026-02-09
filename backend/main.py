from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import tasks
from src.routes import chat
from src.routes import session
from auth.routes import router as auth_router
from contextlib import asynccontextmanager
from sqlmodel import SQLModel
from db import async_engine

@asynccontextmanager
async def lifespan(app: FastAPI):
    # This runs when the server starts
    async with async_engine.begin() as conn:
        # This creates all tables defined in your models.py
        await conn.run_sync(SQLModel.metadata.create_all)
    yield
    # This runs when the server stops

app = FastAPI(title="Todo Application API", version="1.0.0", lifespan=lifespan)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include task routes
app.include_router(tasks.router, prefix="/api", tags=["tasks"])

# Include chat routes
app.include_router(chat.router, prefix="/api", tags=["chat"])

# Include chat session routes for ChatKit
app.include_router(session.router, prefix="/api", tags=["chat-session"])

# Include auth routes
app.include_router(auth_router, prefix="/api/auth", tags=["auth"])

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
