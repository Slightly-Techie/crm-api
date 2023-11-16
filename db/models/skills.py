from db.database import Base
from sqlalchemy import Column, String, Integer, TIMESTAMP, text
from sqlalchemy.orm import relationship



class Skill(Base):
    __tablename__ = 'skills'
    id = Column(Integer, primary_key = True, index = True)
    name = Column(String)
    created_at = Column(TIMESTAMP(timezone=True),
                        nullable=False, server_default=text('now()'))
    updated_at = Column(TIMESTAMP(timezone=True),
                        nullable=False, server_default=text('now()'))

    users = relationship('User', secondary = "users_skills", back_populates='skills')