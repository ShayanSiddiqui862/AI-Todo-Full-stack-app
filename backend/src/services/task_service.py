"""
Task Service Module
Provides business logic for task-related operations that can be used by the chat functionality.
"""

from typing import List, Optional, Dict, Any
from sqlmodel import select
from models import Task
from db import get_session
from datetime import datetime


class TaskService:
    """
    Service class for handling task-related business logic.
    """
    
    @staticmethod
    async def create_task(user_id: str, title: str, description: str = None, 
                         scheduled_time: datetime = None) -> Optional[Task]:
        """
        Create a new task for a user.
        
        Args:
            user_id: The ID of the user creating the task
            title: The title of the task
            description: Optional description of the task
            scheduled_time: Optional scheduled time for the task
            
        Returns:
            The created Task object or None if creation failed
        """
        async with get_session() as session:
            task = Task(
                user_id=user_id,
                title=title,
                description=description,
                scheduled_time=scheduled_time,
                completed=False
            )
            
            session.add(task)
            await session.commit()
            await session.refresh(task)
            
            return task
    
    @staticmethod
    async def get_user_tasks(user_id: str, status: str = "all") -> List[Task]:
        """
        Get all tasks for a specific user, optionally filtered by status.
        
        Args:
            user_id: The ID of the user whose tasks to retrieve
            status: Filter by status ('all', 'pending', 'completed')
            
        Returns:
            List of Task objects
        """
        async with get_session() as session:
            query = select(Task).where(Task.user_id == user_id)
            
            if status == "pending":
                query = query.where(Task.completed == False)
            elif status == "completed":
                query = query.where(Task.completed == True)
            
            result = await session.execute(query)
            tasks = result.scalars().all()
            
            return tasks
    
    @staticmethod
    async def get_task_by_id(user_id: str, task_id: int) -> Optional[Task]:
        """
        Get a specific task by its ID for a user.
        
        Args:
            user_id: The ID of the user who owns the task
            task_id: The ID of the task to retrieve
            
        Returns:
            Task object if found, None otherwise
        """
        async with get_session() as session:
            query = select(Task).where(Task.id == task_id, Task.user_id == user_id)
            result = await session.execute(query)
            task = result.scalar_one_or_none()
            
            return task
    
    @staticmethod
    async def update_task(task_id: int, user_id: str, title: str = None, 
                         description: str = None, completed: bool = None, 
                         scheduled_time: datetime = None) -> Optional[Task]:
        """
        Update properties of an existing task.
        
        Args:
            task_id: The ID of the task to update
            user_id: The ID of the user who owns the task
            title: New title for the task (optional)
            description: New description for the task (optional)
            completed: New completion status (optional)
            scheduled_time: New scheduled time (optional)
            
        Returns:
            Updated Task object or None if update failed
        """
        async with get_session() as session:
            query = select(Task).where(Task.id == task_id, Task.user_id == user_id)
            result = await session.execute(query)
            task = result.scalar_one_or_none()
            
            if not task:
                return None
            
            # Apply updates if provided
            if title is not None:
                task.title = title
            if description is not None:
                task.description = description
            if completed is not None:
                task.completed = completed
            if scheduled_time is not None:
                task.scheduled_time = scheduled_time
            
            task.updated_at = datetime.utcnow()
            
            await session.commit()
            await session.refresh(task)
            
            return task
    
    @staticmethod
    async def delete_task(task_id: int, user_id: str) -> bool:
        """
        Delete a task for a user.
        
        Args:
            task_id: The ID of the task to delete
            user_id: The ID of the user who owns the task
            
        Returns:
            True if deletion was successful, False otherwise
        """
        async with get_session() as session:
            query = select(Task).where(Task.id == task_id, Task.user_id == user_id)
            result = await session.execute(query)
            task = result.scalar_one_or_none()
            
            if not task:
                return False
            
            await session.delete(task)
            await session.commit()
            
            return True
    
    @staticmethod
    async def complete_task(task_id: int, user_id: str) -> Optional[Task]:
        """
        Mark a task as completed.
        
        Args:
            task_id: The ID of the task to mark as completed
            user_id: The ID of the user who owns the task
            
        Returns:
            Updated Task object or None if operation failed
        """
        return await TaskService.update_task(task_id, user_id, completed=True)
    
    @staticmethod
    async def get_tasks_due_today(user_id: str) -> List[Task]:
        """
        Get all tasks for a user that are scheduled for today.
        
        Args:
            user_id: The ID of the user whose tasks to retrieve
            
        Returns:
            List of Task objects scheduled for today
        """
        from datetime import date
        
        today = date.today()
        async with get_session() as session:
            query = select(Task).where(
                Task.user_id == user_id,
                Task.scheduled_time is not None,
                Task.scheduled_time >= datetime.combine(today, datetime.min.time()),
                Task.scheduled_time <= datetime.combine(today, datetime.max.time())
            )
            
            result = await session.execute(query)
            tasks = result.scalars().all()
            
            return tasks