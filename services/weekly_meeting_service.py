from db.repository.weekly_meetings import WeeklyMeetingRepository


class WeeklyMeetingService:
    def __init__(self, repository: WeeklyMeetingRepository):
        self.repository = repository

    def create(self, data: dict, user_id: int):
        return self.repository.create(data, user_id)

    def get_by_id(self, meeting_id: int):
        return self.repository.get_by_id(meeting_id)

    def get_active(self):
        """Get the currently active meeting"""
        return self.repository.get_active()

    def get_all_query(self):
        return self.repository.get_all_query()

    def update(self, meeting_id: int, data: dict):
        return self.repository.update(meeting_id, data)

    def delete(self, meeting_id: int):
        return self.repository.delete(meeting_id)
