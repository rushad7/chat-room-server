import re
from datetime import datetime
from typing import List, Dict
import psycopg2

from logger import Logger


class DataBase:

    """ Handles database transactions
    """

    def __init__(self, db_url: str) -> None:

        """ Connect to database 
        Args:
            db_url (str): URL of postgresql database
        """
        
        self.logger = Logger("CHATROOM-SERVER-LOG", "chatroom_server.log")
        self.connection = None

        try:
            self.connection = psycopg2.connect(db_url, sslmode='require')
            self.logger.info("Connection to Database successful")
        except:
            self.logger.error("Failed to connect to Data Base")


    def execute_query(self, query: str) -> None:

        """ Execute query
        Args:
            query (str): Query to be executed
        """

        cursor = self.connection.cursor()

        try:
            cursor.execute(query)
            self.connection.commit()
            self.logger.debug("Query executed successfully")
        except Exception as e:
            self.logger.error(e)
            self.logger.error("Failed to exeute query")


    def read_execute_query(self, query: str) -> List[tuple]:
        
        """ Returns query result
        Args:
            query (str): Query to be executed
        Returns:
            List[tuple]: List of tuples of the query result.
        """

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

    """ Query generation
    """

    @staticmethod
    def create_table(table_name: str, **columns: Dict[str, str]) -> str:

        """ Returns query for creating a table
        Args:
            table_name (str): Name of table to be created
        Returns:
            str: Query for table creation
        """

        query = f"CREATE TABLE IF NOT EXISTS {table_name} ( id SERIAL, "

        for column_name, dtype in columns.items():
            query += (column_name + " " + dtype + ", ")

        query = query[:-2] + " );"
        return query


    @staticmethod
    def user_signup(uid: str, username: str, password: str) -> str:

        """ Returns query for user registration
        Args:
            uid (str): Unique Identification (UID) of user
            username (str): Corresponding username
            password (str): Corresponding password
        Returns:
            str: Query for user registration
        """

        return f"INSERT INTO users (uid, username, password) VALUES ('{uid}', '{username}', '{password}');"


    @staticmethod
    def get_uid(username: str) -> str:

        """ Returns query for UID lookup
        Args:
            username (str): Corresponding username
        Returns:
            str: Query for UID lookup
        """

        return f"SELECT uid FROM users WHERE username='{username}';"


    @staticmethod
    def get_username(uid: str) -> str:
        
        """ Returns query for username lookup
        Args:
            uid (str): Corresponding UID
        Returns:
            str: Query for username lookup
        """

        return f"SELECT username FROM users WHERE uid='{uid}';"


    @staticmethod
    def get_password(username: str) -> str:

        """ Returns query for password lookup
        Args:
            username (str): Corresponding username
        Returns:
            str: Query for password lookup
        """

        return f"SELECT password FROM users WHERE username='{username}';"


    @staticmethod
    def create_room(roomname: str, creator: str) -> str:

        """ Returns query for creating a room
        Args:
            roomname (str): Name of room to be created
            creator (str): Creator/Author/Owner(s) of the room
        Returns:
            str: [description]
        """

        datetime_stamp = str(datetime.now())
        creator = f"{creator} "
        return f"INSERT INTO rooms (roomname, admins, datetime, members) VALUES ('{roomname}', '{creator}', '{datetime_stamp}', '{creator}');"


    @staticmethod
    def room_exists(roomname: str) -> str:

        """ Returns query for room verification
        Args:
            roomname (str): Corresponding username
        Returns:
            str: Query for room verification
        """

        return f"SELECT roomname FROM rooms WHERE roomname='{roomname}';"


    @staticmethod
    def delete_room(roomname: str) -> str:

        """ Returns query for deleting a room
        Args:
            roomname (str): Name of room to be deleted
        Returns:
            str: Query for deleting a room
        """

        return f"DELETE FROM rooms WHERE roomname='{roomname}';"


    @staticmethod
    def get_room_members(roomname: str) -> str:

        """ Returns query for listing members of a room
        Args:
            roomname (str): Name of room for member lookup
        Returns:
            str: Query for listing room members
        """

        return f"SELECT members FROM rooms WHERE roomname='{roomname}';"


    @staticmethod
    def get_room_admins(roomname: str) -> str:

        """ Returns query for listing admins of a room
        Args:
            roomname (str): Name of room for admin lookup
        Returns:
            str: Query for listing room admins
        """

        return f"SELECT admins FROM rooms WHERE roomname='{roomname}';"


    @staticmethod
    def add_member(roomname: str, username: str, existing_members: str) -> str:

        """ Returns query for adding a member to a room
        Args:
            roomname (str): Room to be added to
            username (str): User to be add
            existing_members (str): Existing members (Return value of get_room_members method)
        Returns:
            str: Query for adding a user to a room
        """

        members = f"{existing_members}{username} "
        return f"UPDATE rooms SET members = '{members}' WHERE roomname='{roomname}';"


    @staticmethod
    def modify_privileges(roomname: str, username: str, change_role_to: str, existing_admins: str) -> str:
        
        """ Returns query to modify user privileges
        Args:
            roomname (str): Room whos user privileges are being modified
            username (str): Username whos privileges are being modified
            change_role_to (str): Role type (member OR admin)
            existing_admins (str): Existing admins (Return value of get_room_admins method)
        Returns:
            str: Query for modifying user privileges.
        """

        if change_role_to == "admin":
            admins = f"{existing_admins}{username} "
        elif change_role_to == "member":
            admins = re.sub(rf'\b{username} \b', "", existing_admins)
        
        return f"UPDATE rooms SET admins = '{admins}' WHERE roomname='{roomname}';"