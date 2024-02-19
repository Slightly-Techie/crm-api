from db.database import Base
from sqlalchemy import Column, Integer
from sqlalchemy import ForeignKey


class UserSkill(Base):
    __tablename__ = 'users_skills'
    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    skill_id = Column(Integer, ForeignKey('skills.id'), primary_key=True)
