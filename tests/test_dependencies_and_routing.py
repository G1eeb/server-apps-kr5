import pytest

USER_HEADERS = {"X-User-Id": "10", "X-User-Role": "user"}
ADMIN_HEADERS = {"X-User-Id": "99", "X-User-Role": "admin"}
OTHER_USER_HEADERS = {"X-User-Id": "20", "X-User-Role": "user"}
TASK_PAYLOAD = {"title": "Some task", "status": "todo", "priority": 2}


def create_task(client, headers=None):
    return client.post("/tasks", json=TASK_PAYLOAD, headers=headers or USER_HEADERS)


def test_users_me_returns_current_user(client):
    resp = client.get("/users/me", headers=USER_HEADERS)
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == 10
    assert data["role"] == "user"


def test_no_user_id_header_returns_401(client):
    resp = client.get("/users/me")
    assert resp.status_code == 401


def test_regular_user_cannot_access_admin_stats(client):
    resp = client.get("/admin/stats", headers=USER_HEADERS)
    assert resp.status_code == 403


def test_admin_gets_stats(client):
    create_task(client, headers=USER_HEADERS)
    create_task(client, headers=OTHER_USER_HEADERS)
    resp = client.get("/admin/stats", headers=ADMIN_HEADERS)
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_tasks"] == 2
    assert "todo" in data["by_status"]
    assert data["by_status"]["todo"] == 2


def test_regular_user_cannot_delete_others_task(client):
    create_task(client, headers=OTHER_USER_HEADERS)
    resp = client.delete("/tasks/1", headers=USER_HEADERS)
    assert resp.status_code == 404


def test_admin_can_delete_any_task(client):
    create_task(client, headers=USER_HEADERS)
    resp = client.delete("/admin/tasks/1", headers=ADMIN_HEADERS)
    assert resp.status_code == 204

    resp = client.get("/tasks/1", headers=USER_HEADERS)
    assert resp.status_code == 404


def test_health_endpoint(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert "env" in data
