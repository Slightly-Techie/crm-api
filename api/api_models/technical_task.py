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
    github_link: Text
    live_demo_url: Optional[Text]
    description: Optional[Text]


class TechnicalTaskSubmissionResponse(TechnicalTaskSubmissionBase):
    id: int
    created_at: datetime
    updated_at: datetime
    task_id: int

    model_config = ConfigDict(from_attributes=True)
