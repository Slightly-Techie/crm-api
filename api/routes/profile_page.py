from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, status, File
from fastapi_pagination.links import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import desc
from sqlalchemy.orm import Session

from api.api_models.email_template import EmailTemplateName
from api.api_models.user import ProfileUpdate, ProfileResponse
from core.config import settings
from db.database import get_db
from db.models.email_template import EmailTemplate
from db.models.skills import Skill
from db.models.users import User
from utils.mail_service import send_email, read_html_file
from utils.oauth2 import get_current_user
from utils.permissions import is_admin
from utils.enums import UserStatus
from utils.s3 import upload_file_to_s3
from utils.utils import is_image_file
from db.models import users_skills

profile_route = APIRouter(tags=["User"], prefix="/users")


@profile_route.get("/profile/{user_id}", response_model=ProfileResponse)
async def get_profile(user_id: int, db: Session = Depends(get_db)):
    user_details = db.query(User).filter(User.id == user_id).first()
    if user_details:
        return user_details
    else:
        raise HTTPException(
            status_code=404, detail=settings.ERRORS.get("INVALID ID"))


@profile_route.put("/profile", response_model=ProfileResponse)
async def update_profile(
    userDetails: ProfileUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    user_exists = db.query(User).filter(User.id == current_user.id)
    try:
        if user_exists.first():
            # convert json into a python dict and exclude fields not specified
            update_data = userDetails.dict(exclude_unset=True)
            user_exists.update(update_data)

            db.commit()

            return user_exists.first()
        else:
            raise HTTPException(
                status_code=404, detail=settings.ERRORS.get("INVALID ID"))
    except Exception:
        raise HTTPException(
            status_code=400, detail=settings.ERRORS.get("UNKNOWN ERROR"))


@profile_route.get("/", response_model=Page[ProfileResponse])
def get_all_profile(skill: str = Query(None, title="Skill", description="The skill to filter users"),
                    stack: str = Query(None, title="Stack", description="The stack to filter users"),
                    active: Optional[bool] = None, p: Optional[str] = None,
                    db: Session = Depends(get_db)):
    query = db.query(User)

    if skill:
        query = query.join(users_skills.UserSkill).join(Skill).filter(Skill.name == skill.capitalize())

    if stack:
        query = query.filter(User.stack.has(name=stack.capitalize()))

    if active is not None:
        query = query.filter(User.is_active == active)

    if p:
        query = query.filter(
            User.username.ilike(f"%{p}%") | User.first_name.ilike(f"%{p}%") | User.last_name.ilike(f"%{p}%"))
        if not query.all():
            raise HTTPException(status_code=404, detail="No users found")

    users = paginate(query.order_by(desc(User.created_at)))

    return users

    # return paginate(db, select(User).order_by(desc(User.created_at)))


@profile_route.put("/profile/{user_id}/activate", response_model=ProfileResponse, status_code=status.HTTP_200_OK)
def update_profile_status(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(is_admin)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=404, detail=settings.ERRORS.get("INVALID ID"))
    if user.is_active:
        raise HTTPException(
            status_code=400, detail=settings.ERRORS.get("USER ALREADY ACTIVE"))
    user.is_active = True
    db.commit()
    return user


@profile_route.get("/user_info", response_model=dict)
def get_user_info(email: str, db: Session = Depends(get_db)):
    user_details = db.query(User).filter(User.email == email.lower()).first()
    if user_details:
        return {
            "status": 200,
            "data": {
                "first_name": user_details.first_name,
                "last_name": user_details.last_name,
                "phone_number": user_details.phone_number
            }
        }
    else:
        raise HTTPException(status_code=404, detail="USER NOT FOUND")


@profile_route.put("/profile/{user_id}/status", response_model=ProfileResponse, status_code=status.HTTP_200_OK)
async def update_user_status(user_id: int, new_status: UserStatus, db: Session = Depends(get_db),
                       current_user: User = Depends(is_admin)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=404, detail=settings.ERRORS.get("USER NOT FOUND"))

    user.status = new_status
    db.commit()

    if new_status == UserStatus.ACCEPTED or new_status == UserStatus.REJECTED:
        email_template = db.query(EmailTemplate).filter(EmailTemplate.template_name == new_status.value).first()
        if email_template:
            html_content = email_template.html_content.format(user.username)
            await send_email(email_template.subject, user.email, html_content)
    return user


@profile_route.patch("/profile/avatar", response_model=ProfileResponse, status_code=status.HTTP_200_OK)
async def update_avi(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db), file: UploadFile = File(...)
):
    if not is_image_file(file.filename):
        raise HTTPException(status_code=400, detail="Invalid file format. Please upload an image.")

    url = await upload_file_to_s3(file, current_user.username, "profile")

    if not url:
        raise HTTPException(status_code=500, detail="Failed to upload profile picture")

    current_user.profile_pic_url = url
    db.commit()
    db.refresh(current_user)

    return current_user
