from fastapi import HTTPException, status

from db.models.announcements import Announcement
from db.repository.announcements import AnnouncementRepository


class AnnouncementService:
    def __init__(self, announcement_repo: AnnouncementRepository):
        self.announcement_repo = announcement_repo

    def create(self, user_id: int, data: dict) -> Announcement:
        return self.announcement_repo.create(user_id, data)

    def get_all_query(self):
        return self.announcement_repo.get_all_paginated_query()

    def get_by_id(self, announcement_id: int) -> Announcement:
        announcement = self.announcement_repo.get_by_id(announcement_id)
        if not announcement:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"announcement with id: {announcement_id} was not found"
            )
        return announcement

    def update(self, announcement_id: int, update_data: dict) -> Announcement:
        self.get_by_id(announcement_id)  # raises 404 if not found
        return self.announcement_repo.update(announcement_id, update_data)

    def delete(self, announcement_id: int) -> None:
        self.get_by_id(announcement_id)  # raises 404 if not found
        self.announcement_repo.delete_by_id(announcement_id)
