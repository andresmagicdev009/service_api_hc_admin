from pydantic import BaseModel, EmailStr
from uuid import UUID

class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    
class MessageResponse(BaseModel):
    message: str
    
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer "
    
