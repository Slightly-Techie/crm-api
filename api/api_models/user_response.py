from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class UserResponse(BaseModel):
    id: int = Field(...)
    email: EmailStr = Field(...)
    first_name: str = Field(...)
    last_name: str = Field(...)
    github_profile: str=Field('')
    twitter_profile: str=Field('')
    linkedin_profile: str=Field('')
    portfolio_url: Optional[str]=Field('')
    profile_pic_url: str=Field('')
    created_at: datetime = Field(...)

    class Config:
        orm_mode = True
