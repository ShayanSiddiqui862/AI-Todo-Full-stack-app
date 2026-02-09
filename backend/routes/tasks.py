from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select
from typing import List
from models import Task
from schemas import TaskCreate as TaskCreateSchema, TaskUpdate as TaskUpdateSchema, TaskResponse as TaskResponseSchema
from db import get_session
from auth import verify_jwt
from sqlmodel.ext.asyncio.session import AsyncSession
from datetime import datetime, timedelta

router = APIRouter()

@router.post("/tasks", response_model=TaskResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_data: TaskCreateSchema,
    current_user_id: str = Depends(verify_jwt),
    session: AsyncSession = Depends(get_session)
):
    # Convert scheduled_time to naive datetime if it has timezone info
    scheduled_time = task_data.scheduled_time
    if scheduled_time and scheduled_time.tzinfo is not None:
        scheduled_time = scheduled_time.replace(tzinfo=None)
    
    # Create task with user_id from JWT
    task = Task(
        title=task_data.title,
        description=task_data.description,
        completed=task_data.completed,
        scheduled_time=scheduled_time,
        user_id=current_user_id
    )

    session.add(task)
    await session.commit()
    await session.refresh(task)

    # Create response object
    response = TaskResponseSchema(
        id=task.id,
        user_id=task.user_id,
        title=task.title,
        description=task.description,
        completed=task.completed,
        scheduled_time=task.scheduled_time,
        created_at=task.created_at,
        updated_at=task.updated_at
    )

    return response

@router.get("/tasks", response_model=List[TaskResponseSchema])
async def get_tasks(
    current_user_id: str = Depends(verify_jwt),
    session: AsyncSession = Depends(get_session)
):
    # Get only tasks belonging to the current user
    statement = select(Task).where(Task.user_id == current_user_id)
    result = await session.execute(statement)
    tasks = result.scalars().all()

    # Convert to response models
    response_tasks = [
        TaskResponseSchema(
            id=task.id,
            user_id=task.user_id,
            title=task.title,
            description=task.description,
            completed=task.completed,
            scheduled_time=task.scheduled_time,
            created_at=task.created_at,
            updated_at=task.updated_at
        )
        for task in tasks
    ]

    return response_tasks


@router.get("/tasks/completed", response_model=List[TaskResponseSchema])
async def get_completed_tasks(
    current_user_id: str = Depends(verify_jwt),
    session: AsyncSession = Depends(get_session)
):
    # Get only completed tasks belonging to the current user
    statement = select(Task).where(Task.user_id == current_user_id, Task.completed == True)
    result = await session.execute(statement)
    tasks = result.scalars().all()

    # Convert to response models
    response_tasks = [
        TaskResponseSchema(
            id=task.id,
            user_id=task.user_id,
            title=task.title,
            description=task.description,
            completed=task.completed,
            scheduled_time=task.scheduled_time,
            created_at=task.created_at,
            updated_at=task.updated_at
        )
        for task in tasks
    ]

    return response_tasks


@router.get("/tasks/pending", response_model=List[TaskResponseSchema])
async def get_pending_tasks(
    current_user_id: str = Depends(verify_jwt),
    session: AsyncSession = Depends(get_session)
):
    # Get only pending (incomplete) tasks belonging to the current user
    statement = select(Task).where(Task.user_id == current_user_id, Task.completed == False)
    result = await session.execute(statement)
    tasks = result.scalars().all()

    # Convert to response models
    response_tasks = [
        TaskResponseSchema(
            id=task.id,
            user_id=task.user_id,
            title=task.title,
            description=task.description,
            completed=task.completed,
            scheduled_time=task.scheduled_time,
            created_at=task.created_at,
            updated_at=task.updated_at
        )
        for task in tasks
    ]

    return response_tasks

@router.get("/tasks/{task_id}", response_model=TaskResponseSchema)
async def get_task(
    task_id: int,
    current_user_id: str = Depends(verify_jwt),
    session: AsyncSession = Depends(get_session)
):
    # Get task belonging to the current user
    statement = select(Task).where(Task.id == task_id, Task.user_id == current_user_id)
    result = await session.execute(statement)
    task = result.scalars().first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found or does not belong to user"
        )

    # Create response object
    response = TaskResponseSchema(
        id=task.id,
        user_id=task.user_id,
        title=task.title,
        description=task.description,
        completed=task.completed,
        scheduled_time=task.scheduled_time,
        created_at=task.created_at,
        updated_at=task.updated_at
    )

    return response

