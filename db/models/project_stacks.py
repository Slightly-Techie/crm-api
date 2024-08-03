from db.database import Base
from sqlalchemy import Table, Column, Integer, ForeignKey, String, PrimaryKeyConstraint


class ProjectStack(Base):
    __tablename__ = 'project_stacks'
    project_id = Column(Integer, ForeignKey("projects.id"), primary_key=True)
    stack_id = Column(Integer, ForeignKey("stacks.id"), primary_key=True)
    __table_args__ = (
        PrimaryKeyConstraint('stack_id', 'project_id'),
    )
