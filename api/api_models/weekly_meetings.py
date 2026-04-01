from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import Optional


class WeeklyMeetingBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    meeting_url: str = Field(..., min_length=1)
    description: Optional[str] = None
    scheduled_time: Optional[datetime] = None
    recurrence: Optional[str] = Field(None, pattern="^(weekly|biweekly|monthly|none)$")


class WeeklyMeetingCreate(WeeklyMeetingBase):
    pass


class WeeklyMeetingUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    meeting_url: Optional[str] = Field(None, min_length=1)
    description: Optional[str] = None
    is_active: Optional[bool] = None
    scheduled_time: Optional[datetime] = None
    recurrence: Optional[str] = Field(None, pattern="^(weekly|biweekly|monthly|none)$")


class WeeklyMeetingResponse(WeeklyMeetingBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    created_by: int
    model_config = ConfigDict(from_attributes=True)
