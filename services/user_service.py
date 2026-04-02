import html
from typing import Optional

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.exc import ProgrammingError

from core.config import settings
from db.models.users import User
from db.repository.email_templates import EmailTemplateRepository
from db.repository.technical_tasks import TechnicalTaskSubmissionRepository
from db.repository.users import UserRepository
from utils.enums import UserStatus
from utils.mail_service import send_email
from utils.cloudinary import upload_file
from utils.utils import is_image_file


class UserService:
    def __init__(self, user_repo: UserRepository,
                 email_template_repo: EmailTemplateRepository,
                 submission_repo: TechnicalTaskSubmissionRepository):
        self.user_repo = user_repo
        self.email_template_repo = email_template_repo
        self.submission_repo = submission_repo

    def get_profile(self, user_id: int) -> User:
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=settings.ERRORS.get("INVALID ID"))
        submission = self.submission_repo.get_by_user_id(user_id)
        user.technical_task = submission if submission else None
        return user

    def update_profile(self, user_id: int, update_data: dict) -> User:
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=settings.ERRORS.get("INVALID ID"))
        updated = self.user_repo.update_by_id(user_id, update_data)
        if not updated:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail=settings.ERRORS.get("UNKNOWN ERROR"))
        return updated

    def build_search_query(self, skill: Optional[str], stack: Optional[str],
                           active: Optional[bool], p: Optional[str]):
        return self.user_repo.build_search_query(skill, stack, active, p)

    def activate_user(self, user_id: int) -> User:
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=settings.ERRORS.get("INVALID ID"))
        if user.is_active:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail=settings.ERRORS.get("USER ALREADY ACTIVE"))
        return self.user_repo.activate(user)

    def get_user_info(self, email: str) -> dict:
        user = self.user_repo.get_by_email(email.lower())
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="USER NOT FOUND")
        return {
            "status": 200,
            "data": {
                "first_name": user.first_name,
                "last_name": user.last_name,
                "phone_number": user.phone_number
            }
        }

    async def update_user_status(self, user_id: int, new_status: UserStatus) -> User:
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=settings.ERRORS.get("INVALID ID"))
        self.user_repo.update_status(user, new_status)

        # Activate user when status becomes ACCEPTED
        if new_status == UserStatus.ACCEPTED and not user.is_active:
            self.user_repo.activate(user)

        if new_status in (UserStatus.ACCEPTED, UserStatus.REJECTED):
            try:
                template = self.email_template_repo.get_by_name(new_status.value)
            except ProgrammingError:
                # Keep status changes working even if the email_templates migration has not run yet.
                self.email_template_repo.db.rollback()
                template = None
            if template:
                html_content = template.html_content.format(html.escape(user.username))
                await send_email(template.subject, user.email, html_content)
        return user

    async def update_avatar(self, user: User, file: UploadFile) -> User:
        if not is_image_file(file.filename):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Invalid file format. Please upload an image.")
        url = await upload_file(file, user.username, "profile")
        if not url:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Failed to upload profile picture")
        return self.user_repo.update_avatar(user, url)
