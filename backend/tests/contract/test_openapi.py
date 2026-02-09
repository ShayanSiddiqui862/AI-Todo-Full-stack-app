import pytest
from fastapi.testclient import TestClient
from backend.src.api.tasks import router
from backend.src.main import app  # Assuming the main app is in main.py
from datetime import datetime


# Create a test client for the API
client = TestClient(app)


class TestApiContract:
    """API contract tests for new endpoints."""

    def test_create_task_with_advanced_features(self):
        """Test creating a task with all advanced features."""
        task_data = {
            "title": "Test Recurring Task",
            "description": "A task to test advanced features",
            "user_id": "test_user_123",
            "priority": "high",
            "tags": ["test", "recurring", "important"],
            "due_date": "2026-12-31T10:00:00",
            "remind_at": "2026-12-31T09:00:00",
            "recurrence_type": "daily",
            "recurrence_interval": 1
        }

        response = client.post("/api/tasks/", json=task_data)
        
        # Should return 200 OK
        assert response.status_code == 200
        
        # Parse the response
        result = response.json()
        
        # Verify all fields are present and correct
        assert result["title"] == task_data["title"]
        assert result["description"] == task_data["description"]
        assert result["priority"] == task_data["priority"]
        assert result["tags"] == task_data["tags"]
        assert result["due_date"] is not None  # Should be converted to proper datetime format
        assert result["remind_at"] is not None  # Should be converted to proper datetime format
        assert result["recurrence_type"] == task_data["recurrence_type"]
        assert result["recurrence_interval"] == task_data["recurrence_interval"]

    def test_get_tasks_with_filters(self):
        """Test retrieving tasks with various filters."""
        # First create a few test tasks
        tasks_to_create = [
            {
                "title": "High Priority Task",
                "description": "A high priority task",
                "user_id": "test_user_123",
                "priority": "high",
                "tags": ["urgent", "work"],
                "due_date": "2026-12-31T10:00:00",
                "completed": False
            },
            {
                "title": "Low Priority Task",
                "description": "A low priority task",
                "user_id": "test_user_123",
                "priority": "low",
                "tags": ["later", "personal"],
                "due_date": "2026-12-31T10:00:00",
                "completed": False
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
            "user_id": "test_user_123",
            "priority": "high"
        })
        assert response.status_code == 200
        result = response.json()
        high_priority_tasks = [task for task in result if task["priority"] == "high"]
        assert len(high_priority_tasks) >= 1

        # Test filtering by tag
        response = client.get("/api/tasks/", params={
            "user_id": "test_user_123",
            "tags": ["work"]
        })
        assert response.status_code == 200
        result = response.json()
        work_tagged_tasks = [task for task in result if "work" in task["tags"]]
        assert len(work_tagged_tasks) >= 1

        # Test sorting by priority
        response = client.get("/api/tasks/", params={
            "user_id": "test_user_123",
            "sort_by": "priority",
            "sort_order": "desc"
        })
        assert response.status_code == 200
        result = response.json()
        # Verify that the first task has higher or equal priority than the second
        if len(result) > 1:
            # This test assumes a mapping where high=3, medium=2, low=1
            priority_map = {"high": 3, "medium": 2, "low": 1}
            first_task_priority = priority_map[result[0]["priority"]]
            second_task_priority = priority_map[result[1]["priority"]]
            assert first_task_priority >= second_task_priority

    def test_search_endpoint(self):
        """Test the search endpoint functionality."""
        # Create a test task
        task_data = {
            "title": "Searchable Task Title",
            "description": "This task has searchable content in description",
            "user_id": "test_user_123",
            "priority": "medium",
            "tags": ["search", "test"],
            "completed": False
        }
        
        response = client.post("/api/tasks/", json=task_data)
        assert response.status_code == 200
        created_task = response.json()

        # Test searching by title
        response = client.get("/api/tasks/search", params={
            "query": "Searchable",
            "user_id": "test_user_123"
        })
        assert response.status_code == 200
        result = response.json()
        assert len(result) >= 1
        found_task = next((task for task in result if task["id"] == created_task["id"]), None)
        assert found_task is not None

        # Test searching by tag
        response = client.get("/api/tasks/search", params={
            "query": "search",
            "user_id": "test_user_123"
        })
        assert response.status_code == 200
        result = response.json()
        assert len(result) >= 1

    def test_update_task_with_advanced_features(self):
        """Test updating a task with advanced features."""
        # Create a task first
        task_data = {
            "title": "Original Task",
            "description": "Original description",
            "user_id": "test_user_123",
            "priority": "low",
            "tags": ["original"],
            "due_date": "2026-12-31T10:00:00",
            "completed": False
        }
        
        response = client.post("/api/tasks/", json=task_data)
        assert response.status_code == 200
        created_task = response.json()

        # Update the task with new values
        update_data = {
            "title": "Updated Task Title",
            "description": "Updated description",
            "priority": "high",
            "tags": ["updated", "important"],
            "due_date": "2027-01-01T10:00:00",
            "remind_at": "2027-01-01T09:00:00",
            "recurrence_type": "weekly",
            "recurrence_interval": 2
        }
        
        response = client.put(f"/api/tasks/{created_task['id']}", json=update_data)
        assert response.status_code == 200
        
        updated_task = response.json()
        assert updated_task["title"] == update_data["title"]
        assert updated_task["description"] == update_data["description"]
        assert updated_task["priority"] == update_data["priority"]
        assert updated_task["tags"] == update_data["tags"]
        assert updated_task["recurrence_type"] == update_data["recurrence_type"]
        assert updated_task["recurrence_interval"] == update_data["recurrence_interval"]

    def test_complete_task_endpoint(self):
        """Test completing a task endpoint."""
        # Create a task first
        task_data = {
            "title": "Task to Complete",
            "description": "A task that will be marked as completed",
            "user_id": "test_user_123",
            "priority": "medium",
            "tags": ["test"],
            "completed": False
        }
        
        response = client.post("/api/tasks/", json=task_data)
        assert response.status_code == 200
        created_task = response.json()
        assert created_task["completed"] is False

        # Complete the task
        response = client.patch(f"/api/tasks/{created_task['id']}/complete")
        assert response.status_code == 200
        
        completed_task = response.json()
        assert completed_task["completed"] is True