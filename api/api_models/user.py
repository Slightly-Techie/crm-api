from pydantic import BaseModel, EmailStr, Field # validator
from datetime import datetime
from typing import Optional



class Role(BaseModel):
  id: int = Field(...)
  name: str  = Field(...)

  class Config:
    orm_mode = True

  
class UserSignUp(BaseModel):
    email: EmailStr = Field(...)
    first_name: str = Field(..., min_length=2)
    last_name: str = Field(..., min_length=2)
    password: str = Field(...)
    password_confirmation: str = Field(...)
    role_id: Optional[int] = Field(None)
    github_profile: Optional[str] = Field(None)
    twitter_profile: Optional[str] = Field(None)
    linkedin_profile: Optional[str] = Field(None)
    portfolio_url: Optional[str] = Field(None)
    profile_pic_url: Optional[str] = Field(None)

    class Config:
        orm_mode = True
        validate_assignment = True
        
    # @validator("role", pre=True, always=True)
    # def set_role(cls, role):
    #     return role or "user"


class UserResponse(BaseModel):
    id: int = Field(...)
    email: Optional[EmailStr] = Field(...)
    first_name: Optional[str] = Field(...)
    last_name: Optional[str] = Field(...)
    role: Optional[Role] = Field(None)
    github_profile: Optional[str] = Field(None)
    twitter_profile: Optional[str] = Field(None)
    linkedin_profile: Optional[str] = Field(None)
    portfolio_url: Optional[str] = Field(None)
    profile_pic_url: Optional[str] = Field(None)
    created_at: datetime = Field(...)

    class Config:
        orm_mode = True

class ProfileUpdate(BaseModel):
    email: Optional[EmailStr] 
    first_name: Optional[str] 
    last_name: Optional[str] 
    github_profile: Optional[str] 
    twitter_profile: Optional[str] 
    linkedin_profile: Optional[str] 
    portfolio_url: Optional[str]
    profile_pic_url: Optional[str] 

    class Config:
      orm_mode = True

class ProfileResponse(ProfileUpdate):
  id : int = Field(...)


class UserLogin(BaseModel):
  email: EmailStr = Field(...)
  password: str = Field(...)


class Token(BaseModel):
  token: str = Field(...)
  token_type: str = Field(...)

class TokenData(BaseModel):
  id: Optional[str] = Field(default=None)
