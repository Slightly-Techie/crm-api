from db.database import Base
from sqlalchemy import Column, Integer, ForeignKey, String, PrimaryKeyConstraint

class UserProject(Base):
    __tablename__ = 'users_projects'
    project_id = Column(Integer, ForeignKey("projects.id"), primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    team = Column(String, nullable = True)  # Add a role field to store the user's role in the project
    __table_args__ = (
        PrimaryKeyConstraint('user_id', 'project_id'),
    )
