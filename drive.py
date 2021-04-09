# pylint: disable=maybe-no-member

import os
import json
import requests
from datetime import datetime
from typing import Union
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.http import MediaFileUpload

from logger import Logger


class ChatDrive:

    """ Handles chat message storage and retrieval
    """

    def __init__(self) -> None:

        """ Initialise ChatDrive 
        """

        creds = None
        SCOPES = ["https://www.googleapis.com/auth/drive"]
        self.logger = Logger("CHATROOM-SERVER-LOG", "chatroom_server.log")

        if os.path.exists("token.json"):
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
                url = 'https://api.heroku.com/apps/chat-service/config-vars'
                payload = {'TOKEN': creds.to_json()}
                head = {'Content-Type':'application/json', 'Accept': 'application/vnd.heroku+json; version=3'}
                requests.patch(url, data=json.dumps(payload), headers=head)
                token.write(creds.to_json())

        self.service = build("drive", "v3", credentials=creds)
        self.logger.info("Drive Initialised")


    def get_rooms(self) -> Union[list, None]:

        """ Returns a list of all the rooms
        Returns:
            Union[list, None]: List of all the rooms or None
        """
        
        results = self.service.files().list(q="trashed=false",
                                            fields="nextPageToken, files(id, name)").execute()
        items = results.get("files", [])

        roomname_list = []
        for item in items:
            roomname_list.append(item["name"])

        if not items:
            self.logger.error("Rooms fetch failed")
            return None
        else:
            self.logger.debug("Romms fetched")
            return roomname_list


    def get_room_id(self, roomname: str) -> Union[str, None]:

        """ Returns room ID given room name
        Args:
            roomname (str): Name of the room for ID lookup
        Returns:
            Union[str, None]: String containing room ID or None
        """

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
            self.logger.debug(f"Room ID lookup: Room '{roomname}' exists")
            return roomid_list[0]


    def room_exists(self, roomname: str) -> bool:
        
        """ Check if room exists
        Args:
            roomname (str): Name of the room to check
        Returns:
            bool: True if it exists, False if it does not
        """

        rooms_list = self.get_rooms()

        if rooms_list is not None:
            if f"{roomname}.room" in rooms_list:
                rooms_unique = list(set(rooms_list))

                if rooms_list == rooms_unique:
                    self.logger.debug(f"Room lookup: Room '{roomname}' exists")
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


    def create_room(self, roomname: str) -> None:

        """ Creates new room if room doesnt already exist
        Args:
            roomname (str): Name of the room to create
        """

        if not self.room_exists(roomname):
            file_metadata = {"name": f"{roomname}.room"}
            self.service.files().create(body=file_metadata, fields="id").execute()
            self.logger.info(f"Room '{roomname}' created")
        else:
            self.logger.warning(f"Room '{roomname}' already exists, not created")


    async def add_chat(self, roomname: str, username: str, chat: str) -> bool:

        """ Add chat to room
        Args:
            roomname (str): Name of room to add message to
            username (str): Corresponding username
            chat (str): Message to add
        Returns:
            bool: True if added successfully, False if not
        """

        room_id = self.get_room_id(roomname)

        if room_id is not None:
            content_bytes: bytes = self.service.files().get_media(fileId=room_id).execute()
            content_str = content_bytes.decode("utf-8")
            datetime_str = str(datetime.now()) 
            message = f"{datetime_str} {username}:{chat}"
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
            self.logger.debug(f"Chat added to room '{roomname}'")
            return True
        else:
            self.logger.error(f"Failed to add chat too Room {roomname}")
            return False


    def delete_room(self, roomname: str) -> None:

        """ Delete a room
        Args:
            roomname (str): Name of the room to be deleted 
        """
        
        try:
            room_id = self.get_room_id(roomname)
            self.service.files().delete(fileId=room_id).execute()
        except:
            self.logger.error(f"Failed to delete room '{roomname}'")