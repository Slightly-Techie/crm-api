from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List
from utils.enums import ProjectType, ProjectPriority, ProjectTeam, ProjectStatus
from ..api_models.stacks import Stacks
from ..api_models.user import UserResponse


class ProjectBase(BaseModel):
    name: str = Field(...)
    description: str = Field(...)
    project_type: ProjectType = Field(...)
    project_priority: ProjectPriority = Field(...)
    project_tools: Optional[List[str]] = Field(None)
    manager_id: int = Field(...)

class CreateProject(ProjectBase):
    stacks: Optional[list[int] | None] = Field(None)
    members: Optional[list[int] | None] = Field(None)


class ProjectResponse(ProjectBase):
    id: int
    created_at: datetime
    updated_at: datetime
    members: Optional[list[UserResponse]] = Field(None)
    stacks: Optional[list[Stacks]] = Field(None)
    status: ProjectStatus

    model_config = ConfigDict(from_attributes=True)


class UpdateProject(BaseModel):
    name: Optional[str]
    description: Optional[str]
    project_type: Optional[ProjectType]
    project_priority: Optional[ProjectPriority]
    project_tools: Optional[List[str]]
    manager_id: Optional[int]


class ProjectMember(BaseModel):
    team: ProjectTeam = Field(...)


class MembersResponse(BaseModel):
    id: int
    first_name: str = Field(...)
    last_name: str = Field(...)
    username: str = Field(...)
    email: str = Field(...)
    profile_pic_url: Optional[str] = None
    stack: Optional[Stacks] = Field(None)
