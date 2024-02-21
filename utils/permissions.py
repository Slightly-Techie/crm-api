from db.database import get_db
from db.models.projects import Project
from .oauth2 import get_current_user
from fastapi import Depends, HTTPException, status
from api.api_models.user import UserResponse
from utils.utils import RoleChoices
from core.exceptions import ForbiddenError
from sqlalchemy.orm import Session
from utils.enums import UserStatus


def is_authenticated(user: UserResponse = Depends(get_current_user)):
    """
        No need to do anything because `get_current_user` raises all the errors
        his would be used as a path dependecy so return value is required

    Usage: @app.<method>("<route>", dependencies=[Depends(is_authenticated)] )
    """

    return user


# Admin permission dependency
def is_admin(user: UserResponse = Depends(is_authenticated)):
    if user.role.name != RoleChoices.ADMIN:
        raise ForbiddenError()

    return user


def is_project_manager(
    project_id: int,
    db: Session = Depends(get_db),
    user: UserResponse = Depends(get_current_user),
):
    project = db.query(Project).filter(
        Project.id == project_id, Project.manager_id == user.id
    )
    if not project.first():
        raise HTTPException(
            status_code=403, detail="Only the project manager can perform this action"
        )

    return user


# Function to check ownership or admin
def is_owner_or_admin(user, obj):
    """
    params:
            user: current user model
            obj: object model with user field

    return:
            bool
    """
    if not hasattr(user, "role"):
        raise ForbiddenError()

    if user.role.name == RoleChoices.ADMIN:
        return True

    if user.id == obj.user_id:
        return True

    raise ForbiddenError()


# Function to check if user is owner
def is_owner(user, obj):
    if user.id == obj.user_id:
        return True

    raise ForbiddenError()


def user_accepted(user: UserResponse = Depends(get_current_user)):
    """Only accepted users can access feeds page"""
    if user.status != UserStatus.ACCEPTED:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this resource"
        )
    return user
