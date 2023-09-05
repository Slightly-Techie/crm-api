from db.database import Base
from sqlalchemy import Boolean, Column, String, Integer, TIMESTAMP, Text, text
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey
from sqlalchemy.sql import func



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


    skills = relationship('Skill',secondary = "users_skills",  back_populates='users') 
    role = relationship("Role",  back_populates="users")
    tags = relationship('Tag', secondary='users_tags', back_populates='users')
    stack = relationship("Stack", back_populates='users')  


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
