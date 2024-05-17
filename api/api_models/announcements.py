from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import Optional


class AnnouncementBase(BaseModel):
    title: str
    content: str
    image_url: Optional[str] = Field(None)


class AnnouncementCreate(AnnouncementBase):
    pass


class AnnouncementResponse(AnnouncementBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AnnouncementUpdate(BaseModel):
    title: Optional[str]
    content: Optional[str]

    model_config = ConfigDict(from_attributes=True)
