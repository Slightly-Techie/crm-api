from db.database import Base
from sqlalchemy import Column, String, Integer, TIMESTAMP, Text, text
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey


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
    
    users: list = relationship("User", back_populates="projects")