@router.put("/tasks/{task_id}", response_model=TaskResponseSchema)
async def update_task(
    task_id: int,
    task_data: TaskUpdateSchema,
    current_user_id: str = Depends(verify_jwt),
    session: AsyncSession = Depends(get_session)
):
    # Get task belonging to the current user
    statement = select(Task).where(Task.id == task_id, Task.user_id == current_user_id)
    result = await session.execute(statement)
    task = result.scalars().first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found or does not belong to user"
        )

    # Apply updates if provided
    if task_data.title is not None:
        # Validate title length if provided (min_length=1, max_length=200)
        if len(task_data.title) > 200 or len(task_data.title.strip()) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Title must be between 1 and 200 characters"
            )
        task.title = task_data.title

    if task_data.description is not None:
        task.description = task_data.description

    if task_data.completed is not None:
        task.completed = task_data.completed

    if task_data.scheduled_time is not None:
        scheduled_time = task_data.scheduled_time
        if scheduled_time.tzinfo is not None:
            scheduled_time = scheduled_time.replace(tzinfo=None)
        task.scheduled_time = scheduled_time

    # Update the updated_at timestamp
    task.updated_at = datetime.utcnow()

    await session.commit()
    await session.refresh(task)

    # Create response object
    response = TaskResponseSchema(
        id=task.id,
        user_id=task.user_id,
        title=task.title,
        description=task.description,
        completed=task.completed,
        scheduled_time=task.scheduled_time,
        created_at=task.created_at,
        updated_at=task.updated_at
    )

    return response

@router.delete("/tasks/{task_id}")
async def delete_task(
    task_id: int,
    current_user_id: str = Depends(verify_jwt),
    session: AsyncSession = Depends(get_session)
):
    # Get task belonging to the current user
    statement = select(Task).where(Task.id == task_id, Task.user_id == current_user_id)
    result = await session.execute(statement)
    task = result.scalars().first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found or does not belong to user"
        )

    await session.delete(task)
    await session.commit()

    return {"message": "Task deleted successfully"}

@router.patch("/tasks/{task_id}/complete", response_model=TaskResponseSchema)
async def update_task_completion(
    task_id: int,
    request_data: dict,
    current_user_id: str = Depends(verify_jwt),
    session: AsyncSession = Depends(get_session)
):
    # Get task belonging to the current user
    statement = select(Task).where(Task.id == task_id, Task.user_id == current_user_id)
    result = await session.execute(statement)
    task = result.scalars().first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found or does not belong to user"
        )

    # Determine the new completion status
    if "completed" in request_data:
        # Explicit set logic
        task.completed = request_data["completed"]
    else:
        # Toggle logic (if no "completed" field provided, toggle current status)
        task.completed = not task.completed

    # Update the updated_at timestamp
    task.updated_at = datetime.utcnow()

    await session.commit()
    await session.refresh(task)

    # Create response object
    response = TaskResponseSchema(
        id=task.id,
        user_id=task.user_id,
        title=task.title,
        description=task.description,
        completed=task.completed,
        scheduled_time=task.scheduled_time,
        created_at=task.created_at,
        updated_at=task.updated_at
    )

    return response


@router.patch("/tasks/{task_id}/delay", response_model=TaskResponseSchema)
async def delay_task(
    task_id: int,
    delay_data: dict,
    current_user_id: str = Depends(verify_jwt),
    session: AsyncSession = Depends(get_session)
):
    """Delay a task's scheduled time by a specified number of minutes."""
    # Get task belonging to the current user
    statement = select(Task).where(Task.id == task_id, Task.user_id == current_user_id)
    result = await session.execute(statement)
    task = result.scalars().first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found or does not belong to user"
        )

    # Get delay minutes from request (default 15 minutes)
    delay_minutes = delay_data.get("delay_minutes", 15)
    
    # Calculate new scheduled time
    if task.scheduled_time:
        task.scheduled_time = task.scheduled_time + timedelta(minutes=delay_minutes)
    else:
        # If no scheduled time, set it to current time + delay
        task.scheduled_time = datetime.utcnow() + timedelta(minutes=delay_minutes)

    # Update the updated_at timestamp
    task.updated_at = datetime.utcnow()

    await session.commit()
    await session.refresh(task)

    # Create response object
    response = TaskResponseSchema(
        id=task.id,
        user_id=task.user_id,
        title=task.title,
        description=task.description,
        completed=task.completed,
        scheduled_time=task.scheduled_time,
        created_at=task.created_at,
        updated_at=task.updated_at
    )

    return response