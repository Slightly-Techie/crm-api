from fastapi import Depends, FastAPI,HTTPException, APIRouter
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from api.api_models.skills import  SkillCreate, SkillResponse
from db.models.skills import Skill, UserSkills
from db.database import get_db


from db.models.users import User
from api.api_models.user import UserResponse


def create_skills(db:Session, skill: SkillCreate):
    db_skill = Skill(name = skill.name)
    db.add(db_skill)
    db.commit()
    db.refresh(db_skill)
    return db_skill


def create_user_skills(db:Session, skill:  SkillCreate, user_id: int):
    db_skill = Skill(name = skill.name, user_id=user_id)
    
    db.add(db_skill)
    
    db.commit()
    db_user = UserSkills(user_id = user_id, skill_id = db_skill.id)
    db.add(db_user)
    db.commit()
    db.refresh(db_skill)
    return db_skill



#auth_router = APIRouter(tags=["Auth"], )
skill_route = APIRouter(tags=["user_details"],prefix="/users")

@skill_route.post('/skills', )
    
def create_skill_for_user( skill: SkillCreate, db:Session = Depends(get_db)):

    new_skill = create_user_skills(db=db, skill=skill, user_id=4)
    return new_skill


@skill_route.get('/user', response_model=UserResponse)
def get_user( user_id: int, db:Session = Depends(get_db)):
    return db.query(User).filter(User.id == user_id).first()


@skill_route.get('/skill', )
def get_skill( skill_id: int, db:Session = Depends(get_db)):
    return db.query(Skill).filter(Skill.id == skill_id).first()
