from sqlalchemy import select

from db.models.announcements import Announcement
from db.repository.base import BaseRepository


class AnnouncementRepository(BaseRepository):
    model = Announcement

    def create(self, user_id: int, data: dict) -> Announcement:
        announcement = Announcement(user_id=user_id, **data)
        return self.save(announcement)

    def get_all_paginated_query(self):
        return select(Announcement).order_by(Announcement.created_at)

    def update(self, announcement_id: int, update_data: dict) -> Announcement:
        query = self.db.query(Announcement).filter(Announcement.id == announcement_id)
        query.update(update_data)
        self.db.commit()
        return query.first()

    def delete_by_id(self, announcement_id: int) -> None:
        self.db.query(Announcement).filter(Announcement.id == announcement_id).delete()
        self.db.commit()
