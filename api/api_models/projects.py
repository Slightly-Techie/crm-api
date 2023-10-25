from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional, List
from utils.enums import ProjectType, ProjectPriority, ProjectTeam

class CreateProject(BaseModel):
    name: str = Field(...)
    description: str = Field(...)
    project_type: ProjectType = Field(...)
    project_priority: ProjectPriority = Field(...)
    project_tools: Optional[List[str]]
    manager_id: int = Field(...)
    

class ProjectResponse(CreateProject):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

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
    email: str = Field(...)
    
