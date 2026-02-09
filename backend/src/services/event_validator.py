"""Event schema validation for the Todo Chatbot application."""
from typing import Dict, Any, List
from datetime import datetime
import json

def validate_task_event_schema(event_data: Dict[str, Any]) -> tuple[bool, List[str]]:
    """
    Validate the schema of a task event.
    
    Args:
        event_data: Dictionary containing the event data
        
    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []
    
    # Required fields
    required_fields = ['event_type', 'task_id', 'task_data', 'user_id', 'timestamp']
    for field in required_fields:
        if field not in event_data:
            errors.append(f"Missing required field: {field}")
    
    # Validate event_type
    if 'event_type' in event_data:
        valid_types = ['created', 'updated', 'completed', 'deleted']
        if event_data['event_type'] not in valid_types:
            errors.append(f"Invalid event_type: {event_data['event_type']}. Must be one of {valid_types}")
    
    # Validate task_id
    if 'task_id' in event_data and not isinstance(event_data['task_id'], int):
        errors.append("task_id must be an integer")
    
    # Validate user_id
    if 'user_id' in event_data and not isinstance(event_data['user_id'], str):
        errors.append("user_id must be a string")
    
    # Validate timestamp format
    if 'timestamp' in event_data:
        try:
            # Try to parse the timestamp
            datetime.fromisoformat(event_data['timestamp'].replace('Z', '+00:00'))
        except ValueError:
            errors.append(f"Invalid timestamp format: {event_data['timestamp']}")
    
    # Validate task_data if present
    if 'task_data' in event_data:
        task_data = event_data['task_data']
        if not isinstance(task_data, dict):
            errors.append("task_data must be a dictionary")
        else:
            # Validate task fields
            if 'title' in task_data and not isinstance(task_data['title'], str):
                errors.append("task title must be a string")
            if 'priority' in task_data:
                valid_priorities = ['low', 'medium', 'high']
                if task_data['priority'] not in valid_priorities:
                    errors.append(f"Invalid priority: {task_data['priority']}. Must be one of {valid_priorities}")
            if 'tags' in task_data and not isinstance(task_data['tags'], list):
                errors.append("task tags must be a list")
            if 'due_date' in task_data and task_data['due_date']:
                try:
                    datetime.fromisoformat(task_data['due_date'].replace('Z', '+00:00'))
                except ValueError:
                    errors.append(f"Invalid due_date format: {task_data['due_date']}")
            if 'remind_at' in task_data and task_data['remind_at']:
                try:
                    datetime.fromisoformat(task_data['remind_at'].replace('Z', '+00:00'))
                except ValueError:
                    errors.append(f"Invalid remind_at format: {task_data['remind_at']}")
            if 'recurrence_type' in task_data:
                valid_recurrence = ['none', 'daily', 'weekly', 'monthly']
                if task_data['recurrence_type'] not in valid_recurrence:
                    errors.append(f"Invalid recurrence_type: {task_data['recurrence_type']}. Must be one of {valid_recurrence}")
            if 'recurrence_interval' in task_data and not isinstance(task_data['recurrence_interval'], int):
                errors.append("recurrence_interval must be an integer")
    
    return len(errors) == 0, errors


def validate_reminder_event_schema(event_data: Dict[str, Any]) -> tuple[bool, List[str]]:
    """
    Validate the schema of a reminder event.
    
    Args:
        event_data: Dictionary containing the event data
        
    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []
    
    # Required fields
    required_fields = ['event_type', 'task_id', 'user_id', 'task_title', 'reminder_time', 'timestamp']
    for field in required_fields:
        if field not in event_data:
            errors.append(f"Missing required field: {field}")
    
    # Validate event_type
    if 'event_type' in event_data:
        if event_data['event_type'] != 'reminder_triggered':
            errors.append(f"Invalid event_type for reminder: {event_data['event_type']}. Must be 'reminder_triggered'")
    
    # Validate task_id
    if 'task_id' in event_data and not isinstance(event_data['task_id'], int):
        errors.append("task_id must be an integer")
    
    # Validate user_id
    if 'user_id' in event_data and not isinstance(event_data['user_id'], str):
        errors.append("user_id must be a string")
    
    # Validate task_title
    if 'task_title' in event_data and not isinstance(event_data['task_title'], str):
        errors.append("task_title must be a string")
    
    # Validate reminder_time and timestamp format
    for field in ['reminder_time', 'timestamp']:
        if field in event_data:
            try:
                datetime.fromisoformat(event_data[field].replace('Z', '+00:00'))
            except ValueError:
                errors.append(f"Invalid {field} format: {event_data[field]}")
    
    return len(errors) == 0, errors


def validate_task_updates_event_schema(event_data: Dict[str, Any]) -> tuple[bool, List[str]]:
    """
    Validate the schema of a task-updates event.
    
    Args:
        event_data: Dictionary containing the event data
        
    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []
    
    # Required fields
    required_fields = ['event_type', 'operation', 'task_id', 'user_id', 'timestamp']
    for field in required_fields:
        if field not in event_data:
            errors.append(f"Missing required field: {field}")
    
    # Validate event_type
    if 'event_type' in event_data:
        valid_types = ['sync_request', 'sync_response', 'notification_sent']
        if event_data['event_type'] not in valid_types:
            errors.append(f"Invalid event_type: {event_data['event_type']}. Must be one of {valid_types}")
    
    # Validate operation
    if 'operation' in event_data:
        valid_operations = ['create', 'update', 'delete']
        if event_data['operation'] not in valid_operations:
            errors.append(f"Invalid operation: {event_data['operation']}. Must be one of {valid_operations}")
    
    # Validate task_id
    if 'task_id' in event_data and not isinstance(event_data['task_id'], int):
        errors.append("task_id must be an integer")
    
    # Validate user_id
    if 'user_id' in event_data and not isinstance(event_data['user_id'], str):
        errors.append("user_id must be a string")
    
    # Validate timestamp format
    if 'timestamp' in event_data:
        try:
            datetime.fromisoformat(event_data['timestamp'].replace('Z', '+00:00'))
        except ValueError:
            errors.append(f"Invalid timestamp format: {event_data['timestamp']}")
    
    return len(errors) == 0, errors


def validate_event(event_data: Dict[str, Any], topic: str) -> tuple[bool, List[str]]:
    """
    Validate an event based on its topic.
    
    Args:
        event_data: Dictionary containing the event data
        topic: The topic the event was published to
        
    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    if topic == 'task-events':
        return validate_task_event_schema(event_data)
    elif topic == 'reminders':
        return validate_reminder_event_schema(event_data)
    elif topic == 'task-updates':
        return validate_task_updates_event_schema(event_data)
    else:
        return False, [f"Unknown topic: {topic}"]