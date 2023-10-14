from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from api.api_models.projects import CreateProject,ProjectResponse
from sqlalchemy.orm import Session
from db.database import get_db
from db.models.users import User
from db.models.projects import Project
from utils.permissions import is_admin, is_project_manager


project_router = APIRouter(tags=["Project"], prefix="/projects")


@project_router.post(
    "/", status_code=status.HTTP_201_CREATED, response_model=ProjectResponse
)
def create(
    project: CreateProject,
    db: Session = Depends(get_db),
    user: User = Depends(is_admin),
):
    manager = db.query(User).filter(User.id == project.manager_id).first()
    if not manager:
        raise HTTPException(status_code=404, detail="Manager not found")

    new_project = Project(**project.dict())
    db.add(new_project)
    db.commit()
    db.refresh(new_project)

    return new_project


"""
@project_router.put(
    "/{project_id}", status_code=status.HTTP_201_CREATED, response_model=ProjectResponse
)
def update(
    project_id: int,
    updated_project: UpdateProject,
    db: Session = Depends(get_db),
    user: User = Depends(is_admin),
):
    project_query = db.query(Project).filter(Project.id == project_id)
    project = project_query.first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if updated_project.manager_id and updated_project.manager_id != project.manager_id:
        manager = db.query(User).filter(User.id == updated_project.manager_id).first()
        if not manager:
            raise HTTPException(status_code=404, detail="Manager not found")

    for field, value in updated_project.dict().items():
        if value is not None:
            setattr(project, field, value)

    project.updated_at = datetime.now()
    db.commit()
    db.refresh(project)

    return project
"""

@project_router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete(
    project_id: int, db: Session = Depends(get_db), user: User = Depends(is_admin)
):
    project_query = db.query(Project).filter(Project.id == project_id)
    project = project_query.first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    project_query.delete()
    db.commit()


@project_router.get(
    "/{project_id}", status_code=status.HTTP_200_OK, response_model=ProjectResponse
)
def get(project_id: int, db: Session = Depends(get_db)):
    project_query = db.query(Project).filter(Project.id == project_id)
    project = project_query.first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    return project


@project_router.get(
    "/", status_code=status.HTTP_200_OK, response_model=List[ProjectResponse]
)
def get_all(db: Session = Depends(get_db)):
    projects = db.query(Project).all()

    return projects


@project_router.post("/{project_id}/add/{user_id}", status_code=status.HTTP_201_CREATED)
def add_user(
    project_id: int,
    user_id: int,
    db: Session = Depends(get_db),
):
    project_query = db.query(Project).filter(Project.id == project_id)
    project: Project = project_query.first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    user_query = db.query(User).filter(User.id == user_id)
    user = user_query.first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    project.users.append(user)
    db.commit()

    return {"message": "User added to project"}


@project_router.delete(
    "/{project_id}/remove/{user_id}", status_code=status.HTTP_202_ACCEPTED
)
def remove_user(
    project_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(is_project_manager),
):
    project_query = db.query(Project).filter(Project.id == project_id)
    project: Project = project_query.first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    user_query = db.query(User).filter(User.id == user_id)
    user = user_query.first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user not in project.users:
        raise HTTPException(
            status_code=404, detail="User is not associated with the project"
        )

    project.users.remove(user)
    db.commit()

    return {"message": "User removed from project"}
