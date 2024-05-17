from datetime import datetime
from typing import List, Optional
from fastapi_pagination.links import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import desc, select
from fastapi import APIRouter, Depends, HTTPException, status
from api.api_models.projects import CreateProject, MembersResponse, ProjectResponse, UpdateProject, ProjectMember
from sqlalchemy.orm import Session
from db.database import get_db
from db.models.users import User
from db.models.projects import Project
from db.models.users_projects import UserProject
from utils.permissions import is_admin, is_project_manager
from utils.enums import ProjectTeam


project_router = APIRouter(tags=["Project"], prefix="/projects")


@project_router.post("/", status_code=status.HTTP_201_CREATED, response_model=ProjectResponse)
def create(project: CreateProject, db: Session = Depends(get_db), user: User = Depends(is_admin)):
    manager = db.query(User).filter(User.id == project.manager_id).first()
    if not manager:
        raise HTTPException(status_code=404, detail="Manager not found")

    new_project = Project(**project.model_dump())
    db.add(new_project)
    db.commit()
    db.refresh(new_project)

    return new_project


@project_router.put("/{project_id}", status_code=status.HTTP_201_CREATED, response_model=ProjectResponse)
def update(
    project_id: int, updated_project: UpdateProject, db: Session = Depends(get_db), user: User = Depends(is_admin)
):
    project_query = db.query(Project).filter(Project.id == project_id)
    project = project_query.first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if updated_project.manager_id and updated_project.manager_id != project.manager_id:
        manager = db.query(User).filter(User.id == updated_project.manager_id).first()
        if not manager:
            raise HTTPException(status_code=404, detail="Manager not found")

    for field, value in updated_project.model_dump().items():
        if value is not None:
            setattr(project, field, value)

    project.updated_at = datetime.now()
    db.commit()
    db.refresh(project)

    return project


@project_router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete(project_id: int, db: Session = Depends(get_db), user: User = Depends(is_admin)):
    project_query = db.query(Project).filter(Project.id == project_id)
    project = project_query.first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    project_query.delete()
    db.commit()


@project_router.get("/{project_id}", status_code=status.HTTP_200_OK, response_model=ProjectResponse)
def get(project_id: int, db: Session = Depends(get_db)):
    project_query = db.query(Project).filter(Project.id == project_id)
    project = project_query.first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    return project


@project_router.get("/", status_code=status.HTTP_200_OK, response_model=Page[ProjectResponse])
def get_all(db: Session = Depends(get_db)):
    return paginate(db, select(Project).order_by(desc(Project.created_at)))


@project_router.post("/{project_id}/add/{user_id}", status_code=status.HTTP_201_CREATED)
def add_user_to_project(
    project_id: int, user_id: int, user_project_data: ProjectMember,
    db: Session = Depends(get_db), current_user: User = Depends(is_project_manager)
):
    # Check if the project exists
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Check if the user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Check if the user is already a member of the project
    existing_member = db.query(
        UserProject).filter(UserProject.user_id == user_id, UserProject.project_id == project_id).first()
    if existing_member:
        raise HTTPException(status_code=400, detail="User is already a member of the project")

    # Create a UserProject entry with the specified role
    user_project = UserProject(user_id=user_id, project_id=project_id, team=user_project_data.team)
    db.add(user_project)
    db.commit()

    return {"message": "User added to project with team specified"}


@project_router.delete("/{project_id}/remove/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_user_from_project(
    project_id: int, user_id: int, db: Session = Depends(get_db), current_user: User = Depends(is_project_manager)
):
    # Check if the project exists
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Check if the user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Query the UserProject table to find the entry linking the user to the project
    user_project_entry = db.query(
        UserProject).filter(UserProject.user_id == user_id, UserProject.project_id == project_id).first()

    if user_project_entry:
        # Delete the entry if it exists
        db.delete(user_project_entry)
        db.commit()
    else:
        raise HTTPException(status_code=404, detail="User is not associated with the project")

    return None


@project_router.get("/{project_id}/members", status_code=status.HTTP_200_OK, response_model=List[MembersResponse])
def get_project_members(project_id: int, team: Optional[ProjectTeam] = None, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    user_project_query = db.query(UserProject).filter(UserProject.project_id == project_id)

    if team:
        user_project_query = user_project_query.filter(UserProject.team == team)

    user_project_rows = user_project_query.all()
    user_ids = [row.user_id for row in user_project_rows]

    members = db.query(User).filter(User.id.in_(user_ids)).all()

    # user_responses = [
    #     MembersResponse(
    #         id=user.id, first_name=user.first_name, last_name=user.last_name,
    #         email=user.email, username=user.username, profile_pic_url=user.profile_pic_url, stack=user.stack)
    #     for user in members
    # ]
    # print(user_responses)

    return members
