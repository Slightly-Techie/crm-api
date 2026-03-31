from db.database import Base
from sqlalchemy import Column, String, Integer, TIMESTAMP, text, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey


class WeeklyMeeting(Base):
    __tablename__ = 'weekly_meetings'
    id = Column(Integer, primary_key=True, nullable=False)
    title = Column(String, nullable=False)
    meeting_url = Column(String, nullable=False)
    description = Column(String)
    is_active = Column(Boolean, server_default='true', nullable=False)
    scheduled_time = Column(TIMESTAMP(timezone=True), nullable=True)
    recurrence = Column(String, nullable=True)  # weekly, biweekly, monthly, none
    created_at = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()"))
    updated_at = Column(TIMESTAMP(timezone=True),
                        nullable=False, server_default=text('now()'))
    created_by = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    user = relationship("User")
