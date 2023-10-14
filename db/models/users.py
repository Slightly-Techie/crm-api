from db.database import Base
from sqlalchemy import Boolean, Column, String, Integer, TIMESTAMP, Text, text
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey
from utils.enums import UserStatus
from sqlalchemy import Enum as SQLAlchemyEnum


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=True)
    password = Column(String, nullable=False)
    years_of_experience = Column(Integer)
    bio = Column(Text)
    phone_number = Column(String)
    github_profile = Column(String)
    twitter_profile = Column(String)
    linkedin_profile = Column(String)
    portfolio_url = Column(String)
    profile_pic_url = Column(String)
    stack_id = Column(Integer, ForeignKey("stacks.id"), nullable=True)
    created_at = Column(TIMESTAMP(timezone=True),
        nullable=False, server_default=text('now()')) 
    updated_at = Column(
        TIMESTAMP(timezone=True), 
            nullable=False, server_default=text('now()'), server_onupdate=text("now()"))
    is_active = Column(Boolean)
    status = Column(SQLAlchemyEnum(UserStatus), default=UserStatus.TO_CONTACT, nullable=False)


    skills = relationship('Skill',secondary = "users_skills",  back_populates='users') 
    role = relationship("Role",  back_populates="users")
    tags = relationship('Tag', secondary='users_tags', back_populates='users')
    stack = relationship("Stack", back_populates='users')  
    projects = relationship('Project', back_populates='users')