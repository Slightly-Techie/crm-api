from db.database import Base
from sqlalchemy import Column, ForeignKey, String, Integer, TIMESTAMP, text
from sqlalchemy.orm import relationship



class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    role_id = Column(Integer, ForeignKey('roles.id'), nullable=False)
    role = Column(String, nullable=False)
    password = Column(String, nullable=False)
    github_profile = Column(String)
    twitter_profile = Column(String)
    linkedin_profile = Column(String)
    portfolio_url = Column(String)
    profile_pic_url = Column(String)
    created_at = Column(TIMESTAMP(timezone=True),
                        nullable=False, server_default=text('now()'))


class Role(Base):
    __tablename__ = "roles"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)


#Role.users = relationship("User", order_by=User.id, back_populates="role")
