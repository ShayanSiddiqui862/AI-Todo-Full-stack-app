from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import ARRAY, String as sa_String
from typing import Optional, List
from datetime import datetime

# User Model for authentication
class User(SQLModel, table=True):
    id: Optional[str] = Field(default=None, primary_key=True)  # Using string ID to match Better Auth
    email: str = Field(unique=True, index=True)
    username: str = Field(unique=True, index=True)
    hashed_password: Optional[str] = Field(default=None)  # Optional for OAuth-only users
    full_name: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = Field(default=True)
    is_verified: bool = Field(default=False)  # For email verification status
    avatar_url: Optional[str] = Field(default=None)  # For profile picture from OAuth
    oauth_provider: Optional[str] = Field(default=None)  # 'google' or null for regular users

# Refresh Tokens Model for secure token management
class RefreshToken(SQLModel, table=True):
    token_hash: str = Field(primary_key=True, max_length=64)  # SHA-256 hash
    user_id: str = Field(index=True)  # Foreign key to user
    expires_at: datetime
    is_revoked: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)


# Task Model
class Task(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True)  # Foreign key to user, indexed for performance
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = Field(default=None)
    completed: bool = Field(default=False)
    scheduled_time: Optional[datetime] = Field(default=None)  # Time when task should be performed
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    # New fields for advanced features
    priority: str = Field(default="medium", max_length=10)  # low, medium, high
    tags: List[str] = Field(default=None, sa_column=Field(ARRAY(sa_String)))  # e.g., ["work", "personal"]
    due_date: Optional[datetime] = None
    remind_at: Optional[datetime] = None
    recurrence_type: str = Field(default="none", max_length=20)  # none, daily, weekly, monthly
    recurrence_interval: int = Field(default=1)


# Conversation Model
class Conversation(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True)  # Foreign key to User, indexed for performance
    title: Optional[str] = Field(default=None, max_length=200)  # Optional title for the conversation
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationship to messages
    messages: List["Message"] = Relationship(back_populates="conversation")


# Message Model
class Message(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    conversation_id: int = Field(foreign_key="conversation.id", index=True)  # Foreign key to Conversation
    role: str = Field(regex="^(user|assistant)$")  # Either "user" or "assistant"
    content: str = Field(min_length=1, max_length=10000)  # The message content
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationship to conversation
    conversation: Optional[Conversation] = Relationship(back_populates="messages")