from pydantic import BaseModel, Field, EmailStr
from datetime import datetime
from typing import Optional


class SkillBase(BaseModel):
    name: str

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    pass

    class Config:
        orm_mode = True


class SkillCreate(SkillBase):
    name: str
    


class Skills(BaseModel):
    id: int
    name: str
    user_id: int

    class Config:
        orm_mode = True


# class UserBase(BaseModel):
#    pass
  


class Users(UserBase):
    id: int
    skills: list[Skills] = []


    class Config:
        orm_mode = True
        allow_population_by_field_name = True



class SkillSchema(SkillBase):
    users: list[UserBase] = []

    class Config:
        orm_mode = True
        allow_population_by_field_name = True





