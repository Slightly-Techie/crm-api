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
    managed_projects = relationship("Project", back_populates="manager")
    projects = relationship("Project", secondary="users_projects", back_populates="users")


class Role(Base):
    __tablename__ = "roles"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)

    users = relationship("User", order_by=User.id, back_populates="role")


class UserSkills(Base):
    __tablename__ = 'users_skills'
    user_id = Column(Integer, ForeignKey('users.id'), primary_key = True)
    skill_id = Column(Integer, ForeignKey('skills.id'), primary_key = True)
   
class Skill(Base):
    __tablename__ = 'skills'
    id = Column(Integer, primary_key = True, index = True)
    name = Column(String)
    user_id = Column(Integer, ForeignKey('users.id'))
    created_at = Column(TIMESTAMP(timezone=True),
                        nullable=False, server_default=text('now()'))
    updated_at = Column(TIMESTAMP(timezone=True),
                        nullable=False, server_default=text('now()'))

    users = relationship('User', secondary = "users_skills", back_populates='skills')  


class UserTag(Base):
    __tablename__ = 'users_tags'
    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    tag_id = Column(Integer, ForeignKey('tags.id'), primary_key=True)


class Tag(Base):
    __tablename__ = 'tags'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    created_at = Column(TIMESTAMP(timezone=True),
                        nullable=False, server_default=text('now()'))
    updated_at = Column(TIMESTAMP(timezone=True),
                        nullable=False, server_default=text('now()'))
    users = relationship('User', secondary='users_tags', back_populates='tags')


class Feed(Base):
    __tablename__ = 'feeds'
    id = Column(Integer, primary_key=True, nullable=False)
    content = Column(String, nullable=False)
    feed_pic_url = Column(String)
    created_at = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()"))
    updated_at = Column(TIMESTAMP(timezone=True),
                        nullable=False, server_default=text('now()'))
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    user = relationship("User")  

class Stack(Base):
    __tablename__ = 'stacks'
    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String, nullable=False, unique=True)
    created_at = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=func.now(), server_onupdate=func.now())

    users = relationship('User', back_populates='stack')


class TechieOTM(Base):
    __tablename__ = "techie_of_the_month"
    id = Column(Integer, primary_key=True, nullable=False)
    created_at = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()"))
    points = Column(Integer, nullable=False)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    user = relationship("User")


class Announcement(Base):
    __tablename__ = 'announcements'
    id = Column(Integer, primary_key=True, nullable=False)
    title = Column(String, nullable=False)
    content = Column(String, nullable=False)
    image_url = Column(String)
    created_at = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()"))
    updated_at = Column(TIMESTAMP(timezone=True),
                        nullable=False, server_default=text('now()'))
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    user = relationship("User")


class Project(Base):
    __tablename__ = 'projects'
    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    created_at = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()"))
    updated_at = Column(TIMESTAMP(timezone=True),
                        nullable=False, server_default=text('now()'))
    
    manager_id = Column(Integer, ForeignKey("users.id"))
    manager = relationship("User", back_populates="managed_projects")
    users = relationship("User", secondary="users_projects", back_populates="projects")


class UserProject(Base):
    __tablename__ = 'users_projects'
    project_id = Column(Integer, ForeignKey("projects.id"), primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
