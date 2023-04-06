from fastapi import Depends, FastAPI,HTTPException, APIRouter, status, Response
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
        db.commit()
        db.refresh(db_user)
        return db_user
    
    else:
        db_skill = Skill(**skill.dict(), user_id=user_id)
        db.add(db_skill)
        db.commit()
        db_user = UserSkills(user_id = user_id, skill_id = db_skill.id)
        db.add(db_user)
        db.commit()
        db.refresh(db_skill)
        db.refresh(db_user)
        return db_skill
       
    
def delete_user_skill(db:Session, skill_id:  int, user_id: int):
   
    db_skill =  db.query(UserSkills).filter(UserSkills.skill_id == skill_id)
        
    skill = db_skill.first()   
    if not skill:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'No skill with this id: {skill_id} found')
    db_skill.delete(synchronize_session=False)
    db.commit()
    return 'skill deleted'
    


skill_route = APIRouter(tags=["User"],prefix="/users")

@skill_route.post('/skills', status_code=status.HTTP_201_CREATED,response_model=UserResponse )
    
def create_skill_for_user( skill: SkillCreate, user=Depends(get_current_user), db:Session = Depends(get_db)):

    new_skill = create_user_skills(db=db, skill=skill, user_id=user.id)
    return new_skill




@skill_route.get('/user')
def get_skill( user=Depends(get_current_user), db:Session = Depends(get_db)):
    db_query =  db.query(User).filter(User.id == user.id).\
        options(joinedload(User.skills)).first()   
    return db_query



@skill_route.delete('/skill/{skill_id}', )
def delete_skill( skill_id: int, user=Depends(get_current_user), db:Session = Depends(get_db)):
   delete_skill = delete_user_skill(db=db, skill_id=skill_id, user_id=user.id)
   return delete_skill
   
