from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy.orm import Session
from db.models.users import User
from db.models.user_details import UserDetails
from api.api_models.user_details import UserDetails
from db.database import get_db


details_route = APIRouter(tags=["user_details"])

@details_route.get("/profile",response_model=UserDetails)
async def get_profile(user_id:int,db: Session = Depends(get_db)) -> UserDetails:
    user_exists = await db.query(User).filter(User.id == user_id).first()
    if user_exists:
        user_details = await db.query(UserDetails).filter(UserDetails.user_id == user_id).first()
    else:
        raise HTTPException(status_code=404,details = "User does not exist")    

    return UserDetails(**user_details)     



