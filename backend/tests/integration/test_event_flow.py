import pytest
from unittest.mock import AsyncMock, patch
from datetime import datetime
from backend.src.services.dapr_client import dapr_publish_event
from backend.src.services.event_publisher import publish_task_created_event


class TestEventFlow:
    """Integration tests for Dapr pub/sub functionality."""

    @pytest.mark.asyncio
    async def test_publish_task_created_event(self):
        """Test publishing a task created event."""
        task_id = 123
        user_id = "user123"
        task_data = {
            "title": "Test Task",
            "description": "Test Description",
            "completed": False,
            "priority": "medium",
            "tags": ["test", "integration"],
            "due_date": datetime(2026, 2, 8, 10, 0, 0).isoformat(),
            "remind_at": datetime(2026, 2, 8, 9, 0, 0).isoformat(),
            "recurrence_type": "none",
            "recurrence_interval": 1,
            "created_at": datetime(2026, 2, 1, 10, 0, 0).isoformat(),
            "updated_at": datetime(2026, 2, 1, 10, 0, 0).isoformat()
        }

        # Mock the aiohttp ClientSession and response
        with patch('aiohttp.ClientSession') as mock_session_class:
            mock_session = AsyncMock()
            mock_context_manager = AsyncMock()
            mock_context_manager.__aenter__ = AsyncMock(return_value=mock_session)
            mock_context_manager.__aexit__ = AsyncMock(return_value=None)
            mock_session_class.return_value = mock_context_manager
            
            mock_post = AsyncMock()
            mock_resp = AsyncMock()
            mock_resp.status = 200
            mock_post.return_value.__aenter__ = AsyncMock(return_value=mock_resp)
            mock_post.return_value.__aexit__ = AsyncMock(return_value=None)
            mock_session.post = mock_post

            # Call the function
            await publish_task_created_event(task_id, task_data, user_id)

            # Verify the call was made correctly
            mock_session_class.assert_called_once()
            mock_post.assert_called_once()
            args, kwargs = mock_post.call_args
            
            # Verify URL
            assert args[0] == "http://localhost:3500/v1.0/publish/kafka-pubsub/task-events"
            
            # Verify headers
            assert kwargs['headers']["Content-Type"] == "application/json"
            
            # Verify payload
            import json
            payload = json.loads(kwargs['data'])
            assert payload["event_type"] == "created"
            assert payload["task_id"] == task_id
            assert payload["user_id"] == user_id
            assert payload["task_data"]["title"] == "Test Task"

    @pytest.mark.asyncio
    async def test_publish_task_completed_event(self):
        """Test publishing a task completed event."""
        task_id = 456
        user_id = "user456"
        task_data = {
            "title": "Completed Task",
            "completed": True,
            "priority": "high",
            "tags": ["completed"],
            "created_at": datetime(2026, 2, 1, 10, 0, 0).isoformat(),
            "updated_at": datetime(2026, 2, 1, 10, 0, 0).isoformat()
        }

        # Mock the aiohttp ClientSession and response
        with patch('aiohttp.ClientSession') as mock_session_class:
            mock_session = AsyncMock()
            mock_context_manager = AsyncMock()
            mock_context_manager.__aenter__ = AsyncMock(return_value=mock_session)
            mock_context_manager.__aexit__ = AsyncMock(return_value=None)
            mock_session_class.return_value = mock_context_manager
            
            mock_post = AsyncMock()
            mock_resp = AsyncMock()
            mock_resp.status = 200
            mock_post.return_value.__aenter__ = AsyncMock(return_value=mock_resp)
            mock_post.return_value.__aexit__ = AsyncMock(return_value=None)
            mock_session.post = mock_post

            # Call the function
            await publish_task_completed_event(task_id, task_data, user_id)

            # Verify the call was made correctly
            mock_session_class.assert_called_once()
            mock_post.assert_called_once()
            args, kwargs = mock_post.call_args
            
            # Verify URL
            assert args[0] == "http://localhost:3500/v1.0/publish/kafka-pubsub/task-events"
            
            # Verify payload
            import json
            payload = json.loads(kwargs['data'])
            assert payload["event_type"] == "completed"
            assert payload["task_id"] == task_id
            assert payload["user_id"] == user_id
            assert payload["task_data"]["title"] == "Completed Task"

    @pytest.mark.asyncio
    async def test_direct_publish_event(self):
        """Test the direct event publishing function."""
        pubsub_name = "kafka-pubsub"
        topic = "test-topic"
        data = {
            "event_type": "test_event",
            "test_field": "test_value"
        }

        # Mock the aiohttp ClientSession and response
        with patch('aiohttp.ClientSession') as mock_session_class:
            mock_session = AsyncMock()
            mock_context_manager = AsyncMock()
            mock_context_manager.__aenter__ = AsyncMock(return_value=mock_session)
            mock_context_manager.__aexit__ = AsyncMock(return_value=None)
            mock_session_class.return_value = mock_context_manager
            
            mock_post = AsyncMock()
            mock_resp = AsyncMock()
            mock_resp.status = 200
            mock_post.return_value.__aenter__ = AsyncMock(return_value=mock_resp)
            mock_post.return_value.__aexit__ = AsyncMock(return_value=None)
            mock_session.post = mock_post

            # Call the function
            await dapr_publish_event(pubsub_name, topic, data)

            # Verify the call was made correctly
            mock_session_class.assert_called_once()
            mock_post.assert_called_once()
            args, kwargs = mock_post.call_args
            
            # Verify URL
            assert args[0] == f"http://localhost:3500/v1.0/publish/{pubsub_name}/{topic}"
            
            # Verify payload
            import json
            payload = json.loads(kwargs['data'])
            assert payload == data