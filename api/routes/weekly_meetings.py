from fastapi import APIRouter, Depends, status
from fastapi_pagination.ext.sqlalchemy import paginate
from fastapi_pagination.links import Page
from sqlalchemy.orm import Session

from api.api_models.weekly_meetings import (
    WeeklyMeetingCreate,
    WeeklyMeetingResponse,
    WeeklyMeetingUpdate
)
from db.database import get_db
from db.repository.weekly_meetings import WeeklyMeetingRepository
from services.weekly_meeting_service import WeeklyMeetingService
from utils.permissions import is_admin, user_accepted

weekly_meeting_route = APIRouter(tags=["Weekly Meetings"], prefix="/weekly-meetings")


def _service(db: Session) -> WeeklyMeetingService:
    return WeeklyMeetingService(WeeklyMeetingRepository(db))


@weekly_meeting_route.post("/", status_code=status.HTTP_201_CREATED, response_model=WeeklyMeetingResponse)
def create_meeting(
    meeting: WeeklyMeetingCreate,
    current_user=Depends(is_admin),
    db: Session = Depends(get_db)
):
    """Create a new weekly meeting - Admin only"""
    return _service(db).create(meeting.model_dump(), current_user.id)


@weekly_meeting_route.get("/active", status_code=status.HTTP_200_OK, response_model=WeeklyMeetingResponse | None)
def get_active_meeting(db: Session = Depends(get_db), current_user=Depends(user_accepted)):
    """Get the current active meeting - Accepted users"""
    return _service(db).get_active()


@weekly_meeting_route.get("/", status_code=status.HTTP_200_OK, response_model=Page[WeeklyMeetingResponse])
def get_all_meetings(db: Session = Depends(get_db), current_user=Depends(user_accepted)):
    """Get all meetings - Accepted users"""
    return paginate(db, _service(db).get_all_query())


@weekly_meeting_route.get("/{meeting_id}", status_code=status.HTTP_200_OK, response_model=WeeklyMeetingResponse)
def get_meeting_by_id(
    meeting_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(user_accepted)
):
    """Get a specific meeting by ID"""
    return _service(db).get_by_id(meeting_id)


@weekly_meeting_route.put("/{meeting_id}", status_code=status.HTTP_200_OK, response_model=WeeklyMeetingResponse)
def update_meeting(
    meeting_id: int,
    meeting: WeeklyMeetingUpdate,
    current_user=Depends(is_admin),
    db: Session = Depends(get_db)
):
    """Update a meeting - Admin only"""
    return _service(db).update(meeting_id, meeting.model_dump(exclude_unset=True))


@weekly_meeting_route.delete("/{meeting_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_meeting(
    meeting_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(is_admin)
):
    """Delete a meeting - Admin only"""
    _service(db).delete(meeting_id)
