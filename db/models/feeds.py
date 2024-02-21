from db.database import Base
from sqlalchemy import Column, String, Integer, TIMESTAMP, text
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey


class Feed(Base):
    __tablename__ = 'feeds'
    id = Column(Integer, primary_key=True, nullable=False)
    content = Column(String, nullable=False)
    feed_pic_url = Column(String)
    created_at = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()"))
    updated_at = Column(TIMESTAMP(timezone=True),
                        nullable=False, server_default=text('now()'))
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    user = relationship("User")
