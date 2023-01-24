from pydantic import BaseModel, Field
from datetime import datetime


class SkillBase(BaseModel):
    name: str

class SkillCreate(SkillBase):
    pass

class Skill(SkillBase):
    id: int
    user_id: int
    created_at: datetime = Field(...)

    class Config:
        orm_mode: True

class UserBase(BaseModel):
    email: str

class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    skills: list[Skill]


    class Config:
        orm_mode = True



class SkillSchema(SkillBase):
    users: list[UserBase]


class UserSchema(BaseModel):
    skills: list[SkillBase]