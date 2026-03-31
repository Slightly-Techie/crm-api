from sqlalchemy.orm import Session
from db.models.weekly_meetings import WeeklyMeeting


class WeeklyMeetingRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, data: dict, user_id: int) -> WeeklyMeeting:
        meeting = WeeklyMeeting(**data, created_by=user_id)
        self.db.add(meeting)
        self.db.commit()
        self.db.refresh(meeting)
        return meeting

    def get_by_id(self, meeting_id: int) -> WeeklyMeeting | None:
        return self.db.query(WeeklyMeeting).filter(WeeklyMeeting.id == meeting_id).first()

    def get_active(self) -> WeeklyMeeting | None:
        """Get the most recent active meeting"""
        return (
            self.db.query(WeeklyMeeting)
            .filter(WeeklyMeeting.is_active == True)
            .order_by(WeeklyMeeting.created_at.desc())
            .first()
        )

    def get_all_query(self):
        return self.db.query(WeeklyMeeting).order_by(WeeklyMeeting.created_at.desc())

    def update(self, meeting_id: int, data: dict) -> WeeklyMeeting:
        meeting = self.get_by_id(meeting_id)
        if not meeting:
            raise ValueError(f"Meeting with id {meeting_id} not found")

        for key, value in data.items():
            setattr(meeting, key, value)

        self.db.commit()
        self.db.refresh(meeting)
        return meeting

    def delete(self, meeting_id: int) -> None:
        meeting = self.get_by_id(meeting_id)
        if not meeting:
            raise ValueError(f"Meeting with id {meeting_id} not found")

        self.db.delete(meeting)
        self.db.commit()
