from fastapi import APIRouter, Depends, HTTPException, status, Response, Request

from sqlalchemy.orm import Session

from utils.utils import get_password_hash

from db.models.users import User

from db.database import get_db
from db.repository.users import create_new_user

from api.api_models.user import ProfileResponse, UserSignUp, Token
from api.api_models.user import UserResponse
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from utils.utils import verify_password
from utils.oauth2 import get_access_token, get_refresh_token, verify_refresh_token
from utils.permissions import is_authenticated
from core.config import settings

auth_router = APIRouter(tags=["Auth"], prefix="/users")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

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
def login(response: Response,user: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user_data = db.query(User).filter(User.email == user.username).first()
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=settings.ERRORS.get("INVALID_CREDENTIALS"))

    if not verify_password(user.password, user_data.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=settings.ERRORS.get("INVALID_CREDENTIALS"))

    token = get_access_token(str(user_data.id))
    refresh_token = get_refresh_token(str(user_data.id))

    response.set_cookie(key="st.token", value=refresh_token, httponly=True, max_age=settings.REFRESH_TOKEN_EXPIRE_MINUTES * 60, samesite="none", secure=True)
    return Token(token=token, token_type="Bearer")

@auth_router.get('/refresh', response_model=Token)
def refresh_token(request: Request, db: Session = Depends(get_db)):
    refresh_token = request.cookies.get("st.token")
    if not refresh_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=settings.ERRORS.get("INVALID_CREDENTIALS"))
    try:
        payload = verify_refresh_token(refresh_token)
        user = db.query(User).filter(User.id == payload.id).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=settings.ERRORS.get("INVALID_CREDENTIALS"))
        token = get_access_token(str(user.id))
        return Token(token=token, token_type="Bearer")
    except:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=settings.ERRORS.get("INVALID_CREDENTIALS"))
    
@auth_router.post('/logout')
def logout(response: Response):
    response.set_cookie(key="st.token", value="", httponly=True, max_age=10, samesite="none", secure=True)
    return {"message": "Logout Successful"}

@auth_router.get("/me", response_model=ProfileResponse)
def me(user: User = Depends(is_authenticated), db: Session = Depends(get_db)):
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=settings.ERRORS.get("INVALID_CREDENTIALS"))
    return user


















