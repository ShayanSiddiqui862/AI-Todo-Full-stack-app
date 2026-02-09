"""Recurrence logic for calculating next occurrence of recurring tasks."""
from datetime import datetime, timedelta
import calendar
from typing import Optional


def calculate_next_occurrence(current_date: datetime, recurrence_type: str, interval: int) -> datetime:
    """
    Calculate the next occurrence based on recurrence type and interval.
    
    Args:
        current_date: The current occurrence date
        recurrence_type: One of 'daily', 'weekly', 'monthly'
        interval: The interval multiplier (e.g., every 2 weeks)
    
    Returns:
        datetime: The calculated next occurrence date
    """
    if recurrence_type == "daily":
        return current_date + timedelta(days=interval)
    elif recurrence_type == "weekly":
        return current_date + timedelta(weeks=interval)
    elif recurrence_type == "monthly":
        # Handle month-end dates properly
        current_year = current_date.year
        current_month = current_date.month
        current_day = current_date.day

        # Calculate new month and year
        new_month = current_month + interval
        new_year = current_year + (new_month - 1) // 12
        new_month = ((new_month - 1) % 12) + 1

        # Handle day overflow (e.g., Jan 31 + 1 month -> Feb 28/29)
        max_day_in_new_month = calendar.monthrange(new_year, new_month)[1]
        new_day = min(current_day, max_day_in_new_month)

        return current_date.replace(year=new_year, month=new_month, day=new_day)
    else:
        # Default case for 'none' or invalid types
        return current_date


def create_next_recurring_instance(task_data: dict) -> dict:
    """
    Create the next instance of a recurring task.
    
    Args:
        task_data: Dictionary containing the current task data
    
    Returns:
        dict: New task instance with updated fields
    """
    from copy import deepcopy
    from datetime import datetime
    
    next_task = deepcopy(task_data)
    # Reset ID for new record
    if 'id' in next_task:
        del next_task['id']
    
    next_task['completed'] = False
    next_task['created_at'] = datetime.utcnow()
    next_task['updated_at'] = datetime.utcnow()

    # Update due date to next occurrence if it exists
    if task_data.get('due_date'):
        due_date = task_data['due_date']
        if isinstance(due_date, str):
            from datetime import datetime
            due_date = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
        
        next_task['due_date'] = calculate_next_occurrence(
            due_date,
            task_data.get('recurrence_type', 'none'),
            task_data.get('recurrence_interval', 1)
        )

    # Update reminder time if applicable
    if task_data.get('remind_at') and task_data.get('due_date'):
        due_date = task_data['due_date']
        if isinstance(due_date, str):
            from datetime import datetime
            due_date = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
        
        remind_at = task_data['remind_at']
        if isinstance(remind_at, str):
            from datetime import datetime
            remind_at = datetime.fromisoformat(remind_at.replace('Z', '+00:00'))
        
        # Calculate the time difference between due date and reminder
        time_diff = remind_at - due_date
        next_task['remind_at'] = next_task['due_date'] + time_diff

    return next_task