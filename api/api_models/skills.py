from pydantic import BaseModel, ConfigDict, field_validator


class SkillBase(BaseModel):
    name: str
    image_url: str | None

    model_config = ConfigDict(from_attributes=True)

    @field_validator('name')
    def normalize_name(cls, v):
        return v.strip().title()


class SkillCreate(SkillBase):
    name: str
