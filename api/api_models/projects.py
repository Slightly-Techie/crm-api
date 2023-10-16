from datetime import date
from typing import List, Dict
from pydantic import BaseModel
from utils.enums import ProjectPriority, ProjectType

class Project(BaseModel):
    name: str
    description: str
    project_type: ProjectType
    project_priority: ProjectPriority
    project_tools: str
    manager_id: int
    members: List[Dict] = []
    

class CreateProject(Project):
    pass
    class Config:
        orm_mode = True

class ProjectResponse(Project):
    id: int
    members: list[Dict] = []
    created_at: date

    
    class Config:
        orm_mode = True


class UpdateProject(Project):
    
    members: list[Dict] = []

    class Config:
        orm_mode = True
