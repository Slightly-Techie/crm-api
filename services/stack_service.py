from fastapi import HTTPException, status

from db.models.stacks import Stack
from db.repository.stacks import StackRepository


class StackService:
    def __init__(self, stack_repo: StackRepository):
        self.stack_repo = stack_repo

    def list_stacks(self, page: int = 1, limit: int = 100) -> list[Stack]:
        return self.stack_repo.list(page=page, limit=limit)

    def create(self, name: str) -> Stack:
        try:
            return self.stack_repo.create(name)
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    def get_by_id(self, stack_id: int) -> Stack:
        stack = self.stack_repo.get_by_id(stack_id)
        if not stack:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Stack not found")
        return stack

    def update(self, stack_id: int, payload: dict) -> Stack:
        stack = self.get_by_id(stack_id)
        try:
            return self.stack_repo.update(stack, payload)
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    def delete(self, stack_id: int) -> None:
        stack = self.get_by_id(stack_id)
        self.stack_repo.delete_by_id(stack)
