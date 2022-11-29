from pydantic import BaseModel, EmailStr
from datetime import datetime


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    first_name: str
    last_name: str
    created_at: datetime

    class Config:
        orm_mode: True
