"""
Basic Unit Tests
================
Run with: pytest tests/ -v
"""

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_root_endpoint():
    """Confirm the server is running and returns the correct status."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "running"


def test_health_check():
    """Confirm the health check endpoint works."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_send_outreach_returns_success():
    """Confirm sending an outreach email returns a valid response."""
    response = client.post(
        "/email/send-outreach",
        json={
            "lead_email": "test@example.com",
            "lead_name": "Test User",
            "lead_company": "Test Co",
        },
    )
    assert response.status_code == 200
    assert response.json()["status"] == "sent"
    assert "subject" in response.json()


def test_webhook_returns_success():
    """Confirm the webhook processes a reply and returns a valid response."""
    response = client.post(
        "/email/webhook",
        data={
            "from": "test2@example.com",
            "subject": "Re: Hi",
            "text": "Hello",
        },
    )
    assert response.status_code == 200
    assert response.json()["status"] == "replied"