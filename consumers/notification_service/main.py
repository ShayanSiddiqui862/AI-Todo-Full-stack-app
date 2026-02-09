from dapr.ext.grpc import App
from dapr.clients import DaprClient
import json
import asyncio

app = App()

@app.subscribe(pubsub_name='kafka-pubsub', topic='reminders')
def reminder_handler(event_data):
    """
    Handle reminder events and send notifications to users.
    """
    try:
        with DaprClient() as client:
            reminder_event = json.loads(event_data.data.decode('utf-8'))

            user_id = reminder_event['user_id']
            task_title = reminder_event['task_title']
            task_id = reminder_event['task_id']

            print(f"Processing reminder for user {user_id}: {task_title}")

            # In a real implementation, this would send an actual notification
            # (email, push notification, SMS, etc.)
            asyncio.run(send_notification(user_id, task_title, task_id))

            # Log the notification event
            client.publish_event(
                pubsub_name='kafka-pubsub',
                topic='task-updates',
                data=json.dumps({
                    'event_type': 'notification_sent',
                    'user_id': user_id,
                    'task_id': task_id,
                    'timestamp': reminder_event['timestamp']
                })
            )
    except Exception as e:
        print(f"Error processing reminder: {str(e)}")

async def send_notification(user_id: str, task_title: str, task_id: int):
    """
    Send actual notification to user.
    This is a stub implementation.
    """
    # Placeholder for actual notification logic
    # Could be email, push notification, SMS, etc.
    print(f"STUB: Sending notification to user {user_id} for task '{task_title}'")
    await asyncio.sleep(0.1)  # Simulate async operation

if __name__ == '__main__':
    print("Notification Service starting...")
    app.run(50001)  # Different port from main API