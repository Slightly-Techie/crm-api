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

auth_router = APIRouter(tags=["Auth"])


@auth_router.post('/users/register', status_code=status.HTTP_201_CREATED, response_model=UserResponse)
def signup(user: UserSignUp, db: Session = Depends(get_db)):
    '''
      user {
      first_name: Essilfie
      last_name: Genesis, 
      email: essigen@gmail.com, 
      password: food, 
      password_confirmation: food
      }
    '''

    user_data = db.query(User).filter(User.email == user.email).first()
    if user_data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="User with email already exists")
    hash_passwd = get_password_hash(user.password)
    if user.password != user.password_confirmation:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password and password confirmation do not match")

    extract_keys = ["first_name", "last_name", "email", "password"]
    user_edit = {key: user.dict()[key] for key in extract_keys}
    user_edit['password'] = hash_passwd

    new_user = create_new_user(user_edit, db)

    return UserResponse(id=new_user.id, email=new_user.email, first_name=new_user.first_name, last_name=new_user.last_name, created_at=new_user.created_at)


@auth_router.post('/users/login', response_model=Token)
def login(user: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user_data = db.query(User).filter(User.email == user.username).first()
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail='Invalid credentials')

    if not verify_password(user.password, user_data.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail='Invalid credentials')

    token = get_access_token({"sub": user_data.id})

    return Token(token=token, token_type="Bearer")
