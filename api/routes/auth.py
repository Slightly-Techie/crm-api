from fastapi import APIRouter, Depends, HTTPException, status

from sqlalchemy.orm import Session

from utils import get_password_hash

from db.models.users import User

from db.database import get_db
from db.repository.users import create_new_user

from api.api_models.user_sign_up import UserSignUp
from api.api_models.user_response import UserResponse


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

    hash_passwd = get_password_hash(user.password)
    if user.password != user.password_confirmation:
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password and password confirmation do not match")

    extract_keys = ["first_name", "last_name", "email", "password"]
    user_edit = {key: user.dict()[key] for key in extract_keys}
    user_edit['password'] = hash_passwd

    new_user = create_new_user(user_edit, db)

    return new_user
