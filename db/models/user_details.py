from sqlalchemy import Column,String,Integer,ForeignKey
from sqlalchemy.orm import relationship
from db.database import Base

class UserDetails:
    __tablename__ = "user_details"
    id = Column(Integer,primary_key=True)
    user_id = Column(Integer,ForeignKey('users.id',ondelete="CASCADE"))
    user = relationship(back_populates = 'userdetails')