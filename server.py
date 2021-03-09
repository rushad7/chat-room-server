import os
import hashlib
from fastapi import FastAPI, status, WebSocket, WebSocketDisconnect

from db_utils import DataBase, Query
from data_models import UserCredentials
from connection_manager import ConnectionManager


app = FastAPI()
manager = ConnectionManager()

DATABASE_URL = os.environ['DATABASE_URL']
db = DataBase(DATABASE_URL)

create_user_table_query = Query.create_table("users", **{"uid": "TEXT NOT NULL", "username": "TEXT NOT NULL", \
    "password": "TEXT NOT NULL"})

create_message_table_query = Query.create_table("messages", **{"username": "TEXT NOT NULL", \
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
        uid_uname = hashlib.sha512(credentials.username.encode("UTF-8")).hexdigest().upper()
        uid_pswd = credentials.password.upper()
        uid = uid_uname + uid_pswd

        query = Query.add_user(uid, credentials.username, credentials.password)
        db.execute_query(query)
        return True
    except:
        return False


@app.post("/verify", status_code=status.HTTP_200_OK)
async def verify_user(credentials: UserCredentials) -> bool:
    try:
        query = f"SELECT uid FROM users WHERE username='{credentials.username}' AND password='{credentials.password}';"
        query_response = db.read_execute_query(query)
        user_exists = not bool(query_response)
        return user_exists
    except:
        return False


@app.post("/login", status_code=status.HTTP_200_OK)
async def login(credentials: UserCredentials) -> bool:
    try:
        query = f"SELECT password FROM users WHERE username='{credentials.username}';"
        query_response = db.read_execute_query(query)
        user_password = query_response[0][0]
        print(user_password)
        if user_password == credentials.password:
            return True
        return False

    except:
        return False


@app.websocket("/chat/{uid}")
async def chat_websocket(websocket: WebSocket, uid: str) -> None:   
    
    await manager.connect(uid, websocket)
    user_access = is_valid_uid(uid)

    if user_access:
        try:
            while True:
                message = await websocket.receive_text()
                print(message)
                
                await manager.broadcast_message(message)

        except WebSocketDisconnect:
            manager.disconnect(websocket)


@app.post("/active", status_code=status.HTTP_200_OK)
async def active_users() -> str:
    users_active =  list(manager.active_connections.keys())
    return {"active_users": users_active}
