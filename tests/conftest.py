import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.storage import storage
from app.routers.rooms import room_manager


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture(autouse=True)
def reset_state():
    storage.clear()
    room_manager.reset()
    yield
    storage.clear()
    room_manager.reset()
