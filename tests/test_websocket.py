import pytest


def test_connect_to_room(client):
    with client.websocket_connect("/ws/rooms/python?username=alice") as ws:
        msg = ws.receive_json()
        assert msg["type"] == "join"
        assert msg["username"] == "alice"
        assert msg["room_id"] == "python"


def test_send_and_receive_message(client):
    with client.websocket_connect("/ws/rooms/python?username=alice") as ws:
        ws.receive_json()  # join event
        ws.send_json({"type": "message", "text": "hello"})
        msg = ws.receive_json()
        assert msg["type"] == "message"
        assert msg["text"] == "hello"
        assert msg["username"] == "alice"
        assert msg["room_id"] == "python"


def test_two_clients_same_room_receive_same_message(client):
    with client.websocket_connect("/ws/rooms/python?username=alice") as alice:
        alice.receive_json()  # alice join

        with client.websocket_connect("/ws/rooms/python?username=bob") as bob:
            alice.receive_json()  # bob joined (broadcast to alice)
            bob.receive_json()    # bob joined (broadcast to bob)

            alice.send_json({"type": "message", "text": "broadcast test"})

            alice_msg = alice.receive_json()
            bob_msg = bob.receive_json()

            assert alice_msg == bob_msg
            assert alice_msg["text"] == "broadcast test"


def test_different_rooms_isolation(client):
    with client.websocket_connect("/ws/rooms/python?username=alice") as alice:
        alice.receive_json()  # alice join

        with client.websocket_connect("/ws/rooms/java?username=bob") as bob:
            bob.receive_json()  # bob join

            alice.send_json({"type": "message", "text": "python only"})
            msg = alice.receive_json()
            assert msg["room_id"] == "python"

            python_users = client.get("/rooms/python/users").json()["users"]
            java_users = client.get("/rooms/java/users").json()["users"]
            assert "alice" in python_users and "alice" not in java_users
            assert "bob" in java_users and "bob" not in python_users


def test_message_too_long_returns_error(client):
    with client.websocket_connect("/ws/rooms/python?username=alice") as ws:
        ws.receive_json()  # join
        ws.send_json({"type": "message", "text": "x" * 301})
        msg = ws.receive_json()
        assert msg["type"] == "error"
        assert msg["detail"] == "Message is too long"


def test_disconnect_removes_user_from_room(client):
    with client.websocket_connect("/ws/rooms/python?username=alice") as ws:
        ws.receive_json()  # join

    resp = client.get("/rooms/python/users")
    assert "alice" not in resp.json()["users"]
