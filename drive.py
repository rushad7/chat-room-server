import os
from typing import Union
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.http import MediaFileUpload

from logger import Logger


class ChatDrive:

    def __init__(self) -> None:

        creds = None
        self.logger = Logger("CHATROOM-SERVER-LOG", "chatroom_server.log")

        if os.path.exists("token.json"):
            SCOPES = ["https://www.googleapis.com/auth/drive"]
            creds = Credentials.from_authorized_user_file("token.json", SCOPES)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
                self.logger.debug("Google Drive access refreshed")
                
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    "credentials.json", SCOPES)
                creds = flow.run_local_server()

            with open("token.json", "w") as token:
                token.write(creds.to_json())

        self.service = build("drive", "v3", credentials=creds)
        self.create_room("global", None, "admin")
        self.logger.info("Drive Initialised")


    def get_rooms(self) -> Union[list, None]:
        
        results = self.service.files().list(q="trashed=false",
                                            fields="nextPageToken, files(id, name)").execute()
        items = results.get("files", [])

        roomname_list = []
        for item in items:
            roomname_list.append(item["name"])

        if not items:
            return None
        else:
            return roomname_list


    def get_room_id(self, roomname) -> Union[str, None]:

        results = self.service.files().list(q=f"name='{roomname}.room' and trashed=false",
                                            fields="nextPageToken, files(id, name)").execute()
        items = results.get("files", [])

        roomid_list = []
        for item in items:
            roomid_list.append(item["id"])

        if not items:
            self.logger.error(f"Room ID lookup: Room '{roomname}' does not exist")
            return None
        else:
            self.logger.info(f"Room ID lookup: Room '{roomname}' exists")
            return roomid_list[0]


    def room_exists(self, roomname: str):

        rooms_list = self.get_rooms()

        if rooms_list is not None:
            if f"{roomname}.room" in rooms_list:
                rooms_unique = list(set(rooms_list))

                if rooms_list == rooms_unique:
                    self.logger.info(f"Room lookup: Room '{roomname}' exists")
                    return True
                else:
                    self.logger.error(f"Room lookup: Room '{roomname}' does not exist")
                    return False
            else:
                self.logger.error(f"Room lookup: Room '{roomname}' does not exist")
                return False
        else:
            self.logger.error(f"Room lookup: Room '{roomname}' does not exist")
            return False


    def create_room(self, roomname: str, roomkey: str, username: str) -> None:

        if not self.room_exists(roomname):
            file_metadata = {"name": f"{roomname}.room"}
            self.service.files().create(body=file_metadata, fields="id").execute()
            self.logger.info(f"Room '{roomname}' created")
        else:
            self.logger.warning(f"Room '{roomname}' already exists, not created")


    async def add_chat(self, roomname: str, username: str, chat: str) -> bool:

        room_id = self.get_room_id(roomname)

        if room_id is not None:
            content_bytes: bytes = self.service.files().get_media(fileId=room_id).execute()
            content_str = content_bytes.decode("utf-8")
            message = f"{username}:{chat}"
            updated_content = f"{content_str}{message}\n"
            file_metadata = {"name": f"{roomname}.room"}

            with open(f"{roomname}.room", "w") as room:
                room.write(updated_content)
            
            media_body = MediaFileUpload(
                f"{roomname}.room", resumable=True)

            self.service.files().update(
                fileId=room_id,
                body=file_metadata,
                media_body=media_body).execute()

            del(media_body)
            os.remove(f"{roomname}.room")
            self.logger.info(f"Chat added to room '{roomname}'")
            return True
        else:
            self.logger.info(f"Failed to add chat too Room {roomname}")
            return False