from db.database import Base
from sqlalchemy import Column, Integer, TIMESTAMP, text
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey


class TechieOTM(Base):
    __tablename__ = "techie_of_the_month"
    id = Column(Integer, primary_key=True, nullable=False)
    created_at = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()"))
    points = Column(Integer, nullable=False)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    user = relationship("User")
