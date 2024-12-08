import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_send_message():
    response = client.post("/messages/", json={"content": "Hello, World!", "webhook_id": "12345"})
    assert response.status_code == 200
    assert response.json()["status"] == "sent"
