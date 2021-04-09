from typing import Any, Union
from fastapi import WebSocket
from logger import Logger


class PairedList:

    """ Dictionary like data structure without hashing and support for repeating pairs
    """

    def __init__(self, *elements: tuple) -> None:

        """ Initialise PairedList
        Args:
            elements (tuple): tuples of (key, value) pairs
        """

        self.pairs = list(elements)
        self.keys = [i[0] for i in self.pairs]
        self.values = [i[1] for i in self.pairs]


    def append(self, element: tuple) -> None:

        """ Add key-value pair
        Args:
            element (tuple): tuple containing (key, value)
        """

        if element[0] not in self.keys:
            self.pairs.append(element)
            self.keys = [i[0] for i in self.pairs]
            self.values = [i[1] for i in self.pairs]
        else:
            key_index = self.keys.index(element[0])
            self.values[key_index] = element[1]
            self.pairs = list(zip(self.keys, self.values))


    def remove(self, key: Any) -> None:
        
        """ Delete key-value pair
        Args:
            key (Any): The key corresponding to the pair which is to be deleted
        """

        key_index = self.keys.index(key)
        self.keys.pop(key_index)
        self.values.pop(key_index)
        self.pairs = list(zip(self.keys, self.values))


    def clear(self) -> None:

        """ Remove all key-value pairs
        """

        self.pairs.clear()
        self.keys.clear()
        self.values.clear()


    def get(self, key: Any) -> Union[WebSocket, Any]:

        """ Return the value corresponding to key in
        Args: 
            key (Any): The key corresponding to the pair
        Returns:
            [Any]: Default: WebSocket object
        """

        key_index = self.keys.index(key)
        return self.values[key_index]


    def __str__(self) -> str:
        return str(self.pairs)


    def __repr__(self) -> str:
        return str(self.pairs)


class ConnectionManager:

    """ Handles incoming and outgoing websocket connections and messages
    """

    def __init__(self) -> None:

        """ Initialise Connection Manger
        """

        self.active_connections = PairedList()
        self.logger = Logger("CHATROOM-SERVER-LOG", "chatroom_server.log")
        self.logger.info("Connection Manager Initialised")


    async def connect(self, uid: str, websocket: WebSocket) -> None:

        """ Connect to websocket 
        Args:
            uid (str): Unique Identification (UID) of user
            websocket (WebSocket): WebSocket object
        """

        try:
            await websocket.accept()
            self.active_connections.append((uid, websocket))
            self.logger.info(f"Connected : {uid}")
        except:
            self.logger.error("Connection Failed")


    def disconnect(self, uid: str) -> None:
        
        """ Disconnect from user
        Args:
            uid (str): Unique Identification (UID) of user
        """

        try:
            self.active_connections.remove(uid)
            self.logger.info(f"Disconnected : {uid}")
        except:
            pass


    async def send_message(self, message: str, websocket: WebSocket) -> None:

        """ Send message to websocket
        Args:
            message (str): Message to be sent
            websocket (WebSocket): WebSocket object
        """

        await websocket.send_text(message)


    async def broadcast_message(self, sender_websocket: WebSocket, message: str) -> None:
        
        """ Broadcast message to all users
        Args:
            sender_websocket (WebSocket): WebSocket object of sender
            message (str): Message to be sent
        """

        for connection in self.active_connections.values:
            if sender_websocket == connection:
                continue
            else:
                await connection.send_text(message)