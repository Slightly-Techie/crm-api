from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional

class UserSignUp(BaseModel):
    email: EmailStr = Field(...)
    first_name: str = Field(..., min_length=2)
    last_name: str = Field(..., min_length=2)
    password: str = Field(...)
    password_confirmation: str = Field(...)
    github_profile: Optional[str] = Field(None)
    twitter_profile: Optional[str] = Field(None)
    linkedin_profile: Optional[str] = Field(None)
    portfolio_url: Optional[str] = Field(None)
    profile_pic_url: Optional[str] = Field(None)


class UserResponse(BaseModel):
    id: int = Field(...)
    email: Optional[EmailStr] = Field(...)
    first_name: Optional[str] = Field(...)
    last_name: Optional[str] = Field(...)
    github_profile: Optional[str] = Field(None)
    twitter_profile: Optional[str] = Field(None)
    linkedin_profile: Optional[str] = Field(None)
    portfolio_url: Optional[str] = Field(None)
    profile_pic_url: Optional[str] = Field(None)
    created_at: datetime = Field(...)

    class Config:
        orm_mode = True

class Profile (BaseModel):
    email: Optional[EmailStr] 
    first_name: Optional[str] 
    last_name: Optional[str] 
    github_profile: Optional[str] 
    twitter_profile: Optional[str] 
    linkedin_profile: Optional[str] 
    portfolio_url: Optional[str]
    profile_pic_url: Optional[str] 



class UserLogin(BaseModel):
  email: EmailStr = Field(...)
  password: str = Field(...)


class Token(BaseModel):
  token: str = Field(...)
  token_type: str = Field(...)

class TokenData(BaseModel):
  id: Optional[str] = Field(default=None)
