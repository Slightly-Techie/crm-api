from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional

class CreateProject(BaseModel):
    name: str = Field(...)
    description: str = Field(...)
    manager_id: int = Field(...)

class ProjectResponse(CreateProject):
    id: int
    created_at: datetime
    updated_at: datetime
    manager_id: int

    class Config:
        orm_mode = True

class UpdateProject(BaseModel):
    name: Optional[str]
    description: Optional[str]
    manager_id: Optional[int]

