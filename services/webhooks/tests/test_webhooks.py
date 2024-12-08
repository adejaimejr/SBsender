import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_create_webhook():
    response = client.post("/webhooks/", json={"url": "http://example.com", "description": "Test webhook"})
    assert response.status_code == 200
    assert "id" in response.json()
