from fastapi import Depends, HTTPException, APIRouter, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, select
from db.database import get_db
from utils.oauth2 import get_current_user
from db.models.announcements import Announcement
from api.api_models.announcements import AnnouncementCreate, AnnouncementResponse, PaginatedResponse, AnnouncementUpdate
from utils.permissions import is_admin


announcement_route = APIRouter(tags=["Announcements"], prefix="/announcements")

@announcement_route.post("/", status_code=status.HTTP_201_CREATED, response_model=AnnouncementResponse)
def create_announcement(announcement: AnnouncementCreate, current_user = Depends(is_admin), db: Session = Depends(get_db)):
    new_announcement = Announcement(user_id=current_user.id, **announcement.dict())

    db.add(new_announcement)
    db.commit()
    db.refresh(new_announcement)
    return new_announcement

@announcement_route.get("/", status_code=status.HTTP_200_OK, response_model=PaginatedResponse)
def get_announcements(limit: int = Query(default=3, ge=1, le=50), page: int = Query(default=1, ge=1), db: Session = Depends(get_db)):
    announcements_query = db.query(Announcement).order_by(desc(Announcement.created_at))
    total_announcements = announcements_query.count()

    pages = (total_announcements - 1) // limit + 1
    offset = limit * (page - 1)
    announcements = announcements_query.limit(limit).offset(offset).all()

    next_page = None
    prev_page = None

    if page < pages:
        next_page = f"/api/v1/announcements/?limit={limit}&page={page + 1}"
    
    if page > 1:
        prev_page = f"/api/v1/announcements/?limit={limit}&page={page - 1}"

    links = {
        "first": f"/api/v1/announcements/?limit={limit}&page=1",
        "last": f"/api/v1/announcements/?limit={limit}&page={pages}",
        "self": f"/api/v1/announcements/?limit={limit}&page={page}",
        "next": next_page,
        "prev": prev_page,
    }

    return PaginatedResponse(
        items=announcements,
        total=total_announcements,
        page=page,
        size=limit,
        pages=pages,
        links=links
    )

@announcement_route.get("/{announcement_id}", status_code=status.HTTP_200_OK, response_model=AnnouncementResponse)
def get_announcement_by_id(announcement_id: int, db: Session = Depends(get_db)):
    announcement_query = db.query(Announcement).filter(Announcement.id == announcement_id)
    announcement = announcement_query.first()
    if not announcement:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=f"announcement with id: {announcement_id} was not found")
    
    return announcement

@announcement_route.put("/{announcement_id}", status_code=status.HTTP_200_OK, response_model=AnnouncementResponse)
def update_announcement_by_id(announcement_id: int, announcement: AnnouncementUpdate, current_user = Depends(is_admin), db: Session = Depends(get_db)):
    announcement_query = db.query(Announcement).filter(Announcement.id == announcement_id)
    old_announcement = announcement_query.first()
    if not old_announcement:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=f"announcement with id: {announcement_id} was not found")
    
    announcement_query.update(announcement.dict())
    db.commit()

    return announcement_query.first()

@announcement_route.delete("/{announcement_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_announcement_by_id(announcement_id: int, db: Session = Depends(get_db),current_user = Depends(is_admin)):
    announcement_query = db.query(Announcement).filter(Announcement.id == announcement_id)
    announcement = announcement_query.first()
    if not announcement:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=f"announcement with id: {announcement_id} was not found")
    
    announcement_query.delete()
    db.commit()