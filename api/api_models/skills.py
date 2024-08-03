from pydantic import BaseModel, ConfigDict, field_validator


class SkillBase(BaseModel):
    name: str
    image_url: str | None

    model_config = ConfigDict(from_attributes=True)

    @field_validator('name')
    def convert_to_lower_case(cls, v):
        return v.lower()


class SkillCreate(SkillBase):
    name: str
