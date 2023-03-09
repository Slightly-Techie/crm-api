from pydantic import BaseModel, Field, EmailStr
from datetime import datetime
from typing import Optional


class SkillBase(BaseModel):
    name: str

    class Config:
        orm_mode = True



class SkillCreate(SkillBase):
    name: str
    


