import os
from drive import ChatDrive
from db_utils import DataBase, Query
from logger import Logger


class RoomManager:

    """ Room Manager class
    """

    def __init__(self) -> None:

        """ Initialises Room Manager
        """

        DATABASE_URL = os.environ.get('DATABASE_URL')
        self.db = DataBase(DATABASE_URL)
        self.chatdrive = ChatDrive()
        self.logger = Logger("CHATROOM-SERVER-LOG", "chatroom_server.log")


    def room_exists(self, roomname: str) -> bool:
        
        """ Checks if room exists
        Args:
            roomname (str): Name of the room for verification
        Returns:
            bool: True if room exists, False if it does not
        """

        room_exists_query = Query.room_exists(roomname)
        query_result = self.db.read_execute_query(room_exists_query)
        room_exists_in_drive = self.chatdrive.room_exists(roomname)
        room_exists_in_table = True if (roomname, ) in query_result else False
        
        if room_exists_in_drive and room_exists_in_table:
            self.logger.debug("Room exists")
            return True
        elif (not room_exists_in_drive) and (not room_exists_in_table):
            self.logger.error(f"Room '{roomname}' does not exist")
            return False
        else:
            self.logger.error("Data corrupt")
            return False


    def create_room(self, roomname: str, creator: str) -> bool:
        
        """ Create a Room
        Args:
            roomname (str): Name of the room to be created
            creator (str): Creator/Author/Owner(s) of the room
        Returns:
            bool: True if successfully created, False if not created
        """

        try:
            room_exists = self.room_exists(roomname)

            if not room_exists:
                query = Query.create_room(roomname, creator)
                self.db.execute_query(query)
                self.chatdrive.create_room(roomname)
                self.logger.info(f"Room {roomname} created")
                return True
            else: 
                return False

        except: 
            self.logger.error(f"Failed to create room")
            return False


    def delete_room(self, roomname: str) -> bool:
        
        """ Delete room
        Args:
            roomname (str): Name of the room to delete
        Returns:
            bool: True if successfully deleted, False if not deleted
        """

        try:
            room_exists = self.room_exists(roomname)

            if room_exists:
                self.chatdrive.delete_room(roomname)
                delete_room_query = Query.delete_room(roomname)
                self.db.execute_query(delete_room_query)
                self.logger.info(f"Room '{roomname}' deleted successfully")
                return True
            else:
                self.logger.error(f"Failed to delete room '{roomname}'")
                return False
        except:
            self.logger.error(f"Failed to delete room '{roomname}'")
            return False


    def add_member(self, roomname: str, username: str) -> bool:
        
        """ Add a user to the room
        Args:
            roomname (str): Name of the room to add user to
            username (str): User to add to room
        Returns:
            bool: True if successfully added, False if not added 
        """

        try:
            room_exists = self.room_exists(roomname)

            if room_exists:
                get_members_query = Query.get_room_members(roomname)
                room_members: str = self.db.read_execute_query(get_members_query)[0][0]
                room_members_list = room_members.split()

                if username in room_members_list:
                    self.logger.warning(f"User '{username}' is already a part of room {roomname}")
                    return False

                else:
                    add_member_query = Query.add_member(roomname, username, room_members)
                    self.db.execute_query(add_member_query)
                    self.logger.info(f"User '{username}' added to {roomname}")
                    return True

            else:
                self.logger.error(f"Room '{roomname}' does not exist")
                return False

        except:
            self.logger.error(f"Failed to add '{username}' to '{roomname}'")
            return False

        
    def modify_privileges(self, roomname: str, username: str, change_role_to: str) -> bool:
        
        """ Modify user privileges
        Args:
            roomname (str): Room whos user privileges are to be modified
            username (str): User whos privilege is to be modiied
            change_role_to (str): Users new/modified role
        Returns:
            bool: True if successfully modified, False if not modified
        """
        try:
            room_exists = self.room_exists(roomname)

            if room_exists:
                get_admins_query = Query.get_room_admins(roomname)
                room_admins: str = self.db.read_execute_query(get_admins_query)[0][0]
                room_admins_list = room_admins.split()

                if (username in room_admins_list) and change_role_to == "admin":
                    self.logger.warning(f"User '{username}' is already an admin")
                    return False

                elif (username not in room_admins) and change_role_to == "member":
                    self.logger.warning(f"User '{username}'' is already a member")
                    return False

                else:
                    modify_privileges_query = Query.modify_privileges(roomname, username, change_role_to, room_admins)
                    self.db.execute_query(modify_privileges_query)
                    self.logger.info(f"User privileges updated: '{username}' is now a {change_role_to}")
                    return True
            
            else:
                self.logger.error(f"Room '{roomname}' does not exist")
                return False
        
        except:
            self.logger.error(f"Failed to modify user '{username}' to {change_role_to}")
            return False


    def has_access(self, roomname: str, uid: str) -> bool:
        
        """ Check if user has access to a room
        Args:
            roomname (str): Name of the room to verify
            uid (str): UID of the user to verify
        Returns:
            bool: True if user has access, False if user does not have access
        """

        try:
            room_exists = self.room_exists(roomname)
            get_username_query = Query.get_username(uid)
            username = self.db.read_execute_query(get_username_query)[0][0]

            if room_exists:
                get_members_query = Query.get_room_members(roomname)
                room_members: str = self.db.read_execute_query(get_members_query)[0][0]
                room_members_list = room_members.split()


                if username in room_members_list:
                    self.logger.debug(f"User with UID = '{uid}' has access to room '{roomname}'")
                    return True
                else:
                    self.logger.error(f"User with UID = '{uid}' does not have access to room '{roomname}'")
                    return False
            else:
                self.logger.error(f"Room '{roomname}' does not exist")
                return False

        except:
            self.logger.error(f"Failed to verify room access")
            return False