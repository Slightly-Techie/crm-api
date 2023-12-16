from fastapi import Depends, HTTPException, APIRouter, status, Query
from fastapi.params import Body
from rapidfuzz import fuzz, process
from sqlalchemy.orm import Session, joinedload
from typing import List
from sqlalchemy import desc, select
from fastapi_pagination.links import Page
from fastapi_pagination.ext.sqlalchemy import paginate

from db.database import SessionLocal, get_db
from utils.oauth2 import get_current_user

from db.models.users import User
from db.models.skills import Skill
from db.models.users_skills import UserSkill
from api.api_models.user import Skills
from utils.tools import tools as skills_data


skill_route = APIRouter(tags=["Skills"],prefix="/skills")

@skill_route.get('/', response_model=List[Skills], status_code=status.HTTP_200_OK)
def get_skills( user=Depends(get_current_user), db:Session = Depends(get_db)):
    db_query =  db.query(User).filter(User.id == user.id).\
        options(joinedload(User.skills)).first()   
    return db_query.skills


@skill_route.post('/', response_model=List[Skills], status_code=status.HTTP_201_CREATED)
def add_skills(skill_ids: list[int] = Body(...), db: Session = Depends(get_db), 
                  current_user: User = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=401, detail='Unauthorized')

    db_skills = db.query(Skill).filter(Skill.id.in_(skill_ids)).all()
    if not db_skills:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='No skills found with the given ids')
    
    # Check if the user already has the skills
    user_skills = db.query(UserSkill).filter(UserSkill.skill_id.in_(skill_ids), UserSkill.user_id == current_user.id).all()

    existing_skill_ids = [user_skill.skill_id for user_skill in user_skills]

    if existing_skill_ids:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f'User already has skills with IDs: {existing_skill_ids}')
    
    user_skills = [UserSkill(user_id=current_user.id, skill_id=skill.id) for skill in db_skills]
    db.add_all(user_skills)
    db.commit()
    db.refresh(current_user)

    return current_user.skills


@skill_route.delete("/{skill_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_skill_by_id(skill_id: int, user=Depends(get_current_user), 
        db:Session = Depends(get_db)):
    
    db_skill =  db.query(UserSkill).filter(UserSkill.skill_id == skill_id)
    skill = db_skill.first()

    if not skill:
         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                             detail=f'No skill with this id: {skill_id} found')
    
    db_skill.delete(synchronize_session=False)
    db.commit()



@skill_route.get("/all", status_code=status.HTTP_200_OK, response_model=Page[Skills])
def get_all(db: Session = Depends(get_db)):
    return paginate(db, select(Skill).order_by(desc(Skill.created_at)))


@skill_route.post("/data")
def populate_skills():
    db = SessionLocal()
    try:
        for skill_name in skills_data:
            skill = Skill(name=skill_name)
            db.add(skill)
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Skill insertion error")
    finally:
        db.close()
    return {"message": "Skills table populated successfully!"}

@skill_route.get("/search", response_model=List[dict], status_code=status.HTTP_200_OK)
def search_skills(name: str = Query(..., min_length=1, max_length=50), db: Session = Depends(get_db)):
    try:
        skills = db.query(Skill).all()
        results = process.extract(name.lower(), [skill.name.lower() for skill in skills], scorer=fuzz.partial_ratio)
        threshold = 78
        filtered_results = [result[0] for result in results if result[1] >= threshold]
        final_results = [{"skill_id": skill.id, "skill_name": skill_name} for skill, skill_name in zip(skills, filtered_results)]
        return final_results
    except Exception as e:
        error_message = f"An error occurred: {str(e)}"
        raise HTTPException(status_code=500, detail=error_message)