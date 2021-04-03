from typing import Dict, Tuple
from fastapi import WebSocket


class PairedList:

    def __init__(self, *elements: tuple) -> None:
        self.pairs = list(elements)
        self.keys = [i[0] for i in self.pairs]
        self.values = [i[1] for i in self.pairs]

    def append(self, element: tuple) -> None:
        self.keys = [i[0] for i in self.pairs]
        if element[0] not in self.keys:
            self.pairs.append(element)
        else:
            raise ValueError(f"Pair with value {element[0]} exists")

    def remove(self, key):
        self.keys = [i[0] for i in self.pairs]
        self.values = [i[1] for i in self.pairs]

        key_index = self.keys.index(key)
        self.keys.pop(key_index)
        self.values.pop(key_index)
        self.pairs = list(zip(self.keys, self.values))

    def clear(self):
        self.pairs.clear()
        self.keys.clear()
        self.pairs.clear()

    def __str__(self) -> str:
        return str(self.pairs)

    def __repr__(self) -> str:
        return str(self.pairs)


class ConnectionManager:

    def __init__(self) -> None:
        self.active_connections = PairedList()

    async def connect(self, uid: str, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active_connections.append((uid, websocket))

    def disconnect(self, uid: str) -> None:
        self.active_connections.remove(uid)

    async def send_message(self, message: str, websocket: WebSocket) -> None:
        await websocket.send_text(message)

    async def broadcast_message(self, sender_websocket: WebSocket, message: str) -> None:
        for connection in self.active_connections.values():
            if sender_websocket == connection:
                continue
            else:
                await connection.send_text(message)