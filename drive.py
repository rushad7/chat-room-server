import os
import json
from pydrive.drive import GoogleDrive
from pydrive.auth import GoogleAuth, ServiceAccountCredentials


class ChatDrive:
    
    def __init__(self):

        gauth = GoogleAuth()
        CREDS1 = os.environ.get('creds1')
        CREDS2 = os.environ.get('creds2')
        CREDS = CREDS1 + CREDS2
        scope = ['https://www.googleapis.com/auth/drive']
        
        with open("creds.json", "w") as creds_file:
            json.dump(SECRETS, creds_file)

        gauth.credentials = ServiceAccountCredentials.from_json_keyfile_name('creds.json', scope)
        self.drive = GoogleDrive(gauth)
        self.is_expired = gauth.access_token_expired


    def create_room(self, name: str):
        room_file = self.drive.CreateFile({'title': name})
        room_file.Upload()
        return room_file


    def add_chat(self, room_name: str, uid: str, message: str) -> None:
        room_id = self._get_room_id(room_name)
        room = self.drive.CreateFile({'id': room_id})
        updated_content = f"{room.GetContentString()}\n{uid}:{message}"
        room.SetContentString(updated_content)
        room.Upload()


    def _get_room_id(self, filename: str) -> str:
        files = self.drive.ListFile({'q': f"title='{filename}' and trashed=false"}).GetList()
        file_list = [file['id'] for file in files]
        if len(file_list) != 1:
            raise FileExistsError
        else:
            return file_list[0]
