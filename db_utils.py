from datetime import datetime
from typing import List, Dict
import psycopg2

from logger import Logger


class DataBase:

    def __init__(self, db_url: str) -> None:

        self.logger = Logger("CHATROOM-SERVER-LOG", "chatroom_server.log")
        self.connection = None

        try:
            self.connection = psycopg2.connect(db_url, sslmode='require')
            self.logger.info("Connection to Database successful")
        except:
            self.logger.error("Failed to connect to Data Base")

    def execute_query(self, query: str) -> None:

        self.connection.autocommit = True
        cursor = self.connection.cursor()

        try:
            cursor.execute(query)
            self.logger.debug("Query executed successfully")
        except:
            self.logger.error("Failed to exeute query")

    def read_execute_query(self, query: str) -> List[tuple]:

        cursor = self.connection.cursor()
        result = None

        try:
            cursor.execute(query)
            result = cursor.fetchall()
            self.logger.debug("Query executed, and data returned successfully")
            return result
        except:
            self.logger.error("Failed to execute query, no data returned")


class Query:

    @staticmethod
    def add_user(uid: str, username: str, password: str) -> str:
        return f"INSERT INTO users (uid, username, password) VALUES ('{uid}', '{username}', '{password}');"

    @staticmethod
    def create_table(table_name: str, **columns: Dict[str, str]) -> str:
        query = f"CREATE TABLE IF NOT EXISTS {table_name} ( id SERIAL, "

        for column_name, dtype in columns.items():
            query += (column_name + " " + dtype + ", ")

        query = query[:-2] + " );"
        return query

    @staticmethod
    def create_room(roomname: str, roomkey: str, creator: str) -> str:
        return f"INSERT INTO rooms (roomname, roomkey, creator, datetime) VALUES ('{roomname}', '{roomkey}', '{creator}', '{str(datetime.now())}');"

    @staticmethod
    def room_exists(roomname: str):
        return f"SELECT roomname FROM rooms WHERE roomname='{roomname}';"