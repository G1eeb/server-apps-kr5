import pytest
from fastapi.testclient import TestClient

USER_10 = {"X-User-Id": "10"}
USER_20 = {"X-User-Id": "20"}


def make_task(client, headers=None, **kwargs):
    payload = {"title": "Test task", "status": "todo", "priority": 3}
    payload.update(kwargs)
    return client.post("/tasks", json=payload, headers=headers or USER_10)


def test_create_task_success(client):
    resp = make_task(client)
    assert resp.status_code == 201
    data = resp.json()
    assert data["id"] == 1
    assert data["title"] == "Test task"
    assert data["owner_id"] == 10


def test_create_task_short_title_returns_422(client):
    resp = make_task(client, title="ab")
    assert resp.status_code == 422


def test_create_task_no_auth_returns_401(client):
    resp = client.post("/tasks", json={"title": "Test task", "status": "todo", "priority": 3})
    assert resp.status_code == 401


def test_user_sees_only_own_tasks(client):
    make_task(client, headers=USER_10, title="User10 task")
    make_task(client, headers=USER_20, title="User20 task")

    resp = client.get("/tasks", headers=USER_10)
    assert resp.status_code == 200
    tasks = resp.json()
    assert len(tasks) == 1
    assert tasks[0]["owner_id"] == 10


def test_filter_by_status(client):
    make_task(client, title="Task todo", status="todo")
    make_task(client, title="Task done", status="done")

    resp = client.get("/tasks?status=todo", headers=USER_10)
    assert resp.status_code == 200
    tasks = resp.json()
    assert all(t["status"] == "todo" for t in tasks)
    assert len(tasks) == 1


def test_filter_by_min_priority(client):
    make_task(client, title="Low priority", priority=1)
    make_task(client, title="High priority", priority=5)

    resp = client.get("/tasks?min_priority=4", headers=USER_10)
    assert resp.status_code == 200
    tasks = resp.json()
    assert all(t["priority"] >= 4 for t in tasks)
    assert len(tasks) == 1


def test_update_task_status(client):
    make_task(client)
    resp = client.patch("/tasks/1/status", json={"status": "done"}, headers=USER_10)
    assert resp.status_code == 200
    assert resp.json()["status"] == "done"


def test_get_other_user_task_returns_404(client):
    make_task(client, headers=USER_20)
    resp = client.get("/tasks/1", headers=USER_10)
    assert resp.status_code == 404


def test_get_nonexistent_task_returns_404(client):
    resp = client.get("/tasks/999", headers=USER_10)
    assert resp.status_code == 404


def test_delete_task_success(client):
    make_task(client)
    resp = client.delete("/tasks/1", headers=USER_10)
    assert resp.status_code == 204

    resp = client.get("/tasks/1", headers=USER_10)
    assert resp.status_code == 404
