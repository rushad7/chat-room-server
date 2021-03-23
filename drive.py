import os
import json
from pydrive.drive import GoogleDrive
from pydrive.auth import GoogleAuth, ServiceAccountCredentials


class ChatDrive:
    
    def __init__(self):

        gauth = GoogleAuth()
        SECRETS = json.loads(os.environ.get('secrets'))
        scope = ['https://www.googleapis.com/auth/drive']
        
        with open("client_secrets.json", "w") as secrets_file:
            json.dump(SECRETS, secrets_file)

        gauth.credentials = ServiceAccountCredentials.from_json_keyfile_name('client_secrets.json', scope)
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
