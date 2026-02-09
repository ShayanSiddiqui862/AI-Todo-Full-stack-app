from fastapi import APIRouter, Depends, Query, HTTPException
from sqlmodel import Session, select
from typing import List, Optional
from datetime import datetime
import uuid
from backend.src.database import get_session
from backend.src.models.task import Task, TaskCreate, TaskUpdate
from backend.src.services.dapr_client import dapr_publish_event, dapr_schedule_job
from backend.src.services.recurrence import calculate_next_occurrence

router = APIRouter(prefix="/tasks", tags=["tasks"])

@router.post("/", response_model=Task)
async def create_task(task: TaskCreate, session: Session = Depends(get_session)):
    db_task = Task.model_validate(task)
    session.add(db_task)
    session.commit()
    session.refresh(db_task)

    # Publish task creation event
    await dapr_publish_event(
        pubsub_name="kafka-pubsub",
        topic="task-events",
        data={
            "event_type": "created",
            "task_id": db_task.id,
            "task_data": db_task.model_dump(),
            "user_id": db_task.user_id,
            "timestamp": datetime.utcnow().isoformat()
        }
    )

    # Schedule reminder if specified
    if db_task.remind_at:
        job_id = f"reminder-{db_task.id}-{uuid.uuid4()}"
        await dapr_schedule_job(
            job_id=job_id,
            due_time=db_task.remind_at.isoformat(),
            data={
                "task_id": db_task.id,
                "user_id": db_task.user_id,
                "task_title": db_task.title
            }
        )

    # Schedule next recurring task if applicable
    if db_task.recurrence_type != "none":
        job_id = f"recurring-{db_task.id}-{uuid.uuid4()}"
        next_occurrence_time = calculate_next_occurrence(
            db_task.due_date or datetime.utcnow(),
            db_task.recurrence_type,
            db_task.recurrence_interval
        )
        await dapr_schedule_job(
            job_id=job_id,
            due_time=next_occurrence_time.isoformat(),
            data={
                "original_task_id": db_task.id,
                "user_id": db_task.user_id
            }
        )

    return db_task

@router.get("/", response_model=List[Task])
async def get_tasks(
    user_id: str = Query(...),
    priority: Optional[str] = Query(None),
    tags: Optional[List[str]] = Query(None),
    due_date_start: Optional[datetime] = Query(None),
    due_date_end: Optional[datetime] = Query(None),
    completed: Optional[bool] = Query(None),
    sort_by: Optional[str] = Query("created_at"),
    sort_order: Optional[str] = Query("desc"),
    session: Session = Depends(get_session)
):
    query = select(Task).where(Task.user_id == user_id)

    if priority:
        query = query.where(Task.priority == priority)

    if tags:
        for tag in tags:
            query = query.where(Task.tags.any(tag))  # Using any() for array containment

    if due_date_start:
        query = query.where(Task.due_date >= due_date_start)

    if due_date_end:
        query = query.where(Task.due_date <= due_date_end)

    if completed is not None:
        query = query.where(Task.completed == completed)

    # Apply sorting
    if sort_by == "due_date":
        query = query.order_by(Task.due_date.desc() if sort_order == "desc" else Task.due_date.asc())
    elif sort_by == "priority":
        # Map priority to numeric values for proper sorting
        priority_order = {"high": 3, "medium": 2, "low": 1}
        # This would require a custom sort in the query or post-processing
        pass
    else:
        query = query.order_by(Task.created_at.desc() if sort_order == "desc" else Task.created_at.asc())

    tasks = session.exec(query).all()
    return tasks

