from typing import List

from fastapi import APIRouter, Depends, Query, status
from fastapi.params import Body
from fastapi_pagination.ext.sqlalchemy import paginate
from fastapi_pagination.links import Page
from sqlalchemy.orm import Session

from api.api_models.user import Skills
from db.database import get_db
from db.repository.skills import SkillRepository
from services.skill_service import SkillService
from utils.oauth2 import get_current_user

skill_route = APIRouter(tags=["Skills"], prefix="/skills")


def _service(db: Session) -> SkillService:
    return SkillService(SkillRepository(db))


@skill_route.get("/", response_model=List[Skills], status_code=status.HTTP_200_OK)
def get_skills(user=Depends(get_current_user), db: Session = Depends(get_db)):
    return _service(db).get_user_skills(user.id)


@skill_route.post("/", response_model=List[Skills], status_code=status.HTTP_201_CREATED)
def add_skills(skill_ids: list[int] = Body(...), db: Session = Depends(get_db),
               current_user=Depends(get_current_user)):
    return _service(db).add_skills(current_user, skill_ids)


@skill_route.delete("/{skill_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_skill_by_id(skill_id: int, user=Depends(get_current_user),
                       db: Session = Depends(get_db)):
    _service(db).delete_skill(skill_id)


@skill_route.get("/all", status_code=status.HTTP_200_OK, response_model=Page[Skills])
def get_all(db: Session = Depends(get_db)):
    return paginate(db, _service(db).get_all_query())


@skill_route.post("/data")
def populate_skills(db: Session = Depends(get_db)):
    return _service(db).populate_skills()


@skill_route.get("/search", response_model=List[dict], status_code=status.HTTP_200_OK)
def search_skills(name: str = Query(..., min_length=1, max_length=50),
                  db: Session = Depends(get_db)):
    return _service(db).search_skills(name)
