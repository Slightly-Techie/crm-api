from fastapi import Depends, FastAPI,HTTPException, APIRouter
from sqlalchemy.orm import Session, joinedload

from api.api_models.skills import  SkillCreate

from db.database import get_db
from utils.permissions import is_authenticated
from utils.oauth2 import get_current_user

from db.models.users import User, Skill, UserSkills
from api.api_models.user import UserResponse




def create_user_skills(db:Session, skill:  SkillCreate, user_id: int): 
    lowercase = skill.name.lower()
    skill.name = lowercase
    find_skill = db.query(Skill).filter(Skill.name == lowercase).first()
    if(find_skill):  
        db_user = UserSkills(user_id = user_id, skill_id = find_skill.id)
        db.add(db_user)
        return db_user
    
    else:
        db_skill = Skill(**skill.dict(), user_id=user_id)
        db.add(db_skill)
        db.commit()
        db_user = UserSkills(user_id = user_id, skill_id = db_skill.id)
        db.add(db_user)
        db.commit()
        db.refresh(db_skill)
        return db_skill
       
    
    

skill_route = APIRouter(tags=["User"],prefix="/users")

@skill_route.post('/skills')
    
def create_skill_for_user( skill: SkillCreate, user=Depends(get_current_user), db:Session = Depends(get_db)):

    new_skill = create_user_skills(db=db, skill=skill, user_id=user.id)
    return new_skill




@skill_route.get('/user', response_model = UserResponse)
def get_skill( user=Depends(get_current_user), db:Session = Depends(get_db)):
    db_query =  db.query(User).filter(User.id == user.id).\
        options(joinedload(User.skills)).first()   
    return db_query



# @skill_route.delete('/skill', )
# def delete_skill( skill_id: int, db:Session = Depends(get_db)):
#    db.query(Skill).filter(Skill.id == skill_id).delete()
