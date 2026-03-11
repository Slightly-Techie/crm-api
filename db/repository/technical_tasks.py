from typing import Optional

from db.models.technical_task import TechnicalTask, TechnicalTaskSubmission
from db.repository.base import BaseRepository


class TechnicalTaskRepository(BaseRepository):
    model = TechnicalTask

    def get_by_stack_and_level(self, stack_id: int, experience_level: str) -> Optional[TechnicalTask]:
        return self.db.query(TechnicalTask).filter(
            TechnicalTask.stack_id == stack_id,
            TechnicalTask.experience_level == experience_level
        ).first()

    def get_all(self) -> list[TechnicalTask]:
        return self.db.query(TechnicalTask).all()

    def create(self, data: dict) -> TechnicalTask:
        task = TechnicalTask(**data)
        return self.save(task)

    def update(self, task_id: int, payload: dict) -> TechnicalTask:
        query = self.db.query(TechnicalTask).filter(TechnicalTask.id == task_id)
        query.update(payload)
        self.db.commit()
        return query.first()

    def delete_by_id(self, task_id: int) -> None:
        self.db.query(TechnicalTask).filter(TechnicalTask.id == task_id).delete()
        self.db.commit()


class TechnicalTaskSubmissionRepository(BaseRepository):
    model = TechnicalTaskSubmission

    def get_all(self) -> list[TechnicalTaskSubmission]:
        return self.db.query(TechnicalTaskSubmission).all()

    def get_by_user_id(self, user_id: int) -> Optional[TechnicalTaskSubmission]:
        return self.db.query(TechnicalTaskSubmission).filter(
            TechnicalTaskSubmission.user_id == user_id
        ).first()

    def get_existing_for_user(self, user_id: int) -> Optional[TechnicalTaskSubmission]:
        return self.db.query(TechnicalTaskSubmission).filter(
            TechnicalTaskSubmission.user_id == user_id
        ).first()

    def create(self, task_id: int, user_id: int, data: dict) -> TechnicalTaskSubmission:
        submission = TechnicalTaskSubmission(task_id=task_id, user_id=user_id, **data)
        return self.save(submission)

    def update(self, submission_id: int, payload: dict) -> TechnicalTaskSubmission:
        query = self.db.query(TechnicalTaskSubmission).filter(
            TechnicalTaskSubmission.id == submission_id
        )
        query.update(payload)
        self.db.commit()
        return query.first()
