from db.database import Base
from sqlalchemy import Column, String, Integer, Boolean, TIMESTAMP, text


class Endpoints(Base):
    __tablename__ = 'endpoints'
    id = Column(Integer, primary_key=True, nullable=False)
    endpoint = Column(String, nullable=False)
    status = Column(Boolean, nullable=False)
    toggled_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("now()"))
