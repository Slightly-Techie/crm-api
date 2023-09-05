from fastapi import Depends, HTTPException, APIRouter, status, Query
from sqlalchemy.orm import Session
from db.database import get_db
from utils.oauth2 import get_current_user
from db.models.users import User
from db.models.feeds import Feed
from api.api_models.user import FeedCreate, FeedUpdate, Feeds, PaginatedResponse
from sqlalchemy import desc, select


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
def delete_feed_by_id(feed_id: int, db: Session = Depends(get_db), current_user= Depends(get_current_user)):
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


@feed_route.get("/{feed_id}", status_code=status.HTTP_200_OK, response_model=Feeds)
def get_feed_by_id(feed_id: int, db: Session = Depends(get_db)):
    feed_query = db.query(Feed).filter(Feed.id == feed_id)
    feed = feed_query.first()
    if not feed:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=f"feed with id: {feed_id} was not found")
    
    return feed


@feed_route.get("/", response_model=PaginatedResponse)
def get_all_feeds(limit: int = Query(default=50, ge=1, le=100), page: int = Query(default=1, ge=1), db: Session = Depends(get_db)):
    total_feeds = db.query(Feed).count()
    pages = (total_feeds - 1) // limit + 1
    offset = (page - 1) * limit
    feeds = db.query(Feed).order_by(desc(Feed.created_at)).offset(offset).limit(limit).all()

    # Determine pagination links
    links = {
        "first": f"/api/v1/feed/?limit={limit}&page=1",
        "last": f"/api/v1/feed/?limit={limit}&page={pages}",
        "self": f"/api/v1/feed/?limit={limit}&page={page}",
        "next": None,
        "prev": None,
    }

    if page < pages:
        links["next"] = f"/api/v1/feed/?limit={limit}&page={page + 1}"

    if page > 1:
        links["prev"] = f"/api/v1/feed/?limit={limit}&page={page - 1}"

    return PaginatedResponse(
        feeds=feeds,
        total=total_feeds,
        page=page,
        size=limit,
        pages=pages,
        links=links,
    )