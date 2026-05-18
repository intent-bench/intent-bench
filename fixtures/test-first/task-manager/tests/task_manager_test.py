"""Test suite for the task manager API.

The implementation must provide a Flask or FastAPI application
accessible via a test client. The app factory should be importable
as `from app import create_app` or `from main import create_app`.
"""

import pytest


@pytest.fixture
def client():
    """Create a test client for the task manager app."""
    try:
        from app import create_app
    except ImportError:
        from main import create_app
    app = create_app(testing=True)
    if hasattr(app, "test_client"):
        # Flask
        with app.test_client() as c:
            yield c
    else:
        # FastAPI
        from fastapi.testclient import TestClient

        yield TestClient(app)


class TestTaskCRUD:
    def test_create_task(self, client):
        resp = client.post("/tasks", json={"title": "Buy groceries", "description": "Milk, eggs, bread"})
        assert resp.status_code in (200, 201)
        data = resp.get_json() if hasattr(resp, "get_json") else resp.json()
        assert data["title"] == "Buy groceries"
        assert "id" in data

    def test_get_task(self, client):
        resp = client.post("/tasks", json={"title": "Read book"})
        data = resp.get_json() if hasattr(resp, "get_json") else resp.json()
        task_id = data["id"]

        resp2 = client.get(f"/tasks/{task_id}")
        assert resp2.status_code == 200
        data2 = resp2.get_json() if hasattr(resp2, "get_json") else resp2.json()
        assert data2["title"] == "Read book"

    def test_list_tasks(self, client):
        client.post("/tasks", json={"title": "Task 1"})
        client.post("/tasks", json={"title": "Task 2"})
        client.post("/tasks", json={"title": "Task 3"})

        resp = client.get("/tasks")
        assert resp.status_code == 200
        data = resp.get_json() if hasattr(resp, "get_json") else resp.json()
        assert len(data) >= 3

    def test_update_task(self, client):
        resp = client.post("/tasks", json={"title": "Original"})
        data = resp.get_json() if hasattr(resp, "get_json") else resp.json()
        task_id = data["id"]

        resp2 = client.put(f"/tasks/{task_id}", json={"title": "Updated"})
        assert resp2.status_code == 200
        data2 = resp2.get_json() if hasattr(resp2, "get_json") else resp2.json()
        assert data2["title"] == "Updated"

    def test_delete_task(self, client):
        resp = client.post("/tasks", json={"title": "To delete"})
        data = resp.get_json() if hasattr(resp, "get_json") else resp.json()
        task_id = data["id"]

        resp2 = client.delete(f"/tasks/{task_id}")
        assert resp2.status_code in (200, 204)

        resp3 = client.get(f"/tasks/{task_id}")
        assert resp3.status_code == 404

    def test_get_nonexistent_task(self, client):
        resp = client.get("/tasks/99999")
        assert resp.status_code == 404


class TestTaskStatus:
    def test_default_status(self, client):
        resp = client.post("/tasks", json={"title": "New task"})
        data = resp.get_json() if hasattr(resp, "get_json") else resp.json()
        assert data.get("status") in ("pending", "todo", "open")

    def test_update_status(self, client):
        resp = client.post("/tasks", json={"title": "Status test"})
        data = resp.get_json() if hasattr(resp, "get_json") else resp.json()
        task_id = data["id"]

        resp2 = client.put(f"/tasks/{task_id}", json={"status": "completed"})
        assert resp2.status_code == 200
        data2 = resp2.get_json() if hasattr(resp2, "get_json") else resp2.json()
        assert data2["status"] == "completed"

    def test_filter_by_status(self, client):
        client.post("/tasks", json={"title": "Done task", "status": "completed"})
        client.post("/tasks", json={"title": "Open task"})

        resp = client.get("/tasks?status=completed")
        assert resp.status_code == 200
        data = resp.get_json() if hasattr(resp, "get_json") else resp.json()
        for task in data:
            assert task["status"] == "completed"


class TestTaskPriority:
    def test_set_priority(self, client):
        resp = client.post("/tasks", json={"title": "Urgent", "priority": "high"})
        data = resp.get_json() if hasattr(resp, "get_json") else resp.json()
        assert data.get("priority") == "high"

    def test_filter_by_priority(self, client):
        client.post("/tasks", json={"title": "High pri", "priority": "high"})
        client.post("/tasks", json={"title": "Low pri", "priority": "low"})

        resp = client.get("/tasks?priority=high")
        assert resp.status_code == 200
        data = resp.get_json() if hasattr(resp, "get_json") else resp.json()
        for task in data:
            assert task["priority"] == "high"


class TestValidation:
    def test_create_without_title(self, client):
        resp = client.post("/tasks", json={"description": "No title"})
        assert resp.status_code in (400, 422)

    def test_create_empty_body(self, client):
        resp = client.post("/tasks", json={})
        assert resp.status_code in (400, 422)

    def test_invalid_status(self, client):
        resp = client.post("/tasks", json={"title": "Test"})
        data = resp.get_json() if hasattr(resp, "get_json") else resp.json()
        task_id = data["id"]

        resp2 = client.put(f"/tasks/{task_id}", json={"status": "invalid_status"})
        assert resp2.status_code in (400, 422)


class TestHealthCheck:
    def test_health(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200
