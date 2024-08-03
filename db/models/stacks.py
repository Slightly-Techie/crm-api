from db.database import Base
from sqlalchemy import Column, String, Integer, TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func


class Stack(Base):
    __tablename__ = 'stacks'
    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String, nullable=False, unique=True)
    created_at = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(
        TIMESTAMP(timezone=True), nullable=False,
        server_default=func.now(), server_onupdate=func.now())

    users = relationship('User', back_populates='stack')
    technical_task = relationship("TechnicalTask", back_populates="stack")
    projects = relationship("Project", secondary="project_stacks", back_populates="stacks")
