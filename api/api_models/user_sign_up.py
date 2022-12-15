from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class UserSignUp(BaseModel):
    email: EmailStr = Field(...)
    first_name: str = Field(..., min_length=2)
    last_name: str = Field(..., min_length=2)
    github_profile: str=Field('')
    twitter_profile: str=Field('')
    linkedin_profile: str=Field('')
    portfolio_url: Optional[str]=Field('')
    profile_pic_url: str=Field('')
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
