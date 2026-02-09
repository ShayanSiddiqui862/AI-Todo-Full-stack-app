from dapr.ext.grpc import App
from dapr.clients import DaprClient
import json

app = App()

@app.subscribe(pubsub_name='kafka-pubsub', topic='task-events')
def task_events_audit_handler(event_data):
    """
    Audit handler for task events.
    """
    try:
        with DaprClient() as client:
            task_event = json.loads(event_data.data.decode('utf-8'))
            
            # Log the task event for audit purposes
            print(f"AUDIT: Task event received - Type: {task_event['event_type']}, "
                  f"Task ID: {task_event['task_id']}, User ID: {task_event['user_id']}")
            
            # In a real implementation, this would store the event in an audit log
            # or send it to a monitoring system
            store_audit_log(task_event)
    except Exception as e:
        print(f"Error processing task event for audit: {str(e)}")


@app.subscribe(pubsub_name='kafka-pubsub', topic='reminders')
def reminder_events_audit_handler(event_data):
    """
    Audit handler for reminder events.
    """
    try:
        with DaprClient() as client:
            reminder_event = json.loads(event_data.data.decode('utf-8'))
            
            # Log the reminder event for audit purposes
            print(f"AUDIT: Reminder event received - Task ID: {reminder_event['task_id']}, "
                  f"User ID: {reminder_event['user_id']}, Title: {reminder_event['task_title']}")
            
            # In a real implementation, this would store the event in an audit log
            store_audit_log(reminder_event)
    except Exception as e:
        print(f"Error processing reminder event for audit: {str(e)}")


def store_audit_log(event_data):
    """
    Store audit log entry.
    This is a stub implementation.
    """
    # Placeholder for actual audit logging logic
    # Could store in database, send to logging service, etc.
    print(f"AUDIT LOG: {event_data}")


if __name__ == '__main__':
    print("Audit Service starting...")
    app.run(50003)  # Different port from main API