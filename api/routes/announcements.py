from fastapi import Depends, HTTPException, APIRouter, status
from sqlalchemy.orm import Session
from sqlalchemy import select
from db.database import get_db
from db.models.announcements import Announcement
from fastapi_pagination.links import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from api.api_models.announcements import AnnouncementCreate, AnnouncementResponse, AnnouncementUpdate
from utils.permissions import is_admin


announcement_route = APIRouter(tags=["Announcements"], prefix="/announcements")


@announcement_route.post("/", status_code=status.HTTP_201_CREATED, response_model=AnnouncementResponse)
def create_announcement(
    announcement: AnnouncementCreate, current_user=Depends(is_admin), db: Session = Depends(get_db)
):
    new_announcement = Announcement(user_id=current_user.id, **announcement.model_dump())

    db.add(new_announcement)
    db.commit()
    db.refresh(new_announcement)
    return new_announcement


@announcement_route.get("/", status_code=status.HTTP_200_OK, response_model=Page[AnnouncementResponse])
def get_announcements(db: Session = Depends(get_db)):
    return paginate(db, select(Announcement).order_by(Announcement.created_at))


@announcement_route.get("/{announcement_id}", status_code=status.HTTP_200_OK, response_model=AnnouncementResponse)
def get_announcement_by_id(announcement_id: int, db: Session = Depends(get_db)):
    announcement_query = db.query(Announcement).filter(Announcement.id == announcement_id)
    announcement = announcement_query.first()
    if not announcement:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=f"announcement with id: {announcement_id} was not found")

    return announcement


@announcement_route.put("/{announcement_id}", status_code=status.HTTP_200_OK, response_model=AnnouncementResponse)
def update_announcement_by_id(
    announcement_id: int, announcement: AnnouncementUpdate,
    current_user=Depends(is_admin), db: Session = Depends(get_db)
):
    announcement_query = db.query(Announcement).filter(Announcement.id == announcement_id)
    old_announcement = announcement_query.first()
    if not old_announcement:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=f"announcement with id: {announcement_id} was not found")

    announcement_query.update(announcement.dict())
    db.commit()

    return announcement_query.first()


@announcement_route.delete("/{announcement_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_announcement_by_id(announcement_id: int, db: Session = Depends(get_db), current_user=Depends(is_admin)):
    announcement_query = db.query(Announcement).filter(Announcement.id == announcement_id)
    announcement = announcement_query.first()
    if not announcement:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=f"announcement with id: {announcement_id} was not found")

    announcement_query.delete()
    db.commit()
