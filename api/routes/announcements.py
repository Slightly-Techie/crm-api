from typing import Annotated, Any

from fastapi import APIRouter, Depends, status
from fastapi_pagination.ext.sqlalchemy import paginate
from fastapi_pagination.links import Page
from sqlalchemy.orm import Session

from api.api_models.announcements import AnnouncementCreate, AnnouncementResponse, AnnouncementUpdate
from db.database import get_db
from db.repository.announcements import AnnouncementRepository
from services.announcement_service import AnnouncementService
from utils.permissions import is_admin

announcement_route = APIRouter(tags=["Announcements"], prefix="/announcements")

DBSession = Annotated[Session, Depends(get_db)]
AdminUser = Annotated[Any, Depends(is_admin)]


def _service(db: Session) -> AnnouncementService:
    return AnnouncementService(AnnouncementRepository(db))


@announcement_route.post("/", status_code=status.HTTP_201_CREATED, response_model=AnnouncementResponse)
def create_announcement(
    announcement: AnnouncementCreate,
    current_user: AdminUser,
    db: DBSession,
):
    return _service(db).create(current_user.id, announcement.model_dump())


@announcement_route.get("/", status_code=status.HTTP_200_OK, response_model=Page[AnnouncementResponse])
def get_announcements(db: DBSession):
    return paginate(db, _service(db).get_all_query())


@announcement_route.get("/{announcement_id}", status_code=status.HTTP_200_OK,
                        response_model=AnnouncementResponse)
def get_announcement_by_id(announcement_id: int, db: DBSession):
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
