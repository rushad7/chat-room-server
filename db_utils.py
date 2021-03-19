from datetime import date, datetime
from typing import List, Dict
import psycopg2
from psycopg2 import OperationalError


class DataBase:

    def __init__(self, db_url: str) -> None:
        connection = None
        try:
            connection = psycopg2.connect(db_url, sslmode='require')
            print("Connection to Database successful")
        except OperationalError as e:
            print(e)

        self.connection = connection

    def execute_query(self, query: str) -> None:
        self.connection.autocommit = True
        cursor = self.connection.cursor()
        try:
            cursor.execute(query)
            print("Query executed successfully")
        except OperationalError as e:
            print(e)

    def read_execute_query(self, query: str) -> List[tuple]:
        cursor = self.connection.cursor()
        result = None
        try:
            cursor.execute(query)
            result = cursor.fetchall()
            return result
        except OperationalError as e:
            print(e)


class Query:

    @staticmethod
    def add_user(uid: str, username: str, password: str) -> str:
        print("User added successfully")
        return f"INSERT INTO users (uid, username, password) VALUES ('{uid}', '{username}', '{password}');"


    @staticmethod
    def save_message(uid: str, message: str) -> str:
        date_time = str(datetime.now())
        return f"INSERT INTO messages (uid, date_time, message) VALUES ('{uid}', '{date_time}', '{message}');"

    @staticmethod
    def create_table(table_name: str, **columns: Dict[str, str]) -> str:
        query = f"CREATE TABLE IF NOT EXISTS {table_name} ( id SERIAL, "

        for column_name, dtype in columns.items():
            query += (column_name + " " + dtype + ", ")

        query = query[:-2] + " );"
        return query
