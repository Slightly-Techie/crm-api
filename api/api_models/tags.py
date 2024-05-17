from pydantic import BaseModel, ConfigDict, Field, field_validator


class TagBase(BaseModel):
    name: str = Field(...)

    model_config = ConfigDict(from_attributes=True)

    @field_validator('name')
    def convert_to_lower_case(cls, v):
        return v.lower()


class TagCreate(TagBase):
    pass
