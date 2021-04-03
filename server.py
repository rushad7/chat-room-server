import os
import hashlib
from fastapi import FastAPI, status, WebSocket, WebSocketDisconnect

from db_utils import DataBase, Query 
from data_models import UserCredentials, Room
from connection_manager import ConnectionManager
from drive import ChatDrive


app = FastAPI()
manager = ConnectionManager()

DATABASE_URL = os.environ.get('DATABASE_URL')
db = DataBase(DATABASE_URL)

create_user_table_query = Query.create_table("users", **{"uid": "TEXT NOT NULL", "username": "TEXT NOT NULL", \
    "password": "TEXT NOT NULL"})

db.execute_query(create_user_table_query, logging_message="Created users table")

chatdrive = ChatDrive()

def is_valid_uid(uid: str) -> bool:
    query = f"SELECT uid FROM users WHERE uid='{uid}';"
    query_response = db.read_execute_query(query, logging_message="User Verfication")
    if not query_response:
        return False
    return True


@app.post("/signup", status_code=status.HTTP_201_CREATED)
async def add_user(credentials: UserCredentials) -> bool:
    try:
        query = f"SELECT uid FROM users WHERE username='{credentials.username}';"
        query_response = db.read_execute_query(query, logging_message="User lookup")
        
        if query_response == []:
            uid_uname = hashlib.sha512(credentials.username.encode("UTF-8")).hexdigest().upper()
            uid_pswd = credentials.password.upper()
            uid = uid_uname + uid_pswd

            query = Query.add_user(uid, credentials.username, credentials.password)
            db.execute_query(query,logging_message="User registered")
            return True
        return False
    except:
        return False
    

@app.post("/login", status_code=status.HTTP_200_OK)
async def login(credentials: UserCredentials) -> bool:
    try:
        query = f"SELECT password FROM users WHERE username='{credentials.username}';"
        query_response = db.read_execute_query(query, logging_message="User lookup")
        user_password = query_response[0][0]
        
        if user_password == credentials.password:
            return True
        return False

    except:
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
                print(message)
                
                await manager.broadcast_message(websocket, message)
                await chatdrive.add_chat(roomname, username, chat)

        except WebSocketDisconnect:
            manager.disconnect(uid)


@app.post("/active", status_code=status.HTTP_200_OK)
async def active_users() -> str:
    users_active = manager.active_connections.keys
    return {"active_users": users_active}


@app.post("/create-room", status_code=status.HTTP_200_OK)
async def create_room(room: Room) -> bool:
    try:
        if not chatdrive.room_exists(room.name):
            chatdrive.create_room(room.name, room.key, room.creator)
            print(f"Roomname: {room.name}")
            return True
    except:
        return False