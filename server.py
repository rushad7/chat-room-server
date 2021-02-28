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


@app.post("/signup", status_code=status.HTTP_201_CREATED)
async def add_user(credentials: UserCredentials):
    query = Query.add_user(credentials.username, credentials.password)
    user_db.execute_query(query)
    return True


@app.post("/checkuser", status_code=status.HTTP_200_OK)
async def check_user(credentials: UserCredentials):
    query = f"SELECT username FROM users WHERE username='{credentials.username}';"
    query_response = pd.read_sql_query(query, user_db.connection)
    user_exists: bool = not query_response.empty
    return user_exists


@app.post("/login", status_code=status.HTTP_200_OK)
async def login(credentials: UserCredentials):
    try:
        query = f"SELECT username, password FROM users WHERE username='{credentials.username}';"
        query_response = pd.read_sql_query(query, user_db)
        user_password = query_response.get("password")[0]
        if user_password == credentials.password:
            return True
        return False

    except:
        return False


@app.websocket("/chat")
async def chat_websocket(websocket: WebSocket):

    await manager.connect(websocket)

    try:
        while True:
            message = await websocket.receive_text()
            print(message)
            
            await manager.broadcast_message(message)

    except WebSocketDisconnect:
        manager.disconnect(websocket)