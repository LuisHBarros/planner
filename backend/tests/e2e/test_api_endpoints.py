"""E2E tests for API endpoints."""
from datetime import datetime, timedelta, timezone


def test_auth_endpoints(client):
    """Register, login, and verify."""
    test_client, _manager, _worker = client

    response = test_client.post("/api/auth/register", json={
        "email": "new@example.com",
        "name": "New User",
    })
    assert response.status_code == 200

    expires_at = (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()
    response = test_client.post("/api/auth/login", json={
        "email": "new@example.com",
        "expires_at": expires_at,
    })
    assert response.status_code == 200
    token = response.json()["token"]

    response = test_client.post("/api/auth/verify", json={"token": token})
    assert response.status_code == 200
    assert response.json()["email"] == "new@example.com"


def test_me_endpoint(client):
    """Get current user profile."""
    test_client, manager, _worker = client

    response = test_client.get("/api/me", headers={"X-User": "manager"})
    assert response.status_code == 200
    assert response.json()["email"] == manager.email
