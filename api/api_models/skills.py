from pydantic import BaseModel, Field, EmailStr
from datetime import datetime
from typing import Optional


class SkillBase(BaseModel):
    name: str

class SkillCreate(SkillBase):
    name: str
    

class SkillResponse(SkillBase):
    id: int
    

    class Config:
        orm_mode: True
        allow_population_by_field_name = True

class UserBase(BaseModel):
   pass
  


class User(UserBase):
    id: int
    skills: list[SkillResponse]


    class Config:
        orm_mode = True
        allow_population_by_field_name = True



class SkillSchema(SkillBase):
    users: list[UserBase]


class UserSchema(BaseModel):
    skills: list[SkillBase]