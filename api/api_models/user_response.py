from pydantic import BaseModel, EmailStr, Field
from datetime import datetime


class UserResponse(BaseModel):
    id: int = Field(...)
    email: EmailStr = Field(...)
    first_name: str = Field(...)
    last_name: str = Field(...)
    created_at: datetime = Field(...)

    class Config:
        orm_mode = True
