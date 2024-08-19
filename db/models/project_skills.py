from db.database import Base
from sqlalchemy import Table, Column, Integer, ForeignKey, String, PrimaryKeyConstraint


class ProjectSkill(Base):
    __tablename__ = 'project_skills'
    project_id = Column(Integer, ForeignKey("projects.id"), primary_key=True)
    skill_id = Column(Integer, ForeignKey("skills.id"), primary_key=True)
    __table_args__ = (
        PrimaryKeyConstraint('skill_id', 'project_id'),
    )
