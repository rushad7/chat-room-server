from pydantic import BaseModel


class UserCredentials(BaseModel):
    username: str
    password: str

class Room(BaseModel):
    name: str
    key: str
    creator: str