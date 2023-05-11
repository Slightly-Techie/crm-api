from fastapi import Depends, HTTPException, APIRouter, status
from sqlalchemy.orm import Session
from db.database import get_db
from utils.oauth2 import get_current_user
from db.models.users import User, Feed
from api.api_models.user import FeedCreate, FeedOut, FeedUpdate, Feeds


feed_route = APIRouter(tags=["Feed"], prefix="/feed")


@feed_route.post("/", status_code=status.HTTP_201_CREATED, response_model=Feeds)
def create_feed(feed: FeedCreate, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    new_feed = Feed(user_id=current_user.id, **feed.dict())

    db.add(new_feed)
    db.commit()
    db.refresh(new_feed)
    return new_feed