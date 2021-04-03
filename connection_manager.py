from typing import Dict, Tuple
from fastapi import WebSocket


class ConnectionManager:

    def __init__(self) -> None:
        self.active_connections: Dict[str, Tuple[WebSocket]] = {}

    async def connect(self, uid: str, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active_connections[uid] = tuple(websocket)

    def disconnect(self, uid: str) -> None:
        self.active_connections.pop(uid)

    async def send_message(self, message: str, websocket: WebSocket) -> None:
        await websocket.send_text(message)

    async def broadcast_message(self, sender_websocket: WebSocket, message: str) -> None:
        for connection in list(self.active_connections.values()):
            connection = connection[0]
            if sender_websocket == connection:
                continue
            else:
                await connection.send_text(message)