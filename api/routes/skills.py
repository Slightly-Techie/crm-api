from ast import List
from fastapi import Depends, HTTPException, APIRouter, status
from sqlalchemy.orm import Session, joinedload

from api.api_models.skills import  SkillCreate

from db.database import get_db
from utils.permissions import is_authenticated
from utils.oauth2 import get_current_user

from db.models.users import User, Skill, UserSkills
from api.api_models.user import Skills, UserResponse


skill_route = APIRouter(tags=["User"],prefix="/users")

@skill_route.get('/skills')
def get_skills( user=Depends(get_current_user), db:Session = Depends(get_db)):
    db_query =  db.query(User).filter(User.id == user.id).\
        options(joinedload(User.skills)).first()   
    return {"skills": db_query.skills}


@skill_route.post('/skills', response_model=Skills, status_code=status.HTTP_201_CREATED)
def create_skill(skill: SkillCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=401, detail='Unauthorized')

    db_skill = db.query(Skill).filter(Skill.name == skill.name).first()
    if db_skill:
        if db_skill in current_user.skills:
            raise HTTPException(status_code=400, detail='Skill already exists for user')
        else:
            current_user.skills.append(db_skill)
            db.commit()
            return db_skill
    else:
        db_skill = Skill(name=skill.name)
        db.add(db_skill)
        db.commit()
        db.refresh(db_skill)

        current_user.skills.append(db_skill)
        db.commit()

        return db_skill


@skill_route.delete("/skills/{skill_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_skill_by_id(skill_id: int, user=Depends(get_current_user), db:Session = Depends(get_db)):
    db_skill =  db.query(UserSkills).filter(UserSkills.skill_id == skill_id)
    skill = db_skill.first()

    if not skill:
         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                             detail=f'No skill with this id: {skill_id} found')
    
    db_skill.delete(synchronize_session=False)
    db.commit()

