from pydantic import BaseModel, EmailStr


class UserSignUp(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    password: str
    password_confirmation: str
