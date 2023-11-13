from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, status, File
from fastapi_pagination.links import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import desc, select
from sqlalchemy.orm import Session
from api.api_models.user import ProfileUpdate, ProfileResponse, SearchUser
from core.config import settings
from db.database import get_db
from db.models.users import User
from utils.oauth2 import get_current_user
from utils.permissions import is_admin
from utils.enums import UserStatus
from utils.s3 import upload_file_to_s3
from utils.utils import is_image_file


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

@profile_route.get("/", response_model=Page[ProfileResponse])
def get_all_profile(db: Session = Depends(get_db)):
    return paginate(db, select(User).order_by(desc(User.created_at)))

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



@profile_route.get("/user_info", response_model=dict)
def get_user_info(email: str, db: Session = Depends(get_db)):
    user_details = db.query(User).filter(User.email == email).first()
    if user_details:
        return {
            "status": 200,
            "data": {
                "first_name": user_details.first_name,
                "last_name": user_details.last_name,
                "phone_number": user_details.phone_number
            }
        }
    else:
        raise HTTPException(status_code=404, detail="USER NOT FOUND")


@profile_route.put("/profile/{user_id}/status", response_model=ProfileResponse, status_code=status.HTTP_200_OK)
def update_user_status(user_id: int, new_status: UserStatus, db: Session = Depends(get_db), current_user: User = Depends(is_admin)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=404, detail=settings.ERRORS.get("USER NOT FOUND"))

    user.status = new_status
    db.commit()
    return user

@profile_route.put("/profile/avatar", response_model=ProfileResponse, status_code=status.HTTP_200_OK)
async def update_avi(current_user: User = Depends(get_current_user), db: Session = Depends(get_db), file: UploadFile = File(...)):
    if not is_image_file(file.filename):
        raise HTTPException(status_code=400, detail="Invalid file format. Please upload an image.")
    
    url = await upload_file_to_s3(file, current_user.username)

    if not url:
        raise HTTPException(status_code=500, detail="Failed to upload profile picture")
    
    current_user.profile_pic_url = url
    db.commit()
    db.refresh(current_user)

    return current_user

@profile_route.get("/search", response_model=Page[SearchUser], status_code=status.HTTP_200_OK)
def search(p: str, db: Session = Depends(get_db)):
    users_query = db.query(User).filter(User.username.ilike(f"%{p}%") | User.first_name.ilike(f"%{p}%") | User.last_name.ilike(f"%{p}%"))
    if not users_query.all():
        raise HTTPException(status_code=404, detail="No users found")
        
    users = paginate(users_query)
    
    return users