from typing import Optional

from fastapi import HTTPException, UploadFile, status

from db.models.feeds import Feed
from db.repository.feeds import FeedRepository
from utils.cloudinary import upload_file
from utils.utils import is_image_file


class FeedService:
    def __init__(self, feed_repo: FeedRepository):
        self.feed_repo = feed_repo

    async def create_feed(self, user_id: int, username: str, content: str,
                          file: Optional[UploadFile]) -> Feed:
        image_url = None
        if file:
            if not is_image_file(file.filename):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid file format. Please upload an image."
                )
            image_url = await upload_file(file, username, "feed")
        return self.feed_repo.create(user_id, content, image_url)

    def update_feed(self, feed_id: int, user_id: int, update_data: dict) -> Feed:
        feed = self.feed_repo.get_by_id(feed_id)
        if not feed:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"feed with id: {feed_id} was not found"
            )
        if feed.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not authorized to perform this request"
            )
        return self.feed_repo.update(feed_id, update_data)

    def delete_feed(self, feed_id: int, user_id: int) -> None:
        feed = self.feed_repo.get_by_id(feed_id)
        if not feed:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"feed with id: {feed_id} was not found"
            )
        if feed.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not authorized to perform this request"
            )
        self.feed_repo.delete_by_query(feed_id)

    def get_feed(self, feed_id: int) -> Feed:
        feed = self.feed_repo.get_by_id(feed_id)
        if not feed:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"feed with id: {feed_id} was not found"
            )
        return feed

    def get_all_query(self):
        return self.feed_repo.get_all_paginated_query()
