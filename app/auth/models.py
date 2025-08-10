from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class RegisterRequest(BaseModel):
    login: str = Field(min_length=3, max_length=64)
    password: str = Field(min_length=8, max_length=256)

class LoginRequest(BaseModel):
    login: str
    password: str
    remember: bool = False

class UserPublic(BaseModel):
    id: int
    login: str
    created_at: datetime
    last_login_at: Optional[datetime]
