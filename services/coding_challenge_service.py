from db.repository.coding_challenges import CodingChallengeRepository


class CodingChallengeService:
    def __init__(self, repository: CodingChallengeRepository):
        self.repository = repository

    def create(self, data: dict, user_id: int):
        return self.repository.create(data, user_id)

    def get_by_id(self, challenge_id: int):
        return self.repository.get_by_id(challenge_id)

    def get_latest(self):
        """Get the most recent coding challenge"""
        return self.repository.get_latest()

    def get_all_query(self):
        return self.repository.get_all_query()

    def update(self, challenge_id: int, data: dict):
        return self.repository.update(challenge_id, data)

    def delete(self, challenge_id: int):
        return self.repository.delete(challenge_id)
