from sqlalchemy.orm import Session
from db.models.coding_challenges import CodingChallenge


class CodingChallengeRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, data: dict, user_id: int) -> CodingChallenge:
        challenge = CodingChallenge(**data, created_by=user_id)
        self.db.add(challenge)
        self.db.commit()
        self.db.refresh(challenge)
        return challenge

    def get_by_id(self, challenge_id: int) -> CodingChallenge | None:
        return self.db.query(CodingChallenge).filter(CodingChallenge.id == challenge_id).first()

    def get_latest(self) -> CodingChallenge | None:
        """Get the most recent coding challenge"""
        return (
            self.db.query(CodingChallenge)
            .order_by(CodingChallenge.posted_at.desc())
            .first()
        )

    def get_all_query(self):
        return self.db.query(CodingChallenge).order_by(CodingChallenge.posted_at.desc())

    def update(self, challenge_id: int, data: dict) -> CodingChallenge:
        challenge = self.get_by_id(challenge_id)
        if not challenge:
            raise ValueError(f"Challenge with id {challenge_id} not found")

        for key, value in data.items():
            setattr(challenge, key, value)

        self.db.commit()
        self.db.refresh(challenge)
        return challenge

    def delete(self, challenge_id: int) -> None:
        challenge = self.get_by_id(challenge_id)
        if not challenge:
            raise ValueError(f"Challenge with id {challenge_id} not found")

        self.db.delete(challenge)
        self.db.commit()
