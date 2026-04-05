from fastapi import APIRouter, Depends, File, Form, UploadFile, status
from fastapi_pagination.ext.sqlalchemy import paginate
from fastapi_pagination.links import Page
from sqlalchemy.orm import Session

from api.api_models.user import FeedUpdate, Feeds
from db.database import get_db
from db.repository.feeds import FeedRepository
from services.feed_service import FeedService
from utils.permissions import user_accepted

feed_route = APIRouter(tags=["Feed"], prefix="/feed")


def _service(db: Session) -> FeedService:
    return FeedService(FeedRepository(db))


@feed_route.post("/", status_code=status.HTTP_201_CREATED, response_model=Feeds)
async def create_feed(content: str = Form(...), feed_pic_url: UploadFile = File(None),
                      current_user=Depends(user_accepted), db: Session = Depends(get_db)):
    return await _service(db).create_feed(current_user.id, current_user.username, content, feed_pic_url)


@feed_route.put("/{feed_id}", status_code=status.HTTP_200_OK, response_model=Feeds)
def update_feed_by_id(feed_id: int, updated_feed: FeedUpdate,
                      db: Session = Depends(get_db), current_user=Depends(user_accepted)):
    return _service(db).update_feed(feed_id, current_user.id, updated_feed.model_dump())


@feed_route.delete("/{feed_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_feed_by_id(feed_id: int, db: Session = Depends(get_db),
                      current_user=Depends(user_accepted)):
    _service(db).delete_feed(feed_id, current_user.id)


@feed_route.get("/{feed_id}", status_code=status.HTTP_200_OK, response_model=Feeds)
def get_feed_by_id(feed_id: int, db: Session = Depends(get_db),
                   current_user=Depends(user_accepted)):
    return _service(db).get_feed(feed_id)


@feed_route.get("/", response_model=Page[Feeds])
def get_all_feeds(db: Session = Depends(get_db), current_user=Depends(user_accepted)):
    return paginate(db, _service(db).get_all_query())
