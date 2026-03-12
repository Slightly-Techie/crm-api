from typing import Optional

from sqlalchemy import desc, select

from db.models.feeds import Feed
from db.repository.base import BaseRepository


class FeedRepository(BaseRepository):
    model = Feed

    def create(self, user_id: int, content: str, image_url: Optional[str]) -> Feed:
        feed = Feed(user_id=user_id, content=content, feed_pic_url=image_url)
        return self.save(feed)

    def get_all_paginated_query(self):
        return select(Feed).order_by(desc(Feed.created_at))

    def update(self, feed_id: int, update_data: dict) -> Feed:
        query = self.db.query(Feed).filter(Feed.id == feed_id)
        query.update(update_data)
        self.db.commit()
        return query.first()

    def delete_by_query(self, feed_id: int) -> None:
        self.db.query(Feed).filter(Feed.id == feed_id).delete()
        self.db.commit()
