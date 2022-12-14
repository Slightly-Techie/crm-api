from db.database import Base
from sqlalchemy import Column, String, Integer, TIMESTAMP, text
from sqlalchemy.orm import relationship


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    password = Column(String, nullable=False)
    userdetails = relationship(back_populates = 'user')
    created_at = Column(TIMESTAMP(timezone=True),
                        nullable=False, server_default=text('now()'))
