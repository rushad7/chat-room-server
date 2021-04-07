import os
import hashlib
from fastapi import FastAPI, status, WebSocket, WebSocketDisconnect

from db_utils import DataBase, Query 
from data_models import UserCredentials, Room
from connection_manager import ConnectionManager
from room_manager import RoomManager
from drive import ChatDrive
from logger import Logger


DATABASE_URL = os.environ.get('DATABASE_URL')

app = FastAPI()
chatdrive = ChatDrive()
db = DataBase(DATABASE_URL)
ws_manager = ConnectionManager()
room_manager = RoomManager()
logger = Logger("CHATROOM-SERVER-LOG", "chatroom_server.log")


create_user_table_query = Query.create_table("users", **{"uid": "TEXT NOT NULL", "username": "TEXT NOT NULL", \
    "password": "TEXT NOT NULL"})
db.execute_query(create_user_table_query)
logger.info("Users table created")

create_room_table_query = Query.create_table("rooms", **{"roomname": "TEXT NOT NULL", \
    "admins": "TEXT NOT NULL", "datetime": "TEXT NOT NULL", "members": "TEXT NOT NULL"})
db.execute_query(create_room_table_query)
logger.info("Rooms table created")

room_manager.create_room("global", "admin")

@app.post("/signup", status_code=status.HTTP_201_CREATED)
async def add_user(credentials: UserCredentials) -> bool:
    try:
        query = Query.get_uid(credentials.username)
        query_response = db.read_execute_query(query)
        
        if query_response == []:
            uid_uname = hashlib.sha512(credentials.username.encode("UTF-8")).hexdigest().upper()
            uid_pswd = credentials.password.upper()
            uid = uid_uname + uid_pswd

            query = Query.user_signup(uid, credentials.username, credentials.password)
            db.execute_query(query)
            logger.info(f"User signup: '{credentials.username}' registered successfully")
            return True
        else:
            logger.error(f"User signup: '{credentials.username}' failed to register")
            return False
    except:
        logger.error(f"User signup: '{credentials.username}' failed to register")
        return False
    

@app.post("/login", status_code=status.HTTP_200_OK)
async def login(credentials: UserCredentials) -> bool:
    try:
        query = Query.get_password(credentials.username)
        query_response = db.read_execute_query(query)
        user_password = query_response[0][0]
        
        if user_password == credentials.password:
            logger.info(f"User login: '{credentials.username}' logged in successfully")
            return True
        else:
            logger.error(f"User login: '{credentials.username}' failed to login")
            return False

    except:
        logger.error(f"User login: '{credentials.username}' failed to login")
        return False


@app.websocket("/chat/{roomname}/{uid}")
async def chat_websocket(websocket: WebSocket, roomname: str, uid: str) -> None:   
    
    await ws_manager.connect(uid, websocket)
    user_access = room_manager.has_access(roomname, uid)

    if user_access:
        try:
            while True:
                message = await websocket.receive_text()
                username, chat = message.split(":")[0], message.split(":")[1]
                
                await ws_manager.broadcast_message(websocket, message)
                await chatdrive.add_chat(roomname, username, chat)

                logger.info(f"Message: User with UID = '{uid}' to Room '{roomname}'")

        except WebSocketDisconnect:
            ws_manager.disconnect(uid)
            logger.warning(f"User with UID = {uid} disconnected from Room '{roomname}'")


@app.post("/active", status_code=status.HTTP_200_OK)
async def active_users() -> str:
    users_active = ws_manager.active_connections.keys
    logger.debug("Active users lookup")
    return {"active_users": users_active}


@app.post("/create-room", status_code=status.HTTP_200_OK)
async def create_room(room: Room) -> bool:
    room_status = room_manager.create_room(room.name, room.creator)
    return room_status