from db.database import Base
from sqlalchemy import Column, String, Integer, TIMESTAMP, text, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey
from utils.enums import ChallengeType


class CodingChallenge(Base):
    __tablename__ = 'coding_challenges'
    id = Column(Integer, primary_key=True, nullable=False)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    challenge_type = Column(SQLEnum(ChallengeType), nullable=False, default=ChallengeType.LEETCODE)
    difficulty = Column(String)  # Easy, Medium, Hard
    challenge_url = Column(String)  # Link to LeetCode, etc.
    posted_at = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()"))
    deadline = Column(TIMESTAMP(timezone=True), nullable=True)
    created_by = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    user = relationship("User")
