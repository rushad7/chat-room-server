# pylint: disable=no-name-in-module
# pylint: disable=no-self-argument

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