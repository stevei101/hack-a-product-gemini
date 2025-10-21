# backend/test_api.py

import pytest
from fastapi.testclient import TestClient
from test_server import app  # Import the FastAPI app from your test server

client = TestClient(app)

def test_read_root():
    """Test the root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {
        "message": "The Product Mindset - Agentic Application API",
        "version": "1.0.0",
        "status": "running"
    }

def test_health_check():
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {
        "status": "healthy",
        "message": "The Product Mindset is running correctly"
    }

def test_nim_health_check():
    """Test the NVIDIA NIM health check endpoint."""
    response = client.get("/api/v1/nim/health")
    assert response.status_code == 200
    assert response.json()["status"] == "nim_available"
