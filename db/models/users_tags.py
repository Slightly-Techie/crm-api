from db.database import Base
from sqlalchemy import Column, Integer
from sqlalchemy import ForeignKey


class UserTag(Base):
    __tablename__ = 'users_tags'
    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    tag_id = Column(Integer, ForeignKey('tags.id'), primary_key=True)
