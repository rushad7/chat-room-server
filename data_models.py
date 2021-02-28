from pydantic import BaseModel


class UserCredentials(BaseModel):
    username: str
    password: str

class Message(BaseModel):
    sent_by: str
    date_time: str
    message: str
