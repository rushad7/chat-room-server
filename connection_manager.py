from fastapi import WebSocket
from logger import Logger


class PairedList:

    def __init__(self, *elements: tuple) -> None:
        self.pairs = list(elements)
        self.keys = [i[0] for i in self.pairs]
        self.values = [i[1] for i in self.pairs]


    def append(self, element: tuple) -> None:

        if element[0] not in self.keys:
            self.pairs.append(element)
            self.keys = [i[0] for i in self.pairs]
            self.values = [i[1] for i in self.pairs]
        else:
            key_index = self.keys.index(element[0])
            self.values[key_index] = element[1]
            self.pairs = list(zip(self.keys, self.values))


    def remove(self, key):
        key_index = self.keys.index(key)
        self.keys.pop(key_index)
        self.values.pop(key_index)
        self.pairs = list(zip(self.keys, self.values))


    def clear(self):
        self.pairs.clear()
        self.keys.clear()
        self.values.clear()


    def get(self, key):
        key_index = self.keys.index(key)
        return self.values[key_index]


    def __str__(self) -> str:
        return str(self.pairs)


    def __repr__(self) -> str:
        return str(self.pairs)


class ConnectionManager:

    def __init__(self) -> None:
        self.active_connections = PairedList()
        self.logger = Logger("CHATROOM-SERVER-LOG", "chatroom_server.log")
        self.logger.info("Connection Manager Initialised")


    async def connect(self, uid: str, websocket: WebSocket) -> None:
        try:
            await websocket.accept()
            self.active_connections.append((uid, websocket))
            self.logger.info(f"Connected : {uid}")
        except:
            self.logger.error("Connection Failed")


    def disconnect(self, uid: str) -> None:
        try:
            self.active_connections.remove(uid)
            self.logger.info(f"Disconnected : {uid}")
        except:
            pass


    async def send_message(self, message: str, websocket: WebSocket) -> None:
        await websocket.send_text(message)


    async def broadcast_message(self, sender_websocket: WebSocket, message: str) -> None:
        for connection in self.active_connections.values:
            if sender_websocket == connection:
                continue
            else:
                await connection.send_text(message)