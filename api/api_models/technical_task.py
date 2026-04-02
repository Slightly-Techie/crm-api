"""
Model validation for Technical Task
"""
from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import Optional, Text
from utils.enums import ExperienceLevel


class TechnicalTaskBase(BaseModel):
    content: Text
    stack_id: int = Field(...)
    experience_level: ExperienceLevel = Field(...)


class TechnicalTaskResponse(TechnicalTaskBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TechnicalTaskSubmissionBase(BaseModel):
    github_link: Optional[Text] = None
    live_demo_url: Optional[Text] = None
    description: Optional[Text] = None


class UserMinimal(BaseModel):
    id: int
    first_name: str
    last_name: str
    username: str
    profile_pic_url: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class StackMinimal(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)


class TechnicalTaskMinimal(BaseModel):
    id: int
    content: str
    experience_level: ExperienceLevel
    stack: Optional[StackMinimal] = None

    model_config = ConfigDict(from_attributes=True)


class TechnicalTaskSubmissionResponse(TechnicalTaskSubmissionBase):
    id: int
    created_at: datetime
    updated_at: datetime
    task_id: int
    user_id: Optional[int] = None
    user: Optional[UserMinimal] = None
    technical_task: Optional[TechnicalTaskMinimal] = None

    model_config = ConfigDict(from_attributes=True)
