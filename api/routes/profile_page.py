from typing import List
from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy.orm import Session
from api.api_models.user import ProfileUpdate,ProfileResponse
from core.config import settings
from db.database import get_db
from db.models.users import User
from utils.oauth2 import get_current_user


profile_route = APIRouter(tags=["User"],prefix="/users")

@profile_route.get("/profile",response_model=ProfileResponse)
async def get_profile(current_user: User = Depends(get_current_user),db: Session = Depends(get_db)) -> ProfileResponse:
    user_details =  db.query(User).filter(User.id == current_user.id).first()
    if user_details:
        return user_details
    else:
        raise HTTPException(status_code=404,detail=settings.ERRORS.get("INVALID ID"))    

@profile_route.put("/profile",response_model=ProfileResponse)
async def update_profile(id:int,userDetails:ProfileUpdate,db:Session = Depends(get_db)):
    user_exists =  db.query(User).filter(User.id == id)
    try:
        if user_exists.first():
            update_data = userDetails.dict(exclude_unset=True) #convert json into a python dict and exclude fields not specified
            user_exists.update(update_data)
                        
            db.commit()
       
            return user_exists.first()
                    
        else:
                raise HTTPException(status_code=404,detail=settings.ERRORS.get("INVALID ID"))                       
    except:
        raise HTTPException(status_code=400,detail=settings.ERRORS.get("UNKNOWN ERROR"))
        
@profile_route.get("/", response_model=List[ProfileResponse])
def get_all_profile(db:Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> List[ProfileResponse]:
    
    user = db.query(User).all()

    return user

