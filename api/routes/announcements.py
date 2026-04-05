from typing import Annotated, Any

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi_pagination.ext.sqlalchemy import paginate
from fastapi_pagination.links import Page
from sqlalchemy.orm import Session

from api.api_models.announcements import AnnouncementCreate, AnnouncementResponse, AnnouncementUpdate
from db.database import get_db
from db.repository.announcements import AnnouncementRepository
from services.announcement_service import AnnouncementService
from utils.cloudinary import upload_file
from utils.permissions import is_admin, user_accepted
from utils.utils import is_image_file

announcement_route = APIRouter(tags=["Announcements"], prefix="/announcements")

DBSession = Annotated[Session, Depends(get_db)]
AdminUser = Annotated[Any, Depends(is_admin)]
AcceptedUser = Annotated[Any, Depends(user_accepted)]


def _service(db: Session) -> AnnouncementService:
    return AnnouncementService(AnnouncementRepository(db))


@announcement_route.post("/image", status_code=status.HTTP_200_OK)
async def upload_announcement_image(
    file: UploadFile = File(...),
    _admin: Any = Depends(is_admin),
):
    if not is_image_file(file.filename):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file format. Please upload an image.",
        )
    resource_type = "announcement"
    upload_folder = "announcements"
    url = await upload_file(file, resource_type, upload_folder)
    if not url:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload image",
        )
    return {"url": url}


@announcement_route.post("/", status_code=status.HTTP_201_CREATED, response_model=AnnouncementResponse)
def create_announcement(
    announcement: AnnouncementCreate,
    current_user: AdminUser,
    db: DBSession,
):
    return _service(db).create(current_user.id, announcement.model_dump())


@announcement_route.get("/", status_code=status.HTTP_200_OK, response_model=Page[AnnouncementResponse])
def get_announcements(current_user: AcceptedUser, db: DBSession):
    return paginate(db, _service(db).get_all_query())


@announcement_route.get("/{announcement_id}", status_code=status.HTTP_200_OK,
                        response_model=AnnouncementResponse)
def get_announcement_by_id(announcement_id: int, current_user: AcceptedUser, db: DBSession):
    return _service(db).get_by_id(announcement_id)


@announcement_route.put("/{announcement_id}", status_code=status.HTTP_200_OK,
                        response_model=AnnouncementResponse)
def update_announcement_by_id(
    announcement_id: int, announcement: AnnouncementUpdate,
    current_user: AdminUser, db: DBSession
):
    return _service(db).update(announcement_id, announcement.model_dump(exclude_unset=True))


@announcement_route.delete("/{announcement_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_announcement_by_id(
    announcement_id: int,
    db: DBSession,
    current_user: AdminUser,
):
    _service(db).delete(announcement_id)
