import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_health_check():
    """Test the health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_api_routes_exist():
    """Test that the API routes exist (will fail without authentication)"""
    # These will fail due to missing authentication, but should return 401, not 404
    response = client.get("/api/tasks")
    assert response.status_code == 401  # Unauthorized due to missing JWT

    response = client.post("/api/tasks", json={"title": "test"})
    assert response.status_code == 401  # Unauthorized due to missing JWT

if __name__ == "__main__":
    pytest.main([__file__])