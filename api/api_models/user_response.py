from pydantic import BaseModel, EmailStr


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    first_name: str
    last_name: str
