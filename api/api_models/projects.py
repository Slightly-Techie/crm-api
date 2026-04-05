from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List
from utils.enums import ProjectType, ProjectPriority, ProjectTeam, ProjectStatus
from ..api_models.stacks import Stacks
from ..api_models.user import UserResponse
from ..api_models.user import Skills


class ProjectBase(BaseModel):
    name: str = Field(...)
    description: str = Field(...)
    project_type: ProjectType = Field(...)
    project_priority: ProjectPriority = Field(...)
    manager_id: int = Field(...)


class CreateProject(ProjectBase):
    stacks: Optional[list[int] | None] = Field(None)
    members: Optional[list[int] | None] = Field(None)
    project_tools: Optional[List[int]] = Field(None)


class MemberWithTeamResponse(BaseModel):
    id: int
    first_name: str = Field(...)
    last_name: str = Field(...)
    username: str = Field(...)
    email: str = Field(...)
    profile_pic_url: Optional[str] = None
    team: Optional[str] = Field(None)

    model_config = ConfigDict(from_attributes=True)


# Alias for backward compatibility
MembersResponse = MemberWithTeamResponse


class ProjectResponse(ProjectBase):
    id: int
    created_at: datetime
    updated_at: datetime
    manager: Optional[UserResponse] = Field(None)
    members: Optional[list[MemberWithTeamResponse]] = Field(None)
    stacks: Optional[list[Stacks]] = Field(None)
    project_tools: Optional[list[Skills]] = Field(None)
    status: ProjectStatus

    model_config = ConfigDict(from_attributes=True)


class UpdateProject(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    project_type: Optional[ProjectType] = None
    project_priority: Optional[ProjectPriority] = None
    project_tools: Optional[List[int]] = None
    stacks: Optional[List[int]] = None
    manager_id: Optional[int] = None


class ProjectMember(BaseModel):
    team: ProjectTeam = Field(...)
