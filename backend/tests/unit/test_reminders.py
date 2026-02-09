import pytest
from unittest.mock import AsyncMock, patch
from datetime import datetime, timedelta
from backend.src.services.dapr_client import dapr_schedule_job


class TestReminderScheduling:
    """Unit tests for reminder scheduling functionality."""

    @pytest.mark.asyncio
    async def test_schedule_reminder_success(self):
        """Test scheduling a reminder successfully."""
        job_id = "reminder-123-test"
        due_time = "2026-02-08T10:00:00Z"
        data = {
            "task_id": 123,
            "user_id": "user123",
            "task_title": "Test Task"
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
            await dapr_schedule_job(job_id, due_time, data)

            # Verify the call was made correctly
            mock_session_class.assert_called_once()
            mock_post.assert_called_once()
            args, kwargs = mock_post.call_args
            assert args[0] == "http://localhost:3500/v1.0-alpha1/jobs/" + job_id
            assert kwargs['headers']["Content-Type"] == "application/json"

    @pytest.mark.asyncio
    async def test_schedule_reminder_failure(self):
        """Test scheduling a reminder with failure response."""
        job_id = "reminder-456-test"
        due_time = "2026-02-08T11:00:00Z"
        data = {
            "task_id": 456,
            "user_id": "user456",
            "task_title": "Another Test Task"
        }

        # Mock the aiohttp ClientSession and response with failure
        with patch('aiohttp.ClientSession') as mock_session_class:
            mock_session = AsyncMock()
            mock_context_manager = AsyncMock()
            mock_context_manager.__aenter__ = AsyncMock(return_value=mock_session)
            mock_context_manager.__aexit__ = AsyncMock(return_value=None)
            mock_session_class.return_value = mock_context_manager
            
            mock_post = AsyncMock()
            mock_resp = AsyncMock()
            mock_resp.status = 500
            mock_resp.text = AsyncMock(return_value="Internal Server Error")
            mock_post.return_value.__aenter__ = AsyncMock(return_value=mock_resp)
            mock_post.return_value.__aexit__ = AsyncMock(return_value=None)
            mock_session.post = mock_post

            # Call the function
            await dapr_schedule_job(job_id, due_time, data)

            # Verify the call was made and failure was handled
            mock_session_class.assert_called_once()
            mock_post.assert_called_once()
            # The function should handle the error gracefully without raising an exception

    @pytest.mark.asyncio
    async def test_schedule_reminder_payload_format(self):
        """Test that the payload is formatted correctly for scheduling."""
        job_id = "reminder-789-test"
        due_time = "2026-02-08T12:00:00Z"
        data = {
            "task_id": 789,
            "user_id": "user789",
            "task_title": "Yet Another Test Task"
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
            await dapr_schedule_job(job_id, due_time, data)

            # Verify the payload format
            args, kwargs = mock_post.call_args
            payload = kwargs['data']
            import json
            parsed_payload = json.loads(payload)
            
            assert parsed_payload['dueTime'] == due_time
            assert parsed_payload['data'] == data