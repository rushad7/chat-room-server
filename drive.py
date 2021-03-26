import os
import json
from pydrive.drive import GoogleDrive
from pydrive.auth import GoogleAuth


class ChatDrive:
    
    def __init__(self):
        gauth = GoogleAuth()
        self.drive = GoogleDrive(gauth)
        self.is_expired = gauth.access_token_expired


    def create_room(self, name: str) -> None:
        roomname  = f"{name}.room"
        room_exists = self._room_exists(roomname)

        if ~room_exists:
            self.drive.CreateFile({'title': roomname})
        room = self.drive.CreateFile({'title': roomname})
        room.Upload()


    def add_chat(self, room_name: str, uid: str, message: str) -> None:
        room_id = self._get_room_id(f"{room_name}.room")
        room = self.drive.CreateFile({'id': room_id})
        updated_content = f"{room.GetContentString()}\n{uid}:{message}"
        room.SetContentString(updated_content)
        room.Upload()


    def _get_room_id(self, roomname: str) -> str:
        files = self.drive.ListFile({'q': f"title='{roomname}' and trashed=false"}).GetList()
        file_list = [file['id'] for file in files]
        print(file_list)
        if len(file_list) > 1:
            raise FileExistsError
        elif len(file_list) == 0:
            raise FileNotFoundError
        else:
            return file_list[0]

    
    def _room_exists(self, roomname) -> bool:
        files = self.drive.ListFile({'q': f"title='{roomname}' and trashed=false"}).GetList()
        file_list = [file['title'] for file in files]
        print(file_list)
        if roomname in file_list:
            return True
        return False 