from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from typing import Dict, List, Optional

router = APIRouter(tags=["rooms"])


class RoomManager:
    def __init__(self):
        self.rooms: Dict[str, Dict[str, WebSocket]] = {}

    async def connect(self, room_id: str, username: str, websocket: WebSocket):
        await websocket.accept()
        if room_id not in self.rooms:
            self.rooms[room_id] = {}
        self.rooms[room_id][username] = websocket
        await self.broadcast(room_id, {"type": "join", "room_id": room_id, "username": username})

    def disconnect(self, room_id: str, username: str):
        if room_id in self.rooms:
            self.rooms[room_id].pop(username, None)
            if not self.rooms[room_id]:
                del self.rooms[room_id]

    async def broadcast(self, room_id: str, payload: dict):
        if room_id not in self.rooms:
            return
        for ws in list(self.rooms[room_id].values()):
            try:
                await ws.send_json(payload)
            except Exception:
                pass

    def get_users(self, room_id: str) -> List[str]:
        return list(self.rooms.get(room_id, {}).keys())

    def reset(self):
        self.rooms.clear()


room_manager = RoomManager()


@router.websocket("/ws/rooms/{room_id}")
async def websocket_room(
    room_id: str,
    websocket: WebSocket,
    username: Optional[str] = Query(None),
):
    if not username or not username.strip():
        await websocket.close(code=1008)
        return

    username = username.strip()
    await room_manager.connect(room_id, username, websocket)

    try:
        while True:
            try:
                data = await websocket.receive_json()
            except ValueError:
                await websocket.send_json({"type": "error", "detail": "Invalid JSON"})
                continue

            if data.get("type") == "message":
                text = data.get("text", "")
                if len(text) > 300:
                    await websocket.send_json({"type": "error", "detail": "Message is too long"})
                else:
                    await room_manager.broadcast(
                        room_id,
                        {"type": "message", "room_id": room_id, "username": username, "text": text},
                    )
    except WebSocketDisconnect:
        room_manager.disconnect(room_id, username)


@router.get("/rooms/{room_id}/users")
def get_room_users(room_id: str):
    return {"room_id": room_id, "users": room_manager.get_users(room_id)}
