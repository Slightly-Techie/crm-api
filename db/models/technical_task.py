"""
Technical task to be completed by applicants
"""
from db.database import Base
from sqlalchemy import Column, Integer, TIMESTAMP, text, Text
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey
from utils.enums import ExperienceLevel
from sqlalchemy import Enum as SQLAlchemyEnum


class TechnicalTask(Base):
    __tablename__ = 'technical_tasks'
    id = Column(Integer, primary_key=True, nullable=False)
    created_at = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()"))
    updated_at = Column(TIMESTAMP(timezone=True),
                        nullable=False, server_default=text('now()'))
    content = Column(Text)
    stack_id = Column(Integer, ForeignKey("stacks.id"))
    experience_level = Column(SQLAlchemyEnum(ExperienceLevel), default=ExperienceLevel.JUNIOR)

    stack = relationship("Stack", back_populates='technical_task')
    task_submission = relationship("TechnicalTaskSubmission", back_populates="technical_task")


class TechnicalTaskSubmission(Base):
    __tablename__ = 'technical_task_submissions'
    id = Column(Integer, primary_key=True, nullable=False)
    created_at = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()"))
    updated_at = Column(TIMESTAMP(timezone=True),
                        nullable=False, server_default=text('now()'))
    github_link = Column(Text)
    live_demo_url = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    task_id = Column(Integer, ForeignKey("technical_tasks.id"), nullable=True)

    user = relationship("User",  back_populates="technical_task_submission")
    technical_task = relationship("TechnicalTask",  back_populates="task_submission")
