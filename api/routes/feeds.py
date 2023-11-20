from fastapi import Depends, Form, HTTPException, APIRouter, status, Form, File, UploadFile
from sqlalchemy.orm import Session
from sqlalchemy import select
from db.database import get_db
from utils.oauth2 import get_current_user
from fastapi_pagination.links import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from db.models.feeds import Feed
from api.api_models.user import FeedUpdate, Feeds
from sqlalchemy import desc

from utils.s3 import upload_file_to_s3
from utils.utils import is_image_file


feed_route = APIRouter(tags=["Feed"], prefix="/feed")


@feed_route.post("/", status_code=status.HTTP_201_CREATED, response_model=Feeds)
async def create_feed(content: str = Form(...), feed_pic_url: UploadFile = File(None), current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    if feed_pic_url:
        if not is_image_file(feed_pic_url.filename):
            raise HTTPException(status_code=400, detail="Invalid file format. Please upload an image.")
        
        image_url = await upload_file_to_s3(feed_pic_url, current_user.username, "feed")
    else:
        image_url = None

    new_feed = Feed(user_id=current_user.id, content=content, feed_pic_url=image_url)

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
def delete_feed_by_id(feed_id: int, db: Session = Depends(get_db), current_user= Depends(get_current_user)):
    feed_query = db.query(Feed).filter(Feed.id == feed_id)
    feed = feed_query.first()
    if feed is None:
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


@feed_route.get("/{feed_id}", status_code=status.HTTP_200_OK, response_model=Feeds)
def get_feed_by_id(feed_id: int, db: Session = Depends(get_db)):
    feed_query = db.query(Feed).filter(Feed.id == feed_id)
    feed = feed_query.first()
    if not feed:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=f"feed with id: {feed_id} was not found")
    
    return feed


@feed_route.get("/", response_model=Page[Feeds])
def get_all_feeds(db: Session = Depends(get_db)):
    return paginate(db, select(Feed).order_by(desc(Feed.created_at)))