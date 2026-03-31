from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class CodingChallengeBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=300)
    description: str = Field(..., min_length=1)
    challenge_type: str = Field(..., pattern="^(LEETCODE|SYSTEM_DESIGN|GENERAL)$")
    difficulty: Optional[str] = Field(None, pattern="^(Easy|Medium|Hard)$")
    challenge_url: Optional[str] = None
    deadline: Optional[datetime] = None


class CodingChallengeCreate(CodingChallengeBase):
    pass


class CodingChallengeUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=300)
    description: Optional[str] = Field(None, min_length=1)
    challenge_type: Optional[str] = Field(None, pattern="^(LEETCODE|SYSTEM_DESIGN|GENERAL)$")
    difficulty: Optional[str] = Field(None, pattern="^(Easy|Medium|Hard)$")
    challenge_url: Optional[str] = None
    deadline: Optional[datetime] = None


class CodingChallengeResponse(CodingChallengeBase):
    id: int
    posted_at: datetime
    created_by: int

    class Config:
        from_attributes = True
