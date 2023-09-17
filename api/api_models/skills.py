from pydantic import BaseModel, validator


class SkillBase(BaseModel):
    name: str

    class Config:
        orm_mode = True

    @validator('name')
    def convert_to_lower_case(cls, v):
        return v.lower()


class SkillCreate(SkillBase):
    name: str
    


