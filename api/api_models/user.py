from pydantic import BaseModel, EmailStr, Field, validator
from datetime import datetime
from typing import Dict, Optional
from api.api_models.tags import TagBase
from utils.utils import RoleChoices


class Role(BaseModel):
    id: int = Field(...)
    name: str = Field(...)

    class Config:
        orm_mode = True


class Skills(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True


class UserSkills(BaseModel):
    id: int
    skills: list[Skills]

    class Config:
        orm_mode = True
        allow_population_by_field_name = True


class Tags(TagBase):
    id: int = Field(...)


class UserTags(TagBase):
    id: int = Field(...)
    tags: list[Tags]

    class Config:
        orm_mode = True
        allow_population_by_field_name = True


class FeedBase(BaseModel):
    title: str
    content: str
    feed_pic_url: Optional[str] = Field(None)
    


class FeedCreate(FeedBase):
    pass


class UserSignUp(BaseModel):
    email: EmailStr = Field(...)
    first_name: str = Field(..., min_length=2)
    last_name: str = Field(..., min_length=2)
    password: str = Field(...)
    password_confirmation: str = Field(...)
    role_id: Optional[int] = Field(None)
    bio: Optional[str] = Field(None)
    phone_number: str = Field(...)
    years_of_experience: Optional[int] = Field(None)
    github_profile: Optional[str] = Field(None)
    twitter_profile: Optional[str] = Field(None)
    linkedin_profile: Optional[str] = Field(None)
    portfolio_url: Optional[str] = Field(None)
    profile_pic_url: Optional[str] = Field(None)
    is_active: bool = False

    class Config:
        orm_mode = True
        validate_assignment = True

    @validator("role_id", pre=True, always=True)
    def set_role_id(cls, role_id):
        from db.database import SessionLocal
        from db.models.users import Role as _Role
        db = SessionLocal()
        check_role = db.query(_Role).filter(
            _Role.name == RoleChoices.USER).first()
        db.close()
        if not check_role:
            return role_id
        return role_id or check_role.id


class UserResponse(BaseModel):
    id: int = Field(...)
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

    class Config:
        orm_mode = True


class ProfileUpdate(BaseModel):
    email: Optional[EmailStr]
    first_name: Optional[str]
    last_name: Optional[str]
    years_of_experience: Optional[int]
    bio: Optional[str]
    phone_number: Optional[str]
    github_profile: Optional[str]
    twitter_profile: Optional[str]
    linkedin_profile: Optional[str]
    portfolio_url: Optional[str]
    profile_pic_url: Optional[str]

    class Config:
        orm_mode = True


class ProfileResponse(ProfileUpdate):
    id: int = Field(...)
    skills: list[Skills]
    tags: list[Tags]
    created_at: datetime = Field(...)
    is_active: bool = Field(...)


class FeedOwner(BaseModel):
    id: int
    first_name: str
    last_name: str
    profile_pic_url: str

    class Config:
        orm_mode = True


class Feeds(FeedBase):
    id: int
    created_at: datetime
    user: FeedOwner

    class Config:
        orm_mode = True

class PaginatedResponse(BaseModel):
    feeds: list[Feeds]
    total: int
    page: int
    size: int
    pages: int
    links: Optional[Dict[str, Optional[str]]]

class FeedUpdate(BaseModel):
    title: Optional[str]
    content: Optional[str]


class UserLogin(BaseModel):
    email: EmailStr = Field(...)
    password: str = Field(...)


class Token(BaseModel):
    token: str = Field(...)
    token_type: str = Field(...)


class TokenData(BaseModel):
    id: Optional[str] = Field(default=None)
