"""Event publishing service for the Todo Chatbot application."""
from typing import Dict, Any
from backend.src.services.dapr_client import dapr_publish_event


async def publish_task_created_event(task_id: int, task_data: Dict[str, Any], user_id: str):
    """Publish an event when a task is created."""
    await dapr_publish_event(
        pubsub_name="kafka-pubsub",
        topic="task-events",
        data={
            "event_type": "created",
            "task_id": task_id,
            "task_data": task_data,
            "user_id": user_id,
            "timestamp": task_data.get("created_at")
        }
    )


async def publish_task_updated_event(task_id: int, task_data: Dict[str, Any], user_id: str):
    """Publish an event when a task is updated."""
    await dapr_publish_event(
        pubsub_name="kafka-pubsub",
        topic="task-events",
        data={
            "event_type": "updated",
            "task_id": task_id,
            "task_data": task_data,
            "user_id": user_id,
            "timestamp": task_data.get("updated_at")
        }
    )


async def publish_task_completed_event(task_id: int, task_data: Dict[str, Any], user_id: str):
    """Publish an event when a task is completed."""
    await dapr_publish_event(
        pubsub_name="kafka-pubsub",
        topic="task-events",
        data={
            "event_type": "completed",
            "task_id": task_id,
            "task_data": task_data,
            "user_id": user_id,
            "timestamp": task_data.get("updated_at")
        }
    )


async def publish_reminder_event(task_id: int, user_id: str, task_title: str, reminder_time: str):
    """Publish a reminder event."""
    await dapr_publish_event(
        pubsub_name="kafka-pubsub",
        topic="reminders",
        data={
            "event_type": "reminder_triggered",
            "task_id": task_id,
            "user_id": user_id,
            "task_title": task_title,
            "reminder_time": reminder_time,
            "timestamp": reminder_time
        }
    )


async def publish_notification_sent_event(task_id: int, user_id: str, task_title: str):
    """Publish an event when a notification is sent."""
    await dapr_publish_event(
        pubsub_name="kafka-pubsub",
        topic="task-updates",
        data={
            "event_type": "notification_sent",
            "task_id": task_id,
            "user_id": user_id,
            "task_title": task_title,
            "timestamp": None  # Will be set by the event system
        }
    )