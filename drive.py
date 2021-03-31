import os
from pydrive.drive import GoogleDrive
from pydrive.auth import GoogleAuth

from db_utils import DataBase, Query


class ChatDrive:
    
    def __init__(self) -> None:
        gauth = GoogleAuth(settings_file="settings.yaml")
        self.drive = GoogleDrive(gauth)

        DATABASE_URL = os.environ.get('DATABASE_URL')
        db = DataBase(DATABASE_URL)
        if not self.room_exists("global"):
            query = Query.create_room("global")
            db.execute_query(query, logging_message="Create Global Room")


    def create_room(self, roomname: str) -> None:
        room_exists = self.room_exists(roomname)

        if not room_exists:
            self.drive.CreateFile({'title': f"{roomname}.room"})
        else:
            room = self.drive.CreateFile({'title' : f"{roomname}.room"})
            room.Upload()


    def add_chat(self, roomname: str, uid: str, message: str) -> None:
        room_id = self._get_room_id(roomname)
        room = self.drive.CreateFile({'id': room_id})
        updated_content = f"{room.GetContentString()}{uid}:{message}\n"
        room.SetContentString(updated_content)
        room.Upload()


    def _get_room_id(self, roomname: str) -> str:
        files = self.drive.ListFile({'q': f"title='{roomname}.room' and trashed=false"}).GetList()
        file_list = [file['id'] for file in files]

        if len(file_list) > 1:
            raise FileExistsError
        elif len(file_list) == 0:
            raise FileNotFoundError
        else:
            return file_list[0]

    
    def room_exists(self, roomname: str) -> bool:
        files = self.drive.ListFile({'q': f"title='{roomname}.room' and trashed=false"}).GetList()
        file_list = [file['id'] for file in files]
 
        if len(file_list) > 1:
            raise FileExistsError
        elif len(file_list) == 0:
            raise FileNotFoundError
        else:
            return True