import os
from pydrive.drive import GoogleDrive
from pydrive.auth import GoogleAuth


class ChatDrive:
    
    def __init__(self) -> None:
        gauth = GoogleAuth(settings_file="settings.yaml")

        if gauth.access_token_expired:
            print("Google Drive Token Expired, Refreshing")
            gauth.Refresh()

        self.drive = GoogleDrive(gauth)
        self.create_room("global")


    def create_room(self, roomname: str) -> None:
        room_exists = self.room_exists(roomname)

        if not room_exists:
            room = self.drive.CreateFile({'title': f"{roomname}.room"})
            room.Upload()
        else:
            self.drive.CreateFile({'title' : f"{roomname}.room"})


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
 
        if len(file_list) == 1:
            return True
        return False


    def get_rooms(self):
        files = self.drive.ListFile({'q': f"'root' in parents and trashed=false"}).GetList()
        file_list = [file['title'] for file in files]
        return {"files": file_list}