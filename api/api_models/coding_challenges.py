from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import Optional
from utils.enums import ChallengeType


class CodingChallengeBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=300)
    description: str = Field(..., min_length=1)
    challenge_type: ChallengeType
    difficulty: Optional[str] = Field(None, pattern="^(Easy|Medium|Hard)$")
    challenge_url: Optional[str] = None
    deadline: Optional[datetime] = None


class CodingChallengeCreate(CodingChallengeBase):
    pass


class CodingChallengeUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=300)
    description: Optional[str] = Field(None, min_length=1)
    challenge_type: Optional[ChallengeType] = None
    difficulty: Optional[str] = Field(None, pattern="^(Easy|Medium|Hard)$")
    challenge_url: Optional[str] = None
    deadline: Optional[datetime] = None


class CodingChallengeResponse(CodingChallengeBase):
    id: int
    posted_at: datetime
    created_by: int
    model_config = ConfigDict(from_attributes=True)
