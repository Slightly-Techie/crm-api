from fastapi import APIRouter, Depends, HTTPException, status, Response

from sqlalchemy.orm import Session

from utils.utils import get_password_hash

from db.models.users import User

from db.database import get_db
from db.repository.users import create_new_user, update_user

from api.api_models.user import ProfileResponse, RefreshTokenRequest, UserSignUp, Token, ForgotPasswordRequest, ResetPasswordRequest
from api.api_models.user import UserResponse
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from utils.utils import verify_password
from utils.oauth2 import get_access_token, get_refresh_token, verify_refresh_token, create_reset_token, verify_reset_token
from utils.permissions import is_authenticated
from core.config import settings
from utils.mail_service import send_reset_password_email


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

    return Token(
        token=token,
        refresh_token=refresh_token,
        token_type="Bearer",
        is_active=user_data.is_active
    )

@auth_router.post('/refresh', response_model=Token)
def refresh_token(refresh_token_data: RefreshTokenRequest, db: Session = Depends(get_db)):
    refresh_token = refresh_token_data.refresh_token
    if not refresh_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=settings.ERRORS.get("INVALID_CREDENTIALS"))
    try:
        payload = verify_refresh_token(refresh_token)
        user = db.query(User).filter(User.id == payload.id).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=settings.ERRORS.get("INVALID_CREDENTIALS"))
        token = get_access_token(str(user.id))
        return Token(
        token=token,
        refresh_token=refresh_token,
        token_type="Bearer",
        is_active=user.is_active
    )
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


@auth_router.post('/forgot-password')
def forgot_password(request: ForgotPasswordRequest, db: Session = Depends(get_db)):
    email = request.email
    user = db.query(User).filter(User.email == email).first()
    
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    reset_token = create_reset_token(email)
    send_reset_password_email(email, reset_token) 
    return {"msg": "Reset token sent to email"}

@auth_router.post('/reset-password')
# url?token=token&new_password=new_password
# When you use py
def reset_password(request: ResetPasswordRequest, db: Session = Depends(get_db)) -> dict:
    try:
        email = verify_reset_token(request.token) 
        user = db.query(User).filter(User.email == email).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        hashed_password = get_password_hash(request.new_password)
        user.password = hashed_password

        db.commit()  # Save the updated user's password to the database

        return {"message": "Password reset successful"}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An error occurred while resetting the password.")
