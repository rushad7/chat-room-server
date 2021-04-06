import os
from drive import ChatDrive
from db_utils import DataBase, Query
from logger import Logger


class RoomManager:

    def __init__(self) -> None:
        DATABASE_URL = os.environ.get('DATABASE_URL')
        self.db = DataBase(DATABASE_URL)
        self.chatdrive = ChatDrive()
        self.logger = Logger("CHATROOM-SERVER-LOG", "chatroom_server.log")


    def room_exists(self, roomname: str) -> bool:
        room_exists_query = Query.room_exists(roomname)
        query_result = self.db.read_execute_query(room_exists_query)
        room_exists_in_drive = self.chatdrive.room_exists(roomname)
        room_exists_in_table = True if (roomname, ) in query_result else False
        
        if room_exists_in_drive and room_exists_in_table:
            return True
        elif (not room_exists_in_drive) and (not room_exists_in_table):
            return False
        else:
            raise Exception("Data corrupt")


    def create_room(self, roomname: str, creator: str) -> bool:
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


    def delete_room(self, roomname: str):
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
        except:
            self.logger.error(f"Failed to delete room '{roomname}'")


    def add_member(self, roomname: str, username: str):
        try:
            room_exists = self.room_exists(roomname)

            if room_exists:
                get_members_query = Query.get_room_members(roomname)
                room_members = self.db.read_execute_query(get_members_query)
                room_members: list = eval(room_members[0][0])

                if username in room_members:
                    return False
                else:
                    add_member_query = Query.add_member(roomname, username, room_members)
                    self.db.execute_query(add_member_query)
                    return True

        except:
            self.logger.error(f"Failed to add '{username}' to '{roomname}'")
            return False

        
    def modify_privileges(self, roomname: str, username: str, role: str):

        try:
            room_exists = self.room_exists(roomname)

            if room_exists:
                get_admins_query = Query.get_room_admins(roomname)
                room_admins = self.db.read_execute_query(get_admins_query)
                room_admins: list = eval(room_admins[0][0])

                if username in room_admins:
                    return False
                else:
                    modify_privileges_query = Query.modify_privileges(roomname, username, role, room_admins)
                    self.db.execute_query(modify_privileges_query)
                    self.logger.info(f"Added user {username} as {role}")
                    return True

        except:
            self.logger.error(f"Failed to modify user '{username}' to {role}")
            return False