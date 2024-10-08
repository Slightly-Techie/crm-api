from fastapi import APIRouter, Depends, HTTPException, status, Response, Request

from sqlalchemy.orm import Session

from utils.utils import get_password_hash

from db.models.users import User
from db.models.email_template import EmailTemplate
from api.api_models.email_template import EmailTemplateName
from db.database import get_db
from db.repository.users import create_new_user

from api.api_models.user import (
    ProfileResponse, RefreshTokenRequest, UserSignUp, Token, ForgotPasswordRequest, ResetPasswordRequest
)
from db.models.technical_task import TechnicalTask
from api.api_models.user import UserResponse
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from utils.utils import verify_password
from utils.oauth2 import (
    get_access_token, get_refresh_token, verify_refresh_token, create_reset_token, verify_reset_token
)
from utils.permissions import is_authenticated
from core.config import settings
from utils.mail_service import send_password_reset_email
from utils.mail_service import send_applicant_task
from utils.utils import get_key_by_value
from utils.enums import UserStatus
# from utils.endpoints_status import endpoint_status_dependency
from db.models.endpoints import Endpoints


auth_router = APIRouter(tags=["Auth"], prefix="/users")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@auth_router.post('/register', status_code=status.HTTP_201_CREATED, response_model=UserResponse)
async def signup(user: UserSignUp, db: Session = Depends(get_db)):
    endpoint_query = db.query(Endpoints).filter(Endpoints.endpoint == "signup").first()
    if endpoint_query:
        if not endpoint_query.status:
            raise HTTPException(status.HTTP_403_FORBIDDEN, detail="Signup is closed")
        else:
            user.email = user.email.lower()
            user_name = db.query(User).filter(User.username == user.username).first()
            if user_name:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                    detail=settings.ERRORS.get("USERNAME_EXISTS"))

            user_data = db.query(User).filter(User.email == user.email).first()
            if user_data:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                    detail=settings.ERRORS.get("USER_EXISTS"))
            hash_passwd = get_password_hash(user.password)

            if user.password != user.password_confirmation:
                print("Passwords do not match")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail=settings.ERRORS.get("PASSWORD_MATCH_DETAIL"))

            user.password = hash_passwd
            new_user = create_new_user(user, db)

            try:
                task = db.query(TechnicalTask).filter(
                    TechnicalTask.stack_id == new_user.stack_id,
                    TechnicalTask.experience_level == get_key_by_value(new_user.years_of_experience)
                ).first()
                if task:
                    await send_applicant_task(
                        new_user.email, new_user.first_name, task.content
                        )
                    db.query(User).filter(User.id == new_user.id).update(
                        {"status": UserStatus.CONTACTED}
                        )
                    db.commit()
                else:
                    print("Task not found")
                    pass
            except Exception as user_reg_e:
                print(user_reg_e)
                pass

            return new_user


@auth_router.post('/login', response_model=Token)
def login(response: Response, user: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user.username = user.username.lower()
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
        is_active=user_data.is_active,
        user_status=user_data.status
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
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail=settings.ERRORS.get("INVALID_CREDENTIALS"))
        token = get_access_token(str(user.id))
        return Token(
            token=token,
            refresh_token=refresh_token,
            token_type="Bearer",
            is_active=user.is_active,
            user_status=user.status
        )
    except Exception:
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
async def forgot_password(request: ForgotPasswordRequest, requested: Request, db: Session = Depends(get_db)):
    """
    Send a reset password email to the user.

    Args:
        request (ForgotPasswordRequest): The request containing the user's email.
        db (Session, optional): The database session. Defaults to Depends(get_db).

    Returns:
        JSONResponse: A response indicating the result of sending the reset password email.
    """
    email = request.email.lower()
    user = db.query(User).filter(User.email == email).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    reset_token = create_reset_token(email)
    try:
        email_template = db.query(EmailTemplate).filter(
            EmailTemplate.template_name == EmailTemplateName.password_reset).first()
    except Exception:
        email_template = None
    result = await send_password_reset_email(
        email, reset_token, user.username, email_template)
    return result


@auth_router.post('/reset-password')
def reset_password(request: ResetPasswordRequest, db: Session = Depends(get_db)) -> dict:
    """
    Reset the user's password with a valid reset token.

    Args:
        request (ResetPasswordRequest): The request containing the reset token and new password.
        db (Session, optional): The database session. Defaults to Depends(get_db).

    Returns:
        dict: A message indicating the result of the password reset.
    """
    try:
        email = verify_reset_token(request.token)
        email = email.lower()
        user = db.query(User).filter(User.email == email).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        hashed_password = get_password_hash(request.new_password)
        user.password = hashed_password

        db.commit()

        return {"message": "Password reset successful"}
    except HTTPException as e:
        raise e
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An error occurred while resetting the password.")
