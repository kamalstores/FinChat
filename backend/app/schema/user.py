from pydantic import BaseModel


class UserProfile(BaseModel):
    username: str
    role: str