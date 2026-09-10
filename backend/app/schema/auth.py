from pydantic import BaseModel

class UserLoginRequest(BaseModel):
    username: str
    password: str
    
class UserRegisterRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"