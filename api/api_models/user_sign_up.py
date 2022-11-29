from pydantic import BaseModel, EmailStr
from typing import Optional

class UserSignUp(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    password: str
    password_confirmation: str


class UserLogin(BaseModel):
  email: EmailStr
  password: str


class Token(BaseModel):
  token: str
  token_type: str

class TokenData(BaseModel):
  id: Optional[str] = None
