from sqlmodel import SQLModel, Field, ARRAY, String
from datetime import datetime
from typing import List, Optional

class TaskBase(SQLModel):
    title: str
    description: Optional[str] = None
    completed: bool = False
    user_id: str

class Task(TaskBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    priority: str = Field(default="medium", max_length=10)  # low, medium, high
    tags: List[str] = Field(default=[], sa_column=Field(ARRAY(String)))  # e.g., ["work", "personal"]
    due_date: Optional[datetime] = None
    remind_at: Optional[datetime] = None
    recurrence_type: str = Field(default="none", max_length=20)  # none, daily, weekly, monthly
    recurrence_interval: int = Field(default=1)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class TaskCreate(TaskBase):
    priority: Optional[str] = "medium"
    tags: List[str] = []
    due_date: Optional[datetime] = None
    remind_at: Optional[datetime] = None
    recurrence_type: Optional[str] = "none"
    recurrence_interval: Optional[int] = 1

class TaskUpdate(SQLModel):
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None
    priority: Optional[str] = None
    tags: Optional[List[str]] = None
    due_date: Optional[datetime] = None
    remind_at: Optional[datetime] = None
    recurrence_type: Optional[str] = None
    recurrence_interval: Optional[int] = None