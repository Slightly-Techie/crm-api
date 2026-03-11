from typing import List, Optional

from fastapi import APIRouter, Depends, status
from fastapi_pagination.ext.sqlalchemy import paginate
from fastapi_pagination.links import Page
from sqlalchemy.orm import Session

from api.api_models.projects import CreateProject, MembersResponse, ProjectMember, ProjectResponse, UpdateProject
from db.database import get_db
from db.models.users import User
from db.repository.projects import ProjectRepository
from db.repository.skills import SkillRepository
from db.repository.stacks import StackRepository
from db.repository.users import UserRepository
from services.project_service import ProjectService
from utils.enums import ProjectTeam
from utils.permissions import is_admin, is_project_manager

project_router = APIRouter(tags=["Project"], prefix="/projects")


def _service(db: Session) -> ProjectService:
    return ProjectService(
        ProjectRepository(db),
        UserRepository(db),
        StackRepository(db),
        SkillRepository(db)
    )


@project_router.post("/", status_code=status.HTTP_201_CREATED, response_model=ProjectResponse)
def create(project: CreateProject, db: Session = Depends(get_db), user: User = Depends(is_admin)):
    return _service(db).create_project(project)


@project_router.put("/{project_id}", status_code=status.HTTP_200_OK, response_model=ProjectResponse)
def update(project_id: int, updated_project: UpdateProject, db: Session = Depends(get_db),
           user: User = Depends(is_admin)):
    return _service(db).update_project(project_id, updated_project)


@project_router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete(project_id: int, db: Session = Depends(get_db), user: User = Depends(is_admin)):
    _service(db).delete_project(project_id)


@project_router.get("/{project_id}", status_code=status.HTTP_200_OK, response_model=ProjectResponse)
def get(project_id: int, db: Session = Depends(get_db)):
    return _service(db).get_project(project_id)


@project_router.get("/", status_code=status.HTTP_200_OK, response_model=Page[ProjectResponse])
def get_all(db: Session = Depends(get_db)):
    return paginate(db, _service(db).get_all_query())


@project_router.post("/{project_id}/add/{user_id}", status_code=status.HTTP_201_CREATED)
def add_user_to_project(project_id: int, user_id: int, user_project_data: ProjectMember,
                        db: Session = Depends(get_db),
                        current_user: User = Depends(is_project_manager)):
    return _service(db).add_member(project_id, user_id, user_project_data.team)


@project_router.delete("/{project_id}/remove/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_user_from_project(
    project_id: int, user_id: int, db: Session = Depends(get_db),
    current_user: User = Depends(is_project_manager)
):
    _service(db).remove_member(project_id, user_id)


@project_router.get("/{project_id}/members", status_code=status.HTTP_200_OK,
                    response_model=List[MembersResponse])
def get_project_members(project_id: int, team: Optional[ProjectTeam] = None,
                        db: Session = Depends(get_db)):
    return _service(db).get_project_members(project_id, team)
