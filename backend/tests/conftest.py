import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from contextlib import contextmanager


@pytest.fixture
def mock_dapr_client():
    """Mock Dapr client for testing."""
    with patch('dapr.clients.DaprClient') as mock_client_class:
        mock_client = MagicMock()
        mock_client_class.return_value.__enter__.return_value = mock_client
        
        # Mock the publish_event method
        mock_client.publish_event = AsyncMock()
        
        yield mock_client


@pytest.fixture
def mock_aiohttp_session():
    """Mock aiohttp session for testing Dapr client functions."""
    with patch('aiohttp.ClientSession') as mock_session_class:
        mock_session = AsyncMock()
        mock_context_manager = AsyncMock()
        mock_context_manager.__aenter__.return_value = mock_session
        mock_context_manager.__aexit__.return_value = AsyncMock(return_value=None)
        mock_session_class.return_value = mock_context_manager
        
        # Mock the post method
        mock_post = AsyncMock()
        mock_resp = AsyncMock()
        mock_resp.status = 200
        mock_resp.text = AsyncMock(return_value="")
        mock_post.return_value.__aenter__.return_value = mock_resp
        mock_post.return_value.__aexit__.return_value = AsyncMock(return_value=None)
        mock_session.post = mock_post
        
        yield {
            'session': mock_session,
            'post': mock_post,
            'response': mock_resp,
            'session_class': mock_session_class
        }


@pytest.fixture
def mock_dapr_grpc_app():
    """Mock Dapr gRPC app for testing subscriber services."""
    with patch('dapr.ext.grpc.App') as mock_app_class:
        mock_app = MagicMock()
        mock_app_class.return_value = mock_app
        
        # Mock the subscribe decorator
        mock_subscribe = MagicMock()
        mock_app.subscribe = mock_subscribe
        
        yield {
            'app': mock_app,
            'subscribe': mock_subscribe
        }


@pytest.fixture
def mock_dapr_pubsub_event():
    """Mock Dapr pubsub event for testing subscribers."""
    class MockEventData:
        def __init__(self, data):
            self.data = data.encode('utf-8') if isinstance(data, str) else data
    
    return MockEventData


# Global mock for Dapr components that can be used across tests
@pytest.fixture(autouse=True)
def setup_global_mocks():
    """Set up global mocks for Dapr components."""
    # This runs before each test to ensure clean state
    with patch.dict('os.environ', {'DAPR_HTTP_PORT': '3500'}):
        yield


# Helper function to create a mock event for pubsub testing
def create_mock_pubsub_event(event_data):
    """Helper to create a mock pubsub event."""
    class MockEvent:
        def __init__(self, data):
            self.data = data.encode('utf-8') if isinstance(data, str) else data
    
    return MockEvent(event_data)