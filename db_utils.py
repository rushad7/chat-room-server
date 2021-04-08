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

        cursor = self.connection.cursor()

        try:
            cursor.execute(query)
            self.connection.commit()
            self.logger.debug("Query executed successfully")
        except Exception as e:
            self.logger.error(e)
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
    def create_table(table_name: str, **columns: Dict[str, str]) -> str:
        query = f"CREATE TABLE IF NOT EXISTS {table_name} ( id SERIAL, "

        for column_name, dtype in columns.items():
            query += (column_name + " " + dtype + ", ")

        query = query[:-2] + " );"
        return query


    @staticmethod
    def user_signup(uid: str, username: str, password: str) -> str:
        return f"INSERT INTO users (uid, username, password) VALUES ('{uid}', '{username}', '{password}');"


    @staticmethod
    def get_uid(username: str) -> str:
        return f"SELECT uid FROM users WHERE username='{username}';"


    @staticmethod
    def get_username(uid: str) -> str:
        return f"SELECT username FROM users WHERE uid='{uid}'"


    @staticmethod
    def get_password(username: str) -> str:
        return f"SELECT password FROM users WHERE username='{username}';"


    @staticmethod
    def create_room(roomname: str, creator: str) -> str:
        datetime_stamp = str(datetime.now())
        members = str([creator])
        return f"INSERT INTO rooms (roomname, admins, datetime, members) VALUES ('{roomname}', '{creator}', '{datetime_stamp}', '{members}');"


    @staticmethod
    def room_exists(roomname: str) -> str:
        return f"SELECT roomname FROM rooms WHERE roomname='{roomname}';"


    @staticmethod
    def delete_room(roomname: str) -> str:
        return f"DELETE FROM rooms WHERE roomname='{roomname}';"


    @staticmethod
    def get_room_members(roomname: str) -> str:
        return f"SELECT members FROM rooms WHERE roomname='{roomname}';"


    @staticmethod
    def get_room_admins(roomname: str) -> str:
        return f"SELECT admins FROM rooms WHERE roomname='{roomname}';"


    @staticmethod
    def add_member(roomname: str, username: str, existing_members: list) -> str:
        members = str(existing_members.append(username))
        return f"UPDATE rooms SET members = '{members}' WHERE roomname='{roomname}';"


    @staticmethod
    def modify_privileges(roomname: str, username: str, change_role_to: str, existing_admins: list) -> str:

        if change_role_to == "admin":
            admins = str(existing_admins.append(username))
        elif change_role_to == "member":
            admins = str(existing_admins.remove(username))
        
        return f"UPDATE rooms SET admins = '{admins}' WHERE roomname='{roomname}';"