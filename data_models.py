# pylint: disable=no-name-in-module
# pylint: disable=no-self-argument

from typing import Union
from pydantic import BaseModel


class UserCredentials(BaseModel):

    """ Class for data modelling of users
    """

    username: str
    password: str


class Room(BaseModel):

    """ Class for data modelling of rooms
    """
    
    name: str
    creator: str


class JoinRoom(BaseModel):

    """ Class for data modelling of room joining
    """

    roomname: str
    username: str
    description: Union[str, None]