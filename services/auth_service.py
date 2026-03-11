import logging

from fastapi import HTTPException, status

logger = logging.getLogger(__name__)

from api.api_models.user import Token, UserSignUp
from core.config import settings
from db.models.users import User
from db.repository.email_templates import EmailTemplateRepository
from db.repository.technical_tasks import TechnicalTaskRepository
from db.repository.users import UserRepository
from utils.enums import UserStatus
from utils.mail_service import send_applicant_task, send_password_reset_email
from utils.oauth2 import (
    create_reset_token, get_access_token, get_refresh_token,
    verify_refresh_token, verify_reset_token
)
from utils.utils import get_key_by_value, get_password_hash, verify_password


class AuthService:
    def __init__(self, user_repo: UserRepository,
                 task_repo: TechnicalTaskRepository,
                 email_template_repo: EmailTemplateRepository):
        self.user_repo = user_repo
        self.task_repo = task_repo
        self.email_template_repo = email_template_repo

    async def register(self, user_data: UserSignUp) -> User:
        user_data.email = user_data.email.lower()

        if user_data.password != user_data.password_confirmation:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=settings.ERRORS.get("PASSWORD_MATCH_DETAIL")
            )
        if self.user_repo.get_by_username(user_data.username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=settings.ERRORS.get("USERNAME_EXISTS")
            )
        if self.user_repo.get_by_email(user_data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=settings.ERRORS.get("USER_EXISTS")
            )

        user_data.password = get_password_hash(user_data.password)
        new_user = self.user_repo.create(user_data)

        try:
            task = self.task_repo.get_by_stack_and_level(
                new_user.stack_id,
                get_key_by_value(new_user.years_of_experience)
            )
            if task:
                await send_applicant_task(new_user.email, new_user.first_name, task.content)
                self.user_repo.update_status(new_user, UserStatus.CONTACTED)
        except Exception as e:
            # User is already persisted; log the failure but don't surface it to the caller
            import logging
            logging.getLogger(__name__).error("Failed to send applicant task: %s", e)

        return new_user

    def login(self, email: str, password: str) -> Token:
        email = email.lower()
        user = self.user_repo.get_by_email(email)
        if not user or not verify_password(password, user.password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=settings.ERRORS.get("INVALID_CREDENTIALS")
            )
        return Token(
            token=get_access_token(str(user.id)),
            refresh_token=get_refresh_token(str(user.id)),
            token_type="Bearer",
            is_active=user.is_active,
            user_status=user.status
        )

    def refresh(self, refresh_token: str) -> Token:
        if not refresh_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=settings.ERRORS.get("INVALID_CREDENTIALS")
            )
        try:
            payload = verify_refresh_token(refresh_token)
            user = self.user_repo.get_by_id(int(payload.id))
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=settings.ERRORS.get("INVALID_CREDENTIALS")
                )
            return Token(
                token=get_access_token(str(user.id)),
                refresh_token=refresh_token,
                token_type="Bearer",
                is_active=user.is_active,
                user_status=user.status
            )
        except HTTPException:
            raise
        except Exception as e:
            logger.error("Token refresh failed: %s", e)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=settings.ERRORS.get("INVALID_CREDENTIALS")
            )

    async def forgot_password(self, email: str) -> dict:
        email = email.lower()
        user = self.user_repo.get_by_email(email)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        reset_token = create_reset_token(email)
        email_template = self.email_template_repo.get_by_name("PASSWORD RESET")
        return await send_password_reset_email(email, reset_token, user.username, email_template)

    def reset_password(self, token: str, new_password: str) -> dict:
        try:
            email = verify_reset_token(token).lower()
            user = self.user_repo.get_by_email(email)
            if not user:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
            self.user_repo.update_password(user, get_password_hash(new_password))
            return {"message": "Password reset successful"}
        except HTTPException:
            raise
        except Exception as e:
            logger.error("Password reset failed: %s", e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while resetting the password."
            )
