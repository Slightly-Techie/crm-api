from pydantic import BaseModel, Field, validator


class TagBase(BaseModel):
    name: str = Field(...)

    class Config:
        from_attributes = True

    @validator('name')
    def convert_to_lower_case(cls, v):
        return v.lower()


class TagCreate(TagBase):
    pass
