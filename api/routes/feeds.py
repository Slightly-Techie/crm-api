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


@feed_route.put("/{feed_id}", status_code=status.HTTP_201_CREATED, response_model=Feeds)
def update_feed_by_id(feed_id: int, updated_feed: FeedUpdate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    feed_query = db.query(Feed).filter(Feed.id == feed_id)
    feed = feed_query.first()
    if feed == None:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND, detail=f"feed with id: {feed_id} was not found"
        )
    if feed.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You not authorized to perform this request",
        )

    feed_query.update(updated_feed.dict())
    db.commit()

    return feed_query.first()


@feed_route.delete("/{feed_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post_by_id(feed_id: int, db: Session = Depends(get_db), current_user= Depends(get_current_user)):
    feed_query = db.query(Feed).filter(Feed.id == feed_id)
    feed = feed_query.first()
    if feed == None:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND, detail=f"feed with id: {feed_id} was not found"
        )
    if feed.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You not authorized to perform this request",
        )

    feed_query.delete()
    db.commit()