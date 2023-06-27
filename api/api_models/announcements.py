from pydantic import BaseModel, Field
from datetime import datetime
from typing import Dict, Optional

class AnnouncementBase(BaseModel):
    title: str
    content: str
    image_url: Optional[str] = Field(None)

class AnnouncementCreate(AnnouncementBase):
    pass

class AnnouncementResponse(AnnouncementBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True

class AnnouncementUpdate(BaseModel):
    title: Optional[str]
    content: Optional[str]

    class Config:
        orm_mode = True

class PaginatedResponse(BaseModel):
    items: list[AnnouncementResponse]
    total: int
    page: int
    size: int
    pages: int
    links: Optional[Dict[str, Optional[str]]]