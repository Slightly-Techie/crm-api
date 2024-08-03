from fastapi import Form, UploadFile
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator
from datetime import datetime
from typing import Optional, Union
from api.api_models.tags import TagBase
from utils.utils import RoleChoices
from .stacks import Stacks
import re


class Role(BaseModel):
    id: int = Field(...)
    name: str = Field(...)

    model_config = ConfigDict(from_attributes=True)

class Skills(BaseModel):
    id: int
    name: str
    image_url: str | None

    model_config = ConfigDict(from_attributes=True)


class UserSkills(BaseModel):
    id: int
    skills: list[Skills]

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class Tags(TagBase):
    id: int = Field(...)


class UserTags(TagBase):
    id: int = Field(...)
    tags: list[Tags]

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class FeedBase(BaseModel):
    content: str = Form(...)
    feed_pic_url: Union[UploadFile, str] = None


class FeedCreate(FeedBase):
    pass


class UserSignUp(BaseModel):
    username: str = Field(..., min_length=4)
    email: EmailStr = Field(...)
    first_name: str = Field(..., min_length=2)
    last_name: str = Field(..., min_length=2)
    password: str = Field(...)
    password_confirmation: str = Field(...)
    role_id: Optional[int] = Field(None)
    stack_id: Optional[int] = Field(None)
    bio: Optional[str] = Field(None)
    phone_number: str = Field(...)
    years_of_experience: Optional[int] = Field(None)
    github_profile: Optional[str] = Field(None)
    twitter_profile: Optional[str] = Field(None)
    linkedin_profile: Optional[str] = Field(None)
    portfolio_url: Optional[str] = Field(None)
    profile_pic_url: Optional[str] = Field(None)
    is_active: bool = False

    model_config = ConfigDict(from_attributes=True, validate_assignment=True)

    @field_validator("username")
    def validate_username(cls, value):
        # Use a regular expression to remove non-alphanumeric characters and spaces
        cleaned_username = re.sub(r'[^a-zA-Z0-9]', '', value)
        return cleaned_username.lower()

    @field_validator("role_id", mode="before", check_fields=True)
    def set_role_id(cls, role_id):
        from db.database import SessionLocal
        from db.models.roles import Role as _Role
        db = SessionLocal()
        check_role = db.query(_Role).filter(
            _Role.name == RoleChoices.USER).first()
        db.close()
        if not check_role:
            return role_id
        return role_id or check_role.id


class UserResponse(BaseModel):
    id: int = Field(...)
    username: str = Field(...)
    email: Optional[EmailStr] = Field(...)
    first_name: Optional[str] = Field(...)
    last_name: Optional[str] = Field(...)
    role: Optional[Role] = Field(None)
    years_of_experience: Optional[int] = Field(None)
    bio: Optional[str] = Field(None)
    phone_number: str = Field(...)
    github_profile: Optional[str] = Field(None)
    twitter_profile: Optional[str] = Field(None)
    linkedin_profile: Optional[str] = Field(None)
    portfolio_url: Optional[str] = Field(None)
    profile_pic_url: Optional[str] = Field(None)
    skills: list[Skills]
    tags: list[Tags]
    created_at: datetime = Field(...)
    is_active: bool = Field(...)
    stack: Optional[Stacks] = Field(None)

    model_config = ConfigDict(from_attributes=True)


class ProfileUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    years_of_experience: Optional[int] = None
    bio: Optional[str] = None
    phone_number: Optional[str] = None
    github_profile: Optional[str] = None
    twitter_profile: Optional[str] = None
    linkedin_profile: Optional[str] = None
    portfolio_url: Optional[str] = None
    profile_pic_url: Optional[str] = None
    stack_id: Optional[int] = Field(None)

    model_config = ConfigDict(from_attributes=True)


class ProfileResponse(ProfileUpdate):
    id: int = Field(...)
    skills: list[Skills]
    tags: list[Tags]
    stack: Optional[Stacks] = Field(None)
    created_at: datetime = Field(...)
    role: Optional[Role] = Field(None)
    is_active: bool = Field(...)
    status: str = Field(...)


class FeedOwner(BaseModel):
    id: int
    first_name: str
    last_name: str
    username: str
    profile_pic_url: Optional[str]

    model_config = ConfigDict(from_attributes=True)


class Feeds(FeedBase):
    id: int
    created_at: datetime
    feed_pic_url: Optional[str]
    user: FeedOwner

    model_config = ConfigDict(from_attributes=True)


class FeedUpdate(BaseModel):
    content: Optional[str]


class TechieOTMCreate(BaseModel):
    user_id: int = Field(...)
    points: int = Field(...)

    model_config = ConfigDict(from_attributes=True)


class TechieOTMResponse(BaseModel):
    id: int
    user: FeedOwner
    points: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserLogin(BaseModel):
    email: EmailStr = Field(...)
    password: str = Field(...)


class Token(BaseModel):
    token: str = Field(...)
    token_type: str = Field(...)
    is_active: bool = Field(...)
    user_status: str = Field(...)
    refresh_token: str = Field(...)


class TokenData(BaseModel):
    id: Optional[str] = Field(default=None)


class RefreshTokenRequest(BaseModel):
    refresh_token: str = Field(...)


class ForgotPasswordRequest(BaseModel):
    email: EmailStr = Field(...)


class ResetPasswordRequest(BaseModel):
    token: str = Field(...)
    new_password: str = Field(...)
