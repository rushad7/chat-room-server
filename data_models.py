from pydantic import BaseModel


class UserCredentials(BaseModel):
    username: str
    password: str

class Room(BaseModel):
    name: str
    creator: str