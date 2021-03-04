import hashlib
import pandas as pd
from fastapi import FastAPI, status, WebSocket, WebSocketDisconnect

from db_utils import DataBase, Query
from data_models import UserCredentials
from connection_manager import ConnectionManager


app = FastAPI()
manager = ConnectionManager()

user_db = DataBase("user_db.sqlite")
user_db.execute_query(Query.create_user_table)

message_db = DataBase("messages_db.sqlite")
message_db.execute_query(Query.create_message_table)

def is_valid_uid(uid: str):
    query = f"SELECT username, password FROM users WHERE uid='{uid}';"
    query_response = pd.read_sql_query(query, user_db.connection)
    if query_response.empty: 
        return False
    else: 
        return True

@app.post("/signup", status_code=status.HTTP_201_CREATED)
async def add_user(credentials: UserCredentials):
    uid_uname = hashlib.sha512(credentials.username.encode("UTF-8")).hexdigest().upper()
    uid_pswd = credentials.password.upper()
    uid = uid_uname + uid_pswd

    query = Query.add_user(uid, credentials.username, credentials.password)
    user_db.execute_query(query)
    return True


@app.post("/verify", status_code=status.HTTP_200_OK)
async def verify_user(credentials: UserCredentials):
    query = f"SELECT username, password FROM users WHERE username='{credentials.username}' AND password='{credentials.password}';"
    query_response = pd.read_sql_query(query, user_db.connection)
    user_exists: bool = not query_response.empty
    return user_exists


@app.post("/login", status_code=status.HTTP_200_OK)
async def login(credentials: UserCredentials):
    try:
        query = f"SELECT username, password FROM users WHERE username='{credentials.username}';"
        query_response = pd.read_sql_query(query, user_db.connection)
        user_password = query_response.get("password")[0]

        if user_password == credentials.password:
            return True
        return False

    except:
        return False


@app.websocket("/chat/{uid}")
async def chat_websocket(websocket: WebSocket, uid: str):   
    
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