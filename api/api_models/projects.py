from datetime import date
from pydantic import BaseModel

class Project(BaseModel):
    name: str
    description: str
    manager_id: int

class CreateProject(Project):
    pass
    class Config:
        orm_mode = True

class ProjectResponse(Project):
    id: int
    created_at: date

    
    class Config:
        orm_mode = True

"""
class UpdateProject(Project):

    class Config:
        orm_mode = True
"""
