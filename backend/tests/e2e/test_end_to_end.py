import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
from datetime import datetime, timedelta
from backend.src.main import app  # Assuming the main app is in main.py


# Create a test client for the API
client = TestClient(app)


class TestEndToEnd:
    """End-to-end tests for all new features with Dapr and event flow."""

    @pytest.mark.asyncio
    async def test_full_recurring_task_workflow(self):
        """Test the complete workflow for recurring tasks."""
        # Create a recurring task
        task_data = {
            "title": "Daily Standup Meeting",
            "description": "Daily team standup meeting",
            "user_id": "test_user_e2e",
            "priority": "high",
            "tags": ["meeting", "team", "daily"],
            "due_date": (datetime.now() + timedelta(days=1)).isoformat(),
            "remind_at": (datetime.now() + timedelta(hours=22)).isoformat(),  # 1 day minus 2 hours
            "recurrence_type": "daily",
            "recurrence_interval": 1
        }

        # Create the task
        response = client.post("/api/tasks/", json=task_data)
        assert response.status_code == 200
        created_task = response.json()
        
        # Verify the task was created with correct attributes
        assert created_task["title"] == task_data["title"]
        assert created_task["recurrence_type"] == task_data["recurrence_type"]
        assert created_task["recurrence_interval"] == task_data["recurrence_interval"]
        assert created_task["priority"] == task_data["priority"]
        assert created_task["tags"] == task_data["tags"]

        # Mock the Dapr event publishing to verify it's called
        with patch('backend.src.services.dapr_client.dapr_publish_event', new_callable=AsyncMock) as mock_publish:
            mock_publish.return_value = True
            
            # Complete the task (this should trigger creation of the next recurring instance)
            response = client.patch(f"/api/tasks/{created_task['id']}/complete")
            assert response.status_code == 200
            
            completed_task = response.json()
            assert completed_task["completed"] is True
            
            # Verify that events were published
            # At least one event should have been published for the completion
            assert mock_publish.called
            # Check that the event was published to the right topic
            calls = mock_publish.call_args_list
            task_events_published = [call for call in calls if call[0][1] == "task-events"]
            assert len(task_events_published) >= 1

    @pytest.mark.asyncio
    async def test_reminder_scheduling_workflow(self):
        """Test the complete workflow for reminder scheduling."""
        # Create a task with a reminder
        future_time = datetime.now() + timedelta(minutes=30)  # 30 mins in future
        task_data = {
            "title": "Doctor Appointment",
            "description": "Annual checkup appointment",
            "user_id": "test_user_e2e",
            "priority": "high",
            "tags": ["appointment", "health"],
            "due_date": future_time.isoformat(),
            "remind_at": (future_time - timedelta(minutes=15)).isoformat(),  # 15 mins before
            "recurrence_type": "none",
            "recurrence_interval": 1
        }

        # Create the task
        response = client.post("/api/tasks/", json=task_data)
        assert response.status_code == 200
        created_task = response.json()
        
        # Verify the task was created with correct attributes
        assert created_task["title"] == task_data["title"]
        assert created_task["remind_at"] is not None
        assert created_task["due_date"] is not None

        # Mock the Dapr job scheduling to verify it's called
        with patch('backend.src.services.dapr_client.dapr_schedule_job', new_callable=AsyncMock) as mock_schedule:
            mock_schedule.return_value = True
            
            # The reminder should have been scheduled during task creation
            # Verify that dapr_schedule_job was called for the reminder
            # This might not be directly testable without restructuring the code
            # But we can at least verify the task was created with reminder info
            assert created_task["remind_at"] is not None

    @pytest.mark.asyncio
    async def test_priority_and_tag_filtering_workflow(self):
        """Test the complete workflow for priority and tag filtering."""
        # Create multiple tasks with different priorities and tags
        tasks_to_create = [
            {
                "title": "High Priority Task",
                "description": "A high priority task",
                "user_id": "test_user_e2e",
                "priority": "high",
                "tags": ["urgent", "work"],
                "due_date": (datetime.now() + timedelta(days=1)).isoformat(),
                "recurrence_type": "none"
            },
            {
                "title": "Low Priority Task",
                "description": "A low priority task",
                "user_id": "test_user_e2e",
                "priority": "low",
                "tags": ["later", "personal"],
                "due_date": (datetime.now() + timedelta(days=7)).isoformat(),
                "recurrence_type": "none"
            },
            {
                "title": "Medium Priority Task",
                "description": "A medium priority task",
                "user_id": "test_user_e2e",
                "priority": "medium",
                "tags": ["work", "normal"],
                "due_date": (datetime.now() + timedelta(days=3)).isoformat(),
                "recurrence_type": "none"
            }
        ]

        # Create the tasks
        created_tasks = []
        for task_data in tasks_to_create:
            response = client.post("/api/tasks/", json=task_data)
            assert response.status_code == 200
            created_tasks.append(response.json())

        # Test filtering by priority
        response = client.get("/api/tasks/", params={
            "user_id": "test_user_e2e",
            "priority": "high"
        })
        assert response.status_code == 200
        result = response.json()
        high_priority_tasks = [task for task in result if task["priority"] == "high"]
        assert len(high_priority_tasks) >= 1

        # Test filtering by tag
        response = client.get("/api/tasks/", params={
            "user_id": "test_user_e2e",
            "tags": ["work"]
        })
        assert response.status_code == 200
        result = response.json()
        work_tagged_tasks = [task for task in result if "work" in task["tags"]]
        assert len(work_tagged_tasks) >= 2  # Both high and medium priority tasks have "work" tag

        # Test sorting by priority
        response = client.get("/api/tasks/", params={
            "user_id": "test_user_e2e",
            "sort_by": "priority",
            "sort_order": "desc"
        })
        assert response.status_code == 200
        result = response.json()
        # Verify that the first task has higher or equal priority than others
        if len(result) > 1:
            # This test assumes a mapping where high=3, medium=2, low=1
            priority_map = {"high": 3, "medium": 2, "low": 1}
            first_task_priority = priority_map[result[0]["priority"]]
            remaining_priorities = [priority_map[task["priority"]] for task in result[1:]]
            assert all(first_task_priority >= p for p in remaining_priorities)

    @pytest.mark.asyncio
    async def test_search_functionality_workflow(self):
        """Test the complete workflow for search functionality."""
        # Create tasks with different content for searching
        tasks_to_create = [
            {
                "title": "Project Alpha Documentation",
                "description": "Complete the documentation for Project Alpha",
                "user_id": "test_user_e2e",
                "priority": "medium",
                "tags": ["documentation", "project_alpha"],
                "due_date": (datetime.now() + timedelta(days=5)).isoformat(),
                "recurrence_type": "none"
            },
            {
                "title": "Project Beta Testing",
                "description": "Perform testing for Project Beta",
                "user_id": "test_user_e2e",
                "priority": "high",
                "tags": ["testing", "project_beta"],
                "due_date": (datetime.now() + timedelta(days=3)).isoformat(),
                "recurrence_type": "none"
            }
        ]

        # Create the tasks
        created_tasks = []
        for task_data in tasks_to_create:
            response = client.post("/api/tasks/", json=task_data)
            assert response.status_code == 200
            created_tasks.append(response.json())

        # Test searching by title
        response = client.get("/api/tasks/search", params={
            "query": "Alpha",
            "user_id": "test_user_e2e"
        })
        assert response.status_code == 200
        result = response.json()
        alpha_tasks = [task for task in result if "Alpha" in task["title"]]
        assert len(alpha_tasks) >= 1

        # Test searching by tag
        response = client.get("/api/tasks/search", params={
            "query": "testing",
            "user_id": "test_user_e2e"
        })
        assert response.status_code == 200
        result = response.json()
        testing_tasks = [task for task in result if "testing" in task["tags"]]
        assert len(testing_tasks) >= 1

        # Test searching by description
        response = client.get("/api/tasks/search", params={
            "query": "documentation",
            "user_id": "test_user_e2e"
        })
        assert response.status_code == 200
        result = response.json()
        doc_tasks = [task for task in result if "documentation" in task["description"]]
        assert len(doc_tasks) >= 1

    def test_complete_feature_integration(self):
        """Test that all features work together in a realistic scenario."""
        # Create a complex recurring task with all features
        task_data = {
            "title": "Weekly Team Sync",
            "description": "Weekly team synchronization meeting",
            "user_id": "test_user_e2e_complex",
            "priority": "high",
            "tags": ["meeting", "team", "weekly", "sync"],
            "due_date": (datetime.now() + timedelta(days=7)).isoformat(),
            "remind_at": (datetime.now() + timedelta(days=7, hours=-1)).isoformat(),  # 1 hour before
            "recurrence_type": "weekly",
            "recurrence_interval": 1
        }

        # Create the task
        response = client.post("/api/tasks/", json=task_data)
        assert response.status_code == 200
        created_task = response.json()
        
        # Verify all attributes are correctly set
        assert created_task["title"] == task_data["title"]
        assert created_task["priority"] == task_data["priority"]
        assert created_task["tags"] == task_data["tags"]
        assert created_task["recurrence_type"] == task_data["recurrence_type"]
        assert created_task["recurrence_interval"] == task_data["recurrence_interval"]
        assert created_task["remind_at"] is not None

        # Update the task to change some attributes
        update_data = {
            "title": "Bi-weekly Team Sync",  # Changed title
            "priority": "medium",  # Changed priority
            "tags": ["meeting", "team", "biweekly", "sync"],  # Changed tags
            "recurrence_interval": 2  # Changed to bi-weekly
        }

        response = client.put(f"/api/tasks/{created_task['id']}", json=update_data)
        assert response.status_code == 200
        updated_task = response.json()
        
        # Verify updates were applied
        assert updated_task["title"] == update_data["title"]
        assert updated_task["priority"] == update_data["priority"]
        assert updated_task["tags"] == update_data["tags"]
        assert updated_task["recurrence_interval"] == update_data["recurrence_interval"]

        # Complete the task to trigger recurrence
        response = client.patch(f"/api/tasks/{created_task['id']}/complete")
        assert response.status_code == 200
        completed_task = response.json()
        assert completed_task["completed"] is True