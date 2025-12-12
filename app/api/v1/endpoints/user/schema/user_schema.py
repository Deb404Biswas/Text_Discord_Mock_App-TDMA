from pydantic import BaseModel
class Token(BaseModel):
    access_token: str
    token_type: str  
class UserRequest(BaseModel):
    user_name: str
    user_password: str
    user_id: str