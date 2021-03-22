import os
from pydrive.drive import GoogleDrive
from pydrive.auth import GoogleAuth


class ChatDrive:
    
    def __init__(self):

        SECRETS = os.environ['secrets']
        CREDS1 = os.environ['creds1']
        CREDS2 = os.environ['creds2']
        CREDS = CREDS1 + CREDS2

        with open("client_secrets.json", "w") as secrets_file:
            secrets_file.write(SECRETS)

        with open("creds.txt", "w") as creds_file:
            creds_file.write(CREDS)

        gauth = GoogleAuth()
        gauth.LoadCredentialsFile("creds.txt")
        self.is_expired = gauth.access_token_expired

        if gauth.credentials is None:
            gauth.LocalWebserverAuth()
        elif self.is_expired:
            gauth.Refresh()
        else:
            gauth.Authorize()

        gauth.SaveCredentialsFile("creds.txt")
        self.drive = GoogleDrive(gauth)


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