from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import desc
from sqlalchemy.orm import Session
from api.api_models.user import PaginatedUsers, ProfileUpdate, ProfileResponse
from core.config import settings
from db.database import get_db
from db.models.users import User
from utils.oauth2 import get_current_user
from utils.permissions import is_admin


profile_route = APIRouter(tags=["User"], prefix="/users")


@profile_route.get("/profile/{user_id}", response_model=ProfileResponse)
async def get_profile(user_id: int, db: Session = Depends(get_db)):
    user_details = db.query(User).filter(User.id == user_id).first()
    if user_details:
        return user_details
    else:
        raise HTTPException(
            status_code=404, detail=settings.ERRORS.get("INVALID ID"))


@profile_route.put("/profile", response_model=ProfileResponse)
async def update_profile(userDetails: ProfileUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    user_exists = db.query(User).filter(User.id == current_user.id)
    try:
        if user_exists.first():
            # convert json into a python dict and exclude fields not specified
            update_data = userDetails.dict(exclude_unset=True)
            user_exists.update(update_data)

            db.commit()

            return user_exists.first()
        else:
            raise HTTPException(
                status_code=404, detail=settings.ERRORS.get("INVALID ID"))
    except:
        raise HTTPException(
            status_code=400, detail=settings.ERRORS.get("UNKNOWN ERROR"))


@profile_route.get("/", response_model=PaginatedUsers)
def get_all_profile(limit: int = Query(default=50, ge=1, le=100), page: int = Query(default=1, ge=1), db: Session = Depends(get_db)):
    total_users = db.query(User).count()
    pages = (total_users - 1) // limit + 1
    offset = (page - 1) * limit
    users = db.query(User).order_by(desc(User.created_at)).offset(offset).limit(limit).all()

    links = {
        "first": f"/api/v1/users/?limit={limit}&page=1",
        "last": f"/api/v1/users/?limit={limit}&page={pages}",
        "self": f"/api/v1/users/?limit={limit}&page={page}",
        "next": None,
        "prev": None,
    }

    if page < pages:
        links["next"] = f"/api/v1/users/?limit={limit}&page={page + 1}"

    if page > 1:
        links["prev"] = f"/api/v1/users/?limit={limit}&page={page - 1}"

    return PaginatedUsers(
        users=users,
        total=total_users,
        page=page,
        size=limit,
        pages=pages,
        links=links,
    )


@profile_route.put("/profile/{user_id}/activate", response_model=ProfileResponse, status_code=status.HTTP_200_OK)
def update_profile_status(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(is_admin)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=404, detail=settings.ERRORS.get("INVALID ID"))
    if user.is_active:
        raise HTTPException(
            status_code=400, detail=settings.ERRORS.get("USER ALREADY ACTIVE"))
    user.is_active = True
    db.commit()
    return user
