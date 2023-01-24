from sqlalchemy import Column, String, Table, Integer, TIMESTAMP, text, ForeignKey
from db.database import Base
from sqlalchemy.orm import relationship


users_skills= Table('users_skills', Base.metadata,
    Column('user_id', ForeignKey('users.id'), primary_key = True),
    Column('skill_id', ForeignKey('skills.id'), primary_key = True)
)

class Skill(Base):
    __tablename__ = 'skills'

    id = Column(Integer, primary_key = True, index = True)
    name = Column(String)
    user_id = Column(Integer, ForeignKey('users.id'))
    created_at = Column(TIMESTAMP(timezone=True),
                        nullable=False, server_default=text('now()'))
    updated_at = Column(TIMESTAMP(timezone=True),
                        nullable=False, server_default=text('now()'))

    users = relationship('User', secondary="users_skills", black_populates='skills')                   