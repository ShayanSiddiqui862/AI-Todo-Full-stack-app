from typing import Dict, Any, List
from models import Task
from sqlmodel import select
from db import get_session
from datetime import datetime
import asyncio
from src.mcp.server import mcp_tool


@mcp_tool(name="add_task", description="Create a new task for the user")
async def add_task(user_id: str, title: str, description: str = "", due_date: str = None, priority: str = "medium") -> Dict[str, Any]:
    """
    Creates a new task for the specified user.
    
    Args:
        user_id: The ID of the user creating the task
        title: The title of the task
        description: Optional description of the task
        due_date: Optional due date for the task (ISO format string)
        priority: Priority level ('low', 'medium', 'high'), default is 'medium'
    
    Returns:
        Dictionary with success status and task information
    """
    # Validate inputs
    if not title or len(title.strip()) == 0:
        return {
            "success": False,
            "error_code": "VALIDATION_ERROR",
            "message": "Task title is required and cannot be empty."
        }
    
    if len(title) > 200:
        return {
            "success": False,
            "error_code": "VALIDATION_ERROR",
            "message": f"Task title is too long. Maximum length is 200 characters, got {len(title)}."
        }
    
    if description and len(description) > 1000:  # Assuming a reasonable limit for description
        return {
            "success": False,
            "error_code": "VALIDATION_ERROR",
            "message": f"Task description is too long. Maximum length is 1000 characters, got {len(description)}."
        }
    
    async with get_session() as session:
        # Convert due_date string to datetime if provided
        scheduled_time = None
        if due_date:
            try:
                scheduled_time = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
            except ValueError:
                return {
                    "success": False,
                    "error_code": "VALIDATION_ERROR",
                    "message": f"Invalid date format: {due_date}. Expected ISO format."
                }
        
        # Create new task
        task = Task(
            user_id=user_id,
            title=title.strip(),
            description=description,
            completed=False,
            scheduled_time=scheduled_time
        )
        
        session.add(task)
        await session.commit()
        await session.refresh(task)
        
        return {
            "success": True,
            "task_id": task.id,
            "message": f"Task '{task.title}' created successfully"
        }


@mcp_tool(name="list_tasks", description="Retrieve tasks for the user with optional filtering")
async def list_tasks(
    user_id: str, 
    status: str = "all", 
    limit: int = 50, 
    offset: int = 0, 
    sort_by: str = "created_at", 
    order: str = "desc"
) -> Dict[str, Any]:
    """
    Retrieves tasks for the specified user with optional filtering.
    
    Args:
        user_id: The ID of the user whose tasks to retrieve
        status: Filter by status ('all', 'pending', 'completed', 'deleted'), default is 'all'
        limit: Maximum number of tasks to return (max 100), default is 50
        offset: Number of tasks to skip for pagination, default is 0
        sort_by: Sort by field ('created_at', 'updated_at', 'due_date', 'priority'), default is 'created_at'
        order: Sort order ('asc', 'desc'), default is 'desc'
    
    Returns:
        Dictionary with success status and list of tasks
    """
    # Validate parameters
    if limit > 100:
        limit = 100
    
    valid_statuses = ['all', 'pending', 'completed', 'deleted']
    if status not in valid_statuses:
        status = 'all'
    
    valid_sort_fields = ['created_at', 'updated_at', 'due_date', 'priority']
    if sort_by not in valid_sort_fields:
        sort_by = 'created_at'
    
    valid_orders = ['asc', 'desc']
    if order not in valid_orders:
        order = 'desc'
    
    async with get_session() as session:
        # Build query based on status filter
        query = select(Task).where(Task.user_id == user_id)
        
        if status == 'pending':
            query = query.where(Task.completed == False)
        elif status == 'completed':
            query = query.where(Task.completed == True)
        elif status == 'deleted':
            # Assuming deleted tasks have a deleted flag or similar
            # Since our schema doesn't have a deleted flag, we'll just return empty for 'deleted'
            query = query.where(Task.id == -1)  # This will return no results
        
        # Apply sorting
        if sort_by == 'created_at':
            if order == 'asc':
                query = query.order_by(Task.created_at.asc())
            else:
                query = query.order_by(Task.created_at.desc())
        elif sort_by == 'updated_at':
            if order == 'asc':
                query = query.order_by(Task.updated_at.asc())
            else:
                query = query.order_by(Task.updated_at.desc())
        elif sort_by == 'due_date':
            if order == 'asc':
                query = query.order_by(Task.scheduled_time.asc())
            else:
                query = query.order_by(Task.scheduled_time.desc())
        elif sort_by == 'priority':
            # Our Task model doesn't have a priority field, so we'll use a default sort
            if order == 'asc':
                query = query.order_by(Task.title.asc())
            else:
                query = query.order_by(Task.title.desc())
        
        # Apply limit and offset
        query = query.offset(offset).limit(limit)
        
        result = await session.execute(query)
        tasks = result.scalars().all()
        
        # Convert tasks to dictionaries
        task_list = []
        for task in tasks:
            task_dict = {
                "task_id": task.id,
                "title": task.title,
                "description": task.description,
                "status": "completed" if task.completed else "pending",
                "due_date": task.scheduled_time.isoformat() if task.scheduled_time else None,
                "priority": "medium",  # Default since our model doesn't have a priority field
                "created_at": task.created_at.isoformat(),
                "updated_at": task.updated_at.isoformat()
            }
            task_list.append(task_dict)
        
        return {
            "success": True,
            "tasks": task_list,
            "total_count": len(task_list),
            "message": f"Retrieved {len(task_list)} tasks for user {user_id}"
        }


