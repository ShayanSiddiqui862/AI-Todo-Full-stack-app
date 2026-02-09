from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional

class ScheduledJobs(SQLModel, table=True):
    id: str = Field(max_length=100, primary_key=True)  # Dapr job ID
    job_type: str = Field(max_length=50)  # 'reminder', 'recurring_next'
    task_id: Optional[int] = Field(default=None, foreign_key="task.id")
    user_id: str = Field(max_length=100)
    scheduled_time: datetime
    created_at: datetime = Field(default_factory=datetime.utcnow)
    executed: bool = Field(default=False)