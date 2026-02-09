from dapr.ext.grpc import App
from dapr.clients import DaprClient
import json

app = App()

@app.subscribe(pubsub_name='kafka-pubsub', topic='task-events')
def task_event_handler(event_data):
    """
    Handle task events and process recurring tasks.
    """
    try:
        with DaprClient() as client:
            task_event = json.loads(event_data.data.decode('utf-8'))

            if task_event['event_type'] == 'completed' and task_event['task_data'].get('recurrence_type', 'none') != 'none':
                # Create next recurring instance
                from backend.src.services.recurrence import create_next_recurring_instance
                next_task = create_next_recurring_instance(task_event['task_data'])

                # Publish event for new task creation
                client.publish_event(
                    pubsub_name='kafka-pubsub',
                    topic='task-events',
                    data=json.dumps({
                        'event_type': 'created',
                        'task_id': next_task.get('id'),
                        'task_data': next_task,
                        'user_id': task_event['user_id'],
                        'timestamp': next_task.get('created_at')
                    })
                )
    except Exception as e:
        print(f"Error processing task event: {str(e)}")

if __name__ == '__main__':
    print("Recurring Task Service starting...")
    app.run(50002)  # Different port from main API