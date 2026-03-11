from fastapi import HTTPException, status

from api.api_models.user import TechieOTMResponse
from db.repository.techieotm import TechieOTMRepository
from db.repository.users import UserRepository


class TechieOTMService:
    def __init__(self, techieotm_repo: TechieOTMRepository, user_repo: UserRepository):
        self.techieotm_repo = techieotm_repo
        self.user_repo = user_repo

    def create(self, user_id: int, points: int) -> TechieOTMResponse:
        if self.techieotm_repo.get_for_current_month():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Techie of the Month already posted for the current month"
            )
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        entry = self.techieotm_repo.create(user_id, points)
        return TechieOTMResponse(id=entry.id, user=user, points=entry.points, created_at=entry.created_at)

    def get_latest(self) -> TechieOTMResponse:
        entry = self.techieotm_repo.get_latest()
        if not entry:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No Techie of the Month found")
        user = self.user_repo.get_by_id(entry.user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return TechieOTMResponse(id=entry.id, user=user, points=entry.points, created_at=entry.created_at)

    def get_all_query(self):
        return self.techieotm_repo.get_all_paginated_query()
