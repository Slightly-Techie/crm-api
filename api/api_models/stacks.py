from pydantic import BaseModel, Field
from datetime import datetime


class Stacks(BaseModel):
    id: int = Field(...)
    name: str = Field(...)
    created_at: datetime = Field(...)
    updated_at: datetime = Field(...)

    class Config:
        from_attributes = True


class StackCreate(BaseModel):
    name: str = Field(...)
