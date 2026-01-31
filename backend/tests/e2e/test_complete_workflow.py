"""E2E test for complete workflow."""


def test_complete_workflow(client):
    """Manager creates project, worker completes task."""
    test_client, _manager, _worker = client

    # Create project
    response = test_client.post("/api/projects/", json={
        "name": "Project Alpha",
        "description": "Test",
    }, headers={"X-User": "manager"})
    assert response.status_code == 200
    project_id = response.json()["id"]

    # Create role
    response = test_client.post(f"/api/projects/{project_id}/roles", json={
        "name": "Engineer",
        "description": "Dev",
    }, headers={"X-User": "manager"})
    assert response.status_code == 200
    role_id = response.json()["id"]

    # Invite worker
    response = test_client.post(f"/api/invites/project/{project_id}", json={
        "email": "worker@example.com",
        "role_id": role_id,
    }, headers={"X-User": "manager"})
    assert response.status_code == 200
    token = response.json()["token"]

    # Accept invite as worker
    response = test_client.post("/api/invites/accept", json={
        "token": token,
        "level": "mid",
        "base_capacity": 10,
    }, headers={"X-User": "worker"})
    assert response.status_code == 200, response.text

    # Create task
    response = test_client.post("/api/tasks/", json={
        "project_id": project_id,
        "title": "Build API",
        "description": "Task",
        "role_id": role_id,
    }, headers={"X-User": "manager"})
    assert response.status_code == 200
    task_id = response.json()["id"]

    # Set difficulty
    response = test_client.post("/api/tasks/difficulty/manual", json={
        "task_id": task_id,
        "difficulty": 3,
    }, headers={"X-User": "manager"})
    assert response.status_code == 200

    # Select task as worker
    response = test_client.post(f"/api/tasks/{task_id}/select", headers={"X-User": "worker"})
    assert response.status_code == 200

    # Complete task
    response = test_client.post(f"/api/tasks/{task_id}/complete", headers={"X-User": "worker"})
    assert response.status_code == 200
    assert response.json()["status"] == "done"