@router.put("/{task_id}", response_model=Task)
async def update_task(task_id: int, task_update: TaskUpdate, session: Session = Depends(get_session)):
    db_task = session.get(Task, task_id)
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Store old values for comparison
    old_remind_at = db_task.remind_at
    old_recurrence_type = db_task.recurrence_type

    # Update task
    update_data = task_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_task, field, value)

    session.add(db_task)
    session.commit()
    session.refresh(db_task)

    # Publish task update event
    await dapr_publish_event(
        pubsub_name="kafka-pubsub",
        topic="task-events",
        data={
            "event_type": "updated",
            "task_id": db_task.id,
            "task_data": db_task.model_dump(),
            "user_id": db_task.user_id,
            "timestamp": datetime.utcnow().isoformat()
        }
    )

    # Cancel old reminder if it existed and was changed
    if old_remind_at and (not task_update.remind_at or task_update.remind_at != old_remind_at):
        # Cancel the old reminder job via Dapr
        pass

    # Schedule new reminder if added or changed
    if db_task.remind_at and db_task.remind_at != old_remind_at:
        job_id = f"reminder-{db_task.id}-{uuid.uuid4()}"
        await dapr_schedule_job(
            job_id=job_id,
            due_time=db_task.remind_at.isoformat(),
            data={
                "task_id": db_task.id,
                "user_id": db_task.user_id,
                "task_title": db_task.title
            }
        )

    # Cancel old recurrence job if it existed and was changed
    if old_recurrence_type != "none" and (not task_update.recurrence_type or task_update.recurrence_type != old_recurrence_type):
        # Cancel the old recurrence job via Dapr
        pass

    # Schedule new recurrence job if added or changed
    if db_task.recurrence_type != "none" and db_task.recurrence_type != old_recurrence_type:
        job_id = f"recurring-{db_task.id}-{uuid.uuid4()}"
        next_occurrence_time = calculate_next_occurrence(
            db_task.due_date or datetime.utcnow(),
            db_task.recurrence_type,
            db_task.recurrence_interval
        )
        await dapr_schedule_job(
            job_id=job_id,
            due_time=next_occurrence_time.isoformat(),
            data={
                "original_task_id": db_task.id,
                "user_id": db_task.user_id
            }
        )

    return db_task

@router.patch("/{task_id}/complete", response_model=Task)
async def complete_task(task_id: int, session: Session = Depends(get_session)):
    db_task = session.get(Task, task_id)
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")

    db_task.completed = True
    session.add(db_task)
    session.commit()
    session.refresh(db_task)

    # Publish task completion event
    await dapr_publish_event(
        pubsub_name="kafka-pubsub",
        topic="task-events",
        data={
            "event_type": "completed",
            "task_id": db_task.id,
            "task_data": db_task.model_dump(),
            "user_id": db_task.user_id,
            "timestamp": datetime.utcnow().isoformat()
        }
    )

    # If it's a recurring task, create the next instance
    if db_task.recurrence_type != "none":
        from backend.src.services.recurrence import create_next_recurring_instance
        next_task_data = create_next_recurring_instance(db_task.model_dump())
        next_db_task = Task.model_validate(next_task_data)
        session.add(next_db_task)
        session.commit()
        session.refresh(next_db_task)

        # Publish event for the new recurring task
        await dapr_publish_event(
            pubsub_name="kafka-pubsub",
            topic="task-events",
            data={
                "event_type": "created",
                "task_id": next_db_task.id,
                "task_data": next_db_task.model_dump(),
                "user_id": next_db_task.user_id,
                "timestamp": datetime.utcnow().isoformat()
            }
        )

    return db_task


@router.get("/search", response_model=List[Task])
async def search_tasks(
    query: str = Query(..., min_length=1),
    user_id: str = Query(...),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    session: Session = Depends(get_session)
):
    """
    Search tasks by title, description, or tags.
    """
    # Basic search implementation - in production, use PostgreSQL full-text search
    search_filter = Task.user_id == user_id
    
    # Search in title, description, and tags
    search_filter = search_filter & (
        Task.title.ilike(f"%{query}%") |
        Task.description.ilike(f"%{query}%") |
        Task.tags.any(query)  # Search in tags array
    )
    
    query_result = select(Task).where(search_filter).offset(offset).limit(limit)
    tasks = session.exec(query_result).all()
    
    return tasks