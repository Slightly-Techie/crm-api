from db.database import Base
from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import relationship
from db.models.users import User

class Role(Base):
    __tablename__ = "roles"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)

    users = relationship("User", order_by=User.id, back_populates="role")