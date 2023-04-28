from pydantic import BaseModel, Field, EmailStr, validator
from datetime import datetime
from typing import Optional


class SkillBase(BaseModel):
    name: str

    class Config:
        orm_mode = True

    @validator('name')
    def convert_to_lower_case(cls, v):
        return v.lower()


class SkillCreate(SkillBase):
    name: str
    


