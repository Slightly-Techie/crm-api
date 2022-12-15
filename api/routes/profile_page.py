from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy.orm import Session
from api.api_models.user_response import UserResponse
from db.database import get_db
from db.models.users import User


details_route = APIRouter(tags=["user_details"],prefix="/users")

@details_route.get("/profile",response_model=UserResponse)
async def get_profile(id:int,db: Session = Depends(get_db)) -> UserResponse:
    user_exists = await db.query(User).filter(User.id ==  id).first()
    if user_exists:
        user_details = await db.query(User).filter(User.id == id).first()
    else:
        raise HTTPException(status_code=404,details = "User does not exist")    

    return UserResponse(**user_details)     



