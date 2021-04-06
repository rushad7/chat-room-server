import os
import hashlib
from fastapi import FastAPI, status, WebSocket, WebSocketDisconnect

from db_utils import DataBase, Query 
from data_models import UserCredentials, Room
from connection_manager import ConnectionManager
from drive import ChatDrive
from logger import Logger


DATABASE_URL = os.environ.get('DATABASE_URL')

app = FastAPI()
chatdrive = ChatDrive()
db = DataBase(DATABASE_URL)
manager = ConnectionManager()
logger = Logger("CHATROOM-SERVER-LOG", "chatroom_server.log")


create_user_table_query = Query.create_table("users", **{"uid": "TEXT NOT NULL", "username": "TEXT NOT NULL", \
    "password": "TEXT NOT NULL"})
db.execute_query(create_user_table_query)
logger.info("Users table created")

create_room_table_query = Query.create_table("rooms", **{"roomname": "TEXT NOT NULL", \
    "roomkey": "TEXT NOT NULL", "creator": "TEXT NOT NULL", "datetime": "TEXT NOT NULL"})
db.execute_query(create_room_table_query)
logger.info("Rooms table created")


room_exists_query = Query.room_exists("global")
query_result = db.read_execute_query(room_exists_query)
room_exists_in_table = True if ("global",) in query_result else False

if chatdrive.room_exists("global") and room_exists_in_table:
    query = Query.create_room("global", None, "admin")
    db.execute_query(query)
    chatdrive.create_room("global")


def is_valid_uid(uid: str) -> bool:
    query = f"SELECT uid FROM users WHERE uid='{uid}';"
    query_response = db.read_execute_query(query)

    if not query_response:
        logger.error(f"Users lookup: User with UID = '{uid}' does not exist")
        return False
    else:
        logger.debug(f"Users lookup: User with UID = '{uid}' exists")
        return True


@app.post("/signup", status_code=status.HTTP_201_CREATED)
async def add_user(credentials: UserCredentials) -> bool:
    try:
        query = f"SELECT uid FROM users WHERE username='{credentials.username}';"
        query_response = db.read_execute_query(query)
        
        if query_response == []:
            uid_uname = hashlib.sha512(credentials.username.encode("UTF-8")).hexdigest().upper()
            uid_pswd = credentials.password.upper()
            uid = uid_uname + uid_pswd

            query = Query.add_user(uid, credentials.username, credentials.password)
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
        query = f"SELECT password FROM users WHERE username='{credentials.username}';"
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
    
    await manager.connect(uid, websocket)
    user_access = is_valid_uid(uid)

    if user_access:
        try:
            while True:
                message = await websocket.receive_text()
                username, chat = message.split(":")[0], message.split(":")[1]
                
                await manager.broadcast_message(websocket, message)
                await chatdrive.add_chat(roomname, username, chat)

                logger.info(f"Message: User with UID = '{uid}' to Room '{roomname}'")

        except WebSocketDisconnect:
            manager.disconnect(uid)
            logger.warning(f"User with UID = {uid} disconnected from Room '{roomname}'")


@app.post("/active", status_code=status.HTTP_200_OK)
async def active_users() -> str:
    users_active = manager.active_connections.keys
    logger.debug("Active users lookup")
    return {"active_users": users_active}


@app.post("/create-room", status_code=status.HTTP_200_OK)
async def create_room(room: Room) -> bool:
    try:
        if not chatdrive.room_exists(room.name):
            chatdrive.create_room(room.name, room.key, room.creator)
            query = Query.create_room(room.name, room.key, room.creator)
            db.execute_query(query)
            logger.info(f"Room '{room.name}' created")
            return True
    except:
        logger.error(f"Failed to create Room '{room.name}'")
        return False