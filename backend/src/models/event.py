from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional
import uuid

class TaskEvents(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    event_type: str = Field(max_length=50)  # created, updated, completed, deleted, reminder_triggered, notification_sent
    task_id: Optional[int] = Field(default=None, foreign_key="task.id")
    user_id: str = Field(max_length=100)
    payload: dict  # JSONB field to store event-specific data
    created_at: datetime = Field(default_factory=datetime.utcnow)