@mcp_tool(name="update_task", description="Update properties of an existing task")
async def update_task(
    user_id: str, 
    task_id: int, 
    title: str = None, 
    description: str = None, 
    due_date: str = None, 
    priority: str = None
) -> Dict[str, Any]:
    """
    Updates properties of an existing task for the specified user.
    
    Args:
        user_id: The ID of the user who owns the task
        task_id: The ID of the task to update
        title: New title for the task (optional)
        description: New description for the task (optional)
        due_date: New due date for the task (optional, ISO format string)
        priority: New priority level (optional)
    
    Returns:
        Dictionary with success status and task information
    """
    # Validate inputs if provided
    if title is not None:
        if len(title.strip()) == 0:
            return {
                "success": False,
                "error_code": "VALIDATION_ERROR",
                "message": "Task title cannot be empty."
            }
        if len(title) > 200:
            return {
                "success": False,
                "error_code": "VALIDATION_ERROR",
                "message": f"Task title is too long. Maximum length is 200 characters, got {len(title)}."
            }
    
    if description is not None and len(description) > 1000:
        return {
            "success": False,
            "error_code": "VALIDATION_ERROR",
            "message": f"Task description is too long. Maximum length is 1000 characters, got {len(description)}."
        }
    
    async with get_session() as session:
        # Get the task that belongs to the user
        query = select(Task).where(Task.id == task_id, Task.user_id == user_id)
        result = await session.execute(query)
        task = result.scalar_one_or_none()
        
        if not task:
            return {
                "success": False,
                "error_code": "TASK_NOT_FOUND",
                "message": f"No task found with ID {task_id} for user {user_id}"
            }
        
        # Apply updates if provided
        if title is not None:
            task.title = title.strip()
        if description is not None:
            task.description = description
        if due_date is not None:
            try:
                task.scheduled_time = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
            except ValueError:
                return {
                    "success": False,
                    "error_code": "VALIDATION_ERROR",
                    "message": f"Invalid date format: {due_date}. Expected ISO format."
                }
        # Note: Our Task model doesn't have a priority field, so we ignore priority updates
        
        task.updated_at = datetime.utcnow()
        
        await session.commit()
        await session.refresh(task)
        
        return {
            "success": True,
            "task_id": task.id,
            "message": f"Task {task.id} updated successfully"
        }


@mcp_tool(name="complete_task", description="Mark an existing task as completed")
async def complete_task(user_id: str, task_id: int) -> Dict[str, Any]:
    """
    Marks an existing task as completed for the specified user.
    
    Args:
        user_id: The ID of the user who owns the task
        task_id: The ID of the task to mark as completed
    
    Returns:
        Dictionary with success status and task information
    """
    async with get_session() as session:
        # Get the task that belongs to the user
        query = select(Task).where(Task.id == task_id, Task.user_id == user_id)
        result = await session.execute(query)
        task = result.scalar_one_or_none()
        
        if not task:
            return {
                "success": False,
                "error_code": "TASK_NOT_FOUND",
                "message": f"No task found with ID {task_id} for user {user_id}"
            }
        
        if task.completed:
            return {
                "success": False,
                "error_code": "VALIDATION_ERROR",
                "message": f"Task {task_id} is already completed"
            }
        
        task.completed = True
        task.updated_at = datetime.utcnow()
        
        await session.commit()
        await session.refresh(task)
        
        return {
            "success": True,
            "task_id": task.id,
            "message": f"Task {task.id} marked as completed"
        }


@mcp_tool(name="delete_task", description="Remove a task from the user's task list")
async def delete_task(user_id: str, task_id: int) -> Dict[str, Any]:
    """
    Removes a task from the user's task list (soft delete with status update).
    
    Args:
        user_id: The ID of the user who owns the task
        task_id: The ID of the task to delete
    
    Returns:
        Dictionary with success status and task information
    """
    async with get_session() as session:
        # Get the task that belongs to the user
        query = select(Task).where(Task.id == task_id, Task.user_id == user_id)
        result = await session.execute(query)
        task = result.scalar_one_or_none()
        
        if not task:
            return {
                "success": False,
                "error_code": "TASK_NOT_FOUND",
                "message": f"No task found with ID {task_id} for user {user_id}"
            }
        
        # In our model, we don't have a soft-delete mechanism, so we'll actually delete the record
        await session.delete(task)
        await session.commit()
        
        return {
            "success": True,
            "task_id": task_id,
            "message": f"Task {task_id} deleted successfully"
        }