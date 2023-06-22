from pydantic import BaseModel
from typing import Dict, Optional

class AnnouncementBase(BaseModel):
    title: str
    content: str
    announcement_pic_url: str

class AnnouncementCreate(AnnouncementBase):
    pass

class Announcement(AnnouncementBase):
    id: int

class AnnouncementUpdate(AnnouncementBase):
    title: Optional[str]
    content: Optional[str]

class PaginatedResponse(BaseModel):
    items: list[Announcement]
    total: int
    page: int
    size: int
    pages: int
    links: Optional[Dict[str, Optional[str]]]