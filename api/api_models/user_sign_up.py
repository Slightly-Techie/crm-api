from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class UserSignUp(BaseModel):
    email: EmailStr = Field(...)
    first_name: str = Field(..., min_length=2)
    last_name: str = Field(..., min_length=2)
    password: str = Field(...)
    password_confirmation: str = Field(...)



class UserLogin(BaseModel):
  email: EmailStr = Field(...)
  password: str = Field(...)


class Token(BaseModel):
  token: str = Field(...)
  token_type: str = Field(...)

class TokenData(BaseModel):
  id: Optional[str] = Field(default=None)
