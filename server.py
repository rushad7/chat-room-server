import os
import hashlib
from fastapi import FastAPI, status, WebSocket, WebSocketDisconnect

from db_utils import DataBase, Query
from data_models import UserCredentials
from connection_manager import ConnectionManager
from drive import ChatDrive

app = FastAPI()
manager = ConnectionManager()
chatdrive = ChatDrive()

DATABASE_URL = os.environ.get('DATABASE_URL')
db = DataBase(DATABASE_URL)
chatdrive.create_room("global")
chatdrive.add_chat("global", "testuid", "IT WORKS!")

create_user_table_query = Query.create_table("users", **{"uid": "TEXT NOT NULL", "username": "TEXT NOT NULL", \
    "password": "TEXT NOT NULL"})

create_message_table_query = Query.create_table("messages", **{"uid": "TEXT NOT NULL", \
    "date_time": "TEXT NOT NULL", "message": "TEXT NOT NULL"})

db.execute_query(create_user_table_query)
db.execute_query(create_message_table_query)


def is_valid_uid(uid: str) -> bool:
    query = f"SELECT uid FROM users WHERE uid='{uid}';"
    query_response = db.read_execute_query(query)
    if not query_response:
        return False
    return True


@app.post("/signup", status_code=status.HTTP_201_CREATED)
async def add_user(credentials: UserCredentials) -> bool:
    try:
        query = f"SELECT uid FROM users WHERE username='{credentials.username}'";
        query_response = db.read_execute_query(query)
        
        if query_response == []:
            uid_uname = hashlib.sha512(credentials.username.encode("UTF-8")).hexdigest().upper()
            uid_pswd = credentials.password.upper()
            uid = uid_uname + uid_pswd

            query = Query.add_user(uid, credentials.username, credentials.password)
            db.execute_query(query)
            return True
        return False
    except:
        return False
    

@app.post("/login", status_code=status.HTTP_200_OK)
async def login(credentials: UserCredentials) -> bool:
    try:
        query = f"SELECT password FROM users WHERE username='{credentials.username}';"
        query_response = db.read_execute_query(query)
        user_password = query_response[0][0]
        
        if user_password == credentials.password:
            return True
        return False

    except:
        return False


@app.websocket("/chat/{room_name}/{uid}")
async def chat_websocket(websocket: WebSocket, room_name: str, uid: str) -> None:   
    
    #TODO : CHECK IF ROOM EXISTS
    await manager.connect(uid, websocket)
    user_access = is_valid_uid(uid)

    if chatdrive.is_expired:
        chatdrive = ChatDrive()

    if user_access:
        try:
            while True:
                message = await websocket.receive_text()
                print(message)
                
                chatdrive.add_chat(room_name, uid, message)
                await manager.broadcast_message(websocket, message)

        except WebSocketDisconnect:
            manager.disconnect(websocket)


@app.post("/active", status_code=status.HTTP_200_OK)
async def active_users() -> str:
    users_active =  list(manager.active_connections.keys())
    return {"active_users": users_active}
