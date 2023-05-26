from db.database import Base
from sqlalchemy import Boolean, Column, String, Integer, TIMESTAMP, Text, text
from sqlalchemy.orm import relationship
from sqlalchemy import Column, ForeignKey, String, Integer, TIMESTAMP, text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.ext.associationproxy import association_proxy



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
    created_at = Column(TIMESTAMP(timezone=True),
                        nullable=False, server_default=text('now()'))

     
    created_at = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )
    is_active = Column(Boolean)
    skills = relationship('Skill',secondary = "users_skills",  back_populates='users') 
    role = relationship("Role",  back_populates="users")
    tags = relationship('Tag', secondary='users_tags', back_populates='users')



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
    
