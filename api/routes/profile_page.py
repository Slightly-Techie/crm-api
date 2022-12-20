from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy.orm import Session
from api.api_models.user import UserResponse,Profile
from db.database import get_db
from db.models.users import User


profile_route = APIRouter(tags=["user_details"],prefix="/users")

@profile_route.get("/profile")
async def get_profile(id:int,db: Session = Depends(get_db)) -> UserResponse:
    user_details =  db.query(User).filter(User.id ==  id).first()
    if user_details:
        return {user_details}     
    else:
        raise HTTPException(status_code=404,detail="Id does not exist")    

@profile_route.put("/profile")
async def update_profile(id:int,userDetails:Profile,db:Session = Depends(get_db)):
    user_exists =  db.query(User).filter(User.id == id).first()
    try:
        if user_exists:
            user_exists.email = userDetails.email if userDetails.email else user_exists.email
            user_exists.first_name = userDetails.first_name if userDetails.first_name else user_exists.first_name
            user_exists.last_name = userDetails.last_name if userDetails.last_name else user_exists.last_name
            user_exists.github_profile = userDetails.github_profile
            user_exists.twitter_profile = userDetails.twitter_profile
            user_exists.linkedin_profile = userDetails.linkedin_profile
            user_exists.portfolio_url = userDetails.portfolio_url
            user_exists.profile_pic_url = userDetails.profile_pic_url

            db.commit()

            return {"message" : "Profile update successful"}
        
        else:
            raise HTTPException(status_code=404,detail="Id does not exist")  
    except:
        raise HTTPException(status_code=400,detail="Something went wrong")


