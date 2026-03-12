from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from api.api_models.user import (
    ForgotPasswordRequest, ProfileResponse, RefreshTokenRequest,
    ResetPasswordRequest, Token, UserResponse, UserSignUp
)
from db.database import get_db
from db.repository.email_templates import EmailTemplateRepository
from db.repository.endpoints import EndpointRepository
from db.repository.technical_tasks import TechnicalTaskRepository
from db.repository.users import UserRepository
from services.auth_service import AuthService
from services.endpoint_service import EndpointService
from utils.permissions import is_authenticated

auth_router = APIRouter(tags=["Auth"], prefix="/users")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def _auth_service(db: Session) -> AuthService:
    return AuthService(UserRepository(db), TechnicalTaskRepository(db), EmailTemplateRepository(db))


def _endpoint_service(db: Session) -> EndpointService:
    return EndpointService(EndpointRepository(db))


@auth_router.post("/register", status_code=status.HTTP_201_CREATED, response_model=UserResponse)
async def signup(user: UserSignUp, db: Session = Depends(get_db)):
    _endpoint_service(db).is_signup_open()
    return await _auth_service(db).register(user)


@auth_router.post("/login", response_model=Token)
def login(response: Response, user: OAuth2PasswordRequestForm = Depends(),
          db: Session = Depends(get_db)):
    return _auth_service(db).login(user.username, user.password)


@auth_router.post("/refresh", response_model=Token)
def refresh_token(refresh_token_data: RefreshTokenRequest, db: Session = Depends(get_db)):
    return _auth_service(db).refresh(refresh_token_data.refresh_token)


@auth_router.post("/logout")
def logout(response: Response):
    response.set_cookie(key="st.token", value="", httponly=True, max_age=10,
                        samesite="none", secure=True)
    return {"message": "Logout Successful"}


@auth_router.get("/me", response_model=ProfileResponse)
def me(user=Depends(is_authenticated), db: Session = Depends(get_db)):
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Credentials")
    return user


@auth_router.post("/forgot-password")
async def forgot_password(request: ForgotPasswordRequest, db: Session = Depends(get_db)):
    return await _auth_service(db).forgot_password(request.email)


@auth_router.post("/reset-password")
def reset_password(request: ResetPasswordRequest, db: Session = Depends(get_db)):
    return _auth_service(db).reset_password(request.token, request.new_password)
