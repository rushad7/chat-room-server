import sqlite3
from sqlite3 import Error


class DataBase:

    def __init__(self, path) -> None:
        connection = None
        try:
            connection = sqlite3.connect(path)
            print("Connection to SQLite DB successful")
        except Error as e:
            print(f"The error '{e}' occurred")

        self.connection = connection

    def execute_query(self, query):
        cursor = self.connection.cursor()
        try:
            cursor.execute(query)
            self.connection.commit()
            print("Query executed successfully")
        except Error as e:
            print(f"The error '{e}' occurred")


class Query:

    @staticmethod
    def add_user(uid, username, pswd):
        print("User added successfully")
        return f'''INSERT INTO users (uid, username, password) VALUES ("{uid}", "{username}", "{pswd}");'''


    create_user_table = '''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        uid TEXT NOT NULL,
        username TEXT NOT NULL,
        password TEXT NOT NULL
    );
    '''

    create_message_table = '''
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        date_time TEXT NOT NULL,
        message TEXT NOT NULL
    )
    '''