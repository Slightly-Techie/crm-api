from fastapi import APIRouter, Depends, HTTPException, status

from sqlalchemy.orm import Session

from utils.utils import get_password_hash

from db.models.users import User

from db.database import get_db
from db.repository.users import create_new_user

from api.api_models.user_sign_up import UserSignUp, Token
from api.api_models.user_response import UserResponse
from fastapi.security import OAuth2PasswordRequestForm
from utils.utils import verify_password
from utils.oauth2 import get_access_token
from core.config import settings

auth_router = APIRouter(tags=["Auth"], prefix="/users")


@auth_router.post('/register', status_code=status.HTTP_201_CREATED, response_model=UserResponse)
def signup(user: UserSignUp, db: Session = Depends(get_db)):

    user_data = db.query(User).filter(User.email == user.email).first()
    if user_data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=settings.ERRORS.get("USER_EXISTS"))
    hash_passwd = get_password_hash(user.password)
    if user.password != user.password_confirmation:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=settings.ERRORS.get("PASSWORD_MATCH_DETAIL"))

    user.password = hash_passwd
    new_user = create_new_user(user, db)

    return new_user


@auth_router.post('/login', response_model=Token)
def login(user: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user_data = db.query(User).filter(User.email == user.username).first()
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=settings.ERRORS.get("INVALID_CREDENTIALS"))

    if not verify_password(user.password, user_data.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=settings.ERRORS.get("INVALID_CREDENTIALS"))

    token = get_access_token(str(user_data.id))

    return Token(token=token, token_type="Bearer")
















