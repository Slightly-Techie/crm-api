from fastapi import FastAPI
from passlib.context import CryptContext

context = CryptContext(schemes=["bcrypt"], deprecated="auto")
users = FastAPI()

def get_password_hash(password):
    return context.hash(password)


@users.post("/register/")
def create_user(username: str , password: str):
    return {"username": username}