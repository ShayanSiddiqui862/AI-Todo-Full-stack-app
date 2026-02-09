from sqlmodel import create_engine, Session
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import os
from contextlib import asynccontextmanager
from dotenv import load_dotenv   
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# Create async engine
async_engine = create_async_engine(DATABASE_URL)

# Create async session maker
AsyncSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# For FastAPI dependency injection (no decorator needed)
async def get_session():
    async with AsyncSessionLocal() as session:
        yield session

# For direct use with `async with` in services
@asynccontextmanager
async def get_session_context():
    async with AsyncSessionLocal() as session:
        yield session