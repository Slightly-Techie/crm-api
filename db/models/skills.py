
from db.database import Base
from sqlalchemy import Column, String, Table, Integer, TIMESTAMP, text, ForeignKey

from sqlalchemy.orm import relationship
from sqlalchemy.ext.associationproxy import association_proxy




class UserSkills(Base):
    __tablename__ = 'users_skills'
    user_id = Column(Integer, ForeignKey('users.id'), primary_key = True)
    skill_id = Column(Integer, ForeignKey('skills.id'), primary_key = True)
    users = relationship('User',  back_populates='skills')  
    skills = relationship('Skill',  back_populates='users')   
                 




class Skill(Base):
    __tablename__ = 'skills'
    id = Column(Integer, primary_key = True, index = True)
    name = Column(String)
    user_id = Column(Integer, ForeignKey('users.id'))
    created_at = Column(TIMESTAMP(timezone=True),
                        nullable=False, server_default=text('now()'))
    updated_at = Column(TIMESTAMP(timezone=True),
                        nullable=False, server_default=text('now()'))

    users = relationship('UserSkills', back_populates='skills')  

    users_skills = association_proxy(target_collection='skills', attr='name' )